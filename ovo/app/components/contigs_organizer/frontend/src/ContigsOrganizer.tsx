import React, { useState, useEffect, useMemo, useRef } from "react";
import { Streamlit } from "streamlit-component-lib";
import "./assets/style.css";
import {
    DndContext,
    KeyboardSensor,
    PointerSensor,
    useDroppable,
    useSensor,
    useSensors,
} from "@dnd-kit/core";
import type { Active, UniqueIdentifier } from "@dnd-kit/core";
import {
    SortableContext,
    arrayMove,
    sortableKeyboardCoordinates,
} from "@dnd-kit/sortable";
import { SortableOverlay } from "./components/SortableList/components/SortableOverlay/SortableOverlay";
import { ContigPartInfo, CoordinateData, StreamlitComponentValue } from "./types";
import { PdbParser } from 'pdb-parser-js';
import { AminoAcids, getRange, calculateDistances, isGeneratedSegment, parseFixedSegment } from "./utils";
import ContigsOrganizerItem from "./ContigsOrganizerItem";
import AddSegmentButton from "./AddSegmentButton";
import { v4 as uuidv4 } from 'uuid';

const UNINDEXED_DROP_ID = "unindexed-dropzone";
const INDEXED_DROP_ID = "indexed-dropzone";

interface Props {
    contigs: string;
    pdb: string;
    colors: Map<string, string>;
    unindexedSegments: Set<string>;
    updateStreamlitComponentValue: (value: StreamlitComponentValue) => void;
}

function UnindexedDropzone({ children, isEmpty }: { children: React.ReactNode; isEmpty: boolean }) {
    const { setNodeRef, isOver } = useDroppable({ id: UNINDEXED_DROP_ID });
    const className = [
        "unindexedSection",
        isOver ? "unindexedSectionOver" : "",
    ].filter(Boolean).join(" ");
    return (
        <div ref={setNodeRef} className={className}>
            {isEmpty ? (
                <div className="emptySectionPlaceholder">
                    Drag fixed segments here to let RFdiffusion3 decide their sequence position
                </div>
            ) : (
                <ul className="SortableList">{children}</ul>
            )}
            <div className="unindexedSectionHeader">
                Unindexed motif residues: kept structurally, RFdiffusion3 decides their sequence position within the generated segments
            </div>
        </div>
    );
}

function IndexedDropzone({ children, isEmpty, onAddSegment }: { children: React.ReactNode; isEmpty: boolean; onAddSegment: (index: number) => void }) {
    const { setNodeRef, isOver } = useDroppable({ id: INDEXED_DROP_ID });
    if (!isEmpty) {
        return <ul className="SortableList" role="application">{children}</ul>;
    }
    return (
        <div ref={setNodeRef} className={`indexedSectionEmpty ${isOver ? "indexedSectionOver" : ""}`}>
            <AddSegmentButton
                index={0}
                handleAddContigPart={onAddSegment}
                contigParts={[]}
                isGeneratedSegment={isGeneratedSegment}
                upperButton={false}
                generatedSegmentConnection={() => ""}
                label="Add generated segment"
            />
        </div>
    );
}

