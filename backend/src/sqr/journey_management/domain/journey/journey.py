from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

from sqr.journey_management.domain.exceptions import (
    InvalidJourneyTimeframe,
    InvalidJourneyTitle,
)
from sqr.journey_management.domain.journey.events import JourneyCreated


@dataclass(eq=False)  # entity: equality by identity, not by field values
class Journey:
    id: UUID
    title: str
    start_date: date
    end_date: date
    events: list[JourneyCreated] = field(default_factory=list)

    @classmethod
    def create(
        cls, title: str, start_date: date, end_date: date, now: datetime
    ) -> "Journey":
        today = now.date()
        if start_date <= today:
            raise InvalidJourneyTimeframe("Start date must be in the future")
        if start_date >= end_date:
            raise InvalidJourneyTimeframe("Start date must be before end date")
        title = title.strip()
        if not title:
            raise InvalidJourneyTitle("Title must not be empty")
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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Journey) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
