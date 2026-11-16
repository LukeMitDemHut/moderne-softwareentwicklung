## Exercise 3: System Architecture - DDD Documentation – SQR

> Status: Draft · Based on the Event Storming whiteboard dated 29.10.2026 and 05.11.2026
> Open points are marked with 🔶 TODO.

----

## 1. Event Storming

<!-- Sopha first draft was reviewed bei luc -->

🔶 TODO Bild einfügen

We conducted the Event Storming on our shared Miro board. We use 8 types of sticky notes for the representation:

| Color        | Type                      | Meaning                                                              |
| ------------ | ------------------------- | -------------------------------------------------------------------- |
| Orange       | Domain Event              | A domain-relevant event that has occurred (always in the past tense) |
| Light Yellow | User                      | Person or role that triggers the Command                             |
| Blue         | Command                   | Action that someone triggers in the system                           |
| Yellow       | Aggregate                 | Object to which the Command refers and that produces the Event       |
| Red          | Questions / Risks         | Questions or risks                                                   |
| Green        | View / Read Model         | A view with which Users interact to perform a task in the system     |
| Pink         | External System           | A third party, such as a travel service provider                     |
| Purple       | Business Process / Policy | Processes a Command according to the business rules and logic        |

The topic of Ubiquitous Language arose during the first Event Storming. It became the main topic of our first stroming, and we defined a clear structure.
We conducted the Event Storming in 2 iterations and identified 5 Bounded Contexts. We will focus on two of them. We decided to do it all in english, to stay conform with the coding language.

### Ubiquitous Language and Naming

We use the following English terms consistently throughout the documentation and the domain model:

| German (source term)     | English (target term)        | Additional note |
| :----------------------- | :--------------------------- | :-------------- |
| Nutzer                   | User                         |                 |
| Registrierung            | Registration                 |                 |
| Reisestop                | Destination                  |                 |
| Reise                    | Journey                      |                 |
| Reiseplan                | Journey Destination Overview |                 |
| Mitreisende              | Journey Companion            |                 |
| Tagesbriefing            | Daily Brief                  |                 |
| Aktivität / Unternehmung | Activity                     |                 |
| Änderungsvorschlag KI    | Suggestion                   |                 |

![Event Storming SQR](DDDEventstormingFokusContexte.png)
_Figure 1: Our 2 focus Bounded Contexts_

### Business Processes and Sequence of Events

**Guiding question:** _What happens in the domain, and in which order?_

Registration and Login are the prerequisites for creating Journeys. The process then splits into two options: creating a Journey or planning a Journey with AI.
These two interaction spaces are constantly intertwined because the AI agent is always available through a chat window. The following two Policies are particularly important:

1. AI may only make changes after confirmation by the User.
2. A Journey requires a start date and an end date. Both dates must be in the future when entered, and the start date must be before the end date. A wishlist is no longer part of the model.

### 1.0 Overall Process

Following the sample solution, we attempted to model these two processes.

🔶 TODO Bild einfügen
![Event Storming SQR](DDDEventstormingFokusDiagram.png)

### 1.1 User Management

**Process 1: UserAccount and Login**

| No. | Actor | Command               | Domain Event           | Aggregate |
| --- | ----- | --------------------- | ---------------------- | --------- |
| 1   | User  | `Register User`       | `User Registered`      | User      |
| 2   | User  | `Log In User`         | `User Logged In`       | User      |
| 3   | User  | `Change User Profile` | `User Profile Changed` | User      |

Three parallel flows, each triggered by the actor `User` in interaction with AI:

### 1.2 AI Assistance

| No. | Actor | Command                 | Domain Event                                                                 | Aggregate  |
| --- | ----- | ----------------------- | ---------------------------------------------------------------------------- | ---------- |
| 1   | User  | `Request AI Assistance` | `AI Suggestion Received`                                                     | Suggestion |
| 2   | User  | `Revise Suggestion`     | `Suggestion Revised`, no change in Journey Management                        | Suggestion |
| 3   | User  | `Accept Suggestion`     | `Suggestion Accepted` → triggers the selected Commands in Journey Management | Suggestion |
| 4   | User  | `Reject Suggestion`     | → End of the flow, no changes                                                | Suggestion |

