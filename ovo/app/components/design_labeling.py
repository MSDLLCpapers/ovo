import streamlit as st
import humanize
from datetime import datetime, timezone
from ovo import db, Labeling, DesignLabeling
from ovo.core.auth import get_username
from ovo.core.utils.formatting import get_hash_of_bytes

from ovo.app.utils.cached_db import (
    get_cached_labeling_explanations_by_label_name,
    get_cached_labelings_for_design,
    get_cached_all_available_labels_unique,
    get_cached_available_shared_labels_for_design_ids,
)

EMOJI_ICONS = {"❤️": "favorite", "👎": "thumb_down"}
EMOJI_COLORS = {"❤️": "#ff4b4b", "👎": "#ffaa00"}


def show_explanation_input(label: str, input_label: str = "Explanation for this label", **kwargs):
    explanations = get_cached_labeling_explanations_by_label_name(label)
    if explanations:
        # If the label is already present, load the existing explanation for it
        return st.selectbox(
            label=input_label,
            placeholder="Enter a new explanation or select existing",
            options=explanations,
            index=None,
            accept_new_options=True,
            **kwargs,
        )
    else:
        return st.text_input(label=input_label, placeholder="Enter an optional explanation", **kwargs)


@st.fragment
def design_labeling_fragment(design_ids: str | list[str], key_suffix: str = "", header: str = None, show_header=True):
    if isinstance(design_ids, str):
        design_ids = [design_ids]
    is_bulk = len(design_ids) > 1
    design_ids_key = get_hash_of_bytes(",".join(design_ids).encode())

    with st.container(horizontal=True, vertical_alignment="center"):
        if show_header:
            if header:
                st.markdown(f"## {header}")
            elif is_bulk:
                st.markdown(f"## {len(design_ids):,} designs")
            else:
                st.subheader(design_ids[0], width="content")

        # Get labels based on mode
        if is_bulk:
            # Get shared labels (intersection) - all labels regardless of author for display
            shared_label_names = get_cached_available_shared_labels_for_design_ids(design_ids)
            labels_to_show = [name for name in shared_label_names if name not in EMOJI_ICONS]

            # For emoji buttons, only show as active if current user has them on ALL designs
            user_emoji_labels = get_cached_available_shared_labels_for_design_ids(design_ids, author=get_username())
            emoji_labels = set(user_emoji_labels) & set(EMOJI_ICONS.keys())
        else:
            # Get all labelings for single design
            labelings = get_cached_labelings_for_design(design_ids[0])
            labels_to_show = [l for l in labelings if l.label not in EMOJI_ICONS]
            emoji_labels = {l.label for l in labelings if l.label in EMOJI_ICONS and l.author == get_username()}

        with st.container():
            with st.container(
                horizontal=True,
                vertical_alignment="center",
                horizontal_alignment="right" if show_header else "left",
                gap="small",
            ):
                # Show non-emoji labels
                if labels_to_show:
                    if is_bulk:
                        # Show label names as simple badges
                        for label_name in labels_to_show:
                            st.markdown(f":grey-background[&nbsp;{label_name}&nbsp;]")
                    else:
                        # Show full labeling info with author
                        for labeling in labels_to_show:
                            show_label_badge(labeling)
                else:
                    st.write("*No shared labels*" if is_bulk else "*No labels*")

                # Emoji buttons
                styles = []
                for emoji, icon in EMOJI_ICONS.items():
                    key = f"{icon}_button_{design_ids_key}_{key_suffix}"
                    is_active = emoji in emoji_labels
                    if is_active:
                        styles.append(
                            f".st-key-{key} button:hover {{ opacity: 0.9; }}\n.st-key-{key} button {{ background-color: {EMOJI_COLORS[emoji]} !important; border-color: {EMOJI_COLORS[emoji]} !important; }}"
                        )
                        help_message = (
                            f"{emoji} label was added to all {len(design_ids)} selected designs. Click to remove."
                            if is_bulk
                            else None
                        )
                    else:
                        help_message = (
                            f"Add {emoji} label to all {len(design_ids)} selected designs" if is_bulk else None
                        )

                    if st.button(
                        "",
                        type="primary" if is_active else "tertiary",
                        key=key,
                        icon=f":material/{icon}:",
                        help=help_message,
                    ):
                        if is_active:
                            # Remove the current user's emoji label from all designs
                            labelings_to_remove = db.select(Labeling, label=emoji, author=get_username())
                            for labeling in labelings_to_remove:
                                db.remove_designs_labeling(labeling_id=labeling.id, design_ids=design_ids)
                            if "added_labeling" in st.session_state:
                                del st.session_state["added_labeling"]
                        else:
                            # Add emoji label to designs that don't already have it from current user
                            if is_bulk:
                                # Filter out designs that already have this label from current user
                                designs_with_label = set(
                                    db.get_designs_with_any_labels([emoji], design_ids, author=get_username())
                                )
                                designs_to_label = [d for d in design_ids if d not in designs_with_label]
                            else:
                                designs_to_label = design_ids

                            if designs_to_label:
                                labeling = db.add_label(
                                    label=emoji, design_ids=designs_to_label, username=get_username()
                                )
                                st.session_state["added_labeling"] = (labeling, design_ids)
                        st.rerun(scope="fragment" if not is_bulk else "app")

                st.html("<style>\n{}\n</style>".format("\n".join(styles)))

                if st.button(
                    label="Edit labels",
                    type="tertiary",
                    key=f"label_button_{design_ids_key}_{key_suffix}",
                    icon=":material/new_label:",
                ):
                    label_design_dialog(design_ids=design_ids, key_suffix=key_suffix)

            if labeling_and_design_ids := st.session_state.get("added_labeling"):
                labeling, labeled_design_ids = labeling_and_design_ids
                # do not show explanation input if we switched to another design
                if set(labeled_design_ids) == set(design_ids):
                    with st.container(
                        horizontal=True,
                        horizontal_alignment="right" if show_header else "left",
                        vertical_alignment="center",
                    ):
                        if is_bulk:
                            st.write(f":grey[Added label to {len(design_ids):,} designs:] {labeling.label}")
                        else:
                            st.write(f":grey[Added label:] {labeling.label}")
                        explanation = show_explanation_input(labeling.label, width=400, label_visibility="collapsed")
                        if st.button("Add", key=f"add_explanation_{design_ids_key}_{key_suffix}"):
                            if explanation:
                                # The labeling from emoji button always has explanation=None
                                # Create a new labeling with explanation to avoid affecting other designs
                                db.remove_designs_labeling(labeling_id=labeling.id, design_ids=design_ids)
                                db.add_label(
                                    label=labeling.label,
                                    design_ids=design_ids,
                                    username=get_username(),
                                    explanation=explanation,
                                )
                            del st.session_state["added_labeling"]
                            st.rerun(scope="fragment" if not is_bulk else "app")


