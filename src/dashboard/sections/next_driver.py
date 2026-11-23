"""Section 3: impact of late returns on the next driver."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.data import (
    CONSECUTIVE_BASE,
    PROBLEMATIC_BASE,
    RENTALS_BASE,
    base_label,
    rate,
)


def render(
    rentals: pd.DataFrame,
    consecutive: pd.DataFrame,
    scope: str,
    threshold_minutes: int,
) -> None:
    """Render the impact on the next driver.

    Args:
        rentals: Rentals in scope.
        consecutive: Consecutive rentals in scope.
        scope: Selected scope.
        threshold_minutes: Selected minimum delay threshold.
    """
    st.header("3. Impact on Next Driver")
    st.markdown(
        """
        Analysis of consecutive rentals on the same car
        and how delays affect the next driver.
        """
    )

    consecutive_base = base_label(CONSECUTIVE_BASE, scope)
    problematic_base = base_label(PROBLEMATIC_BASE, scope)
    with_previous = rate(rentals["previous_ended_rental_id"].notna())
    problematic = rate(consecutive["is_problematic"])
    problematic_in_scope = consecutive[consecutive["is_problematic"]]
    time_delta = consecutive["time_delta_with_previous_rental_in_minutes"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Consecutive Rentals",
            f"{len(consecutive):,}",
            f"{with_previous.value:.1f}% of {base_label(RENTALS_BASE, scope)}",
        )
    with col2:
        median_gap = time_delta.median() if len(time_delta) > 0 else 0
        st.metric("Median Gap Between Rentals", f"{median_gap:.0f} min")
    with col3:
        st.metric(
            "Problematic Cases",
            f"{problematic.numerator:,}",
            f"{problematic.value:.1f}% of {consecutive_base}",
        )

    missing_previous = int(consecutive["previous_delay"].isna().sum())
    st.caption(
        "A consecutive rental is problematic when the checkout delay of the "
        "previous rental is longer than the scheduled gap. When the previous "
        f"rental has no recorded checkout delay ({missing_previous:,} of "
        f"{len(consecutive):,} {consecutive_base}), it counts as on time."
    )

    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        fig_delta = px.histogram(
            time_delta.clip(0, 720),
            nbins=40,
            title="Scheduled Gap Between Consecutive Rentals",
            labels={"value": "Time Delta (minutes)", "count": "Count"},
        )
        fig_delta.add_vline(
            x=threshold_minutes,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Threshold: {threshold_minutes}min",
        )
        fig_delta.update_layout(showlegend=False)
        st.plotly_chart(fig_delta, use_container_width=True)
        st.caption(
            f"The median scheduled gap between {consecutive_base} is "
            f"{median_gap:g} min."
        )

    with col_viz2:
        if len(problematic_in_scope) > 0:
            wait_time = -problematic_in_scope["effective_time"]
            fig_wait = px.histogram(
                wait_time.clip(0, 240),
                nbins=30,
                title="Wait Time for Impacted Drivers",
                labels={"value": "Wait Time (minutes)", "count": "Count"},
                color_discrete_sequence=["#e74c3c"],
            )
            fig_wait.update_layout(showlegend=False)
            st.plotly_chart(fig_wait, use_container_width=True)
            over_60 = rate(wait_time > 60)
            st.caption(
                "Impacted next drivers wait a median of "
                f"{wait_time.median():g} min. For {over_60.value:.1f}% of "
                f"{problematic_base}, the next driver waits more than 60 min."
            )
        else:
            st.info("No problematic cases in the selected scope.")

    if scope != "All rentals":
        return

    st.subheader("Problematic Cases by Checkin Type")

    rate_header = f"problematic rate (% of {base_label(CONSECUTIVE_BASE)})"
    prob_by_type = consecutive.groupby("checkin_type").agg(
        consecutive_rentals=("rental_id", "count"),
        problematic=("is_problematic", "sum"),
    )
    prob_by_type[rate_header] = (
        prob_by_type["problematic"] / prob_by_type["consecutive_rentals"] * 100
    ).round(1)
    st.dataframe(prob_by_type, use_container_width=True)

    by_type = prob_by_type[rate_header]
    st.caption(
        f"{with_previous.value:.1f}% of all rentals have a previous rental on "
        f"the same car (consecutive rentals). {problematic.value:.1f}% of "
        f"consecutive rentals are problematic ({problematic.numerator:,} "
        f"cases). Connect: {by_type['connect']:.1f}% of "
        f"{base_label(CONSECUTIVE_BASE, 'Connect only')}, Mobile: "
        f"{by_type['mobile']:.1f}% of {base_label(CONSECUTIVE_BASE, 'Mobile only')}."
    )