A Suggestion can contain operations to **add, change, remove, and reorder** Destinations and Activities, as well as changes to Journey Details. The User can continue chatting with the AI and have the Suggestion revised without accepting or rejecting it yet.

Business rules:

1. Each Suggestion represents an independent batch. The User can accept the entire batch or a selection of its Suggestion Operations.
2. The selected Suggestion Operations, including their dependencies, are validated together and applied atomically. If one operation is invalid or a required dependent operation has not been selected, none of the selected operations are applied.
3. Confirming the selection also confirms any removals it contains. No additional removal confirmation is required.
4. The AI generates Suggestions; only confirmation by the User triggers the actual Commands in Journey Management.

### 1.3 Journey Management

**Process 2: Create a Journey or Interact with AI**

| No. | Actor   | Command                      | Domain Event                  | Aggregate   |
| --- | ------- | ---------------------------- | ----------------------------- | ----------- |
| 1   | User    | `Create Journey`             | `Journey Created`             | Journey     |
| 2   | User/AI | `Add Destination`            | `Destination Added`           | Destination |
| 3   | User/AI | `Add Activity`               | `Activity Added`              | Activity    |
| 4   | User/AI | `Change Journey Details`     | `Journey Details Changed`     | Journey     |
| 5   | User/AI | `Change Journey Timeframe`   | `Journey Timeframe Changed`   | Journey     |
| 6   | User/AI | `Change Destination Details` | `Destination Details Changed` | Destination |
| 7   | User/AI | `Change Activity Details`    | `Activity Details Changed`    | Activity    |
| 8   | User/AI | `Remove Activity`            | `Activity Removed`            | Activity    |
| 9   | User/AI | `Remove Destination`         | `Destination Removed`         | Destination |
| 10  | User/AI | `Reorder Destinations`       | `Destinations Reordered`      | Journey     |
| 11  | User/AI | `Reorder Activities`         | `Activities Reordered`        | Destination |
| 12  | User    | `Archive Journey`            | `Journey Archived`            | Journey     |
| 13  | User    | `Restore Journey`            | `Journey Restored`            | Journey     |

Sequence/dependencies:

- _User Registered/User Logged In_ (User Management) is a prerequisite for **Create Journey**.
- _Journey Created_ → _Destination Added_ → _Activity Added_ (domain sequence: first Journey, then Destinations, then Activities).

Command granularity:

- Not every editable attribute receives its own Command and Event. Simple changes remain grouped in cohesive Commands such as `Change Journey Details` or `Change Destination Details`.
- `Change Journey Timeframe` is modeled separately because special validation and rescheduling rules apply to the start and end dates.

Business rules:

1. **Start and end dates:** Both dates are required, must be in the future when entered, and must satisfy `start_date < end_date`. An existing Journey may become ongoing or past over time without becoming invalid.
2. **Activity removal:** Each Activity belongs to exactly one Destination. `Remove Activity` permanently removes only that Activity after confirmation. An AI Suggestion for alternatives is only provided upon explicit request.
3. **Destination removal:** If Activities are still assigned, the system asks whether similar Activities should be planned at another Destination before removal. The User can revise the AI Suggestion and accept selected Suggestion Operations, including `Remove Destination`. Alternatively, the User can manually remove the Destination without rescheduling; after confirmation, the assigned Activities are also removed.
4. **Journey archiving:** `Archive Journey` archives the Journey, including its Destinations and Activities, as a restorable, read-only state. Archived Journeys are not included in active AI Suggestions. Permanent removal of a Journey is not part of the MVP.
5. **Rescheduling for date changes:** A harmless extension or shortening of previously unplanned periods is applied directly. If the new Journey Timeframe cuts off already planned Destinations or Activities, the AI creates a Suggestion containing both the date change and the required rescheduling. The User can guide the Suggestion in the chat, for example, “move everything one day later”. Only confirmation applies the entire selection atomically.