@st.dialog(f"Add or Edit Labels", width="medium")
def label_design_dialog(design_ids: list[str], key_suffix: str = ""):
    is_bulk = len(design_ids) > 1
    all_labels = get_cached_all_available_labels_unique()

    # Add label section
    if is_bulk:
        st.subheader(f"Add Label to {len(design_ids):,} designs")
    else:
        st.subheader(f"Add Label to {design_ids[0]}")

    new_label = st.selectbox(
        label="Label",
        placeholder="Enter new label or select existing",
        options=all_labels,
        index=None,
        key=f"add_label_select_{key_suffix}",
        accept_new_options=True,
        help="You can select an existing label or type a new one",
    )

    explanation = show_explanation_input(
        label=new_label,
        input_label="Explanation for this label (optional)",
        help="You can select an existing explanation or type a new one",
    )

    if st.button("Add Label", key=f"add_label_btn_{key_suffix}", type="primary", disabled=new_label is None):
        try:
            # Filter out designs that already have this exact label (same name, author, and explanation)
            if is_bulk:
                # Get all labelings with this label name and author
                existing_labelings = db.select(
                    Labeling,
                    label=new_label,
                    author=get_username(),
                    explanation=explanation.strip() if explanation is not None else None,
                )

                if existing_labelings:
                    # Get designs that already have this exact labeling
                    existing_labeling_ids = [l.id for l in existing_labelings]
                    design_labelings = db.select(
                        DesignLabeling, labeling_id__in=existing_labeling_ids, design_id__in=design_ids
                    )
                    designs_with_exact_label = {dl.design_id for dl in design_labelings}
                    designs_to_label = [d for d in design_ids if d not in designs_with_exact_label]
                else:
                    designs_to_label = design_ids
            else:
                designs_to_label = design_ids

            if designs_to_label:
                db.add_label(
                    label=new_label,
                    design_ids=designs_to_label,
                    username=get_username(),
                    explanation=explanation.strip() if explanation is not None else None,
                )
                st.rerun()
        except Exception as e:
            st.error(f"Error adding label: {str(e)}")

    # Remove labels section
    if is_bulk:
        # For bulk operations, show shared labels that can be removed
        shared_labels = get_cached_available_shared_labels_for_design_ids(design_ids)

        if shared_labels:
            st.subheader(f"Remove Shared Labels from All {len(design_ids):,} Designs")
            st.caption(f"These labels are present on all selected designs and can be removed in bulk.")
            with st.container(horizontal=True):
                for label_name in shared_labels:
                    with st.popover(label_name, help="Click to remove this label from all designs"):
                        st.write(f"**Present on:** All {len(design_ids):,} selected designs")

                        if st.button(
                            f"Remove from all {len(design_ids):,} designs",
                            key=f"remove_shared_{label_name}_{key_suffix}",
                            type="secondary",
                            width="stretch",
                        ):
                            try:
                                # Get all labelings with this label for these designs
                                labelings_to_remove = db.select(Labeling, label=label_name)
                                for labeling_obj in labelings_to_remove:
                                    db.remove_designs_labeling(labeling_id=labeling_obj.id, design_ids=design_ids)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error removing label: {str(e)}")
    else:
        # Single design: show all labels with ability to remove
        current_design_labelings = get_cached_labelings_for_design(design_ids[0])
        if current_design_labelings:
            st.subheader(f"Remove Labels from {design_ids[0]}")
            with st.container(horizontal=True):
                for labeling in current_design_labelings:
                    with st.popover(labeling.label, help="Click to see details and remove this label"):
                        st.write(f"**Added by:** {labeling.author}")

                        if labeling.created_date_utc:
                            time_ago = humanize.naturaltime(
                                labeling.created_date_utc, when=datetime.now(timezone.utc).replace(tzinfo=None)
                            )
                            st.write(f"**Added:** {time_ago}")

                        if labeling.explanation:
                            st.write(f"**Explanation:** {labeling.explanation}")
                        else:
                            st.write("**Explanation:** *No explanation provided*")
                        if st.button(
                            "Remove",
                            key=f"remove_{labeling.id}_{key_suffix}",
                            type="secondary",
                            width="stretch",
                        ):
                            try:
                                db.remove_designs_labeling(labeling_id=labeling.id, design_ids=design_ids)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error removing label: {str(e)}")
        else:
            st.caption("No labels assigned to this design yet.")

    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Done", key=f"save_{key_suffix}"):
            st.rerun()


def show_label_badge(labeling: Labeling) -> str:
    badge = f":grey-background[&nbsp;{labeling.label}&nbsp;]"
    if labeling.author != get_username():
        badge += f" :grey[by {labeling.author}]"

    # Build help text with explanation first, then timestamp
    help_parts = []
    if labeling.explanation:
        help_parts.append(f"Explanation: {labeling.explanation}")
    if labeling.created_date_utc:
        time_ago = humanize.naturaltime(labeling.created_date_utc, when=datetime.now(timezone.utc).replace(tzinfo=None))
        help_parts.append(f"Added: {time_ago}")

    help_text = " | ".join(help_parts) if help_parts else None
    st.markdown(badge, help=help_text)
