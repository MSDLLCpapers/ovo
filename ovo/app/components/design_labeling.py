import streamlit as st
from ovo import db, Labeling
from ovo.core.auth import get_username

from ovo.app.utils.cached_db import (
    get_cached_labeling_explanations_by_label_name,
    get_cached_labelings_for_design,
    get_cached_all_available_labels_unique,
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
def design_labeling_fragment(design_id: str, key_suffix: str = "", show_header=True, header_prefix=None):
    with st.container(horizontal=True, vertical_alignment="top"):
        if show_header:
            st.subheader(f"{header_prefix} {design_id}" if header_prefix else design_id, width="content")

        labelings = get_cached_labelings_for_design(design_id)

        with st.container():
            with st.container(
                horizontal=True,
                vertical_alignment="center",
                horizontal_alignment="right" if show_header else "left",
                gap="small",
            ):
                emoji_labelings = {}
                if labelings:
                    for labeling in labelings:
                        if labeling.label in EMOJI_ICONS and labeling.author == get_username():
                            emoji_labelings[labeling.label] = labeling
                            continue
                        show_label_badge(labeling)
                else:
                    st.write("*No labels*")

                styles = []
                for emoji, icon in EMOJI_ICONS.items():
                    key = f"{icon}_button_{design_id}_{key_suffix}"
                    if emoji in emoji_labelings:
                        styles.append(
                            f".st-key-{key} button:hover {{ opacity: 0.9; }}\n.st-key-{key} button {{ background-color: {EMOJI_COLORS[emoji]} !important; border-color: {EMOJI_COLORS[emoji]} !important; }}"
                        )
                    if st.button(
                        "",
                        type="primary" if emoji in emoji_labelings else "tertiary",
                        key=key,
                        icon=f":material/{icon}:",
                    ):
                        if emoji in emoji_labelings:
                            db.remove_designs_labeling(labeling_id=emoji_labelings[emoji].id, design_ids=[design_id])
                            if "added_labeling" in st.session_state:
                                del st.session_state["added_labeling"]
                        else:
                            labeling = db.add_label(label=emoji, design_ids=[design_id], username=get_username())
                            st.session_state["added_labeling"] = labeling
                        st.rerun(scope="fragment")

                st.html("<style>\n{}\n</style>".format("\n".join(styles)))

                if st.button(
                    label="Edit labels",
                    type="tertiary",
                    key=f"label_button_{design_id}_{key_suffix}",
                    icon=":material/new_label:",
                ):
                    label_design_dialog(design_id=design_id, key_suffix=key_suffix)

            if "added_labeling" in st.session_state and (labeling := st.session_state["added_labeling"]):
                with st.container(
                    horizontal=True,
                    horizontal_alignment="right" if show_header else "left",
                    vertical_alignment="center",
                ):
                    st.write(f":grey[Added label:] {labeling.label}")
                    explanation = show_explanation_input(labeling.label, width=400, label_visibility="collapsed")
                    if st.button("Add"):
                        if explanation:
                            labeling.explanation = explanation
                            db.save(labeling)
                        del st.session_state["added_labeling"]
                        st.rerun(scope="fragment")


@st.dialog(f"Add or Edit Labels", width="medium")
def label_design_dialog(design_id: str, key_suffix: str = ""):
    # Get current labelings and available labels
    current_design_labelings = get_cached_labelings_for_design(design_id)
    all_labels = get_cached_all_available_labels_unique()

    # Add label section
    st.subheader(f"Add Label to {design_id}")
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
        label="Explanation for this label (optional)",
        help="You can select an existing explanation or type a new one",
    )

    if st.button("Add Label", key=f"add_label_btn_{key_suffix}", type="primary", disabled=new_label is None):
        try:
            db.add_label(
                label=new_label,
                design_ids=[design_id],
                username=get_username(),
                explanation=explanation.strip() if explanation is not None else None,
            )
            st.rerun(scope="fragment")
        except Exception as e:
            st.error(f"Error adding label: {str(e)}")

    if current_design_labelings:
        st.subheader(f"Remove Labels from {design_id}")
        with st.container(horizontal=True):
            for labeling in current_design_labelings:
                with st.popover(labeling.label, help="Click to see details and remove this label"):
                    st.write(f"**Added by:** {labeling.author}")

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
                            db.remove_designs_labeling(labeling_id=labeling.id, design_ids=[design_id])
                            st.rerun(scope="fragment")
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
    st.markdown(badge, help=f"{labeling.label} Explanation: {labeling.explanation}" if labeling.explanation else None)
