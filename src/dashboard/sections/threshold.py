"""Section 4: threshold impact simulation."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.dashboard.data import (
    CONSECUTIVE_BASE,
    PROBLEMATIC_BASE,
    RENTALS_BASE,
    base_label,
)
from src.dashboard.simulation import COMPARISON_THRESHOLDS, simulate_threshold

TRADEOFF_SCOPES = ("All rentals", "Connect only")


def _render_tradeoff(consecutive: pd.DataFrame) -> None:
    """Render the affected and solved shares by threshold for two scopes.

    Args:
        consecutive: All consecutive rentals.
    """
    st.subheader("Trade-off: Affected vs Solved")

    fig_tradeoff = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["All Rentals", "Connect Only"],
    )

    for i, s in enumerate(TRADEOFF_SCOPES):
        results = [simulate_threshold(consecutive, t, s) for t in COMPARISON_THRESHOLDS]
        fig_tradeoff.add_trace(
            go.Scatter(
                x=COMPARISON_THRESHOLDS,
                y=[result["affected_pct"] for result in results],
                name="Affected (% of consecutive rentals in scope)",
                mode="lines+markers",
                line=dict(color="#e74c3c"),
                showlegend=(i == 0),
            ),
            row=1,
            col=i + 1,
        )
        fig_tradeoff.add_trace(
            go.Scatter(
                x=COMPARISON_THRESHOLDS,
                y=[result["solved_pct"] for result in results],
                name="Solved (% of problematic consecutive rentals in scope)",
                mode="lines+markers",
                line=dict(color="#2ecc71"),
                showlegend=(i == 0),
            ),
            row=1,
            col=i + 1,
        )

    fig_tradeoff.update_xaxes(title_text="Threshold (minutes)")
    fig_tradeoff.update_yaxes(title_text="Share of the base (%)")
    fig_tradeoff.update_layout(
        height=400,
        title_text=(
            "Affected and solved shares by threshold<br><sup>affected: % of "
            "consecutive rentals in scope; solved: % of problematic consecutive "
            "rentals in scope</sup>"
        ),
    )

    st.plotly_chart(fig_tradeoff, use_container_width=True)
    st.caption(
        "Higher thresholds resolve more conflicts but cancel more "
        "revenue-generating rentals. The optimal threshold balances both."
    )


def render(
    rentals: pd.DataFrame,
    consecutive: pd.DataFrame,
    scope: str,
    threshold_minutes: int,
) -> None:
    """Render the threshold simulation.

    Args:
        rentals: All rentals.
        consecutive: All consecutive rentals.
        scope: Selected scope.
        threshold_minutes: Selected minimum delay threshold.
    """
    st.header("4. Threshold Impact Simulation")
    st.markdown(
        f"""
        Simulating impact of **{threshold_minutes}-minute** threshold on **{scope}**.
        """
    )

    affected_header = f"Affected (% of {base_label(CONSECUTIVE_BASE, scope)})"
    solved_header = f"Solved (% of {base_label(PROBLEMATIC_BASE, scope)})"
    sim_result = simulate_threshold(consecutive, threshold_minutes, scope)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Affected Rentals",
            f"{sim_result['affected_rentals']:,}",
            f"{sim_result['affected_pct']:.1f}% of "
            f"{base_label(CONSECUTIVE_BASE, scope)}",
        )
    with col2:
        st.metric("Total Problematic", f"{sim_result['total_problematic']:,}")
    with col3:
        st.metric(
            "Problems Solved",
            f"{sim_result['solved_cases']:,}",
            f"{sim_result['solved_pct']:.1f}% of {base_label(PROBLEMATIC_BASE, scope)}",
        )
    with col4:
        st.metric("Unsolved Cases", f"{sim_result['unsolved_cases']:,}")

    st.subheader("Revenue Impact Estimation")

    total_rentals = len(rentals)
    affected_pct_total = sim_result["affected_rentals"] / total_rentals * 100
    all_rentals = base_label(RENTALS_BASE)
    st.info(
        f"""
        **Share of owner revenue potentially affected:** {affected_pct_total:.2f}% \
of {all_rentals} (each rental counted once)

        - Consecutive rentals represent \
{len(consecutive) / total_rentals * 100:.1f}% of {all_rentals}
        - With {threshold_minutes}-minute threshold on {scope.lower()}:
          {sim_result["affected_rentals"]:,} rentals would need to be rescheduled
        """
    )

    st.subheader("Threshold Comparison")

    comparison_data = []
    for t in COMPARISON_THRESHOLDS:
        result = simulate_threshold(consecutive, t, scope)
        comparison_data.append(
            {
                "Threshold (min)": t,
                "Affected Rentals": result["affected_rentals"],
                affected_header: f"{result['affected_pct']:.1f}%",
                "Problems Solved": result["solved_cases"],
                solved_header: f"{result['solved_pct']:.1f}%",
                "Unsolved": result["unsolved_cases"],
            }
        )
    st.dataframe(
        pd.DataFrame(comparison_data), use_container_width=True, hide_index=True
    )

    _render_tradeoff(consecutive)
