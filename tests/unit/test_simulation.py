"""Tests for the dashboard data helpers and the threshold simulation.

The expected values come from the audit of data/get_around_delay_analysis.csv.
"""

import pandas as pd
import pytest

from src.dashboard.data import (
    filter_scope,
    late_rate,
    load_data,
    prepare_data,
    rate,
)
from src.dashboard.simulation import simulate_threshold

NUMERIC = [
    "delay_at_checkout_in_minutes",
    "previous_ended_rental_id",
    "time_delta_with_previous_rental_in_minutes",
]
ZERO_RESULT = {
    "affected_rentals": 0,
    "affected_pct": 0.0,
    "total_problematic": 0,
    "solved_cases": 0,
    "solved_pct": 0.0,
    "unsolved_cases": 0,
}


@pytest.fixture(scope="module")
def prepared() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Ended, consecutive and problematic rentals of the delay dataset."""
    return prepare_data(load_data())


@pytest.fixture(scope="module")
def ended(prepared) -> pd.DataFrame:
    """Ended rentals."""
    return prepared[0]


@pytest.fixture(scope="module")
def consecutive(prepared) -> pd.DataFrame:
    """Consecutive rentals with the problematic flag."""
    return prepared[1]


def _rentals(delays: list[float | None]) -> pd.DataFrame:
    """Build pairs of consecutive Mobile rentals with a 60 min scheduled gap.

    Args:
        delays: Checkout delay of the first rental of each pair.

    Returns:
        Raw rental data in the format of the delay dataset.
    """
    rows = []
    for i, delay in enumerate(delays):
        first, second = 2 * i + 1, 2 * i + 2
        rows.append((first, "mobile", "ended", delay, None, None))
        rows.append((second, "mobile", "ended", None, first, 60.0))
    frame = pd.DataFrame(rows, columns=["rental_id", "checkin_type", "state"] + NUMERIC)
    return frame.astype(dict.fromkeys(NUMERIC, float))


class TestSimulateThreshold:
    """Audit values of the threshold simulation."""

    def test_threshold_zero_affects_nothing(self, consecutive) -> None:
        result = simulate_threshold(consecutive, 0, "All rentals")
        assert result["affected_rentals"] == 0
        assert result["solved_cases"] == 0

    def test_max_threshold_all_rentals(self, consecutive) -> None:
        result = simulate_threshold(consecutive, 720, "All rentals")
        assert result["affected_rentals"] == 1711
        assert round(result["affected_pct"], 1) == 92.9
        assert result["solved_cases"] == 216
        assert result["total_problematic"] == 218
        assert round(result["solved_pct"], 1) == 99.1

    def test_60_min_connect(self, consecutive) -> None:
        result = simulate_threshold(consecutive, 60, "Connect only")
        assert result["affected_rentals"] == 181
        assert result["solved_cases"] == 48
        assert round(result["solved_pct"], 1) == 69.6

    @pytest.mark.parametrize("threshold", [0, 15, 60, 120, 180, 360, 720])
    def test_connect_affects_no_more_than_all(self, consecutive, threshold) -> None:
        connect = simulate_threshold(consecutive, threshold, "Connect only")
        everyone = simulate_threshold(consecutive, threshold, "All rentals")
        assert connect["affected_rentals"] <= everyone["affected_rentals"]

    def test_frame_with_no_delay(self) -> None:
        _, consecutive, problematic = prepare_data(_rentals([None, None, 0.0]))
        result = simulate_threshold(consecutive, 120, "All rentals")
        assert len(problematic) == 0
        assert result["affected_rentals"] == 3
        assert result["total_problematic"] == 0
        assert result["solved_pct"] == 0

    def test_empty_scope_returns_zero_result(self) -> None:
        _, consecutive, _ = prepare_data(_rentals([90.0]))
        assert simulate_threshold(consecutive, 60, "Connect only") == ZERO_RESULT

    def test_missing_previous_delay_counts_as_on_time(self) -> None:
        _, consecutive, problematic = prepare_data(_rentals([None, 90.0]))
        assert consecutive["is_problematic"].tolist() == [False, True]
        assert len(problematic) == 1


class TestRates:
    """Rates and their bases."""

    def test_problematic_rate_by_checkin_type(self, consecutive) -> None:
        connect = rate(filter_scope(consecutive, "Connect only")["is_problematic"])
        mobile = rate(filter_scope(consecutive, "Mobile only")["is_problematic"])
        assert round(connect.value, 1) == 8.5
        assert round(mobile.value, 1) == 14.5

    @pytest.mark.parametrize(
        ("scope", "expected"),
        [("All rentals", 57.5), ("Connect only", 42.9), ("Mobile only", 61.4)],
    )
    def test_late_rate_over_recorded_delays(self, ended, scope, expected) -> None:
        late = late_rate(filter_scope(ended, scope))
        assert round(late.value, 1) == expected
        assert (
            late.denominator
            == filter_scope(ended, scope)["delay_at_checkout_in_minutes"].notna().sum()
        )

    def test_rate_of_empty_base_is_zero(self) -> None:
        assert rate(pd.Series([], dtype=bool)) == (0.0, 0, 0)
        assert late_rate(prepare_data(_rentals([None]))[0]).value == 0.0
