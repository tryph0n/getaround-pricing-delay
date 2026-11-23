"""Section 5: key findings and recommendations, computed from the data."""

import pandas as pd
import streamlit as st

from src.dashboard.data import (
    CONSECUTIVE_BASE,
    LATE_BASE,
    PROBLEMATIC_BASE,
    RENTALS_BASE,
    base_label,
    late_rate,
    rate,
)
from src.dashboard.simulation import simulate_threshold

STRATEGIES = (
    ("Conservative", 60, "Connect only"),
    ("Balanced", 120, "Connect only"),
    ("Aggressive", 180, "All rentals"),
)


def _insights_table(
    rentals: pd.DataFrame, ended: pd.DataFrame, consecutive: pd.DataFrame
) -> str:
    """Build the data insights table, one rate per row with its base.

    Args:
        rentals: All rentals.
        ended: All ended rentals.
        consecutive: All consecutive rentals.

    Returns:
        Markdown table.
    """
    all_rentals = base_label(RENTALS_BASE)
    rows = [
        ("Total rentals", f"{len(rentals):,}", ""),
        (
            "Mobile checkin share",
            f"{rate(rentals['checkin_type'] == 'mobile').value:.1f}%",
            all_rentals,
        ),
        (
            "Connect checkin share",
            f"{rate(rentals['checkin_type'] == 'connect').value:.1f}%",
            all_rentals,
        ),
        ("Late return rate", f"{late_rate(ended).value:.1f}%", base_label(LATE_BASE)),
        (
            "Consecutive rentals",
            f"{rate(rentals['previous_ended_rental_id'].notna()).value:.1f}%",
            all_rentals,
        ),
        (
            "Problematic cases",
            f"{rate(consecutive['is_problematic']).value:.1f}%",
            base_label(CONSECUTIVE_BASE),
        ),
    ]
    lines = ["| Metric | Value | Base |", "|--------|-------|------|"]
    lines += [f"| {metric} | {value} | {base} |" for metric, value, base in rows]
    return "\n".join(lines)


def _strategies_table(rentals: pd.DataFrame, consecutive: pd.DataFrame) -> str:
    """Build the recommendations table from the threshold simulation.

    Args:
        rentals: All rentals.
        consecutive: All consecutive rentals.

    Returns:
        Markdown table.
    """
    lines = [
        "| Strategy | Threshold | Scope "
        "| Solved (% of problematic consecutive rentals in scope) "
        "| Affected (% of consecutive rentals in scope) "
        "| Affected (% of all rentals) |",
        "|----------|-----------|-------|--------|----------|----------|",
    ]
    for strategy, threshold, scope in STRATEGIES:
        result = simulate_threshold(consecutive, threshold, scope)
        affected_all = result["affected_rentals"] / len(rentals) * 100
        lines.append(
            f"| {strategy} | {threshold} min | {scope.split()[0]} "
            f"| {result['solved_pct']:.1f}% | {result['affected_pct']:.1f}% "
            f"| {affected_all:.1f}% |"
        )
    return "\n".join(lines)


def render(
    rentals: pd.DataFrame, ended: pd.DataFrame, consecutive: pd.DataFrame
) -> None:
    """Render the key findings and recommendations for all rentals.

    Args:
        rentals: All rentals.
        ended: All ended rentals.
        consecutive: All consecutive rentals.
    """
    st.header("5. Key Findings and Recommendations")

    connect_consecutive = base_label(CONSECUTIVE_BASE, "Connect only")
    mobile_consecutive = base_label(CONSECUTIVE_BASE, "Mobile only")
    connect = rate(rentals["checkin_type"] == "connect")
    mobile = rate(rentals["checkin_type"] == "mobile")
    problematic = {
        checkin_type: rate(group["is_problematic"])
        for checkin_type, group in consecutive.groupby("checkin_type")
    }
    first_step = simulate_threshold(consecutive, 60, "Connect only")
    affected_all = first_step["affected_rentals"] / len(rentals) * 100

    st.markdown("### Data Insights")
    st.markdown(_insights_table(rentals, ended, consecutive))
    st.markdown("### Recommendations")
    st.markdown(_strategies_table(rentals, consecutive))
    st.markdown(
        f"""
### Key Takeaways

1. **Connect-only scope is safer**: Connect rentals are {connect.value:.1f}% of
   all rentals, and their automated checkin makes a threshold easier to enforce

2. **60-minute threshold is a good starting point**: on Connect rentals it
   solves {first_step["solved_pct"]:.1f}% of
   {base_label(PROBLEMATIC_BASE, "Connect only")} and affects
   {first_step["affected_pct"]:.1f}% of {connect_consecutive}

3. **Few rentals are affected**: at a 60-min Connect threshold,
   {affected_all:.1f}% of all rentals are affected
   ({first_step["affected_rentals"]:,} of {len(rentals):,})

4. **Mobile rentals have more volume but a higher problematic rate**: Mobile
   rentals are {mobile.value:.1f}% of all rentals, and
   {problematic["mobile"].value:.1f}% of {mobile_consecutive} are problematic
   (Connect: {problematic["connect"].value:.1f}% of {connect_consecutive}).
   Consider a phased rollout starting with Connect
"""
    )
