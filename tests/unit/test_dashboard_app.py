"""Render tests for the Streamlit dashboard."""

import pytest
from streamlit.testing.v1 import AppTest

from src.dashboard.data import SCOPES

# All-ended-rentals rates: the dashboard uses the recorded-delay base instead.
FORBIDDEN_RATES = ("52.1", "41.6", "54.7")


def _rendered_text(at: AppTest) -> list[str]:
    """Collect the text of the elements that can show a rate.

    Args:
        at: App after a run.

    Returns:
        One string per element.
    """
    texts = []
    for kind in ("title", "header", "subheader", "markdown", "caption", "info"):
        texts += [element.value for element in getattr(at, kind)]
    for metric in at.metric:
        texts += [metric.label, metric.value, metric.proto.delta]
    texts += [frame.value.to_string() for frame in at.dataframe]
    return texts


@pytest.mark.parametrize("scope", SCOPES)
def test_dashboard_renders_without_all_ended_rates(scope: str) -> None:
    at = AppTest.from_file("src/dashboard/app.py", default_timeout=60).run()
    if scope != at.sidebar.selectbox[0].value:
        at.sidebar.selectbox[0].set_value(scope).run()

    assert not at.exception
    texts = _rendered_text(at)
    assert len(at.metric) > 0
    assert any("with a recorded checkout delay" in text for text in texts)
    for value in FORBIDDEN_RATES:
        assert not [text for text in texts if value in text], value