## 2. Domain Model

**Guiding question:** _Which terms exist, and how are they related in the domain?_

High-level overview without module boundaries:

## 3. Bounded Contexts

**Guiding question:** _Where does the model need to be split?_

The whiteboard defines three contexts:

| Bounded Context        | Responsibility                                                                                   | Aggregate(s)                                  | Relationship to other Contexts                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **User Management**    | Registration, Login, User Profile                                                                | `User`                                        | Publishes `UserRegistered/UserLoggedIn` → prerequisite for creating a Journey                                         |
| **Journey Management** | Journeys, Destinations, Activities, including detail changes, removal, reordering, and archiving | `Journey` (including Destinations/Activities) | Consumes `UserRegistered/UserLoggedIn`; consumes confirmed Suggestion Operations                                      |
| **AI Assistance**      | AI requests, Suggestion batches, revision, acceptance/rejection                                  | `Suggestion`                                  | Publishes `SuggestionAccepted` with the selected operations → triggers their atomic application in Journey Management |

🔶 TODO (not discussed): Technology for communication between contexts – options:

| Option                                                         | Description                                     | Assessment                                                                         |
| -------------------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Asynchronous via Events** (e.g., message broker / event bus) | Contexts exchange Domain Events, loose coupling | Fits the whiteboard (Events are already highlighted as core elements); recommended |
| Synchronous via REST/gRPC                                      | Direct calls between services                   | Simple start, but stronger coupling                                                |
| Modular monolith with in-process Events                        | One deployment, Events as internal messages     | Easiest start with Python/Docker; can later be split into services                 |

**Recommendation:** Start as a _modular monolith_ with an in-process event bus (point 6), since the context boundaries have already been defined and a later split into container services remains possible.

---

## 4. Entities and Aggregates

**Guiding question:** _What belongs together within a Context, and what does the Aggregate Root protect?_

### 4.1 Context: User Management


🔶 TODO Bild einfügen

**Aggregate Root: `User`**

| Attribute       | Type       | Note                                     |
| --------------- | ---------- | ---------------------------------------- |
| `user_id`       | `UUID`     | Identity, immutable                      |
| `email`         | `str`      | Unique                                   |
| `name`          | `str`      | Profile name                             |
| `registered_at` | `datetime` | Timestamp of the `User Registered` event |

Methods:

- `register()` – Factory method, creates a new User and the `UserRegistered` event
- `change_profile(name, email)` – produces `UserProfileChanged`

Invariants (protected by the Aggregate Root):

- No further invariants defined so far. 🔶 TODO: Email uniqueness is deliberately assigned to the repository/this root, not to the object alone.

### 4.2 Context: Journey Management

**Aggregate Root: `Journey`** – Destinations and Activities are **Entities within the Aggregate** (since exactly 1 Journey → n Destinations → n Activities and all invariants apply at the Journey level).

| Attribute      | Type                                   | Note                                                            |
| -------------- | -------------------------------------- | --------------------------------------------------------------- |
| `journey_id`   | `UUID`                                 | Identity                                                        |
| `owner_id`     | `UUID`                                 | FK to the User (by ID, not as an object!)                       |
| `title`        | `str`                                  | Freely changeable (including through a confirmed AI Suggestion) |
| `start_date`   | `date`                                 | Required; in the future when entered                            |
| `end_date`     | `date`                                 | Required; in the future when entered                            |
| `status`       | `Status` (Enum: `ACTIVE` / `ARCHIVED`) | Archived Journeys are read-only and restorable                  |
| `destinations` | `list[Destination]`                    | Persisted consistently                                          |

