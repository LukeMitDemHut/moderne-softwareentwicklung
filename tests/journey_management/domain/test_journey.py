from datetime import date

import pytest

from sqr.journey_management.domain.exceptions import InvalidJourneyTimeframe
from sqr.journey_management.domain.journey.journey import Journey

TODAY = date(2026, 11, 18)  # fixed date, so the test result never depends on the real day


def test_create_journey_with_valid_timeframe_succeeds():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        today=TODAY,
    )
    assert journey.title == "Lissabon"


def test_create_journey_with_start_after_end_is_rejected():
    with pytest.raises(InvalidJourneyTimeframe):  # expects exactly this error
        Journey.create(
            title="Lissabon",
            start_date=date(2026, 12, 8),
            end_date=date(2026, 12, 1),
            today=TODAY,
        )