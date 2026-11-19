# Übung 4: Advanced Python, TDD und LLM-gestütztes Entwickeln

Gruppe 10 · SQR (KI-Reisebegleiter) ·
Eingesetztes LLM: Claude (Sonnet 5.5, Anthropic)

**Hinweis:** Wir entwickeln in Python 3.13. Statt JUnit verwenden wir pytest, statt Records `@dataclass`, statt Streams Comprehensions und Generatoren, statt `Optional<T>` den Typ `T | None`.

---

## Aufgabe 1: Review der Implementierungsstrategie

**Vorgehen:** Wir haben dem LLM `implementation_plan.md`, `CI-CD-PLAN.md`, `agents.md` und das Miro-Board (Event-Storming, Klassendiagramm mit den Bounded Contexts) gegeben und um eine Analyse der Schwachstellen, Vorschläge für die Domain-Events und eine bessere Entwicklungsreihenfolge gebeten.

### Wichtigste Domain-Events

| Event | Kontext | Auslöser | Wichtige Regel |
|---|---|---|---|
| `UserRegistered` | User Management | Register User | Registrierung und Login sind Pflicht, bevor eine Journey erstellt werden darf |
| `JourneyCreated` | Journey Management | Create Journey | Start und Ende sind Pflicht, beide in der Zukunft, Start vor Ende |
| `JourneyTimeframeChanged` | Journey Management | Change Journey Timeframe | Bei Konflikten mit Aktivitäten nur über einen bestätigten KI-Vorschlag, atomar angewendet |
| `SuggestionAccepted` | AI Assistance | Accept Suggestion | Journey Management wendet die gewählten Änderungen atomar an |

### Angepasste Entwicklungsstrategie

1. **Phase 0 (Grundgerüst):** Wir legen `pyproject.toml` mit pytest und ruff an, ein plattformunabhängiges `dev`-Kommando und eine CI mit Lint und pytest. Docker-Compose und E2E-Tests führen wir erst ein, wenn es mehrere Dienste gibt.
2. **Phase 1 (Journey Management, "Create Journey"):** Wir setzen eine Funktion komplett durch alle Schichten um, per TDD und mit In-Memory-Repository. Den Eigentümer bilden wir über ein `UserId`-Value-Object ab.
3. **Phase 2 (Journey Management, weitere Funktionen):** Wir bauen je Funktion eine Scheibe (Add Destination, Add Activity, Change Timeframe, Reorder, Remove, Archive, Restore).
4. **Phase 3 (User Management):** Wir setzen Register, Login und Profil um und ersetzen damit den festen Nutzer aus Phase 1.
5. **Phase 4 (Persistenz):** Wir wechseln von In-Memory auf SQLite. Die Anwendungsschicht bleibt gleich.
6. **Phase 5 (AI Assistance):** Wir starten mit einem Fake-LLM und binden danach das echte LLM an. Angenommene Vorschläge wenden wir synchron in Journey Management an, damit die Änderung atomar bleibt.

Wir stellen Daily Brief, Audio Guide und Journey-Sharing zurück und halten das als ADR fest.

### Übernommene und abgelehnte LLM-Vorschläge

Das LLM hat zehn Verbesserungsvorschläge gemacht, von denen wir die übernommen haben, die Lücken zwischen Plan und Miro schließen: Journey braucht früh eine Nutzer-Identität, weil die Policy im Event-Storming Login vor "Create Journey" verlangt, der Plan Journey aber vor User Management setzt. Ebenso haben wir übernommen, dass Events dem jeweiligen Kontext gehören und über Kontextgrenzen nur IDs laufen, und dass ein Grundgerüst mit CI vor dem ersten Fachcode entsteht. Auch die Arbeit in vertikalen Scheiben statt in ganzen Kontexten haben wir übernommen, weil die Journey-Phase mit 13 Befehlen im Miro sonst zu groß wäre. Teilweise übernommen haben wir die Anpassung der CI: Lint und pytest gelten früh, Compose und E2E kommen erst später. Abgelehnt haben wir den Vorschlag, die Schichtenstruktur und die Command/Query-Trennung zu vereinfachen, weil sie zum Lernziel (DDD, saubere Architektur) gehören. Nur leere Dateien im Voraus anzulegen und einen Cache-Dienst ohne Anwendungsfall lassen wir weg.

---

## Aufgabe 2: Testfälle mit LLM generieren und validieren

**Testsuite:** `tests/journey_management/domain/test_journey.py` für `Journey.create` (10 Testfunktionen, 11 Testläufe)

