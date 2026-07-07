"""Ranking workflow models for design ranking functionality."""

import os
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Self
import numpy as np

from ovo import db, storage
from ovo.core.database.models import (
    NumericGlobalDescriptor,
    WorkflowTypes,
    WorkflowTask,
    DescriptorWorkflow,
    DescriptorJob,
    DescriptorValue,
    Design,
    Base,
    ProjectArtifact,
)
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.auth import get_username


@dataclass
class RankingDescriptorWorkflow(DescriptorWorkflow, ABC):
    """Base class for ranking workflows.

    Handles result processing and rank descriptor creation.
    Child classes don't need to override this.
    """

    chains: list[str] = field(default_factory=lambda: ["ALL"])
    descriptor_keys: list[str] = field(default_factory=lambda: [])
    ranking_name: str = ""
    ranking_description: str = ""  # filled in by workflow subclasses

    def validate(self):
        if not self.ranking_name:
            raise ValueError("Please enter a name for this ranking")

    def process_results(self, job: DescriptorJob, callback: Callable = None) -> list[Base]:
        """Read ranking results from CSV and create rank descriptors."""
        from ovo import get_scheduler
        from ovo.core.database.descriptors_ranking import RANK

        scheduler = get_scheduler(job.scheduler_key)
        execdir = scheduler.get_output_dir(job.job_id)

        # Read ranking CSV (design_id, rank columns)
        df = pd.read_csv(os.path.join(execdir, "ranking.csv"))
        df = df.sort_values("rank")  # Ensure sorted by rank

        # Save rank as descriptor
        descriptor_values = []
        chains = ",".join(self.chains)
        for _, row in df.iterrows():
            descriptor_values.append(
                DescriptorValue(
                    design_id=row["design_id"],
                    descriptor_key=RANK.key,
                    descriptor_job_id=job.id,
                    chains=chains,
                    value=str(int(row["rank"])),
                )
            )

        return descriptor_values

    @classmethod
    @abstractmethod
    def from_ui(cls, design_ids: list[str]) -> list[Self]:
        """Create workflow instances from UI inputs.

        This method should display Streamlit widgets and return a list of configured
        workflow instances (sometimes a single one). Called inside the submission dialog.

        When some inputs are missing or errors happen, this method should show warnings and return an empty list.

        Args:
            design_ids: Design IDs to use

        Returns:
            Configured workflow instances ready for submission
        """
        raise NotImplementedError()

    def show_design_header(self, design: Design):
        """Show design header with descriptor value using st.metric.

        Args:
            design: Design object to show header for
        """
        from ovo.app.components.workflow_visualization_components import show_design_metrics

        show_design_metrics(
            design.id,
            descriptor_keys=self.descriptor_keys,
        )

    def visualize_summary(self, job: DescriptorJob):
        import streamlit as st

        st.subheader(f"{job.workflow.ranking_name} - {job.workflow.name}")

        with st.expander("Job details", expanded=False):
            st.write(f"**Ranking name:** {job.workflow.ranking_name}")
            st.write(f"**Method:** {job.workflow.name}")
            st.write(job.workflow.ranking_description)
            st.write(
                f"**Descriptors:** {', '.join([ALL_DESCRIPTORS_BY_KEY[d].name for d in job.workflow.descriptor_keys])}"
            )
            st.write(f"**Chains:** {job.workflow.chains}")
            st.write(f"**Submitted:** {job.created_date_utc.strftime('%Y-%m-%d %H:%M:%S')}")

            self._visualize_workflow_specific_params()

    def _visualize_workflow_specific_params(self):
        """Override in subclasses to display workflow-specific parameters."""
        pass


