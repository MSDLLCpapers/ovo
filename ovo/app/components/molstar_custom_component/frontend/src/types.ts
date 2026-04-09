import { ColorListName } from "molstar/lib/mol-util/color/lists";


// analogous to ContigSegment in python
export type ContigSegment = {
    start: number;
    end: number;
    chain: string;
    color: string | null;
    start_label: string | null;
    middle_label: string | null;
    end_label: string | null;
}

export type SequenceSelection = {
    chainId: string;
    residues: number[];
};

export type StreamlitComponentValue = {
    sequenceSelections: SequenceSelection[];
};

export type ChainVisualization = {
    chain_id: string;
    color: "uniform" | "chain-id" | "hydrophobicity" | "plddt" | "molecule-type" | "secondary-structure" | "residue-name" | "residue-charge";
    color_params: ColorParameters | null;
    representation_type: "cartoon" | "molecular-surface" | "gaussian-surface" | "ball-and-stick";
    residues: number[] | null;
    label: string | null;
};

export type StructureVisualization = {
    pdb: string;
    contigs: string | null;
    color: "uniform" | "chain-id" | "hydrophobicity" | "plddt" | "molecule-type" | "secondary-structure" | "residue-name" | "residue-charge";
    color_params: ColorParameters | null;
    representation_type: "cartoon" | "molecular-surface" | "gaussian-surface" | "ball-and-stick";
    highlighted_selections: string[] | null;
    chains: ChainVisualization[] | null;
};

export type ColorParameters = {
    value: string | null;
    palette: ColorListName | null;
};
