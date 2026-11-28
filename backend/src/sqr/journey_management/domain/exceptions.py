class DomainError(Exception):
    """Base class for all rule violations in the domain layer."""


class InvalidJourneyTimeframe(DomainError):
    """Raised when the start and end date of a journey are not valid."""


class InvalidJourneyTitle(DomainError):
    """Title of the journey is invalid."""
