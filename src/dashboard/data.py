"""Data loading, scope filters and rate helpers for the delay dashboard.

Every rate in the dashboard names its base. The base phrases below hold a
``{kind}`` field that becomes the check-in type of the selected scope.
"""

from pathlib import Path
from typing import NamedTuple

import pandas as pd

DATA_PATH = (
    Path(__file__).parent.parent.parent / "data" / "get_around_delay_analysis.csv"
)

SCOPES = ("All rentals", "Connect only", "Mobile only")
SCOPE_CHECKIN_TYPE = {"Connect only": "connect", "Mobile only": "mobile"}
SCOPE_KIND = {"All rentals": "", "Connect only": "Connect ", "Mobile only": "Mobile "}

RENTALS_BASE = "all {kind}rentals"
ENDED_BASE = "ended {kind}rentals"
LATE_BASE = "ended {kind}rentals with a recorded checkout delay"
CONSECUTIVE_BASE = "consecutive {kind}rentals"
PROBLEMATIC_BASE = "problematic consecutive {kind}rentals"


class Rate(NamedTuple):
    """A percentage with the counts it comes from."""

    value: float
    numerator: int
    denominator: int


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the delay analysis data.

    Args:
        path: CSV file with one row per rental.

    Returns:
        DataFrame with rental delay data.
    """
    return pd.read_csv(path)


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Prepare derived datasets for analysis.

    A consecutive rental is problematic when the checkout delay of the
    previous rental is longer than the scheduled gap. A missing previous
    delay counts as on time.

    Args:
        df: Raw rental data.

    Returns:
        Tuple of (ended_rentals, consecutive_rentals, consecutive_with_delay).
    """
    ended = df[df["state"] == "ended"].copy()
    ended["is_late"] = ended["delay_at_checkout_in_minutes"] > 0

    consecutive = df[df["previous_ended_rental_id"].notna()].copy()

    prev_delays = df[["rental_id", "delay_at_checkout_in_minutes"]].copy()
    prev_delays.columns = ["previous_ended_rental_id", "previous_delay"]
    consecutive = consecutive.merge(
        prev_delays, on="previous_ended_rental_id", how="left"
    )

    consecutive["effective_time"] = consecutive[
        "time_delta_with_previous_rental_in_minutes"
    ] - consecutive["previous_delay"].fillna(0)
    consecutive["is_problematic"] = consecutive["effective_time"] < 0

    return ended, consecutive, consecutive[consecutive["is_problematic"]]


def filter_scope(frame: pd.DataFrame, scope: str) -> pd.DataFrame:
    """Keep the rows of the check-in type that the scope selects.

    Args:
        frame: Rental data with a ``checkin_type`` column.
        scope: 'All rentals', 'Connect only', or 'Mobile only'.

    Returns:
        The rows in scope (the same frame for 'All rentals').
    """
    checkin_type = SCOPE_CHECKIN_TYPE.get(scope)
    if checkin_type is None:
        return frame
    return frame[frame["checkin_type"] == checkin_type]


def base_label(base: str, scope: str = "All rentals") -> str:
    """Return a base phrase for the check-in type of the scope.

    Args:
        base: One of the ``*_BASE`` phrases of this module.
        scope: 'All rentals', 'Connect only', or 'Mobile only'.

    Returns:
        The phrase, for example "consecutive Connect rentals".
    """
    return base.format(kind=SCOPE_KIND.get(scope, ""))


def rate(flags: pd.Series) -> Rate:
    """Compute the share of true values in a boolean series.

    Args:
        flags: One boolean per row of the base.

    Returns:
        Rate in percent (0.0 for an empty base), true count and base size.
    """
    numerator = int(flags.sum())
    denominator = len(flags)
    value = numerator / denominator * 100 if denominator else 0.0
    return Rate(value, numerator, denominator)


def recorded_delays(ended: pd.DataFrame) -> pd.Series:
    """Return the checkout delays of ended rentals that have one.

    Args:
        ended: Ended rentals.

    Returns:
        Delays in minutes, without missing values.
    """
    return ended["delay_at_checkout_in_minutes"].dropna()


def late_rate(ended: pd.DataFrame) -> Rate:
    """Compute the late-return rate over rentals with a recorded delay.

    Args:
        ended: Ended rentals.

    Returns:
        Share of ended rentals with a recorded checkout delay above zero.
    """
    return rate(recorded_delays(ended) > 0)
