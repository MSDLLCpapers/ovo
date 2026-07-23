import { ContigPartInfo, CoordinateData } from "./types";

export const hexToRgba = (hexColor: string | null | undefined, alpha: number = 1.0) => {
    // remove # if present, fall back to neutral grey for missing/invalid input
    hexColor = (hexColor ?? "#6d6d6d").replace(/^#/, '');

    if (hexColor.length !== 6) {
        hexColor = "6d6d6d";
    }

    const r = parseInt(hexColor.substring(0, 2), 16);
    const g = parseInt(hexColor.substring(2, 4), 16);
    const b = parseInt(hexColor.substring(4, 6), 16);

    return {
        r: r,
        g: g,
        b: b,
        a: alpha
    };
};

export const calculateResidueCenter = <T extends { x: number | null; y: number | null; z: number | null; atom: string | null; }>(atoms: T[]) => {
    // NOT using average for now, instead we are looking for the CA atom
    const { total, count } = atoms.reduce((acc, { x, y, z }) => {
        if (x !== null && y !== null && z !== null) {
            acc.total.x += x;
            acc.total.y += y;
            acc.total.z += z;
            acc.count++;
        }
        return acc;
    }, { total: { x: 0, y: 0, z: 0 }, count: 0 });

    return count === 0 ? null
        : {
            x: total.x / count,
            y: total.y / count,
            z: total.z / count,
        };
};

export const calculateResidueCoordinates = <T extends { x: number | null; y: number | null; z: number | null; atom: string | null; }>(atoms: T[]) => {
    if (atoms.length === 0) return null;

    const CAatom = atoms.find(atom => atom.atom === "CA");
    if (!CAatom || !CAatom.x || !CAatom.y || !CAatom.z) return null;

    return { x: CAatom.x, y: CAatom.y, z: CAatom.z };
};

export const getRange = (arr: number[]) => {
    const start = arr[0];
    const end = arr[arr.length - 1] - start + 1;
    const range = Array.from(new Array(end), (x, i) => i + start);

    return range;
};

export const AminoAcids = {
    'ALA': 'A', // Alanine
    'ARG': 'R', // Arginine
    'ASN': 'N', // Asparagine
    'ASP': 'D', // Aspartic Acid
    'CYS': 'C', // Cysteine
    'GLU': 'E', // Glutamic Acid
    'GLN': 'Q', // Glutamine
    'GLY': 'G', // Glycine
    'HIS': 'H', // Histidine
    'ILE': 'I', // Isoleucine
    'LEU': 'L', // Leucine
    'LYS': 'K', // Lysine
    'MET': 'M', // Methionine
    'PHE': 'F', // Phenylalanine
    'PRO': 'P', // Proline
    'SER': 'S', // Serine
    'THR': 'T', // Threonine
    'TRP': 'W', // Tryptophan
    'TYR': 'Y', // Tyrosine
    'VAL': 'V', // Valine
    '?': "?"    // Unknown
} as const;

export const isGeneratedSegment = (segment: string) => {
    if (segment === undefined) {
        return false;
    }

    return segment.toLowerCase() === segment.toUpperCase();
};

export const parseFixedSegment = (segment: string): { chainId: string; firstIndex: number; lastIndex: number; } | null => {
    const regex = /^([A-Z]+)(\d+)(-\d+)?$/;
    const match = segment.match(regex);

    // If the match is null, the input does not conform to the pattern
    if (!match) {
        console.error("The regex cannot parse this segment: " + segment);
        return null;
    }

    const [, chainId, firstIndexStr, lastIndexStr] = match;

    const firstIndex = parseInt(firstIndexStr, 10);
    const lastIndex = lastIndexStr ? parseInt(lastIndexStr.slice(1), 10) : firstIndex;

    if (firstIndex > lastIndex) {
        console.error("Invalid segment: " + segment);
        return null;
    }

    return {
        chainId,
        firstIndex,
        lastIndex,
    };
};

export const calculateDistances = (segments: ContigPartInfo[], coordinates: CoordinateData[]) => {
    const fixedSegments = segments.filter((e) => !isGeneratedSegment(e.content));
    const results = [];

    for (let i = 0; i < fixedSegments.length - 1; i++) {
        const segment1 = parseFixedSegment(fixedSegments[i].content);
        const segment2 = parseFixedSegment(fixedSegments[i + 1].content);

        if (!segment1) {
            console.error("Failed parsing distances for this segment: " + fixedSegments[i].content);
            continue;
        }

        if (!segment2) {
            console.error("Failed parsing distances for this segment: " + fixedSegments[i + 1].content);
            continue;
        }

        const segment1atoms = coordinates.filter((e) => e.resSeq === segment1.lastIndex && e.chainID === segment1.chainId);
        const segment2atoms = coordinates.filter((e) => e.resSeq === segment2.firstIndex && e.chainID === segment2.chainId);

        const center1 = calculateResidueCoordinates(segment1atoms);
        const center2 = calculateResidueCoordinates(segment2atoms);

        if (!center1) {
            console.error("Failed parsing distances for this segment: " + fixedSegments[i].content);
            continue;
        }

        if (!center2) {
            console.error("Failed parsing distances for this segment: " + fixedSegments[i + 1].content);
            continue;
        }

        const result = Math.sqrt((center2.x - center1.x) ** 2 + (center2.y - center1.y) ** 2 + (center2.z - center1.z) ** 2);

        results.push({ segment: `${segment1.chainId}${segment1.lastIndex}_${segment2.chainId}${segment2.firstIndex}`, result: result });
    }

    return results;
};