@dataclass
class RankingTask(WorkflowTask, RankingDescriptorWorkflow, ABC):
    """Abstract base for ranking task implementations.

    Child classes must implement:
    - rank(): Returns a pandas DataFrame containing ranking results with 'design_id' and 'rank' columns
    """

    def run(self, execdir: str, scheduler) -> None:
        """Execute ranking and save results to CSV."""
        # Get descriptor value table
        values = self.select_descriptor_values()
        ranking = self.rank(values)

        if "rank" not in ranking.columns:
            raise ValueError("Ranking result must contain a 'rank' column")

        # Save to CSV
        ranking = ranking.sort_values("rank")
        ranking.to_csv(os.path.join(execdir, "ranking.csv"), index_label="design_id")

    def select_descriptor_values(self) -> pd.DataFrame:
        return db.select_wide_descriptor_table(
            self.design_ids,
            self.descriptor_keys,
        )

    @abstractmethod
    def rank(self, values: pd.DataFrame) -> pd.DataFrame:
        """Compute rankings for designs.

        :param values: DataFrame indexed by design_id and descriptor key values needed for ranking

        :return: dataframe indexed by design_id with a 'rank' column (1, 2, 3, ..., lower is better)
        """
        raise NotImplementedError()


AGGREGATION_LABELS = {
    "average": "Average rank",
    "product": "Product of ranks",
    "worst-case": "Worst-case (Max of ranks)",
}