`Destination` (Entity within the Aggregate): `destination_id`, `name`, `activities: list[Activity]`
`Activity` (Entity within the Aggregate): `activity_id`, `name`

Methods:

- `create(owner_id, title, start_date, end_date)` – Factory
- `add_destination(name)`
- `add_activity(destination_id, name)`
- `change_details(...)` / `change_timeframe(start_date, end_date)`
- `change_destination_details(...)` / `change_activity_details(...)`
- `remove_activity(activity_id)` / `remove_destination(destination_id)`
- `reorder_destinations(...)` / `reorder_activities(...)`
- `archive()` / `restore()`

Invariants:

1. **A Journey requires a start date and an end date.** Neither `Journey.create()` nor any change may result in either date being missing. Both dates must be in the future when entered; additionally, `start_date < end_date`. The later passage of time does not make an existing Journey invalid.
2. There is no limit on the number of Destinations/Activities.
3. Each Activity belongs to exactly one Destination. Destinations/Activities only exist within a valid Journey. Removing a Destination also removes its Activities after confirmation; removing an Activity only affects that Activity.
4. An archived Journey, including its Destinations and Activities, is read-only and can be fully restored. It is not included in active AI Suggestions. Permanent Journey removal is not planned for the MVP.
5. AI changes use the same methods as manual changes after confirmation – the Aggregate does not distinguish **where** the confirmed Command originates, only **that** a valid change is made. Without User confirmation, the AI does not invoke any method.
6. If a date change requires existing plans to be rescheduled, the date change and rescheduling are part of the same confirmed Suggestion batch. They are validated together and applied atomically.

### 4.3 Context: AI Assistance

**Aggregate Root: `Suggestion`**

| Attribute       | Type                                              | Note                                                                                  |
| --------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `suggestion_id` | `UUID`                                            | Identity of the independent batch                                                     |
| `user_id`       | `UUID`                                            | The User for whom the Suggestion is intended                                          |
| `operations`    | `list[SuggestionOperation]`                       | Operation type (`ADD`/`CHANGE`/`REMOVE`/`REORDER`), target, content, and dependencies |
| `status`        | `Status` (Enum: `OPEN` / `ACCEPTED` / `REJECTED`) | State machine                                                                         |
| `created_at`    | `datetime`                                        | Timestamp of the AI response                                                          |

Methods:

- `revise(operations)` – only permitted when `status == OPEN`; replaces the Suggestion based on the chat without changing Journey Details and produces `SuggestionRevised`
- `accept(selection)` – only permitted when `status == OPEN`; validates the selection and its dependencies, sets the status to `ACCEPTED`, and publishes `SuggestionAccepted` with the selected operations
- `reject()` – only permitted when `status == OPEN`; sets the status to `REJECTED`

Invariants:

1. **A Suggestion changes Journey Details exclusively after confirmation** (`accept(selection)` by the User). Chatting and revision only change the Suggestion, not Journey Management.
2. A Suggestion is immutable after acceptance/rejection (final state).
3. Each Suggestion is an independent batch. The selected operations are applied atomically; if a required operation is missing or validation fails, none of the selected operations are applied.
4. Selection and confirmation also constitute explicit User confirmation for any included `REMOVE` operations.

---

## 5. Domain Services and Repositories

**Guiding question:** _Which logic does not fit into an Entity, and how are Aggregates stored?_

### 5.1 Domain Services

| Service                        | Context            | Responsibility                                                                                                                                                                                 | Why not an Aggregate?                                        |
| ------------------------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `SuggestionService`            | AI Assistance      | Sends a request to the AI, transforms the response into an independent `Suggestion` batch, and supports its revision in the chat                                                               | Orchestrates an external service, no state of its own        |
| `SuggestionApplicationService` | Journey Management | Validates the _confirmed_ selection, including dependencies, and applies all operations atomically to the target Aggregate (loads the Journey, invokes the Commands/change methods, and saves) | Works across two Contexts and on another Context's Aggregate |
