import React, { useEffect } from "react";
import { DefaultPluginUISpec } from 'molstar/lib/mol-plugin-ui/spec';
import { createPluginUI } from 'molstar/lib/mol-plugin-ui';
import { renderReact18 } from 'molstar/lib/mol-plugin-ui/react18';
import { PluginUIContext } from "molstar/lib/mol-plugin-ui/context";
import { Asset } from "molstar/lib/mol-util/assets";
import { StateTransforms } from "molstar/lib/mol-plugin-state/transforms";
import { MolScriptBuilder as MS } from "molstar/lib/mol-script/language/builder";
import { StateObjectSelector } from "molstar/lib/mol-state";
import { Script } from "molstar/lib/mol-script/script";
import { Bundle } from "molstar/lib/mol-model/structure/structure/element/bundle";
import { Color } from "molstar/lib/mol-util/color";
import { StructureSelection, Structure, StructureProperties } from "molstar/lib/mol-model/structure";
import { PluginConfig } from "molstar/lib/mol-plugin/config";
import { createStructureRepresentationParams } from "molstar/lib/mol-plugin-state/helpers/structure-representation-params";
import { StructureElement } from "molstar/lib/mol-model/structure";
import { PLDDTConfidenceColorThemeProvider } from "molstar/lib/extensions/model-archive/quality-assessment/color/plddt";
import { getColorListFromName } from 'molstar/lib/mol-util/color/lists';

import "./assets/style.css";
import { ColorParameters, ContigSegment, SequenceSelection, StreamlitComponentValue, Representation, StructureVisualization, BondVisualization } from "./types";
import { toBytesFloat64 } from "./utils";

interface Props {
  divName: string;
  showControls: boolean;
  selectionMode: boolean;
  contigs: ContigSegment[][];
  highlightedContig: ContigSegment & { structureIdx: number; } | null;
  updateStreamlitComponentValue: (value: StreamlitComponentValue) => void;
  structures: StructureVisualization[];
  forceReload?: boolean;
}

interface InnerProps {
  plugin: PluginUIContext | null;
  loadingPlugin: boolean;
  loadingPdb: boolean;
  structures: StateObjectSelector[];
  representations: StateObjectSelector[][];
}

// TODO: review if there is no other way to do this (useMemo, useRef or something?)
// right now it works, we do not want useState as this would infinitely reload
const innerProps: InnerProps = { plugin: null, structures: [], representations: [], loadingPlugin: false, loadingPdb: false };

const isMobile = typeof navigator !== "undefined" && /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);

const typeParamsFor = (repType: string, color: string, colorParams: ColorParameters | null): Record<string, unknown> | undefined => {
  // improve performance for gaussian surface representation on mobile by disabling GPU usage, which can cause freezes/crashes due to memory issues
  if (isMobile && repType === "gaussian-surface") return { tryUseGpu: false };
  // use white border color for all labels
  if (repType === "label") return { borderColor: Color(0xffffff), sizeFactor: 1.1 };
  return undefined;
};