@WorkflowTypes.register("Rank Aggregation")
@dataclass
class RankAggregationRankingTask(RankingTask):
    ranking_description: str = """
    Rank designs by multiple descriptors using a configurable aggregation method. 
    
    Each descriptor is ranked individually and scaled by its weight (weight > 1.0 = more important, weight < 1.0 = less important). 
    A rank is the position of a design in the sorted list of designs for a given descriptor (rank 1 = best, rank 2 = second best, etc.). 
    
    The ranks are combined using the selected method: Sum, Product, or Worst-case (worst-case = maximum scaled rank across all metrics).
    """
    descriptor_comparisons: dict[str, str] = field(
        default_factory=lambda: {}
    )  # descriptor_key -> "higher_is_better" or "lower_is_better"
    descriptor_weights: dict[str, float] = field(default_factory=lambda: {})
    aggregation_method: str = "average"  # "average", "product", or "worst-case"

    # BoltzGen descriptors and inverse importances https://github.com/HannesStark/boltzgen/blob/v0.3.2/src/boltzgen/task/filter/filter.py#L203-L209
    # "design_to_target_iptm": 1,
    # "design_ptm": 1,
    # "neg_min_design_to_target_pae": 1,
    # "plip_hbonds" + ("_refolded" if from_inverse_folded else ""): 2,
    # "plip_saltbridge" + ("_refolded" if from_inverse_folded else ""): 2,
    # "delta_sasa_refolded" if from_inverse_folded else "delta_sasa_original": 2,

    def rank(self, values: pd.DataFrame) -> pd.DataFrame:
        """Rank designs based on selected aggregation method."""

        # Compute scaled ranks for all descriptors
        for descriptor_key in self.descriptor_keys:
            # Determine ranking direction
            ascending = self.descriptor_comparisons.get(descriptor_key) == "lower_is_better"

            # Rank the descriptor
            rank_values = values[descriptor_key].rank(ascending=ascending, method="average", na_option="bottom")

            # Scale by weight (default to 1.0 if not specified)
            weight = self.descriptor_weights.get(descriptor_key, 1.0)
            if weight <= 0:
                raise ValueError(f"Weight for descriptor '{descriptor_key}' must be a positive number")

            # Store scaled rank
            values[f"rank_{descriptor_key}"] = rank_values * weight

        # Get all rank columns
        rank_cols = [f"rank_{descriptor_key}" for descriptor_key in self.descriptor_keys]

        # Apply aggregation method
        if self.aggregation_method == "product":
            raw_aggregated_rank = np.prod(values[rank_cols], axis=1)
        elif self.aggregation_method == "average":
            raw_aggregated_rank = values[rank_cols].mean(axis=1)
        elif self.aggregation_method == "worst-case":
            raw_aggregated_rank = values[rank_cols].max(axis=1)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")

        values.insert(0, "raw_aggregated_rank", raw_aggregated_rank)

        # Compute final rank
        values.insert(0, "rank", raw_aggregated_rank.rank(method="first", na_option="bottom"))

        return values

    @classmethod
    def from_ui(cls, design_ids: list[str]) -> list[Self]:
        """UI for selecting aggregation method and descriptors."""
        import streamlit as st
        from ovo.app.utils.cached_db import get_cached_available_descriptors
        from ovo.app.components.ranking_components import configure_rank_aggregation_descriptors

        # Get available numeric descriptors
        descriptors_by_key = get_cached_available_descriptors(design_ids)
        descriptors_by_key = {d.key: d for d in descriptors_by_key.values() if isinstance(d, NumericGlobalDescriptor)}

        if not descriptors_by_key:
            st.warning("No descriptors available for selected designs")
            return []

        # User selects descriptors and assigns the comparison
        selected_keys, descriptor_comparisons, descriptor_weights = configure_rank_aggregation_descriptors(
            descriptors_by_key, design_ids
        )
        if not selected_keys:
            st.info("Please select at least one descriptor")
            return []

        # Check that all selected descriptors have a comparison specified
        if not all(descriptor_comparisons.values()) or len(descriptor_comparisons) != len(selected_keys):
            st.info("Please specify a comparison for all selected descriptors")
            return []

        # Check that all selected descriptors have a weight specified
        if not all(descriptor_weights.values()) or len(descriptor_weights) != len(selected_keys):
            st.info("Please specify a weight for all selected descriptors")
            return []

        # Aggregation method selection
        aggregation_method = st.selectbox(
            "Aggregation method",
            options=["average", "product", "worst-case"],
            format_func=AGGREGATION_LABELS.get,
            help="Method to aggregate individual descriptor ranks into a final ranking",
        )
        aggregation_help = {
            "average": "Ranks of each design are averaged across descriptors. A poor rank in one descriptor can be balanced by strong ranks in others.",
            "product": "Ranks of each design are multiplied across descriptors. A poor rank in any single descriptor heavily penalizes the overall score.",
            "worst-case": "The final rank of each design is the worst rank across all descriptors, inspired by BoltzGen ranking. Emphasizes designs that perform reasonably well on every metric.",
        }
        st.caption(f"**{AGGREGATION_LABELS[aggregation_method]}**: {aggregation_help[aggregation_method]}")

        # Prefill placeholder with auto-generated name, and use that as default when ranking_name is empty
        autogenerated_name = f"{AGGREGATION_LABELS[aggregation_method]} "
        if len(selected_keys) == 1:
            autogenerated_name += f"of {descriptors_by_key[selected_keys[0]].name}"
        elif len(selected_keys) == 2:
            autogenerated_name += (
                f"of {descriptors_by_key[selected_keys[0]].name} and {descriptors_by_key[selected_keys[1]].name}"
            )
        else:
            autogenerated_name += f"of {len(selected_keys)} descriptors"

        ranking_name = st.text_input(
            "Ranking name",
            placeholder=autogenerated_name,
            key="ranking_name",
        )

        return [
            cls(
                ranking_name=ranking_name or autogenerated_name,
                design_ids=design_ids,
                descriptor_keys=selected_keys,
                descriptor_comparisons=descriptor_comparisons,
                descriptor_weights=descriptor_weights,
                aggregation_method=aggregation_method,
            )
        ]

    def _visualize_workflow_specific_params(self):
        """Display aggregation method and descriptor comparisons."""
        import streamlit as st

        st.write(f"**Aggregation method:** {AGGREGATION_LABELS.get(self.aggregation_method, self.aggregation_method)}")

        if self.descriptor_comparisons:
            st.write("**Descriptor comparisons:**")
            for key, comparison in self.descriptor_comparisons.items():
                st.write(f"- {ALL_DESCRIPTORS_BY_KEY[key].name}: {comparison}")

        # Show weights if any are non-default (not 1.0)
        if self.descriptor_weights and any(v != 1.0 for v in self.descriptor_weights.values()):
            st.write("**Descriptor weights:**")
            for key, weight in self.descriptor_weights.items():
                st.write(f"- {ALL_DESCRIPTORS_BY_KEY[key].name}: {weight}")