function ContigsOrganizer(props: Props) {

    const [contigParts, setContigParts] = useState<ContigPartInfo[]>();
    const [parsedPdb, setParsedPdb] = useState<CoordinateData[]>([]);
    const [active, setActive] = useState<Active | null>(null);
    const ref = useRef<HTMLDivElement>(null);

    const distancesMap = useRef(new Map<string, number>());
    const residuesMap = useRef(new Map<string, string>());

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
    );

    //#region Contigs handling
    const unindexedKey = Array.from(props.unindexedSegments).sort().join(",");
    useEffect(() => {
        const contigParts: ContigPartInfo[] = (props.contigs ? props.contigs.split("/") : []).map(part => ({
            id: uuidv4(),
            content: part,
            unindexed: false,
        }));
        const unindexedParts: ContigPartInfo[] = Array.from(props.unindexedSegments).map(content => ({
            id: uuidv4(),
            content,
            unindexed: true,
        }));
        const parts = [...contigParts, ...unindexedParts];
        setContigParts(parts);

        // parse the PDB so we can compute distances between residues
        if (parsedPdb.length === 0) {
            const parser = new PdbParser();
            parser.collect(props.pdb.split('\n'));

            const pdb = parser.parse();
            const parsedPdb = pdb.coordinate.atoms.map((e) => e.data);
            setParsedPdb(parsedPdb);
            const distances = calculateDistances(parts, parsedPdb);
            distances.forEach(dist => distancesMap.current.set(dist.segment, dist.result));
        }

    }, [props.contigs, unindexedKey]);

    const segmentsPostprocessing = (segments: ContigPartInfo[], coordinateData: CoordinateData[]) => {
        const result = [...segments];

        for (let i = 0; i < result.length - 1; i++) {
            // collapse adjacent generated segments in the indexed list
            if (
                !result[i].unindexed && !result[i + 1].unindexed
                && isGeneratedSegment(result[i].content) && isGeneratedSegment(result[i + 1].content)
            ) {
                result.splice(i, 1);
                i--;
            }
        }

        const distances = calculateDistances(segments, coordinateData);
        distances.forEach(dist => distancesMap.current.set(dist.segment, dist.result));

        return result;
    };

    const handleAddContigPart = (index: number) => {
        const newContigPart = { id: uuidv4(), content: "", unindexed: false };
        setContigParts(prev => {
            const newParts = [...(prev || [])];
            newParts.splice(index, 0, newContigPart);
            return segmentsPostprocessing(newParts, parsedPdb);
        });
    };

    const updateContigPart = (index: number, newContent: string | null) => {
        setContigParts(prev => {
            const updatedParts = [...(prev || [])];
            if (newContent === null) {
                updatedParts.splice(index, 1);
            } else {
                updatedParts[index].content = newContent;
            }

            return segmentsPostprocessing(updatedParts, parsedPdb);
        });
    };

    const getColor = (item: ContigPartInfo) => {
        if (item.unindexed) {
            return "#ab9a1d"; // note that this color is also hardcoded inside preview_components.py
        }
        const color = props.colors.get(item.content);
        if (color) {
            return color;
        }

        return "#6d6d6d";
    };

    const generatedSegmentConnection = (index: number, generatedSegmentMissing: boolean, content: string) => {
        if (contigParts === undefined) {
            // should never happen, just for type checking
            return "";
        }
        const indexedOnly = contigParts.filter(p => !p.unindexed);
        const indexedPosition = indexedOnly.findIndex(p => p.id === contigParts[index]?.id);
        if (!generatedSegmentMissing && indexedPosition === 0) {
            return indexedOnly.length === 1 ? "Generated segment" : "N-term generated segment";
        }
        if (indexedPosition === indexedOnly.length - 1) {
            return "C-term generated segment";
        }

        // a missing generated segment sits at indexedPosition; an existing one is preceded by it
        const firstSegment = generatedSegmentMissing
            ? indexedOnly[indexedPosition].content
            : indexedOnly[indexedPosition - 1].content;
        const secondSegment = indexedOnly[indexedPosition + 1]?.content ?? "";

        if (isGeneratedSegment(firstSegment) || isGeneratedSegment(secondSegment)) {
            return ``;
        }

        const segment1 = parseFixedSegment(firstSegment);
        const segment2 = parseFixedSegment(secondSegment);

        if (!segment1) {
            console.error("Failed parsing distances for this segment: " + firstSegment);
            return `Invalid connected fixed segment ${firstSegment}. Please, change it.`;
        }

        if (!segment2) {
            console.error("Failed parsing distances for this segment: " + secondSegment);
            return `Invalid connected fixed segment ${secondSegment}. Please, change it.`;
        }

        const segmentsDistance = distancesMap.current.get(`${segment1.chainId}${segment1.lastIndex}_${segment2.chainId}${segment2.firstIndex}`)?.toFixed(1) ?? "?";

        if (generatedSegmentMissing || !content) {
            return `Please add a segment connecting ${segment1.chainId}${segment1.lastIndex} -> ${segment2.chainId}${segment2.firstIndex} (${segmentsDistance} Å)`;
        }

        const groups = content.match(/^[A-Z]?([0-9]+)(-([0-9]+))?$/);
        if (groups) {
            if (parseInt(groups[1]) > parseInt(groups[3] || groups[1])) {
                return "Invalid range (start > end)";
            }
        } else {
            return "Invalid format, expected: 10, 10-20, or A10-20";
        }
        return (<>
            Generated segment of {content} residues<br />
            <span>
                Connecting {segment1.chainId}{segment1.lastIndex} -&gt; {segment2.chainId}{segment2.firstIndex} ({segmentsDistance} Å)
            </span>
        </>);
    };

    const getFixedSegmentDescription = (segment: string) => {
        const residuesThreshold = 10;

        if (residuesMap.current.has(segment)) {
            const residues = residuesMap.current.get(segment);
            if (residues!.length >= residuesThreshold) {
                return `Fixed segment of ${residues!.length} residues: ${residues!.substring(0, 3)}...${residues!.substring(residues!.length - 3, residues!.length)}`;
            }
            return `Fixed segment of ${residues!.length} residues: ${residues!}`;
        }

        const fixed = parseFixedSegment(segment);
        if (!fixed) {
            return `Invalid segment. Please, change it.`;
        }
        const residuesArray = getRange([fixed.firstIndex, fixed.lastIndex]);

        const relevantAtoms = parsedPdb.filter((e) => e.chainID === fixed.chainId && residuesArray.indexOf(e.resSeq ?? -1) !== -1);

        const resultArray = relevantAtoms.reduce((accumulator: CoordinateData[], current: CoordinateData) => {
            if (accumulator.length === 0 || accumulator[accumulator.length - 1].resName !== current.resName || accumulator[accumulator.length - 1].resSeq !== current.resSeq) {
                accumulator.push(current);
            }
            return accumulator;
        }, []);

        const residues = resultArray.map((e) => AminoAcids[e.resName! as keyof typeof AminoAcids]).join("");
        residuesMap.current.set(segment, residues);
        if (residues.length >= residuesThreshold) {
            return `Fixed segment of length ${residues.length}: ${residues.substring(0, 3)}...${residues.substring(residues!.length - 3, residues.length)}`;
        }
        return `Fixed segment of length ${residues.length}: ${residues}`;
    };
    //#endregion

    useEffect(() => {
        if (ref.current) {
            Streamlit.setFrameHeight(ref.current.clientHeight);
        }
        if (contigParts !== undefined) {
            const indexedParts: string[] = [];
            for (const part of contigParts) {
                if (part.unindexed) {
                    continue;
                }
                if (
                    isGeneratedSegment(part.content)
                    && indexedParts.length > 0
                    && isGeneratedSegment(indexedParts[indexedParts.length - 1])
                ) {
                    continue;
                }
                indexedParts.push(part.content);
            }
            props.updateStreamlitComponentValue({
                contig: indexedParts.join("/"),
                unindexedSegments: contigParts.filter((e) => e.unindexed).map((e) => e.content),
            });
        }
    }, [ref, contigParts]);

    const indexedParts = useMemo(
        () => (contigParts ?? []).filter(p => !p.unindexed),
        [contigParts],
    );
    const unindexedParts = useMemo(
        () => (contigParts ?? []).filter(p => p.unindexed),
        [contigParts],
    );

    const findContainer = (id: UniqueIdentifier): "indexed" | "unindexed" | null => {
        if (id === UNINDEXED_DROP_ID) return "unindexed";
        if (id === INDEXED_DROP_ID) return "indexed";
        if (unindexedParts.some(p => p.id === id)) return "unindexed";
        if (indexedParts.some(p => p.id === id)) return "indexed";
        return null;
    };

    const handleDragEnd = ({ active, over }: { active: Active; over: { id: UniqueIdentifier } | null }) => {
        setActive(null);
        if (!over) return;

        const activeContainer = findContainer(active.id);
        const overContainer = findContainer(over.id);
        if (!activeContainer || !overContainer) return;

        const activeItem = (contigParts ?? []).find(p => p.id === active.id);
        if (!activeItem) return;

        // generated segments stay in the indexed contig
        if (overContainer === "unindexed" && isGeneratedSegment(activeItem.content)) return;

        if (activeContainer === overContainer) {
            if (active.id === over.id) return;
            const list = activeContainer === "indexed" ? indexedParts : unindexedParts;
            const fromIdx = list.findIndex(p => p.id === active.id);
            const toIdx = list.findIndex(p => p.id === over.id);
            if (fromIdx < 0 || toIdx < 0) return;
            const reordered = arrayMove(list, fromIdx, toIdx);
            const others = (contigParts ?? []).filter(p => (activeContainer === "indexed" ? p.unindexed : !p.unindexed));
            const merged = activeContainer === "indexed" ? [...reordered, ...others] : [...others, ...reordered];
            setContigParts(segmentsPostprocessing(merged, parsedPdb));
            return;
        }

        // cross-container move
        const updatedItem = { ...activeItem, unindexed: overContainer === "unindexed" };
        const remainingActiveSide = (activeContainer === "indexed" ? indexedParts : unindexedParts)
            .filter(p => p.id !== active.id);
        const targetList = overContainer === "indexed" ? indexedParts : unindexedParts;

        let insertIdx: number;
        if (over.id === UNINDEXED_DROP_ID || over.id === INDEXED_DROP_ID) {
            insertIdx = targetList.length;
        } else {
            insertIdx = targetList.findIndex(p => p.id === over.id);
            if (insertIdx < 0) insertIdx = targetList.length;
        }
        const newTarget = [...targetList];
        newTarget.splice(insertIdx, 0, updatedItem);

        const newIndexed = overContainer === "indexed" ? newTarget : remainingActiveSide;
        const newUnindexed = overContainer === "unindexed" ? newTarget : remainingActiveSide;
        setContigParts(segmentsPostprocessing([...newIndexed, ...newUnindexed], parsedPdb));
    };

    if (contigParts === undefined) {
        return <div ref={ref} />;
    }

    const indexOfPart = (item: ContigPartInfo) => contigParts.findIndex(p => p.id === item.id);
    const activeItem = contigParts.find(p => p.id === active?.id);

    const renderItem = (item: ContigPartInfo, hideAddButtons: boolean) => (
        <ContigsOrganizerItem
            key={item.id}
            idx={indexOfPart(item)}
            handleAddContigPart={handleAddContigPart}
            contigParts={contigParts}
            isGeneratedSegment={isGeneratedSegment}
            generatedSegmentConnection={generatedSegmentConnection}
            item={item}
            getFixedSegmentDescription={getFixedSegmentDescription}
            getColor={getColor}
            updateContigPart={updateContigPart}
            hideAddButtons={hideAddButtons}
        />
    );

    return (
        <div ref={ref}>
            <DndContext
                sensors={sensors}
                onDragStart={({ active }) => setActive(active)}
                onDragEnd={handleDragEnd}
                onDragCancel={() => setActive(null)}
            >
                <SortableContext items={indexedParts.length > 0 ? indexedParts : [INDEXED_DROP_ID]}>
                    <IndexedDropzone isEmpty={indexedParts.length === 0} onAddSegment={handleAddContigPart}>
                        {indexedParts.map(item => renderItem(item, false))}
                    </IndexedDropzone>
                </SortableContext>

                <SortableContext items={unindexedParts.length > 0 ? unindexedParts : [UNINDEXED_DROP_ID]}>
                    <UnindexedDropzone isEmpty={unindexedParts.length === 0}>
                        {unindexedParts.map(item => renderItem(item, true))}
                    </UnindexedDropzone>
                </SortableContext>

                <SortableOverlay>
                    {activeItem ? renderItem(activeItem, true) : null}
                </SortableOverlay>
            </DndContext>
        </div>
    );
}

export default ContigsOrganizer;
