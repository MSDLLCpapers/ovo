import React from "react";
import AddSegmentButton from "./AddSegmentButton";
import ContigPart from "./ContigPart";
import { SortableList } from "./components/SortableList/SortableList";
import "./assets/style.css";
import { ContigPartInfo } from "./types";

interface Props {
    idx: number | undefined;
    item: ContigPartInfo;
    contigParts: ContigPartInfo[];
    isGeneratedSegment: (contig: string) => boolean;
    handleAddContigPart: (index: number) => void;
    generatedSegmentConnection: (index: number, generatedSegmentMissing: boolean, content: string) => string | JSX.Element;
    getFixedSegmentDescription: (contig: string) => string;
    updateContigPart: (index: number, newContent: string | null) => void;
    getColor: (item: ContigPartInfo) => string;
    hideAddButtons?: boolean;
}

function ContigsOrganizerItem(props: Props) {
    const { idx, isGeneratedSegment, contigParts, handleAddContigPart, generatedSegmentConnection, item, getFixedSegmentDescription, updateContigPart, getColor, hideAddButtons } = props;

    const isFixed = !isGeneratedSegment(item.content);
    const baseDescription = isFixed ? getFixedSegmentDescription(item.content) : generatedSegmentConnection(idx!, false, item.content);
    let spanColor = "inherit";
    if (typeof baseDescription === "string" && baseDescription.toLowerCase().includes("invalid")) spanColor = "red";

    return <>
        {!hideAddButtons && props.idx === 0 && <AddSegmentButton index={props.idx} handleAddContigPart={handleAddContigPart}
            contigParts={contigParts} isGeneratedSegment={isGeneratedSegment} upperButton={true}
            generatedSegmentConnection={generatedSegmentConnection}
        />}

        <div className="contigRowContainer">
            <div className="contigRowColumn1" style={{ display: "block" }}>
                <SortableList.Item id={item.id} color={getColor(item)}>
                    <ContigPart contigPart={item.content} index={idx!} updateContigPart={updateContigPart} />
                    {isFixed && <SortableList.DragHandle />}
                </SortableList.Item>
            </div>
            {idx !== undefined && (
                <div className="contigRowColumn2">
                    <span style={{ color: spanColor }}>
                        {baseDescription}
                    </span>
                </div>
            )}
        </div>

        {!hideAddButtons && idx !== undefined && idx < contigParts.length &&
            <AddSegmentButton index={idx!} handleAddContigPart={handleAddContigPart}
                contigParts={contigParts} isGeneratedSegment={isGeneratedSegment} upperButton={false}
                generatedSegmentConnection={generatedSegmentConnection}
            />
        }
    </>;
}

export default ContigsOrganizerItem;
