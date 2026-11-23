# Exercise 4: Advanced Python, TDD and LLM-Assisted Development

Group 10 · SQR (AI Travel Companion) ·
LLM used: Claude (Sonnet 5.5, Anthropic)

**Note:** We develop in Python 3.13. Instead of JUnit we use pytest, instead of records `@dataclass`, instead of streams comprehensions and generators, and instead of `Optional<T>` the type `T | None`.

---

## Task 1: Review of the Implementation Strategy

**Approach:** We gave the LLM `implementation_plan.md`, `CI-CD-PLAN.md`, `agents.md` and the Miro board (event storming, class diagram with the bounded contexts) and asked for an analysis of the weaknesses, suggestions for the domain events and a better development order.

### Most Important Domain Events

| Event | Context | Trigger | Important Rule |
|---|---|---|---|
| `UserRegistered` | User Management | Register User | Registration and login will eventually be mandatory before a journey may be created |
| `JourneyCreated` | Journey Management | Create Journey | Start and end are mandatory, both in the future, start before end |
| `JourneyTimeframeChanged` | Journey Management | Change Journey Timeframe | In case of conflicts with activities only via a confirmed AI suggestion, applied atomically |
| `SuggestionAccepted` | AI Assistance | Accept Suggestion | Journey Management applies the chosen changes atomically |

### Adapted Development Strategy

1. **Phase 0 (skeleton):** We set up `pyproject.toml` with pytest and ruff, a platform-independent `dev` command and a CI with lint and pytest. We will only introduce Docker Compose and E2E tests once there are multiple services.
2. **Phase 1 (Journey Management, "Create Journey"):** We implement one function completely through all layers, using TDD and an in-memory repository. We model the owner via a `UserId` value object.
3. **Phase 2 (Journey Management, further functions):** For each function we build one slice (Add Destination, Add Activity, Change Timeframe, Reorder, Remove, Archive, Restore).
4. **Phase 3 (User Management):** We implement Register, Login and Profile, thereby replacing the fixed user from Phase 1.
5. **Phase 4 (persistence):** We switch from in-memory to SQLite. The application layer stays the same.
6. **Phase 5 (AI Assistance):** We start with a fake LLM and then connect the real LLM. We apply accepted suggestions synchronously in Journey Management so that the change remains atomic.

We are postponing Daily Brief, Audio Guide and Journey Sharing and record this as an ADR.

### Adopted and Rejected LLM Suggestions

The LLM made ten improvement suggestions, of which we adopted those that close gaps between the plan and Miro: Journey needs a user identity early on, because the policy in the event storming requires login before "Create Journey", while the plan puts Journey before User Management. We also adopted that events belong to their respective context and that only IDs cross context boundaries, and that a skeleton with CI is created before the first domain code. We also adopted working in vertical slices instead of entire contexts, because the Journey phase with 13 commands in Miro would otherwise be too large. We partially adopted the adjustment of the CI: lint and pytest apply early, Compose and E2E come later. We rejected the suggestion to simplify the layer structure and the command/query separation, because they are part of the learning goal (DDD, clean architecture). We only omit creating empty files in advance and a cache service without a use case.

---

## Task 2: Generating and Validating Test Cases with an LLM

**Test suite:** `backend/tests/journey_management/domain/test_journey.py` for `Journey.create` (10 test functions, 11 test runs)

| Type | Test |
|---|---|
| Happy path | valid timeframe is accepted |
| Edge case | start today is rejected, start tomorrow is accepted |
| Edge case | start equal to end is rejected, end one day after start is accepted |
| Edge case | the passed `today` value is actually used |
| Edge case | title with one character is accepted |
| Negative test | start after end is rejected |
| Negative test | start in the past is rejected |
| Negative test | empty title and title consisting of spaces are rejected |

**Documentation:**

We gave Claude (Sonnet 5.5) the context of Journey Management, the rules for `Journey.create` and our first three tests (these originate from a pair-programming session with the same LLM) and asked for further happy-path, edge-case and negative tests as well as a regex for the title. Of the 24 suggestions (4 happy path, 12 edge cases, 8 negative tests), we adopted the boundary pairs (start today and tomorrow, start equal to end and one day after), the test with the passed `today` value, as well as the title consisting of spaces and the title with one character. Tests that only check Python itself (`uuid4`, leap year, year change), type checks that belong at the API boundary, and cases that duplicate existing tests were bad or unnecessary. We adjusted the date values, because the LLM used a different fixed "today" and tests would thereby have turned green for the wrong reason, and the error class (`InvalidJourneyTitle` instead of the invented `JourneyValidationError`). The suggested regex `\S(?:.{0,98}\S)?` was correct according to our examples, but would have introduced two new business rules (at most 100 characters, no whitespace at the edges), so we use `title.strip()`.

---

## Task 3: Implementing the Domain Logic with LLM Pair Programming

**Implementation:** `backend/src/sqr/journey_management/domain/journey/journey.py`, `backend/src/sqr/journey_management/domain/exceptions.py`

**Documentation:**

We built the implementation step by step in pair programming with Claude using TDD (red, green, refactor): For each test, the LLM suggested the minimal code in `Journey.create`, and we ran and committed it. For the domain event `JourneyCreated`, the LLM suggested three variants: the journey collects its events itself, `create` returns a pair of journey and event, or the application service creates the event. We chose the first variant because the business event arises where the rules are checked (in the aggregate root), as DDD intends, and because the existing tests remain unchanged. The event is a `@dataclass(frozen=True)` (the Python replacement for a Java record), because an event describes something that has already happened and must no longer change. For the validation rules, the LLM suggested three variants: `if` blocks, a rule list with `lambda` and generator, or named helper methods. We tried the rule list because the worksheet mentions advanced techniques, and all tests stayed green. For three rules, however, it was harder to read and brought no advantage, so we undid the refactoring via revert; the LLM thus applied the technique correctly, but overdid it here. In our own review, we found that the code satisfies all 12 tests, the domain layer has no framework dependencies and `create` with the three rules is easy to read. The code review by the LLM found no error in behavior, but pointed out gaps: A `Journey` can be created via the constructor without the rules of `create`, and `None` as a date or title raises a `TypeError` or `AttributeError` instead of a domain error. In addition, the title is not trimmed, the event has no timestamp and no owner yet, and a test is missing that checks that each journey has its own event list. We record these points as open decisions in the team, because they concern business rules (trimming, `None`) or belong to the later application layer (timestamp, owner).