function MolstarCustomComponent(props: Props) {

  const initPlugin = async () => {
    if (innerProps.loadingPlugin || innerProps.plugin) return; // plugin is already being loaded or loaded
    const wrapper = document.getElementById(props.divName)!;
    innerProps.loadingPlugin = true;
    // auto-enable animation controls when any structure has a trajectory
    const hasTrajectory = props.structures?.some(s => s.trajectory && s.trajectory_format) ?? false;
    const plugin = await createPluginUI({
      target: wrapper,
      render: renderReact18,
      spec: {
        ...DefaultPluginUISpec(),
        layout: {
          initial: {
            // showControls is actually about expanding the layout (showing the panels), not about showing the buttons
            // do not confuse with isExpanded which is about fullscreen mode :)
            showControls: props.showControls,
            // show panels in multiple columns, never in one column
            controlsDisplay: "landscape",
            regionState: {
              // sequence panel, keep it visible when showing panels
              top: "full",
              // left panel shows component tree, always hide it
              left: "hidden",
              // bottom panel shows log messages, always hide it
              bottom: "hidden",
              // right panel shows structure tools, representation
              // keep it visible when showing panels
              right: "full"
            }
          }
        },
        components: {
          remoteState: 'none'
        },
        config: [
          [PluginConfig.VolumeStreaming.Enabled, true],
          [PluginConfig.Viewport.ShowExpand, false],            // hide the full screen button as we use the fullscreen
          [PluginConfig.Viewport.ShowToggleFullscreen, true],
          [PluginConfig.Viewport.ShowAnimation, hasTrajectory], // show animation controls only for trajectories
          [PluginConfig.Viewport.ShowXR, false],                // we also do not need AR/VR
          [PluginConfig.Viewport.ShowControls, true],
          [PluginConfig.Viewport.ShowSettings, true],
          [PluginConfig.Viewport.ShowSelectionMode, true],
        ],
      }
    });

    // Add a possibility to color by pLDDT
    plugin.representation.structure.themes.colorThemeRegistry.add(PLDDTConfidenceColorThemeProvider);

    // Turn on selection mode if requested
    if (props.selectionMode) {
      plugin.selectionMode = true;

      // When clicking the canvas, the selection is updated as well. We should reflect this in the component state as well.
      plugin.canvas3d?.interaction.click.subscribe(async (e) => {
        updateStreamlitSelections(plugin);
      });

      // Subscribe to user selection events
      plugin.behaviors.interaction.click.subscribe(async (e) => {
        updateStreamlitSelections(plugin);
      });
    }

    // Enable zooming in with Ctrl
    plugin.behaviors.canvas3d.initialized.subscribe((v) => {
      if (v) {
        const modifiers = plugin.canvas3d?.attribs.trackball.bindings.scrollZoom.triggers[0].modifiers;
        if (modifiers) {
          modifiers.control = true;
        }

        // Do not always prevent scrolling, only prevent it if ctrl key is pressed
        plugin.canvas3dContext!.input.noScroll = false;
        wrapper.addEventListener("wheel",
          (event) => {
            if (event.ctrlKey) {
              event.preventDefault();
            }
          },
          false
        );
      }
    });

    innerProps.plugin = plugin;
    innerProps.loadingPlugin = false;
    loadData(props.structures);
  };

  const updateStreamlitSelections = (plugin: PluginUIContext) => {
    const entry = plugin.managers.structure.selection.state.entries.entries().next().value;
    if (!entry || !entry[1].selection.elements[0]) {
      props.updateStreamlitComponentValue({
        sequenceSelections: []
      });
      return;
    }

    const selections: SequenceSelection[] = [];

    // do the selection across chains
    for (let chainIdx = 0; chainIdx < entry[1].selection.elements.length; chainIdx++) {
      // this is a bit messy... we want to get information about the selected atoms, but it might be represented
      // either as a Int32Array or as a number - in the first case we just convert it to a normal array
      // in the second case we need to get the float64 representation and convert it to Int32Array
      // and then get the range defined by this array
      let atomsArray: number[];
      if (typeof entry[1].selection.elements[chainIdx].indices === "number") {
        // @ts-ignore
        const tmp = new Int32Array(toBytesFloat64(entry[1].selection.elements[chainIdx].indices));
        const startIdx = tmp[0];
        // do not consider the next residue, that's why the - 1
        const endIdx = tmp[1] - 1;
        atomsArray = getRange([startIdx, endIdx]);
      } else {
        // @ts-ignore
        atomsArray = Array.from(entry[1].selection.elements[chainIdx].indices);
      }
      // and now for the atoms we have to find the right mapping...
      atomsArray = atomsArray.map((atom: number) => entry[1].selection.elements[chainIdx].unit.elements[atom]);
      // note that here we have to map the atoms + 1 because it's indexed from 0
      const newSelection = getAtomSelection(plugin, atomsArray.map((value: any) => value + 1), entry[1].selection.elements[chainIdx].unit.chainGroupId, 0); // TODO: currently supporting only highlighting of one structure
      const s = StructureSelection.unionStructure(newSelection);

      let currentChain = "?";
      let currentResidues: number[] = [];

      Structure.eachAtomicHierarchyElement(s, {
        residue: l => currentResidues.push(StructureProperties.residue.auth_seq_id(l)),
        chain: c => currentChain = StructureProperties.chain.auth_asym_id(c)
      });

      selections.push({
        chainId: currentChain,
        residues: currentResidues
      });
    }

    props.updateStreamlitComponentValue({
      sequenceSelections: selections
    });
  };

  // parses selection strings like "A" (whole chain), "A123" (single residue), "A123-456" (residue range)
  // into structured SequenceSelection objects with chain ID and optional residue list
  const parseSelections = (selections: string[]): SequenceSelection[] => {
    const expanded = selections.flatMap((sel) => sel.split(/[,/]/));
    const trimmed = expanded.map((sel) => sel.trim()).filter((e) => e !== "");

    const parsedSelections = trimmed.map(item => {
      // group 1: chain letter(s), e.g. "A" or "AB"
      // group 2: start residue number (optional), e.g. "123"
      // group 3: end residue number (optional, requires group 2), e.g. "456" in "A123-456"
      const regex = /^([A-Z]+)(?:(\d+)(?:-(\d+))?)?$/;

      const match = item.match(regex);

      if (match) {
        if (match[2]) {
          // specific residue(s): "A123" becomes [123], "A123-456" becomes [123, 124, ..., 456]
          const start = parseInt(match[2]);
          return {
            chainId: match[1],
            residues: getRange([start, match[3] ? parseInt(match[3]) : start])
          };
        }
        // whole chain selection, e.g. "A" — no residue filtering
        return {
          chainId: match[1],
          residues: null
        };
      } else {
        throw new Error(`Invalid format for selection: ${item}`);
      }
    });

    return parsedSelections;
  };

  const addSelections = async (selections: string[] | null, structureIdx: number) => {
    if (!innerProps.plugin) return;
    if (!selections || selections.length === 0) return;

    const parsed = parseSelections(selections);

    for (const parsedSel of parsed) {
      if (!parsedSel.residues) continue;
      const sel = getSelectionFromChainAuthId(innerProps.plugin!, parsedSel.chainId, parsedSel.residues, structureIdx);
      const loci = StructureSelection.toLociWithSourceUnits(sel);
      innerProps.plugin.managers.structure.selection.fromLoci("add", loci);
    }

    props.updateStreamlitComponentValue({
      sequenceSelections: parsed
    });
  };

  const removeLoadedData = async () => {
    if (innerProps.loadingPdb) return;
    for (const structure of innerProps.structures) {
      if (structure) {
        const update = innerProps.plugin!.build();
        update.delete(structure);
        await update.commit();
      }
    }

    innerProps.structures = [];
    innerProps.representations = [];
  };

  const loadData = async (structures: StructureVisualization[]) => {
    if (innerProps.loadingPdb) return;
    innerProps.loadingPdb = true;

    try {
      innerProps.representations = new Array(structures.length).fill([]);
      innerProps.structures = new Array(structures.length).fill(null);

      for (let i = 0; i < structures.length; i++) {
        const structToLoad = structures[i];
        await loadPdb(structToLoad, i);
        if (props.contigs[i] && props.contigs[i].length) {
          await overPaintStructureByContigs(i);
          addContigLabelsAtEnds(i);
          addContigLabelsInMiddle(i);
          addLinesBetweenContigs(i);
        }
        if ("highlighted_selections" in structures[i]) {
          addSelections(structures[i].highlighted_selections, i);
        }
        if (structures[i].representations) {
          await addStructureRepresentations(structures[i].representations!, i);
        }
        if (structures[i].auto_zoom_chains) {
          await autoZoomToChains(structures[i].auto_zoom_chains!, structures[i].auto_zoom_extra_radius, i);
        }
        if ("bonds" in structures[i]) {
          await addBondsVisualizations(structures[i].bonds, i);
        }
      }
    } finally {
      innerProps.loadingPdb = false;
    }
  };

  const isUrl = (pdb: string) => {
    return pdb.startsWith("http://") || pdb.startsWith("https://");
  };

  const getSizeForRepType = (repType: string) => {
      if (repType == "cartoon" || repType == "label") {
          return "uniform";
      } else {
          return "physical";
      }
  };

  const getColorParameters = (repType: string, color: string, colorParams: ColorParameters | null, plugin: PluginUIContext) => {
    if (repType === "label" && (color === "chain-id" || color === "uniform" && !colorParams?.value)) {
      // use black color for labels when no color is provided or when chain-id representation is used
      return { color: "uniform", colorParams: { value: Color(0x000000) }};
    }
    if (color === "uniform") {
      return {
        color,
        colorParams: {
          ...colorParams,
          ...{
            value: Color(colorParams?.value ? parseInt(colorParams.value, 16) : 0xffffff)
          }
        }
      } as const;
    }
    else if (color === "chain-id") {
      return {
        color,
        colorParams: {
          ...colorParams,
          ...{
            // see https://github.com/molstar/molstar/blob/master/src/mol-util/color/lists.ts
            palette: { name: "colors", params: { list: { colors: getColorListFromName(colorParams?.palette || "pastel-1").list } } }
          }
        }
      } as const;
    }
    else if (color === "plddt") {

      const PLDDTLabelProvider = {
        label: (loci: any) => {
          if (StructureElement.Loci.is(loci)) {
            const loc = StructureElement.Loci.getFirstLocation(loci);
            if (!loc) return;
            const bFactor = StructureProperties.atom.B_iso_or_equiv(loc);
            return `pLDDT: ${bFactor}`;
          }
          return "";
        },
      };

      // add a label provider including the pLDDT value
      plugin.managers.lociLabels.addProvider(PLDDTLabelProvider);

      // return {
      //   color: "uncertainty", // the scores are taken from the B-factor value
      //   colorParams: {
      //     value: 0.5,
      //     domain: [0, 100], // this is not exactly the pLDDT color scheme, but works fine
      //     list: {
      //       colors: [Color(0x0053d6), Color(0x65cbf3), Color(0xffdb13), Color(0xff7d45)],
      //     },
      //   }
      // } as const;

      return {
        color: "plddt-confidence"
      } as const;
    }
    else if (color === "interaction-type") {
      return {
        color: "interaction-type",
        colorParams: {}
      } as const;
    }

    // default
    return { color, colorParams } as const;
  };

  const loadPdb = async (structureToLoad: StructureVisualization, structureIdx: number) => {
    const plugin = innerProps.plugin!;
    if (!plugin) {
      return;
    }

    if (innerProps.structures && innerProps.structures[structureIdx]) {
      // remove current structure if any was present before
      const update = plugin.build();
      update.delete(innerProps.structures[structureIdx]);
      await update.commit();
    }

    let dataSelector: StateObjectSelector;
    let trajectory: StateObjectSelector;

    // detect the structure format: explicit > URL extension > content heuristic
    const detectFormat = (): string => {
      if (structureToLoad.data_format) return structureToLoad.data_format;
      if (isUrl(structureToLoad.data)) {
        const url = structureToLoad.data.toLowerCase();
        if (/\.pdb$/.test(url)) return "pdb";
        if (/\.bcif$/.test(url)) return "bcif";
        if (/\.gro$/.test(url)) return "gro";
        if (/\.mol2$/.test(url)) return "mol2";
        if (/\.mol$/.test(url)) return "mol";
        if (/\.sdf$/.test(url)) return "sdf";
        if (/\.xyz$/.test(url)) return "xyz";
        return "mmcif";
      }
      if (/^loop_$/m.test(structureToLoad.data)) return "mmcif";
      if (/^ATOM /m.test(structureToLoad.data)) return "pdb";
      throw new Error("Structure format not recognized, please pass data_format explicitly");
    };

    const format = detectFormat();
    // bcif is the binary form of mmCIF; molstar's parseTrajectory accepts "mmcif" for both
    // and switches based on whether the underlying data object is String or Binary.
    const isBinaryFormat = format === "bcif";
    // treat bcif as mmcif for the parser
    const parserFormat = format === "bcif" ? "mmcif" : format;

    if (isUrl(structureToLoad.data)) {
      dataSelector = await plugin.builders.data.download({
        url: Asset.Url(structureToLoad.data),
        isBinary: isBinaryFormat,
      }, { state: { isGhost: true } });

      trajectory = await plugin.builders.structure.parseTrajectory(dataSelector, parserFormat as any);
    }
    else if (isBinaryFormat) {
      // base64-encoded binary payload (e.g. bcif)
      const binaryData = Uint8Array.from(atob(structureToLoad.data), c => c.charCodeAt(0));
      dataSelector = await plugin.builders.data.rawData({ data: binaryData });
      trajectory = await plugin.builders.structure.parseTrajectory(dataSelector, parserFormat as any);
    }
    else {
      // for PDB format, prepend COMPND records for representations that have a label
      let structureContent = structureToLoad.data;
      if (format === "pdb") {
        const stringsToPrepend: string[] = [];
        const chainLetterRegex = /^[A-Z]+$/;

        if (structureToLoad.representations) {
          for (let i = 0; i < structureToLoad.representations.length; i++) {
            const rep = structureToLoad.representations[i];
            if (rep.label) {
              const sel = typeof rep.selection === "string" ? rep.selection : rep.selection[0];
              if (chainLetterRegex.test(sel)) {
                const stringToPrepend = `COMPND    MOL_ID: ${i + 1};\nCOMPND   2 MOLECULE: ${rep.label};\nCOMPND   3 CHAIN: ${sel};`;
                stringsToPrepend.push(stringToPrepend);
              }
            }
          }
        }

        if (stringsToPrepend.length > 0) {
          structureContent = stringsToPrepend.join("\n") + "\n" + structureContent;
        }
      }

      dataSelector = await plugin.builders.data.rawData({
        data: structureContent
      });

      trajectory = await plugin.builders.structure.parseTrajectory(dataSelector, parserFormat as any);
    }

    // if trajectory data is provided (e.g. TRR), combine the topology model with coordinates.
    // trajectory arrives as a base64 string
    if (structureToLoad.trajectory && structureToLoad.trajectory_format) {
      const binaryData = Uint8Array.from(atob(structureToLoad.trajectory), c => c.charCodeAt(0));
      const coordData = await plugin.builders.data.rawData({
        data: binaryData
      });

      // pick the right coordinate parser for the trajectory format
      const coordTransforms = {
        trr: StateTransforms.Model.CoordinatesFromTrr,
        xtc: StateTransforms.Model.CoordinatesFromXtc,
        dcd: StateTransforms.Model.CoordinatesFromDcd,
        nctraj: StateTransforms.Model.CoordinatesFromNctraj,
      } as const;
      const coordTransform = coordTransforms[structureToLoad.trajectory_format];

      const coords = await plugin.build()
        .to(coordData)
        .apply(coordTransform)
        .commit();

      const topologyModel = await plugin.builders.structure.createModel(trajectory);

      // combine topology model + coordinate frames into a multi-frame trajectory
      // dependsOn is required so the state tree can resolve the referenced nodes
      const dependsOn = [topologyModel.ref, coords.ref];
      trajectory = await plugin.build()
        .toRoot()
        .apply(StateTransforms.Model.TrajectoryFromModelAndCoordinates, {
          modelRef: topologyModel.ref,
          coordinatesRef: coords.ref,
        }, { dependsOn })
        .commit();
    }

    const model = await plugin.builders.structure.createModel(trajectory);
    const structure = await plugin.builders.structure.createStructure(model, { name: 'model', params: {} });

    const hasExplicitReps = !!structureToLoad.representations && structureToLoad.representations.length > 0;
    const polymer = hasExplicitReps
      ? await plugin.builders.structure.tryCreateComponentFromExpression(
        structure,
        buildPolymerExcludingReps(structureToLoad.representations),
        'polymer-excl',
        { label: 'Polymer' }
      )
      : await plugin.builders.structure.tryCreateComponentStatic(structure, 'polymer');

    if (polymer && structureToLoad.representation_type) {
      const repTypes = structureToLoad.representation_type.split("+") as string[];
      for (const repType of repTypes) {
        const isCartoon = repType === "cartoon";
        const extraTypeParams = typeParamsFor(repType, structureToLoad.color, structureToLoad.color_params);
        // @ts-ignore - here we are using the getColorParameters which raises an error but is in fact correct
        const representation: StateObjectSelector = await plugin.builders.structure.representation.addRepresentation(polymer, {
          type: repType as any,
          size: getSizeForRepType(repType),
          ...(extraTypeParams ? { typeParams: extraTypeParams as any } : {}),
          ...getColorParameters(repType, structureToLoad.color, structureToLoad.color_params, plugin),
        });

        innerProps.representations[structureIdx].push(representation);
      }
    }

    innerProps.structures[structureIdx] = structure;

    if (structureToLoad.color_params?.positions) {
      await applyPositionalOverpaint(structureToLoad.color_params.positions, structureIdx);
    }

    if (structureToLoad.representation_type) {
      const shownGroups = ["ligand", "nucleic", "lipid", "branched", "non-standard", "coarse"] as const;

      for (const group of shownGroups) {
        const component = await plugin.builders.structure.tryCreateComponentStatic(structure, group);
        if (component) {
          plugin.builders.structure.representation.addRepresentation(component, {
            type: 'ball-and-stick',
          });
        }

        if (group === "branched") {
          if (component) {
            plugin.builders.structure.representation.addRepresentation(component, {
              type: 'carbohydrate',
            });
          }
        }
      }
    }

    return [model, structure, polymer];
  };

  const overPaintStructureByContigs = async (structureIdx: number) => {
    if (!innerProps.plugin || !innerProps.structures || !innerProps.representations) return;

    const builder = innerProps.plugin.state.data.build();

    type Params = {
      bundle: Bundle;
      color: Color;
      clear: boolean;
    };

    const params: Params[] = [];

    props.contigs[structureIdx].forEach((e) => {
      const range = Array.from(new Array(e.end - e.start + 1), (_, i) => i + e.start);
      const bundle = Bundle.fromSelection(getSelectionFromChainAuthId(innerProps.plugin!, e.chain, range, structureIdx));
      params.push({ bundle: bundle, color: Color.fromHexString(e.color!.replace("#", "0x")), clear: false });
    });

    innerProps.representations[structureIdx].map(
      rep => builder.to(rep).apply(StateTransforms.Representation.OverpaintStructureRepresentation3DFromBundle, { layers: params })
    );

    await builder.commit();
  };

  const getRange = (arr: number[]) => {
    const start = arr[0];
    const end = arr[arr.length - 1] - start + 1;
    const range = Array.from(new Array(end), (_, i) => i + start);

    return range;
  };

  const addContigLabelsAtEnds = (structureIdx: number) => {
    if (!innerProps.plugin) return;

    // keep just the first and last elements of the array

    const segments = props.contigs[structureIdx].filter(e => e.start);
    const arrays: number[] = segments.flatMap((e: ContigSegment) => [e.start, e.end]);
    const labels: string[] = segments.flatMap((e: ContigSegment) => [
      e.hide_labels ? "" : e.start_label || "",
      e.hide_labels ? "" : e.end_label || ""
    ]);
    const chains: string[] = segments.flatMap((e: ContigSegment) => [e.chain, e.chain]);
    const textColors: Color[] = segments.flatMap((e: ContigSegment) => [Color.fromHexString(e.color!.replace("#", "0x")), Color(0xffffff)]);
    const borderColors: Color[] = segments.flatMap((e: ContigSegment) => [Color(0xffffff), Color.fromHexString(e.color!.replace("#", "0x"))]);

    arrays.forEach((arr, idx) => {
      if (!labels[idx]) {
        return;
      }
      const sel = getSelectionFromChainAuthId(innerProps.plugin!, chains[idx], [arr], structureIdx, true);
      const loci = StructureSelection.toLociWithSourceUnits(sel);

      const options = {
        labelParams: {
          customText: labels[idx],
        },
        visualParams: {
          scaleByRadius: false,
          sizeFactor: 1,
          textSize: 2,
          textColor: textColors[idx],
          borderColor: borderColors[idx],
          offsetZ: 2,
        }
      };

      innerProps.plugin!.managers.structure.measurement.addLabel(loci, options);
    });
  };

  const addLinesBetweenContigs = (structureIdx: number) => {
    // TODO: this applies now every time
    if (!innerProps.plugin) return;

    // keep just the first and last elements of the array
    const segments = props.contigs[structureIdx].filter((e) => e.start && e.show_lines);
    const arrays: number[] = segments.flatMap((e: ContigSegment) => [e.start, e.end]);
    const chains: string[] = segments.flatMap((e: ContigSegment) => [e.chain, e.chain]);
    const colors: Color[] = segments.flatMap((e: ContigSegment) => [
      Color.fromHexString(e.color!.replace("#", "0x")),
      Color.fromHexString(e.color!.replace("#", "0x"))
    ]);

    // Add "linkers" between pairs of contigs
    for (let i = 1; i < arrays.length - 1; i += 2) {
      if (chains[i] == chains[i + 1] && arrays[i] + 1 == arrays[i + 1]) {
        continue; // skip if the contigs are actually continuous
      }
      const firstLoci = StructureSelection.toLociWithSourceUnits(
        getSelectionFromChainAuthId(innerProps.plugin!, chains[i], [arrays[i]], structureIdx, true)
      );
      const secondLoci = StructureSelection.toLociWithSourceUnits(
        getSelectionFromChainAuthId(innerProps.plugin!, chains[i + 1], [arrays[i + 1]], structureIdx, true)
      );

      const options = {
        visualParams: {
          customText: " ", // no label
          scaleByRadius: false,
          sizeFactor: 1,
          linesColor: colors[i],
          dashLength: 0.2
        }
      };

      innerProps.plugin!.managers.structure.measurement.addDistance(firstLoci, secondLoci, options);
    };
  };

  const highlightSelection = (chainId: string, residues: number[], structureIdx: number) => {
    if (!innerProps.plugin) return;

    const sel = getSelectionFromChainAuthId(innerProps.plugin, chainId, residues, structureIdx);
    const loci = StructureSelection.toLociWithSourceUnits(sel);
    innerProps.plugin.managers.interactivity.lociHighlights.highlightOnly({ loci });
  };

  const addContigLabelsInMiddle = (structureIdx: number) => {
    if (!innerProps.plugin) return;

    const segments = props.contigs[structureIdx].filter((segment) => segment.middle_label && !segment.hide_labels);

    // we need to connect array 1 with 2, 2 with 3, and so on...
    // so, first, let's transform the original arrays
    segments.forEach((segment) => {

      const middleElement = Math.ceil((segment.start + segment.end) / 2);

      const sel = getSelectionFromChainAuthId(innerProps.plugin!, segment.chain, [middleElement], structureIdx, true);
      const loci = StructureSelection.toLociWithSourceUnits(sel);

      const options = {
        labelParams: {
          customText: segment.middle_label ?? undefined,
        },
        visualParams: {
          scaleByRadius: false,
          sizeFactor: 1,
          textSize: 3,
          textColor: Color(0x0),
          borderColor: Color.fromHexString(segment.color!.replace("#", "0x")),
          offsetZ: 2,
        }
      };

      innerProps.plugin!.managers.structure.measurement.addLabel(loci, options);
    });
  };

  const getSelectionFromChainAuthId = (plugin: PluginUIContext, chainId: string, positions: number[], structureIdx: number, backboneOnly: boolean = false) => {
    // In reality, this is not the right type - check the argument of MS.struct.generator.atomGroups()
    const groups: {
      'chain-test': any;
      'residue-test': any;
      'group-by': any;
      'atom-test'?: any;
    } = {
      'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), chainId]),
      'residue-test': MS.core.set.has([MS.set(...positions), MS.struct.atomProperty.macromolecular.auth_seq_id()]),
      'group-by': MS.struct.atomProperty.macromolecular.residueKey()
    };
    if (backboneOnly) {
      groups['atom-test'] = MS.core.set.has([
        MS.core.type.set(['C', 'N', 'CA', 'O'].map(MS.atomName)),
        MS.ammp('label_atom_id')
      ]);
    }
    const query = MS.struct.generator.atomGroups(groups);
    return Script.getStructureSelection(query, plugin.managers.structure.hierarchy.current.structures[structureIdx].cell.obj!.data);
  };

  const getAtomSelection = (plugin: PluginUIContext, ids: number[], chainGroupId: number | undefined, structureIdx: number) => {
    const fixedIds = chainGroupId !== undefined ? ids.map((id) => id + chainGroupId) : ids;
    const query = MS.struct.generator.atomGroups({
      'atom-test': MS.core.set.has([MS.set(...fixedIds), MS.struct.atomProperty.macromolecular.id()])
    });
    return Script.getStructureSelection(query, plugin.managers.structure.hierarchy.current.structures[structureIdx].cell.obj!.data);
  };

  const parseAtomId = (atomId: string) => {
    const colonIdx = atomId.indexOf(':');
    const residuePart = atomId.slice(0, colonIdx);
    const atomName = atomId.slice(colonIdx + 1);
    const chain = residuePart[0];
    const m = residuePart.slice(1).match(/^(\d+)([A-Z]?)$/);
    return { chain, resId: parseInt(m![1]), atomName };
  };

  const getAtomSelectionByIds = (plugin: PluginUIContext, atomIds: string[], structureIdx: number) => {
    const queries = atomIds.map(id => {
      const { chain, resId, atomName } = parseAtomId(id);
      return MS.struct.generator.atomGroups({
        'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), chain]),
        'residue-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_seq_id(), resId]),
        'atom-test': MS.core.rel.eq([MS.ammp('label_atom_id'), atomName]),
      });
    });
    const query = queries.length === 1 ? queries[0] : MS.struct.combinator.merge(queries);
    return Script.getStructureSelection(query, plugin.managers.structure.hierarchy.current.structures[structureIdx].cell.obj!.data);
  };

  const getResidueSelectionByAtomId = (plugin: PluginUIContext, atomId: string, structureIdx: number) => {
    const { chain, resId } = parseAtomId(atomId);
    const query = MS.struct.generator.atomGroups({
      'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), chain]),
      'residue-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_seq_id(), resId]),
      'group-by': MS.struct.atomProperty.macromolecular.residueKey(),
    });
    return Script.getStructureSelection(query, plugin.managers.structure.hierarchy.current.structures[structureIdx].cell.obj!.data);
  };

  const applyPositionalOverpaint = async (
    positions: Record<string, string>,
    structureIdx: number,
    repSelectors?: StateObjectSelector[]
  ) => {
    if (!innerProps.plugin) return;

    const builder = innerProps.plugin.state.data.build();

    type Params = {
      bundle: Bundle;
      color: Color;
      clear: boolean;
    };

    const params: Params[] = [];

    for (const [key, colorStr] of Object.entries(positions)) {
      const parsed = parseSelections([key]);
      for (const sel of parsed) {
        if (!sel.residues) continue;
        const bundle = Bundle.fromSelection(
          getSelectionFromChainAuthId(innerProps.plugin!, sel.chainId, sel.residues, structureIdx)
        );
        params.push({
          bundle,
          color: Color.fromHexString(colorStr.replace("#", "0x")),
          clear: false,
        });
      }
    }

    const targets = repSelectors || innerProps.representations[structureIdx];
    targets.map(
      rep => builder.to(rep).apply(StateTransforms.Representation.OverpaintStructureRepresentation3DFromBundle, { layers: params })
    );

    await builder.commit();
  };

  // used to subtract these atoms from the default polymer component so the default rep
  // does not render underneath an explicit rep (which would cause z-fighting / wrong colors).
  const buildExplicitRepsSelectionExpr = (representations: Representation[]) => {
    // flatten selections across all reps: each selection may be a string or list of strings
    const items = representations.flatMap(r => Array.isArray(r.selection) ? r.selection : [r.selection]);
    const parsed = parseSelections(items);
    if (parsed.length === 0) return null;

    const expressions = parsed.map(sel => {
      // partial range like "A1-10": filter by chain and by the set of residue numbers
      if (sel.residues && sel.residues.length > 0) {
        return MS.struct.generator.atomGroups({
          'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), sel.chainId]),
          'residue-test': MS.core.set.has([MS.set(...sel.residues), MS.struct.atomProperty.macromolecular.auth_seq_id()]),
          'group-by': MS.struct.atomProperty.macromolecular.residueKey(),
        });
      }
      // whole-chain selection like "A": filter by chain only
      return MS.struct.generator.atomGroups({
        'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), sel.chainId]),
      });
    });

    // combine all per-rep expressions with union, then expand to whole residues
    return MS.struct.modifier.wholeResidues({
      0: expressions.length === 1 ? expressions[0] : MS.struct.combinator.merge(expressions),
    });
  };

  // build the expression used for the "default" polymer component.
  // without explicit reps: identical to Mol*'s built-in polymer selection.
  // with explicit reps: same polymer selection minus all atoms covered by those reps,
  // so the default representation only renders the parts of the structure not otherwise styled.
  const buildPolymerExcludingReps = (representations: Representation[] | null | undefined) => {
    // mirror of Mol*'s built-in "polymer" selection
    // keep only polymer entities
    const polymerExpr = MS.struct.modifier.union([
      MS.struct.generator.atomGroups({
        'entity-test': MS.core.logic.and([
          MS.core.rel.eq([MS.ammp('entityType'), 'polymer']),
          MS.core.str.match([
            MS.re('(polypeptide|cyclic-pseudo-peptide|peptide-like|nucleotide|peptide nucleic acid)', 'i'),
            MS.ammp('entitySubtype'),
          ]),
        ]),
      }),
    ]);

    // no explicit reps, default representation covers the entire polymer
    if (!representations || representations.length === 0) return polymerExpr;
    const explicitExpr = buildExplicitRepsSelectionExpr(representations);
    if (!explicitExpr) return polymerExpr;

    // exceptBy = set difference: polymerExpr minus atoms matched by explicitExpr
    // (this is what prevents the default representation from drawing under explicit reps)
    return MS.struct.modifier.exceptBy({ 0: polymerExpr, by: explicitExpr });
  };

  const addStructureRepresentations = async (representations: Representation[], structureIdx: number) => {
    if (!innerProps.plugin || !representations) return;

    for (const rep of representations) {
      const parsed = parseSelections(Array.isArray(rep.selection) ? rep.selection : [rep.selection]);
      const builder = innerProps.plugin.state.data.build();

      const expressions = parsed.map(sel => {
        if (sel.residues && sel.residues.length > 0) {
          return MS.struct.generator.atomGroups({
            'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), sel.chainId]),
            'residue-test': MS.core.set.has([MS.set(...sel.residues), MS.struct.atomProperty.macromolecular.auth_seq_id()]),
            'group-by': MS.struct.atomProperty.macromolecular.residueKey()
          });
        }
        return MS.struct.generator.atomGroups({
          'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), sel.chainId]),
        });
      });

      const mergedExpr = expressions.length === 1
        ? expressions[0]
        : MS.struct.combinator.merge(expressions.map(e => MS.struct.modifier.wholeResidues({ 0: e })));

      const finalExpr = expressions.length === 1
        ? MS.struct.modifier.wholeResidues({ 0: mergedExpr })
        : mergedExpr;

      const group = builder.to(innerProps.structures[structureIdx]).apply(
        StateTransforms.Misc.CreateGroup,
        { label: `rep_${structureIdx}_${representations.indexOf(rep)}` }
      );
      const selection = group.apply(
        StateTransforms.Model.StructureSelectionFromExpression,
        { expression: finalExpr }
      );

      const repTypes = rep.representation_type.split("+") as string[];
      const repSelectors: StateObjectSelector[] = [];
      for (const repType of repTypes) {
        const isCartoon = repType === "cartoon";
        const extraTypeParams = typeParamsFor(repType, rep.color, rep.color_params);
        // @ts-ignore - here we are using the getColorParameters which raises an error but is in fact correct
        const repSelector = selection.apply(StateTransforms.Representation.StructureRepresentation3D, createStructureRepresentationParams(innerProps.plugin, innerProps.structures[structureIdx].data, {
          type: repType as any,
          size: getSizeForRepType(repType),
          ...(extraTypeParams ? { typeParams: extraTypeParams as any } : {}),
          ...getColorParameters(repType, rep.color, rep.color_params, innerProps.plugin),
        }));
        repSelectors.push(repSelector as any);
      }

      await builder.commit();

      if (rep.color_params?.positions) {
        await applyPositionalOverpaint(rep.color_params.positions, structureIdx, repSelectors);
      }
    }
  };

  const autoZoomToChains = async (chainIds: string[], extraRadius: number, structureIdx: number) => {
    if (!innerProps.plugin || !chainIds || chainIds.length === 0) return;

    const expressions = chainIds.map(chainId =>
      MS.struct.generator.atomGroups({
        'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), chainId]),
      })
    );

    const mergedExpr = expressions.length === 1
      ? expressions[0]
      : MS.struct.combinator.merge(expressions);

    const structureData = innerProps.plugin.managers.structure.hierarchy.current.structures[structureIdx].cell.obj!.data;
    const sel = Script.getStructureSelection(mergedExpr, structureData);
    const loci = StructureSelection.toLociWithSourceUnits(sel);
    // also zoom out extra 10 angstroms to improve visibility
    innerProps.plugin.managers.camera.focusLoci(loci, { extraRadius });
  };

const addBondsVisualizations = async (bondVisualizations: BondVisualization[] | null, structureIdx: number) => {
    if (!innerProps.plugin || !bondVisualizations) {
    return;
  }

  for (const bondVis of bondVisualizations) {

    const firstSel = getAtomSelectionByIds(innerProps.plugin, bondVis.binder_atoms, structureIdx);
    const firstLoci = StructureSelection.toLociWithSourceUnits(firstSel);

    const secondSel = getAtomSelectionByIds(innerProps.plugin, bondVis.target_atoms, structureIdx);
    const secondLoci = StructureSelection.toLociWithSourceUnits(secondSel);

    // Add distance line with short interaction type label, colored per interaction type.
    const bondColor = Color(parseInt(bondVis.color.replace('#', ''), 16));
    const options = {
      visualParams: {
        customText: bondVis.label ?? " ",
        scaleByRadius: false,
        sizeFactor: 1,
        linesColor: bondColor,
        textSize: 0.8,
        textColor: bondColor,
        borderColor: Color(0xffffff),
        offsetZ: 1.5,
      }
    };

    try {
      innerProps.plugin!.managers.structure.measurement.addDistance(firstLoci, secondLoci, options);
    } catch (error) {
      console.error("Error adding distance:", error);
    }
  }
};



  useEffect(() => {
    initPlugin();
    // to fix this warning, we might move initPlugin into the effect, but this would mean almost everything is in the effect...
    // this happens almost everywhere
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!props.highlightedContig) return;
    highlightSelection(props.highlightedContig.chain, getRange([props.highlightedContig.start, props.highlightedContig.end]), props.highlightedContig.structureIdx);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.highlightedContig]);

  // remove current structures if the structure visualization changes... but ignore "highlighted_selections" to allow selections interaction
  const prevStructuresRef = React.useRef<Partial<StructureVisualization>[]>([]);
  useEffect(() => {
    // remove "highlighted_selections" from each structure for comparison
    const stripSelections = (structures: StructureVisualization[]) =>
      structures.map(({ highlighted_selections, ...rest }) => rest as Partial<StructureVisualization>);

    const prevStripped = JSON.stringify(stripSelections(prevStructuresRef.current as StructureVisualization[]));
    const currStripped = JSON.stringify(stripSelections(props.structures));

    if (prevStripped !== currStripped) {
      const run = async () => {
        await removeLoadedData();  // we need await here, that's why we use the wrapper
        loadData(props.structures);
      };
      run();
      prevStructuresRef.current = props.structures.map(({ highlighted_selections, ...rest }) => rest);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.structures]);

  // force reload of the component data if forceReload changed to true
  useEffect(() => {
    if (props.forceReload) {
      const run = async () => {
        await removeLoadedData();  // we need await here, that's why we use the wrapper
        loadData(props.structures);
      };
      run();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.forceReload]);

  return (
    <></> // return empty component as it gets rendered to a specific div id
  );
};

export default MolstarCustomComponent;
