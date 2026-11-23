"""Getaround Delay Analysis Dashboard.

Interactive dashboard to help PM decide on minimum delay threshold between rentals.
Answers key questions about delay impact and revenue implications.
Includes a pricing prediction section powered by the ML API.

Every displayed rate names its base. Late-return rates use the ended rentals
with a recorded checkout delay; problematic rates use the consecutive rentals.
"""

import pandas as pd
import streamlit as st

from src.config.settings import get_settings
from src.dashboard import data
from src.dashboard.sections import (
    late_returns,
    next_driver,
    overview,
    pricing,
    recommendations,
    threshold,
)

st.set_page_config(
    page_title="Getaround Delay Analysis",
    page_icon="GA",
    layout="wide",
)

st.title("Getaround Delay Analysis Dashboard")
st.markdown(
    """
When using Getaround, drivers book cars for a specific time period.
Late returns at checkout can generate high friction for the next driver
if the car was supposed to be rented again on the same day.

To mitigate this, we evaluate implementing a **minimum delay between
two consecutive rentals**. The Product Manager needs to decide:

- **Threshold**: how long should the minimum delay be?
- **Scope**: should it apply to all cars or only Connect cars?

Use the **sidebar controls** to adjust threshold and scope, and explore
how different scenarios impact rentals across sections 1 to 4.
"""
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the delay analysis data.

    Returns:
        DataFrame with rental delay data.
    """
    return data.load_data()


@st.cache_data
def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Prepare and cache the derived datasets.

    Args:
        df: Raw rental data.

    Returns:
        Tuple of (ended_rentals, consecutive_rentals, consecutive_with_delay).
    """
    return data.prepare_data(df)


try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Ensure data/get_around_delay_analysis.csv exists.")
    st.stop()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

ended, consecutive, _ = prepare_data(df)

st.sidebar.header("Configuration")
scope = st.sidebar.selectbox(
    "Scope",
    options=list(data.SCOPES),
    help="Which rental types to include in analysis",
)
st.sidebar.caption("Applied to sections 1-4.")
threshold_minutes = st.sidebar.slider(
    "Minimum delay threshold (minutes)",
    min_value=0,
    max_value=720,
    value=60,
    step=15,
    help="Proposed minimum time between consecutive rentals",
)
st.sidebar.caption("Applied to sections 3-4.")

df_filtered = data.filter_scope(df, scope)
ended_filtered = data.filter_scope(ended, scope)
consecutive_filtered = data.filter_scope(consecutive, scope)

_filter_parts = []
if scope != "All rentals":
    _filter_parts.append(f"Scope: **{scope}**")
if threshold_minutes > 0:
    _filter_parts.append(f"Threshold: **{threshold_minutes} min**")
if _filter_parts:
    st.info("Active filters: " + " | ".join(_filter_parts))
else:
    st.info("No active filters.")

overview.render(df_filtered, consecutive_filtered, scope)
late_returns.render(ended_filtered, scope)
next_driver.render(df_filtered, consecutive_filtered, scope, threshold_minutes)
threshold.render(df, consecutive, scope, threshold_minutes)
recommendations.render(df, ended, consecutive)
pricing.render(get_settings().api_url)

st.markdown("---")
st.caption("Dashboard built for Getaround PM team")
