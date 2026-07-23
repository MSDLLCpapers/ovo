import { ContigPartInfo } from "./types";
import React from "react";

interface Props {
    isGeneratedSegment: (contig: string) => boolean;
    index: number;
    contigParts: ContigPartInfo[];
    handleAddContigPart: (index: number) => void;
    upperButton: boolean;
    generatedSegmentConnection: (index: number, generatedSegmentMissing: boolean, content: string) => string | JSX.Element;
    // when set, render a single unconditional button with this label (used for the empty indexed contig)
    label?: string;
}

function AddSegmentButton(props: Props) {
    const { contigParts, index, isGeneratedSegment, handleAddContigPart, upperButton, generatedSegmentConnection, label } = props;

    // explicit-label mode: a standalone button that appends a generated segment,
    // used in place of the empty-section placeholder when the indexed contig has no segments
    if (label !== undefined) {
        return (
            <div className="contigRowContainer">
                <div className="contigRowColumn1">
                    <button onClick={() => handleAddContigPart(index)} className="add-button">+</button>
                </div>
                <div className="contigRowColumn2">
                    {label}
                </div>
            </div>
        );
    }

    // unindexed segments are placed in a separate dropzone and don't participate in
    // the chain of generated/fixed segments, so navigation neighbors are computed
    // against the indexed list only
    const indexedOnly = contigParts.filter(p => !p.unindexed);
    const currentPart = contigParts[index];
    const indexedPos = indexedOnly.findIndex(p => p.id === currentPart?.id);
    const nextIndexedPart = indexedOnly[indexedPos + 1];
    const isLastIndexed = indexedPos === indexedOnly.length - 1;

    const currentIsFixed = !isGeneratedSegment(currentPart?.content);
    const nextIndexedIsFixed = !isGeneratedSegment(nextIndexedPart?.content);

    // upper "+" only renders before a fixed segment (to insert an N-term generated piece)
    const showUpperButton = upperButton && currentIsFixed;
    // lower "+" renders between two fixed indexed segments (gap to fill with a generated piece),
    // or after the very last indexed fixed segment (to add a C-term generated piece)
    const showLowerButton =
        !upperButton
        && index !== undefined
        && index < contigParts.length
        && currentIsFixed
        && (isLastIndexed || nextIndexedIsFixed);

    // for the C-term case the description is fixed; otherwise it describes the connection
    // between the two flanking fixed segments (and the distance between them)
    const spanText = isLastIndexed ? "C-term generated segment" : generatedSegmentConnection(index, true, "");
    const isInvalid = typeof spanText === "string" && spanText.toLowerCase().includes("invalid");
    let spanColor: string;
    if (isInvalid) {
        spanColor = "red";
    } else if (isLastIndexed) {
        // C-term is informational, doesn't require user action
        spanColor = "inherit";
    } else {
        // orange highlights a gap the user still needs to fill
        spanColor = "orange";
    }

    return (
        <>
            {showUpperButton && (
                <div className="contigRowContainer">
                    <div className="contigRowColumn1">
                        <button onClick={() => handleAddContigPart(0)} className="add-button">+</button>
                    </div>
                    <div className="contigRowColumn2">
                        N-term generated segment
                    </div>
                </div>
            )}

            {showLowerButton && (
                <div className="contigRowContainer">
                    <div className="contigRowColumn1">
                        <button onClick={() => handleAddContigPart(index + 1)} className="add-button">+</button>
                    </div>
                    <div className="contigRowColumn2">
                        <span style={{ color: spanColor }}>
                            {spanText}
                        </span>
                    </div>
                </div>
            )}
        </>
    );
}

export default AddSegmentButton;