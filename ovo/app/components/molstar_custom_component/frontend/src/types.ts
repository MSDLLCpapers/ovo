import { ColorListName } from "molstar/lib/mol-util/color/lists";

export type ColorScheme = "uniform" | "chain-id" | "hydrophobicity" | "plddt" | "molecule-type" | "secondary-structure" | "residue-name" | "residue-charge" | "interaction-type";

export type RepresentationType = "cartoon" | "cartoon+ball-and-stick" | "molecular-surface" | "gaussian-surface" | "ball-and-stick" | "interactions" | "cartoon+ball-and-stick+interactions";

export type StructureFormat = "pdb" | "mmcif" | "bcif" | "gro" | "mol" | "sdf" | "mol2" | "xyz";

export type TrajectoryFormat = "trr" | "xtc" | "dcd" | "nctraj";

// analogous to ContigSegment in python
export type ContigSegment = {
    start: number;
    end: number;
    chain: string;
    color: string | null;
    start_label: string | null;
    middle_label: string | null;
    end_label: string | null;
};

export type SequenceSelection = {
    chainId: string;
    residues: number[] | null;
};

export type StreamlitComponentValue = {
    sequenceSelections: SequenceSelection[];
};

export type Representation = {
    selection: string | string[];
    color: ColorScheme;
    color_params: ColorParameters | null;
    representation_type: RepresentationType;
    label: string | null;
};

export type StructureVisualization = {
    data: string;
    data_format: StructureFormat | null;
    trajectory: string | null;
    trajectory_format: TrajectoryFormat | null;
    contigs: ContigSegment[] | null;
    color: ColorScheme;
    color_params: ColorParameters | null;
    representation_type: RepresentationType;
    highlighted_selections: string[] | null;
    representations: Representation[] | null;
    auto_zoom_chains: string[] | null;
};

export type ColorParameters = {
    value: string | null;
    palette: ColorListName | null;
    positions: Record<string, string> | null;
};
