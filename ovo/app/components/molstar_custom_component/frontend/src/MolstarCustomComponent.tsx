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
import { ChainVisualization, ColorParameters, ContigSegment, SequenceSelection, StreamlitComponentValue, StructureVisualization } from "./types";
import { toBytesFloat64 } from "./utils";
import { StructureRepresentationRegistry } from "molstar/lib/mol-repr/structure/registry";

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

function MolstarCustomComponent(props: Props) {

  const initPlugin = async () => {
    if (innerProps.loadingPlugin || innerProps.plugin) return; // plugin is already being loaded or loaded
    const wrapper = document.getElementById(props.divName)!;
    innerProps.loadingPlugin = true;
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
          [PluginConfig.Viewport.ShowAnimation, false],         // we do not need animation controls
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

  const parseSelections = (selections: string[]): SequenceSelection[] => {
    const trimmed = selections.map((sel) => sel.trim()).filter((e) => e !== "");

    const parsedSelections = trimmed.map(item => {
      const regex = /([A-Z]+)(\d+)(-\d+)?/;

      const match = item.match(regex);

      if (match) {
        const start = parseInt(match[2]);
        return {
          chainId: match[1],
          residues: getRange([start, match[3] ? parseInt(match[3].slice(1)) : start])
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
      console.log("MolStar loading structures", structures);

      for (let i = 0; i < structures.length; i++) {
        const structToLoad = structures[i];
        await loadPdb(structToLoad, i);
        if (props.contigs[i] && props.contigs[i].length > 0) {
          await overPaintStructureByContigs(i);
          addContigLabelsAtEnds(i);
          addContigLabelsInMiddle(i);
          addLinesBetweenContigs(i);
        }
        if ("highlighted_selections" in structures[i]) {
          addSelections(structures[i].highlighted_selections, i);
        }
        if ("chains" in structures[i]) {
          await addSpecialChainVisualizations(structures[i].chains, i);
        }
      }
    } finally {
      innerProps.loadingPdb = false;
    }
  };

  const isUrl = (pdb: string) => {
    return pdb.startsWith("http://") || pdb.startsWith("https://");
  };

  const getColorParameters = (color: string, colorParams: ColorParameters | null, plugin: PluginUIContext) => {
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

    let data: StateObjectSelector;
    let trajectory: StateObjectSelector;

    if (isUrl(structureToLoad.pdb)) {
      data = await plugin.builders.data.download({
        url: Asset.Url(structureToLoad.pdb),
        isBinary: false
      }, { state: { isGhost: true } });

      if (structureToLoad.pdb.includes(".pdb")) {
        trajectory = await plugin.builders.structure.parseTrajectory(data, "pdb");
      }
      else {
        trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");
      }
    }
    else {
      if (structureToLoad.pdb.includes("loop_")) {
        data = await plugin.builders.data.rawData({
          data: structureToLoad.pdb
        });

        trajectory = await plugin.builders.structure.parseTrajectory(data, "mmcif");
      }
      else {
        // A special case where we add custom labels to the structure.
        const stringsToPrepend = [];

        if (structureToLoad.chains) {
          for (let i = 0; i < structureToLoad.chains.length; i++) {
            const chain = structureToLoad.chains[i];
            if (chain.label) {
              const stringToPrepend = `COMPND    MOL_ID: ${i + 1};\nCOMPND   2 MOLECULE: ${chain.label};\nCOMPND   3 CHAIN: ${chain.chain_id};`;
              stringsToPrepend.push(stringToPrepend);
            }
          }
        }

        const dataToPrepend = stringsToPrepend.join("\n") + "\n";
        const newPdb = dataToPrepend + structureToLoad.pdb;

        data = await plugin.builders.data.rawData({
          data: newPdb
        });

        trajectory = await plugin.builders.structure.parseTrajectory(data, "pdb");
      }
    }

    const model = await plugin.builders.structure.createModel(trajectory);
    const structure = await plugin.builders.structure.createStructure(model, { name: 'model', params: {} });

    const polymer = await plugin.builders.structure.tryCreateComponentStatic(structure, 'polymer');

    if (polymer && structureToLoad.representation_type) {
      const repTypes: StructureRepresentationRegistry.BuiltIn[] = structureToLoad.representation_type.split("+") as StructureRepresentationRegistry.BuiltIn[];
      for (const repType of repTypes) {
        // @ts-ignore - here we are using the getColorParameters which raises an error but is in fact correct
        const representation: StateObjectSelector = await plugin.builders.structure.representation.addRepresentation(polymer, {
          type: repType,
          ...getColorParameters(structureToLoad.color, structureToLoad.color_params, plugin),
        });

        innerProps.representations[structureIdx].push(representation);
      }
    }

    innerProps.structures[structureIdx] = structure;

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

    props.contigs[structureIdx].forEach((e, i) => {
      const range = Array.from(new Array(e.length), (x, i) => i + e.out_res_start);
      const bundle = Bundle.fromSelection(getSelectionFromChainAuthId(innerProps.plugin!, e.out_res_chain, range, structureIdx));

      params.push({ bundle: bundle, color: Color.fromHexString(e.color.replace("#", "0x")), clear: false });
    });

    innerProps.representations[structureIdx].map(
      rep => builder.to(rep).apply(StateTransforms.Representation.OverpaintStructureRepresentation3DFromBundle, { layers: params })
    );

    await builder.commit();
  };

  const getRange = (arr: number[]) => {
    const start = arr[0];
    const end = arr[arr.length - 1] - start + 1;
    const range = Array.from(new Array(end), (x, i) => i + start);

    return range;
  };

  const addContigLabelsAtEnds = (structureIdx: number) => {
    if (!innerProps.plugin) return;

    // keep just the first and last elements of the array
    const arrays: number[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [e.out_res_start, e.out_res_end]);
    const labels: string[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [
      e.input_res_chain + e.input_res_start,
      e.input_res_chain + e.input_res_end
    ]);
    const chains: string[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [e.out_res_chain, e.out_res_chain]);
    const textColors: Color[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [Color.fromHexString(e.color.replace("#", "0x")), Color(0xffffff)]);
    const borderColors: Color[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [Color(0xffffff), Color.fromHexString(e.color.replace("#", "0x"))]);

    arrays.forEach((e, idx) => {
      const sel = getSelectionFromChainAuthId(innerProps.plugin!, chains[idx], [e], structureIdx, true);
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
    const arrays: number[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [e.out_res_start, e.out_res_end]);
    const chains: string[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [e.out_res_chain, e.out_res_chain]);
    const colors: Color[] = props.contigs[structureIdx].filter((e) => e.type === "fixed").flatMap((e: ContigSegment) => [
      Color.fromHexString(e.color.replace("#", "0x")),
      Color.fromHexString(e.color.replace("#", "0x"))
    ]);

    // Add "linkers" between pairs of contigs
    for (let i = 1; i < arrays.length - 1; i += 2) {
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

    const arrays = props.contigs[structureIdx].filter((e) => e.type === "generated");

    // we need to connect array 1 with 2, 2 with 3, and so on...
    // so, first, let's transform the original arrays
    arrays.forEach((arr, idx) => {
      if (arr.length === 0) return;

      const middleElement = Math.ceil((arr.out_res_start + arr.out_res_end) / 2);

      const sel = getSelectionFromChainAuthId(innerProps.plugin!, arr.out_res_chain, [middleElement], structureIdx, true);
      const loci = StructureSelection.toLociWithSourceUnits(sel);

      const connectionDescription = `${arr.length}`;

      const options = {
        labelParams: {
          customText: connectionDescription,
        },
        visualParams: {
          scaleByRadius: false,
          sizeFactor: 1,
          textSize: 3,
          textColor: Color(0x0),
          borderColor: Color.fromHexString(arr.color.replace("#", "0x")),
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

  const addSpecialChainVisualizations = async (chainVisualizations: ChainVisualization[] | null, structureIdx: number) => {
    if (!innerProps.plugin || !chainVisualizations) return;

    for (const chainVis of chainVisualizations) {
      const builder = innerProps.plugin.state.data.build();
      const group = builder.to(innerProps.structures[structureIdx]).apply(StateTransforms.Misc.CreateGroup, { label: `chain_${chainVis.chain_id}_${structureIdx}` }, { ref: `chain_${chainVis.chain_id}_${structureIdx}` });

      let expr;

      if (chainVis.residues && chainVis.residues.length > 0) {
        expr = MS.struct.generator.atomGroups({
          'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), chainVis.chain_id]),
          'residue-test': MS.core.set.has([MS.set(...chainVis.residues), MS.struct.atomProperty.macromolecular.auth_seq_id()]),
          'group-by': MS.struct.atomProperty.macromolecular.residueKey()
        });
      } else {
        expr = MS.struct.generator.atomGroups({
          'chain-test': MS.core.rel.eq([MS.struct.atomProperty.macromolecular.auth_asym_id(), chainVis.chain_id]),
        });
      }

      const expr2 = MS.struct.modifier.wholeResidues({ 0: expr });
      const selection = group.apply(StateTransforms.Model.StructureSelectionFromExpression, { expression: expr2 });

      const repTypes: StructureRepresentationRegistry.BuiltIn[] = chainVis.representation_type.split("+") as StructureRepresentationRegistry.BuiltIn[];
      for (const repType of repTypes) {
        // @ts-ignore - here we are using the getColorParameters which raises an error but is in fact correct
        selection.apply(StateTransforms.Representation.StructureRepresentation3D, createStructureRepresentationParams(innerProps.plugin, innerProps.structures[structureIdx].data, {
          type: repType,
          size: "physical",
          sizeParams: { scale: 1.05 },
          ...getColorParameters(chainVis.color, chainVis.color_params, innerProps.plugin),
        }));
        // here we can store the chain representations somewhere?
      }

      await builder.commit();
    }
  };

  useEffect(() => {
    initPlugin();
    console.log('CONTIGS', props.contigs);
    // to fix this warning, we might move initPlugin into the effect, but this would mean almost everything is in the effect...
    // this happens almost everywhere
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!props.highlightedContig) return;
    highlightSelection(props.highlightedContig.out_res_chain, getRange([props.highlightedContig.out_res_start, props.highlightedContig.out_res_end]), props.highlightedContig.structureIdx);
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
