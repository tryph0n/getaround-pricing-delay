"""Section 1: dataset overview."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.data import (
    CONSECUTIVE_BASE,
    LATE_BASE,
    RENTALS_BASE,
    base_label,
    rate,
)


def render(rentals: pd.DataFrame, consecutive: pd.DataFrame, scope: str) -> None:
    """Render the dataset overview.

    Args:
        rentals: Rentals in scope.
        consecutive: Consecutive rentals in scope.
        scope: Selected scope.
    """
    st.header("1. Dataset Overview")

    base = base_label(RENTALS_BASE, scope)
    ended = rate(rentals["state"] == "ended")
    canceled = rate(rentals["state"] == "canceled")
    with_previous = rate(rentals["previous_ended_rental_id"].notna())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rentals", f"{len(rentals):,}")
    with col2:
        st.metric("Completed", f"{ended.numerator:,}", f"{ended.value:.1f}% of {base}")
    with col3:
        st.metric(
            "Canceled", f"{canceled.numerator:,}", f"{canceled.value:.1f}% of {base}"
        )
    with col4:
        st.metric(
            "Consecutive Rentals",
            f"{len(consecutive):,}",
            f"{with_previous.value:.1f}% of {base}",
        )

    if scope != "All rentals":
        return

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        type_counts = rentals["checkin_type"].value_counts()
        fig_type = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Rentals by Checkin Type<br><sup>share of all rentals</sup>",
            hole=0.4,
        )
        fig_type.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_type, use_container_width=True)

        mobile = rate(rentals["checkin_type"] == "mobile")
        connect = rate(rentals["checkin_type"] == "connect")
        problematic = {
            checkin_type: rate(group["is_problematic"])
            for checkin_type, group in consecutive.groupby("checkin_type")
        }
        st.caption(
            f"Mobile: {mobile.value:.1f}% of all rentals. "
            f"Connect: {connect.value:.1f}% of all rentals. "
            "Problematic rate on consecutive rentals: "
            f"Connect {problematic['connect'].value:.1f}% of "
            f"{base_label(CONSECUTIVE_BASE, 'Connect only')}, "
            f"Mobile {problematic['mobile'].value:.1f}% of "
            f"{base_label(CONSECUTIVE_BASE, 'Mobile only')}."
        )

    with col_chart2:
        state_counts = rentals["state"].value_counts()
        fig_state = px.pie(
            values=state_counts.values,
            names=state_counts.index,
            title="Rentals by State<br><sup>share of all rentals</sup>",
            hole=0.4,
        )
        fig_state.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_state, use_container_width=True)
        st.caption(
            f"{ended.value:.1f}% of all rentals ended and {canceled.value:.1f}% "
            "were canceled. Section 2 gives late-return rates as a share of "
            f"{base_label(LATE_BASE)}."
        )
