from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)  # frozen: cannot be changed afterwards, like a Java record
class JourneyCreated:
    """A journey has been created."""

    journey_id: UUID
    title: str
    start_date: date
    end_date: date
    occurred_at: datetime
