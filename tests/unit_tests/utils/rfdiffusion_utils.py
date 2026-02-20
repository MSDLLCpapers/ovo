import logging
import time
from typing import Callable

from streamlit.testing.v1 import AppTest

from ovo.app.utils.testing import hide_test_dialog, show_test_dialog
from ovo.core.logic.round_logic import get_or_create_project_rounds
from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.asserts import assert_no_error_on_page
from tests.unit_tests.utils.constants import TIMEOUT

logger = logging.getLogger(__name__)


def wait_for(
    at: AppTest,
    condition: Callable,
    interval: float | int = 1,
    timeout: int = 30,
    description: str | None = None,
    *args,
) -> None:
    """
    Wait for a condition to be met within a timeout period.

    Args:
        at (AppTest): The AppTest instance.
        condition (Callable): The condition to wait for.
        interval (float | int, optional): The interval between checks. Defaults to 1.
        timeout (int, optional): The maximum time to wait. Defaults to 30.
        description (str | None, optional): Description of the condition. Defaults to None.
        *args: Additional arguments to pass to the condition function.

    Raises:
        TimeoutError: If the condition is not met within the timeout period.
    """
    start = time.time()
    while not condition(*args) and time.time() - start < timeout:
        time.sleep(interval)
    if time.time() - start >= timeout:
        raise TimeoutError(f"Condition {description} was not fulfilled in {timeout} s!")


def get_contig(target_chain: str, start: str, end: str, binder_length: str) -> str:
    """
    Get the contig string based on the provided parameters.

    Args:
        target_chain (str): The target chain identifier.
        start (str): Start position.
        end (str): End position.
        binder_length (str): Binder length.

    Returns:
        str: The contig string.
    """
    return f"{target_chain}{start}-{end}/0 {binder_length}"


def trim_tab(
    at: AppTest,
    target_chain: str = "A",
    start: int | None = None,
    end: int | None = None,
    go_to_next: bool = True,
) -> None:
    """
    Test the trim tab.

    Args:
        at (AppTest): The AppTest instance.
        target_chain (str, optional): The target chain identifier. Defaults to "A".
        start (int | None, optional): Start position. Defaults to None.
        end (int | None, optional): End position. Defaults to None.
        go_to_next (bool, optional): Whether to proceed to the next tab. Defaults to True.
    """
    logger.info("Testing trim tab...")
    at.selectbox("target_chain").set_value(target_chain).run()
    if start:
        at.number_input(f"start_trim_residue_{target_chain}").set_value(start).run()
    else:
        start = at.number_input(f"start_trim_residue_{target_chain}").value
    if end:
        at.number_input(f"end_trim_residue_{target_chain}").set_value(end).run()
    else:
        end = at.number_input(f"end_trim_residue_{target_chain}").value
    asserts.assert_element_exists(
        at.number_input,
        f"start_trim_residue_{target_chain}",
        "Test that start trim residue number input exists.",
    )
    asserts.assert_element_exists(
        at.number_input,
        f"end_trim_residue_{target_chain}",
        "Test that end trim residue number input exists.",
    )
    asserts.assert_no_error_on_page(at, "trim tab")
    if go_to_next:
        at.button("next_button_top").click().run(timeout=TIMEOUT)
    return target_chain, start, end


def preview_tab_binder_design(
    at: AppTest,
    binder_length: str = "20-40",
    hotspot_residues: str | None = None,
    go_to_next: bool = True,
) -> None:
    """
    Test the preview tab for binder design.

    Args:
        at (AppTest): The AppTest instance.
        binder_length (str, optional): The binder length. Defaults to "20-40".
        hotspot_residues (str | None, optional): The hotspot residues. Defaults to None.
        go_to_next (bool, optional): Whether to proceed to the next tab. Defaults to True.
    """
    logger.info("Testing preview tab...")
    at.text_input("binder_length").set_value(binder_length).run()
    if hotspot_residues:
        at.text_input("hotspots").set_value(hotspot_residues).run()
    else:
        hotspot_residues = at.text_input("hotspots").value
    asserts.assert_no_error_on_page(at, "preview tab")
    if go_to_next:
        at.button("next_button_top").click().run(timeout=TIMEOUT)
    return binder_length, hotspot_residues