| Art | Test |
|---|---|
| Happy-Path | gültiger Zeitraum wird akzeptiert |
| Edge-Case | Start heute wird abgelehnt, Start morgen wird akzeptiert |
| Edge-Case | Start gleich Ende wird abgelehnt, Ende einen Tag nach Start wird akzeptiert |
| Edge-Case | der übergebene `today`-Wert wird wirklich benutzt |
| Edge-Case | Titel mit einem Zeichen wird akzeptiert |
| Negativtest | Start nach Ende wird abgelehnt |
| Negativtest | Start in der Vergangenheit wird abgelehnt |
| Negativtest | leerer Titel und Titel aus Leerzeichen werden abgelehnt |

**Dokumentation:**

Wir haben Claude (Sonnet 5.5) den Kontext von Journey Management, die Regeln für `Journey.create` und unsere drei ersten Tests gegeben (diese stammen aus einem Pair-Programming mit demselben LLM) und um weitere Happy-Path-, Edge-Case- und Negativtests sowie ein Regex für den Titel gebeten. Von den 24 Vorschlägen (4 Happy-Path, 12 Edge-Cases, 8 Negativtests) haben wir die Grenzpaare (Start heute und morgen, Start gleich Ende und ein Tag danach), den Test mit dem übergebenen `today`-Wert sowie den Titel aus Leerzeichen und den Titel mit einem Zeichen übernommen. Schlecht oder unnötig waren Tests, die nur Python selbst prüfen (`uuid4`, Schaltjahr, Jahreswechsel), Typprüfungen, die an die API-Grenze gehören, und Fälle, die vorhandene Tests doppeln. Angepasst haben wir die Datumswerte, weil das LLM ein anderes festes "heute" benutzt hat und Tests dadurch aus dem falschen Grund grün geworden wären, und die Fehlerklasse (`InvalidJourneyTitle` statt der erfundenen `JourneyValidationError`). Das vorgeschlagene Regex `\S(?:.{0,98}\S)?` war nach unseren Beispielen korrekt, hätte aber zwei neue Fachregeln eingeführt (höchstens 100 Zeichen, kein Leerraum am Rand), deshalb nutzen wir `title.strip()`.

---

## Aufgabe 3: Implementierung der Domänenlogik mit LLM-Pair-Programming

**Implementierung:** `src/sqr/journey_management/domain/journey/journey.py`, `src/sqr/journey_management/domain/exceptions.py`

**Dokumentation:**

Wir haben die Implementierung im Pair-Programming mit Claude Schritt für Schritt per TDD (Red, Green, Refactor) aufgebaut: Das LLM hat für jeden Test den minimalen Code in `Journey.create` vorgeschlagen, wir haben ihn ausgeführt und committet. Für das Domain-Event `JourneyCreated` hat das LLM drei Varianten vorgeschlagen: Die Journey sammelt ihre Events selbst, `create` gibt ein Paar aus Journey und Event zurück, oder der Application Service erzeugt das Event. Wir haben die erste Variante gewählt, weil das fachliche Ereignis dort entsteht, wo die Regeln geprüft werden (im Aggregate Root), wie es DDD vorsieht, und weil die vorhandenen Tests dabei unverändert bleiben. Das Event ist ein `@dataclass(frozen=True)` (Python-Ersatz für ein Java-Record), weil ein Ereignis etwas beschreibt, das schon passiert ist und sich nicht mehr ändern darf. Für die Prüfregeln hat das LLM drei Varianten vorgeschlagen: `if`-Blöcke, eine Regelliste mit `lambda` und Generator oder benannte Hilfsmethoden. Wir haben die Regelliste ausprobiert, weil das Blatt fortgeschrittene Techniken nennt, und alle Tests blieben grün. Sie war für drei Regeln aber schwerer zu lesen und brachte keinen Vorteil, deshalb haben wir den Umbau per Revert zurückgenommen; das LLM hat die Technik also korrekt, aber hier übertrieben eingesetzt. In unserer eigenen Prüfung haben wir festgestellt, dass der Code alle 12 Tests erfüllt, die Domain-Schicht keine Framework-Abhängigkeiten hat und `create` mit den drei Regeln gut lesbar ist. Das Code-Review durch das LLM fand keinen Fehler im Verhalten, wies aber auf Lücken hin: Eine `Journey` lässt sich über den Konstruktor ohne die Regeln von `create` anlegen, und `None` als Datum oder Titel löst einen `TypeError` bzw. `AttributeError` statt eines Domain-Fehlers aus. Außerdem wird der Titel nicht getrimmt, das Event hat noch keinen Zeitstempel und keinen Eigentümer, und ein Test fehlt, der prüft, dass jede Journey eine eigene Event-Liste hat. Diese Punkte halten wir als offene Entscheidungen im Team fest, weil sie Fachregeln betreffen (Trimmen, `None`) oder zum späteren Application-Layer gehören (Zeitstempel, Eigentümer).