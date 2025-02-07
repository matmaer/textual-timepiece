from functools import partial

import pytest

from textual_timepiece._activity_heatmap import ActivityHeatmap
from textual_timepiece._activity_heatmap import HeatmapManager


@pytest.fixture
def heatmap_app(create_app):
    return create_app(ActivityHeatmap)


@pytest.fixture
def heatmap_manager_app(create_app):
    return create_app(HeatmapManager)


@pytest.fixture
def heatmap_snap(snap_compare):
    return partial(snap_compare, terminal_size=(165, 21))


@pytest.fixture
def heatmap_data(freeze_time):
    return ActivityHeatmap.generate_empty_activity(freeze_time.year)


@pytest.mark.snapshot
def test_heatmap_hover(heatmap_app, heatmap_snap, heatmap_data, freeze_time):
    async def run_before(pilot):
        heatmap_app.widget.process_data(heatmap_data)
        await pilot.hover(heatmap_app.widget, (16, 1))

    assert heatmap_snap(heatmap_app, run_before=run_before)


@pytest.mark.snapshot
def test_heatmap_hover_month(
    heatmap_app, heatmap_snap, heatmap_data, freeze_time
):
    async def run_before(pilot):
        heatmap_app.widget.process_data(heatmap_data)
        await pilot.hover(heatmap_app.widget, (147, 17))

    assert heatmap_snap(heatmap_app, run_before=run_before)


@pytest.mark.snapshot
def test_heatmap_manager(
    heatmap_manager_app, heatmap_snap, heatmap_data, freeze_time
):
    async def run_before(pilot):
        heatmap_manager_app.widget.heatmap.process_data(heatmap_data)
        heatmap_manager_app.widget.heatmap.focus()
        await pilot.press("left", "left", "down", "down", "up", "right")

    assert heatmap_snap(heatmap_manager_app, run_before=run_before)


@pytest.mark.unit
async def test_heatmap_navigation(
    heatmap_manager_app, heatmap_snap, heatmap_data, freeze_time
):
    async with heatmap_manager_app.run_test() as pilot:
        heatmap_manager_app.widget.heatmap.process_data(heatmap_data)
        heatmap_manager_app.widget.focus()
        await pilot.press("enter", "tab")
        assert heatmap_manager_app.widget.day.year == freeze_time.year - 5

        await pilot.press("enter", "tab")
        assert heatmap_manager_app.widget.day.year == freeze_time.year - 6

        await pilot.press(
            *["backspace"] * 5, "2", "0", "3", "4", "enter", "tab"
        )
        assert heatmap_manager_app.widget.day.year == 2034

        await pilot.press("enter", *["tab"] * 3)
        assert heatmap_manager_app.widget.day.year == freeze_time.year

        await pilot.press("enter", "tab")
        assert heatmap_manager_app.widget.day.year == freeze_time.year + 1

        await pilot.press("enter")
        assert heatmap_manager_app.widget.day.year == freeze_time.year + 6
