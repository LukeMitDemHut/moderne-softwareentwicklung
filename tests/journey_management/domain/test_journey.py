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


def test_create_journey_with_start_in_the_past_is_rejected():
    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(
            title="Lissabon",
            start_date=date(2026, 11, 1),  # before TODAY (2026-11-18)
            end_date=date(2026, 12, 8),
            today=TODAY,
        )


def test_create_journey_with_start_today_is_rejected():
    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(
            title="Lissabon",
            start_date=TODAY,  # exactly today: not "in the future"
            end_date=date(2026, 11, 25),
            today=TODAY,
        )


def test_create_journey_with_start_tomorrow_is_accepted():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 11, 19),  # TODAY + 1 day
        end_date=date(2026, 11, 20),
        today=TODAY,
    )
    assert journey.start_date == date(2026, 11, 19)


def test_create_journey_with_start_equal_to_end_is_rejected():
    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(
            title="Lissabon",
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 1),  # same day: not "start before end"
            today=TODAY,
        )


def test_create_journey_with_end_one_day_after_start_is_accepted():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 2),  # smallest valid timeframe
        today=TODAY,
    )
    assert journey.end_date == date(2026, 12, 2)