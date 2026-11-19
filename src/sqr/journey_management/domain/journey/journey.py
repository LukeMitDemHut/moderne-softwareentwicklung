from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from sqr.journey_management.domain.exceptions import InvalidJourneyTimeframe, InvalidJourneyTitle
from sqr.journey_management.domain.journey.events import JourneyCreated


@dataclass
class Journey:
    id: UUID
    title: str
    start_date: date
    end_date: date
    events: list[JourneyCreated] = field(default_factory=list)

    @classmethod
    def create(cls, title: str, start_date: date, end_date: date, today: date) -> "Journey":
        rules = [
            (
                lambda: start_date <= today,
                InvalidJourneyTimeframe("Start date must be in the future"),
            ),
            (
                lambda: start_date >= end_date,
                InvalidJourneyTimeframe("Start date must be before end date"),
            ),
            (
                lambda: not title.strip(),
                InvalidJourneyTitle("Title must not be empty"),
            ),
        ]
        violation = next((error for is_violated, error in rules if is_violated()), None)
        if violation is not None:
            raise violation
        journey = cls(id=uuid4(), title=title, start_date=start_date, end_date=end_date)
        journey.events.append(
            JourneyCreated(
                journey_id=journey.id,
                title=journey.title,
                start_date=journey.start_date,
                end_date=journey.end_date,
            )
        )
        return journey