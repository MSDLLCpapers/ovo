"""Creating a pool of designs from uploaded files, without a design workflow.

Front-end agnostic — this is the sequence that used to live inside the "Upload new pool" Streamlit
dialog (``ovo/app/components/pool_components.py``). The dialog keeps the whole form (round picker,
file uploader, column configuration, validation and its error messages), collects what the user
entered into a :class:`PoolUpload` and calls :func:`create_pool_from_uploads` with it.

Uploads come in two shapes, and exactly one of them must be given:

- **structure files** — PDB/CIF/MMCIF files plus the chain IDs to analyze
- **a table** — a parsed DataFrame of sequences plus which column is the id and which columns are
  which chains

Either way the result is a saved :class:`Pool` of :class:`Design` objects with a
``seq_composition`` descriptor job submitted for them.

Structure files are duck-typed, not a concrete type: anything with ``.name`` and ``.read()`` works
(``create_designs_from_structure_files`` needs no more than that). That covers Streamlit's
``UploadedFile``, a plain open file object, and — with a thin adapter — FastAPI's ``UploadFile``.
"""

import re
import traceback
from dataclasses import dataclass, field

import pandas as pd

from ovo import config, db, get_username
from ovo.core.database.models import Pool, Round
from ovo.core.database.models_proteinqc import ProteinQCWorkflow
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow
from ovo.core.logic.design_logic import create_designs_from_dataframe, create_designs_from_structure_files

# Number of designs whose descriptors are computed per scheduler task
SEQ_COMPOSITION_BATCH_SIZE = 100


@dataclass
class PoolUpload:
    """One pool to create, together with the uploads to create its designs from.

    Collected by the front-end (see the module docstring) and consumed by
    :func:`create_pool_from_uploads`, which reports a :class:`PoolUploadResult`.

    Either ``structure_files`` or ``dataframe`` is given, never both: :meth:`validate` refuses
    every other combination up front, so a half-specified upload is rejected before any design is
    built. The round is given the same way, as either an existing ``round_id`` or a
    ``new_round_name`` to create.

    :param project_id: Project to create the pool under
    :param pool_name: Name of the new pool (uniqueness within the round is the caller's to check)
    :param round_id: Existing round to add the pool to; omit to create a new round
    :param new_round_name: Name for a new round, when round_id is not given
    :param description: Optional longer pool description
    :param structure_files: PDB/CIF/MMCIF files, each with ``.name`` and ``.read()``
    :param chains: Chain IDs to analyze in the structure files, e.g. "AB", "A,B" or ["A", "B"].
                   Not accepted with ``dataframe``, where the chains come from ``column_chains``.
    :param dataframe: Parsed table of sequences, as an alternative to structure_files
    :param id_column: Column of ``dataframe`` to build design IDs from
    :param column_chains: {sequence column: chain IDs} for ``dataframe``, e.g. {"heavy": "A"}
    """

    project_id: str
    pool_name: str
    round_id: str | None = None
    new_round_name: str | None = None
    description: str = ""
    structure_files: list | None = None
    chains: str | list[str] | None = None
    dataframe: pd.DataFrame | None = None
    id_column: str | None = None
    column_chains: dict[str, str] | None = None

    @property
    def is_tabular(self) -> bool:
        """Whether the designs come from a table of sequences rather than from structure files."""
        return self.dataframe is not None

    def get_chains(self) -> list[str]:
        """Return the chain IDs to analyze, one capital letter each.

        Parsed from any of the "AB", "A,B" and ["A", "B"] forms the front-ends collect them in.
        Empty when no chains were given, and for a table upload, whose chains are only known once
        the designs are built from ``column_chains``.

        :raises ValueError: if the chains are not capital letters, in either form
        """
        if self.is_tabular or not self.chains:
            return []
        # A list is joined into the same string form first, so that both forms are validated here
        joined = self.chains if isinstance(self.chains, str) else "".join(str(chain) for chain in self.chains)
        chains = joined.replace(" ", "").replace(",", "")
        if not re.match(r"^[A-Z]+$", chains):
            raise ValueError(f"Invalid chains {self.chains!r}, expected capital letters, e.g. 'A' or 'AB'")
        return list(chains)

    def validate(self) -> None:
        """Check that the upload is fully and unambiguously specified.

        :raises ValueError: on a missing or ambiguous file argument, round or chain specification
        """
        if bool(self.structure_files) == self.is_tabular:
            raise ValueError("Provide either structure_files or dataframe, not both")
        if bool(self.round_id) == bool(self.new_round_name and self.new_round_name.strip()):
            raise ValueError("Provide exactly one of round_id or a non-empty new_round_name")
        if self.is_tabular:
            if self.chains:
                # The chains of a table upload are defined by column_chains, so a chains argument
                # would be silently ignored — reject it instead of letting the caller believe it had
                # an effect
                raise ValueError("chains cannot be combined with dataframe, the chains come from column_chains")
            if not self.id_column or not self.column_chains:
                raise ValueError("id_column and column_chains are required when creating designs from a dataframe")
        elif not self.get_chains():
            raise ValueError("chains is required when creating designs from structure files")


