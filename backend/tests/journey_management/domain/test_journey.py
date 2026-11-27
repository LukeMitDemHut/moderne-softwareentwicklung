from dataclasses import replace
from datetime import UTC, date, datetime

import pytest

from sqr.journey_management.domain.exceptions import (
    InvalidJourneyTimeframe,
    InvalidJourneyTitle,
)
from sqr.journey_management.domain.journey.events import JourneyCreated
from sqr.journey_management.domain.journey.journey import Journey

NOW = datetime(
    2026, 11, 18, 10, 0, tzinfo=UTC
)  # fixed point in time, so the test result never depends on the real clock


def test_create_journey_with_valid_timeframe_succeeds():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        now=NOW,
    )
    assert journey.title == "Lissabon"


def test_create_journey_with_start_after_end_is_rejected():
    start = date(2026, 12, 8)
    end = date(2026, 12, 1)

    with pytest.raises(InvalidJourneyTimeframe):  # expects exactly this error
        Journey.create(title="Lissabon", start_date=start, end_date=end, now=NOW)


def test_create_journey_with_start_in_the_past_is_rejected():
    start = date(2026, 11, 1)  # before NOW (2026-11-18)
    end = date(2026, 12, 8)

    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(title="Lissabon", start_date=start, end_date=end, now=NOW)


def test_create_journey_with_start_today_is_rejected():
    start = NOW.date()  # exactly today: not "in the future"
    end = date(2026, 11, 25)

    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(title="Lissabon", start_date=start, end_date=end, now=NOW)


def test_create_journey_with_start_tomorrow_is_accepted():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 11, 19),  # NOW + 1 day
        end_date=date(2026, 11, 20),
        now=NOW,
    )
    assert journey.start_date == date(2026, 11, 19)


def test_create_journey_with_start_equal_to_end_is_rejected():
    same_day = date(2026, 12, 1)  # same day: not "start before end"

    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(
            title="Lissabon", start_date=same_day, end_date=same_day, now=NOW
        )


def test_create_journey_with_end_one_day_after_start_is_accepted():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 2),  # smallest valid timeframe
        now=NOW,
    )
    assert journey.end_date == date(2026, 12, 2)


def test_create_journey_uses_the_given_now_value():
    start = date(2026, 12, 1)
    end = date(2026, 12, 8)
    early_now = datetime(2026, 11, 18, 10, 0, tzinfo=UTC)
    late_now = datetime(2026, 12, 5, 10, 0, tzinfo=UTC)

    # with now = 18 Nov the start lies in the future: accepted
    Journey.create(title="Lissabon", start_date=start, end_date=end, now=early_now)

    # with today = 5 Dec the same start lies in the past: rejected
    with pytest.raises(InvalidJourneyTimeframe):
        Journey.create(title="Lissabon", start_date=start, end_date=end, now=late_now)


@pytest.mark.parametrize("title", ["", "   "])  # runs the test once per value
def test_create_journey_with_blank_title_is_rejected(title):
    start = date(2026, 12, 1)
    end = date(2026, 12, 8)

    with pytest.raises(InvalidJourneyTitle):
        Journey.create(title=title, start_date=start, end_date=end, now=NOW)


def test_create_journey_with_single_character_title_is_accepted():
    start = date(2026, 12, 1)
    end = date(2026, 12, 8)

    journey = Journey.create(
        title="A", start_date=start, end_date=end, now=NOW
    )  # lower bound: no minimum length

    assert journey.title == "A"


def test_create_journey_records_journey_created_event():
    start = date(2026, 12, 1)
    end = date(2026, 12, 8)

    journey = Journey.create(title="Lissabon", start_date=start, end_date=end, now=NOW)

    assert journey.events == [
        JourneyCreated(
            journey_id=journey.id, title="Lissabon", start_date=start, end_date=end
        )
    ]


def test_create_journey_strips_whitespace_around_title():
    start = date(2026, 12, 1)
    end = date(2026, 12, 8)

    journey = Journey.create(
        title="  Lissabon und Porto  ", start_date=start, end_date=end, now=NOW
    )

    assert journey.title == "Lissabon und Porto"
    assert journey.events[0].title == "Lissabon und Porto"


def test_journeys_with_same_id_are_equal_even_if_title_differs():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        now=NOW,
    )
    renamed = replace(journey, title="Lissabon und Porto")

    assert renamed == journey


def test_journeys_with_identical_data_but_different_ids_are_not_equal():
    first = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        now=NOW,
    )
    second = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        now=NOW,
    )

    assert first != second


def test_journeys_with_same_id_count_once_in_a_set():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        now=NOW,
    )
    renamed = replace(journey, title="Lissabon und Porto")

    assert len({journey, renamed}) == 1


def test_journey_is_not_equal_to_other_types():
    journey = Journey.create(
        title="Lissabon",
        start_date=date(2026, 12, 1),
        end_date=date(2026, 12, 8),
        now=NOW,
    )

    assert journey != journey.id
