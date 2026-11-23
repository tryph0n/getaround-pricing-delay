"""Minimum delay threshold simulation."""

import pandas as pd

from src.dashboard.data import filter_scope

COMPARISON_THRESHOLDS = (15, 30, 60, 90, 120, 180, 240, 360)


def simulate_threshold(data: pd.DataFrame, threshold_minutes: int, scope: str) -> dict:
    """Simulate the impact of a minimum delay threshold.

    Bases: ``affected_pct`` is a share of the consecutive rentals in scope,
    ``solved_pct`` a share of the problematic consecutive rentals in scope.

    Args:
        data: DataFrame with consecutive rentals.
        threshold_minutes: Minimum required gap between rentals.
        scope: 'All rentals', 'Connect only', or 'Mobile only'.

    Returns:
        Dict with simulation results.
    """
    subset = filter_scope(data, scope).copy()

    if len(subset) == 0:
        return {
            "affected_rentals": 0,
            "affected_pct": 0.0,
            "total_problematic": 0,
            "solved_cases": 0,
            "solved_pct": 0.0,
            "unsolved_cases": 0,
        }

    # A rental is affected when its scheduled gap is below the threshold.
    affected = subset[
        subset["time_delta_with_previous_rental_in_minutes"] < threshold_minutes
    ]

    problematic = subset[subset["is_problematic"]]

    # A problematic case is solved when the threshold would have blocked it.
    solved = problematic[
        problematic["time_delta_with_previous_rental_in_minutes"] < threshold_minutes
    ]

    return {
        "affected_rentals": len(affected),
        "affected_pct": len(affected) / len(subset) * 100 if len(subset) > 0 else 0,
        "total_problematic": len(problematic),
        "solved_cases": len(solved),
        "solved_pct": len(solved) / len(problematic) * 100
        if len(problematic) > 0
        else 0,
        "unsolved_cases": len(problematic) - len(solved),
    }
