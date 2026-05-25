import dataclasses
import json
import warnings
from typing import Literal

ColorScheme = Literal[
    "uniform",
    "chain-id",
    "hydrophobicity",
    "plddt",
    "molecule-type",
    "secondary-structure",
    "residue-name",
    "residue-charge",
    "interaction-type",
]

RepresentationType = Literal[
    "cartoon",
    "cartoon+ball-and-stick",
    "molecular-surface",
    "gaussian-surface",
    "ball-and-stick",
    "interactions",
    "cartoon+ball-and-stick+interactions",
]

StructureFormat = Literal["pdb", "mmcif", "bcif", "gro", "mol", "sdf", "mol2", "xyz"]

TrajectoryFormat = Literal["trr", "xtc", "dcd", "nctraj"]


class EnhancedJSONEncoder(json.JSONEncoder):
    """A JSON encoder for enabling the export of dataclasses."""

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore
        return super().default(o)


def _normalize_color(color: str | None, color_params: dict | None) -> tuple[str, dict | None]:
    """Expand "#hex" / "#rgb" shorthand into a uniform color + color_params."""
    if isinstance(color, str) and color.startswith("#"):
        hex_val = color.lstrip("#")
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        merged = {**(color_params or {}), "value": f"0x{hex_val}"}
        return "uniform", merged
    return color or "uniform", color_params


@dataclasses.dataclass
class Representation:
    """A representation for one or more chains/residue ranges in a structure.

    Parameters
    ----------
    selection : str | list[str]
        Selection string(s), e.g. "A", "A,B", "B123-456" or ["A", "B4"].
        Bare chain letters select the whole chain; digits select residues.
    representation_type : RepresentationType, optional
        Representation type, by default "cartoon". Also accepted as the ``representation`` alias.
    color : str, optional
        Color scheme name (e.g. "chain-id", "plddt") or a hex color like "#ff0000".
        By default "uniform".
    color_params : dict, optional
        Color parameters.
        In the case of "uniform", the `color_params` field should be for example {"value": "0x00ff00"}.
        In the case of "chain-id", the `color_params` field should be for example {"palette": "pastel-1"}.
        Supports positional overpaint via {"value": "0xffffff", "positions": {"A123": "#ff0000"}}.
    label : str, optional
        The label to show when hovering over the visualization, by default None.
        Only works for single-chain selections on PDB string inputs.
    """

    selection: str | list[str]
    color: ColorScheme = "uniform"
    color_params: dict | None = None
    representation_type: RepresentationType = "cartoon"
    label: str | None = None

    def __custom_init__(
        self,
        selection: str | list[str],
        representation: RepresentationType | None = None,
        *,
        color: str = "uniform",
        color_params: dict | None = None,
        representation_type: RepresentationType | None = None,
        label: str | None = None,
    ) -> None:
        """Accept both ``representation=`` (ergonomic) and ``representation_type=`` (dataclass native),
        and normalize hex colors like "#ff0000" into ``color="uniform"`` + ``color_params={"value": "0xff0000"}``."""
        if representation is not None and representation_type is None:
            representation_type = representation
        if representation_type is None:
            representation_type = "cartoon"
        norm_color, norm_color_params = _normalize_color(color, color_params)
        _Representation_orig_init(
            self,
            selection=selection,
            color=norm_color,  # type: ignore[arg-type]
            color_params=norm_color_params,
            representation_type=representation_type,
            label=label,
        )


_Representation_orig_init = Representation.__init__
Representation.__init__ = Representation.__custom_init__  # type: ignore[assignment]


@dataclasses.dataclass
class ChainVisualization:
    """Deprecated per-chain visualization, accepted by ``StructureVisualization(chains=...)``.

    Converted to ``Representation`` on the fly."""

    chain_id: str
    color: ColorScheme = "uniform"
    color_params: dict | None = None
    representation_type: RepresentationType = "cartoon"
    residues: list[int] | None = None
    label: str | None = None


