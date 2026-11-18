from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from sqr.journey_management.domain.exceptions import InvalidJourneyTimeframe


@dataclass
class Journey:
    id: UUID
    title: str
    start_date: date
    end_date: date

    @classmethod
    def create(cls, title: str, start_date: date, end_date: date, today: date) -> "Journey":
        if start_date <= today:
            raise InvalidJourneyTimeframe("Start date must be in the future")
        if start_date >= end_date:
            raise InvalidJourneyTimeframe("Start date must be before end date")
        return cls(id=uuid4(), title=title, start_date=start_date, end_date=end_date)