def settings_tab(
    at: AppTest,
    page_key: str,
    pool_name: str,
    pool_description: str | None = None,
    contig: str | None = None,
    hotspot_residues: str | None = None,
) -> None:
    """
    Test the submission tab.

    Args:
        at (AppTest): The AppTest instance.
        pool_name (str): The pool name.
        pool_description (str | None, optional): The pool description. Defaults to None.
        contig (str | None, optional): The contig string. Defaults to None.
        hotspot_residues (str | None, optional): The hotspot residues. Defaults to None.
    """
    logger.info("Testing submission tab...")

    # test creating new round
    show_test_dialog(at, "create_round")
    round_name = f"Round for {pool_name}"
    at.text_input("round_name").set_value(round_name)
    at.button("create_round").click().run()
    rounds_by_id = get_or_create_project_rounds(project_id=at.session_state.project.id)
    round_ids_by_name = {round.name: round.id for round in rounds_by_id.values()}
    asserts.assert_true(
        round_name in round_ids_by_name,
        "Test that round was added.",
    )
    round_ids = list(rounds_by_id.keys())
    assert round_ids_by_name[round_name] == at.selectbox(f"selected_round_{'_'.join(round_ids)}").value, (
        "Test that newly created round is selected in selectbox by force change logic."
    )

    # pool properties
    at.text_input("input_pool_name").set_value(pool_name).run()
    if pool_description:
        at.text_area("input_pool_description").set_value(pool_description).run()

    # contig and workflow params
    asserts.assert_equal(
        contig,
        at.text_input("input_contig").value,
        "Test that right contig is displayed.",
    )

    if hotspot_residues:
        asserts.assert_equal(
            hotspot_residues,
            at.text_input("hotspots").value,
            "Test that right hotspot residues are displayed.",
        )

    workflow = at.session_state.workflows[page_key]
    num_designs = at.number_input("num_designs")
    num_designs.set_value(1).run()
    assert workflow.rfdiffusion_params.num_designs == 1
    asserts.assert_no_error_on_page(at, "submission tab")


def review_and_submit_tab(at: AppTest, mock_scheduler, pool_name: str) -> None:
    """
    Test the confirmation tab.

    Args:
        at (AppTest): The AppTest instance.
        mock_scheduler: Mocked Scheduler instance
        pool_name (str): The pool name.
    """

    hide_test_dialog(at, "create_round")
    show_test_dialog(at, "submission_dialog")
    at.button("continue").click().run()
    num_jobs_before = len(mock_scheduler.jobs)
    at.button("submit_run").click().run(timeout=TIMEOUT)

    asserts.assert_no_error_on_page(at, "confirm workflow dialog")
    assert len(mock_scheduler.jobs) == num_jobs_before + 1, (
        f"Job should be scheduled with MockScheduler: {mock_scheduler}"
    )

    asserts.assert_equal("⏳️ Jobs", at.title[0].value, "Page should switch to Jobs")
    asserts.assert_equal("Job submitted successfully", at.success[0].value, "Success message should be shown")

    pools_tab_contain_pools(at, [pool_name])


def pools_tab_contain_pools(at: AppTest, pool_names: list[str]) -> None:
    """
    Verify that the pools tab contains the specified pools.

    Args:
        at (AppTest): The AppTest instance.
        pool_names (list[str]): List of pool names to check.
    """
    assert_no_error_on_page(at, "pools")
    try:
        dataframe = at.dataframe[0]
    except Exception as e:
        logger.error(e)
        logger.error(at)
        asserts.assert_true(False, "Try to get pools dataframe.")
    wait_for(
        at,
        lambda: not dataframe.value.empty,
        description="'Dataframe is initialized'",
    )
    df = at.dataframe[0].value["Pool"]
    for name in pool_names:
        rows = df.loc[df["name"] == name]
        asserts.assert_false(rows.empty, f"Test if dataframe contains pool '{name}'")