@dataclasses.dataclass
class StructureVisualization:
    """Class for storing data about structures shown in the Mol* component.

    Parameters
    ----------
    data : str | bytes
        Structure file content (PDB, mmCIF, GRO, etc.) or a URL to a structure file.
        For binary formats like BCIF, pass raw bytes (e.g. ``Path("file.bcif").read_bytes()``)
        and set ``data_format="bcif"``.
    data_format : StructureFormat, optional
        Explicit format of the structure file. If None, auto-detected (PDB vs mmCIF).
        Must be set for non-PDB/mmCIF formats like GRO or BCIF.
    trajectory : bytes, optional
        Raw binary trajectory data (TRR, XTC, DCD, NetCDF). Pass ``Path(...).read_bytes()``
        or equivalent.
    trajectory_format : TrajectoryFormat, optional
        Format of the trajectory file. Required when ``trajectory`` is provided.
    contigs : list[ContigSegment], optional
        A list of contig segments to show (e.g. on the top of the viewer), by default None.
    color : str, optional
        The color scheme name or a hex color like "#ffffff", by default "uniform".
    color_params : dict, optional
        Color parameters (see ``Representation``).
    representation_type : RepresentationType, optional
        Default representation type, by default "cartoon". Also accepted as the ``representation`` alias.
    highlighted_selections : list[str], optional
        Selections to highlight in green. Also accepted as the ``selection`` alias.
    representations : list[Representation] | Representation, optional
        Per-selection representations with individual coloring, by default None.
    auto_zoom_chains : list[str], optional
        Chains to auto-zoom the camera to.
    """

    data: str | bytes
    data_format: StructureFormat | None = None
    trajectory: bytes | None = None
    trajectory_format: TrajectoryFormat | None = None
    contigs: list | None = None
    color: ColorScheme = "uniform"
    color_params: dict | None = None
    representation_type: RepresentationType | None = "cartoon"
    highlighted_selections: list[str] | None = None
    representations: list[Representation] | None = None
    auto_zoom_chains: list[str] | None = None

    def __post_init__(self) -> None:
        if self.trajectory and not self.trajectory_format:
            raise ValueError("'trajectory_format' is required when 'trajectory' is provided")
        if self.representations:
            if isinstance(self.representations, Representation):
                self.representations = [self.representations]
            elif not isinstance(self.representations, list):
                raise ValueError(
                    f"Invalid type for representations, expected Representation or list, got: {type(self.representations).__name__}"
                )
        if self.auto_zoom_chains and not isinstance(self.auto_zoom_chains, list):
            raise ValueError(
                f"Invalid type for auto_zoom_chains, expected list of str, got: {type(self.auto_zoom_chains).__name__}"
            )
        if self.contigs:
            assert isinstance(self.contigs, list), (
                f"Invalid type for contigs, expected list of segment objects, got: {type(self.contigs).__name__}"
            )
            for contig_or_segment in self.contigs:
                if isinstance(contig_or_segment, str):
                    raise ValueError(
                        "Passing contigs as a string is not supported anymore since they need to be interpreted differently"
                        "for the input and the output structure. "
                        "When visualizing contigs on the input structure, "
                        "please provide contigs parsed using the parse_contig_for_input_structure function. "
                        "When visualizing contigs on the output structure, "
                        "please use the parse_contig_for_output_structure function."
                    )
                if (
                    not hasattr(contig_or_segment, "start")
                    or not hasattr(contig_or_segment, "end")
                    or not hasattr(contig_or_segment, "chain")
                ):
                    raise ValueError(
                        f"Invalid type for contig segment, expected ContigSegment object, got: {type(contig_or_segment).__name__}"
                    )

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def add_representation(
        self,
        selection: str | list[str],
        representation: RepresentationType = "cartoon",
        *,
        color: str = "uniform",
        color_params: dict | None = None,
        label: str | None = None,
    ) -> "StructureVisualization":
        """Add a representation and return self for chaining."""
        rep = Representation(
            selection=selection,
            representation_type=representation,
            color=color,  # type: ignore[arg-type]
            color_params=color_params,
            label=label,
        )
        if self.representations is None:
            self.representations = []
        self.representations.append(rep)
        return self

    def __custom_init__(
        self,
        *args,
        selection=None,
        representation=None,
        pdb=None,
        chains=None,
        **kwargs,
    ) -> None:
        """Accept ergonomic aliases (``selection=``, ``representation=``) and deprecated names
        (``pdb=``, ``chains=``), and normalize hex colors for ``color=``.
        """
        # deprecated pdb= -> data=
        if pdb is not None and "data" not in kwargs and not args:
            warnings.warn(
                "StructureVisualization(pdb=...) is deprecated, use data= instead. Example: from ovo import viz; viz.molstar(viz.StructureVisualization(data=pdb_data))",
                DeprecationWarning,
                stacklevel=2,
            )
            kwargs["data"] = pdb

        # deprecated chains= -> representations=
        if chains is not None and "representations" not in kwargs:
            warnings.warn(
                "StructureVisualization(chains=...) is deprecated, use representations= with Representation instead",
                DeprecationWarning,
                stacklevel=2,
            )
            chains_list = chains if isinstance(chains, list) else [chains]
            reps = []
            for ch in chains_list:
                sel = ch.chain_id if hasattr(ch, "chain_id") else ch.selection
                if hasattr(ch, "residues") and ch.residues:
                    sel = [f"{ch.chain_id}{r}" for r in ch.residues]
                reps.append(
                    Representation(
                        selection=sel,
                        color=ch.color,
                        color_params=ch.color_params,
                        representation_type=ch.representation_type,
                        label=ch.label if hasattr(ch, "label") else None,
                    )
                )
            kwargs["representations"] = reps

        # representation= alias for representation_type= in the main visualization (not per-selection)
        # selection= alias for highlighted_selections= in the main visualization (not per-selection)
        if selection is not None and "highlighted_selections" not in kwargs:
            kwargs["highlighted_selections"] = selection
        if representation is not None and "representation_type" not in kwargs:
            kwargs["representation_type"] = representation

        # hex color normalization (applies to both explicit and alias paths)
        if "color" in kwargs or "color_params" in kwargs:
            kwargs["color"], kwargs["color_params"] = _normalize_color(
                kwargs.get("color", "uniform"), kwargs.get("color_params")
            )

        _StructureVisualization_orig_init(self, *args, **kwargs)


_StructureVisualization_orig_init = StructureVisualization.__init__
StructureVisualization.__init__ = StructureVisualization.__custom_init__  # type: ignore[assignment]
