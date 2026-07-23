export type ContigPartInfo = {
    id: string;
    content: string;
    unindexed?: boolean;
};

export type CoordinateData = {
    serial: number | null;
    x: number | null;
    y: number | null;
    z: number | null;
    occupancy: number | null;
    tempFactor: number | null;
    element: string | null;
    charge: string | null;
    resName: string | null;
    chainID: string | null;
    resSeq: number | null;
    iCode: string | null;
    atom: string | null;
    altLoc?: string | null;
};

export type StreamlitComponentValue = {
    contig: string;
    unindexedSegments: string[];
};
