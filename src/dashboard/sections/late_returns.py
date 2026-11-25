"""Section 2: late returns analysis."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard.data import (
    ENDED_BASE,
    LATE_BASE,
    base_label,
    late_rate,
    rate,
    recorded_delays,
)


def _delay_caption(delays: pd.Series, base: str) -> str:
    """Describe the centre and spread of the recorded delays.

    Args:
        delays: Recorded checkout delays in minutes.
        base: Base phrase of the delays.

    Returns:
        Caption text computed from the delays.
    """
    if len(delays) == 0:
        return f"No {base} in the selected scope."
    median = delays.median()
    mean = delays.mean()
    text = f"The median delay is {median:+g} min and the mean is {mean:+.0f} min"
    if mean > median:
        text += ": a few very late returns pull the mean above the median"
    elif mean < median:
        text += ": a few very early returns pull the mean below the median"
    under_30 = rate(delays < 30)
    return (
        f"{text}. {under_30.value:.1f}% of {base} have a delay under 30 min "
        "(early returns included)."
    )


def render(ended: pd.DataFrame, scope: str) -> None:
    """Render the late returns analysis.

    Args:
        ended: Ended rentals in scope.
        scope: Selected scope.
    """
    st.header("2. Late Returns Analysis")

    base = base_label(LATE_BASE, scope)
    delay_data = recorded_delays(ended)
    late = rate(delay_data > 0)
    on_time = rate(delay_data <= 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Late Returns", f"{late.numerator:,}", f"{late.value:.1f}% of {base}")
    with col2:
        median_delay = delay_data.median() if len(delay_data) > 0 else 0
        st.metric("Median Delay", f"{median_delay:.0f} min")
    with col3:
        mean_delay = delay_data.mean() if len(delay_data) > 0 else 0
        st.metric("Mean Delay", f"{mean_delay:.0f} min")

    st.caption(
        f"Base: {late.denominator:,} {base}. "
        f"{len(ended) - late.denominator:,} {base_label(ENDED_BASE, scope)} "
        "have no recorded checkout delay and are not counted."
    )

    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        fig_late = px.pie(
            values=[on_time.numerator, late.numerator],
            names=["On time or early", "Late"],
            title=f"Return Timing Distribution<br><sup>share of {base}</sup>",
            hole=0.4,
            color_discrete_sequence=["#2ecc71", "#e74c3c"],
        )
        fig_late.update_traces(textinfo="label+percent")
        st.plotly_chart(fig_late, use_container_width=True)
        st.caption(
            f"{on_time.value:.1f}% of {base} were returned on time or early, "
            f"{late.value:.1f}% late. Canceled rentals have no checkout and are "
            "not shown."
        )

    with col_viz2:
        delay_capped = delay_data.clip(-120, 360)
        fig_hist = px.histogram(
            delay_capped,
            nbins=50,
            title=f"Delay Distribution (capped at -2h to +6h)<br><sup>{base}</sup>",
            labels={"value": "Delay (minutes)", "count": "Number of rentals"},
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red")
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption(_delay_caption(delay_data, base))

    if scope != "All rentals":
        return

    st.subheader("Late Returns by Checkin Type")

    late_base = base_label(LATE_BASE)
    rate_header = f"late rate (% of {late_base})"
    rows = {}
    for checkin_type, group in ended.groupby("checkin_type"):
        late_type = late_rate(group)
        delays = recorded_delays(group)
        rows[checkin_type] = {
            late_base: late_type.denominator,
            "late returns": late_type.numerator,
            rate_header: round(late_type.value, 1),
            "mean delay (min)": round(delays.mean(), 1),
            "median delay (min)": round(delays.median(), 1),
        }
    late_by_type = pd.DataFrame.from_dict(rows, orient="index")
    late_by_type.index.name = "checkin_type"
    st.dataframe(late_by_type, use_container_width=True)

    rates = ", ".join(
        f"{checkin_type.capitalize()} {value:.1f}%"
        for checkin_type, value in late_by_type[rate_header].items()
    )
    st.caption(
        f"Late rate per check-in type, as a share of the {late_base} of that "
        f"type: {rates}."
    )