@dataclass
class PoolUploadResult:
    """Outcome of :func:`create_pool_from_uploads`."""

    pool: Pool
    num_designs: int
    chains: list[str]
    # Warnings from converting CIF/MMCIF input to PDB, if any
    conversion_warnings: list[str] = field(default_factory=list)
    # Set if the pool was saved but its seq_composition descriptor job could not be submitted
    descriptor_job_error: str = None


def create_pool_from_uploads(upload: PoolUpload, callback: callable = None) -> PoolUploadResult:
    """Create and save a pool of designs from uploaded structure files or a table of sequences.

    The designs, the pool and the new round (if any) are saved in one atomic ``save_all``, so a
    failure to build the designs leaves nothing behind. The ``seq_composition`` descriptor job is
    submitted afterwards and is deliberately non-fatal: a scheduler problem should not lose an
    upload that already succeeded, so the error is returned on the result instead of raised.

    :param upload: The pool to create and the uploads to create its designs from
    :param callback: Optional progress callback, called with a human-readable message per step
    :raises ValueError: on an invalid upload (see :meth:`PoolUpload.validate`), or a missing round
    """
    upload.validate()

    def report(message: str) -> None:
        if callback is not None:
            callback(message)

    username = get_username()

    new_round = None
    round_id = upload.round_id
    if not round_id:
        new_round = Round(project_id=upload.project_id, name=upload.new_round_name.strip(), author=username)
        round_id = new_round.id
    else:
        rounds = db.select(Round, id=round_id)
        if not rounds:
            raise ValueError(f"Round '{round_id}' does not exist")
        if rounds[0].project_id != upload.project_id:
            raise ValueError(f"Round '{round_id}' does not belong to project '{upload.project_id}'")

    pool = Pool(
        id=Pool.generate_id(),
        author=username,
        round_id=round_id,
        name=upload.pool_name,
        description=upload.description,
    )

    chains = upload.get_chains()
    conversion_warnings = []
    if upload.is_tabular:
        report("Processing sequence data...")
        designs = create_designs_from_dataframe(
            df=upload.dataframe,
            id_column=upload.id_column,
            column_chains=upload.column_chains,
            pool_id=pool.id,
        )
        # Descriptors are computed for every chain that ended up on a design
        chains = sorted(
            {chain_id for design in designs for chain in design.spec.chains for chain_id in chain.chain_ids}
        )
    else:
        report("Uploading designs...")
        designs, conversion_warnings = create_designs_from_structure_files(
            structure_files=upload.structure_files,
            chains=chains,
            pool=pool,
            project_id=upload.project_id,
        )

    if not designs:
        raise ValueError("No designs could be created from the uploaded files")

    report(f"Saving {len(designs):,} designs to DB...")
    db.save_all(designs + ([new_round] if new_round else []) + [pool])

    result = PoolUploadResult(
        pool=pool,
        num_designs=len(designs),
        chains=chains,
        conversion_warnings=conversion_warnings,
    )

    # Trigger sequence composition computation with the local scheduler.
    # Non-fatal: the pool is already saved, so report the failure rather than losing the upload.
    try:
        report("Submitting descriptor job...")
        submit_descriptor_workflow(
            workflow=ProteinQCWorkflow(
                tools=["seq_composition"],
                chains=chains,
                design_ids=[design.id for design in designs],
                batch_size=SEQ_COMPOSITION_BATCH_SIZE,
            ),
            scheduler_key=config.local_scheduler,
            project_id=upload.project_id,
        )
    except Exception as e:
        traceback.print_exc()
        result.descriptor_job_error = str(e)

    return result
