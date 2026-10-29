# CI/CD Plan — moderne-softwareentwicklung (SQR)

Strategy document for the Continuous Integration / Continuous Delivery pipeline of this repository.

## 1. Goals & Principles

- **Fast feedback:** quick checks first (lint), expensive checks later (E2E in compose).
- **Single source of truth:** CI invokes the repository's `./dev` script — never raw tool commands. Developers and CI execute exactly the same commands.

## 2. Pipeline Stages & Triggers

| # | Stage | Trigger | Content | Gate for |
|---|-------|---------|---------|----------|
| 1 | **Commit** | `push` to any branch (no tags, no docs-only changes) | Linting (ruff) | Nothing — early feedback only |
| 2 | **Pull Request** | `pull_request` targeting `main` | Linting + full test suite (pytest, coverage) executed **inside the container** via docker compose, including E2E against multiple services | Merging into `main` |
| 3 | **Release** | `push` of a version tag (`v*.*.*`, semver) | Re-run Stage 2 as gate → build Docker image → push image → create GitHub Release | Publishing the version |

### Trigger semantics

- Pushes to a PR branch fire **both** Stage 1 and Stage 2. Stage 2 supersedes Stage 1 runs for the same ref (`concurrency` group with `cancel-in-progress`), so Stage 2 is the relevant result for a PR.
- Version tags matching `vMAJOR.MINOR.PATCH` (e.g. `v0.1.0`) are the only release trigger. Accidental tags should not publish anything.
- `workflow_dispatch` will be enabled on all workflows so any stage can be triggered manually from the Actions tab.

## 3. Workflow Layout

1. **`lint.yml`** — Stage 1. Checkout → set up Python 3.13 (pip-cached) → `./dev lint`.
2. **`test.yml`** — Stage 2. Checkout → build compose environment → run `./dev test` inside the app container → collect exit code, test summary and coverage report → tear down.
3. **`release.yml`** — Stage 3. Runs the same test job as Stage 2 first; only on success: build the image, push to GHCR, create the GitHub Release.


## 4. The `./dev` Script Contract

The developer script is the command interface CI depends on. CI must always be able to run:

| Command | Effect | Used by |
|---------|--------|---------|
| `./dev lint` | Run ruff over the codebase, non-interactive, non-zero exit on findings | Stage 1, Stage 2 |
| `./dev test` | Run the **entire** test suite (backend + frontend + E2E) inside the compose environment | Stage 2, Stage 3 |
| `./dev test-backend` / `./dev test-frontend` | Test one part only | Developers (optional CI use) |
| `./dev build` | Build the runtime image(s) | Stage 3, developers |
| `./dev up / down` | Start/stop the full multi-service environment | Superset used by the above |
| `./dev release` | Tag the current commit and push the tag | Developers (triggers Stage 3) |

Constraints: `./dev` must itself set up its prerequisites (compose build before running tests inside containers), must be deterministic in CI (no interactive prompts), and must report failures via exit codes. If `./dev` changes its interface, CI must be updated in the same change.

## 5. Test Strategy (Stage 2)

- Tests run **inside the application container** in a compose-defined environment, not on the runner host
- The compose file models the real deployment: multiple services (backend app, frontend, supporting services such as database/cache as the project grows) for end-to-end testing.
- `pytest` produces a coverage report; the report is uploaded as a workflow artifact for every Stage 2 run. A coverage threshold (fail below X%) is a later addition (reporting first, enforcement once a meaningful baseline exists)
- Test results are emitted in a machine-readable format (e.g. JUnit XML) so failures surface as GitHub checks annotations.

## 6. Lint Strategy (Stages 1 & 2)

- **Tool:** ruff (lint + formatting rules), configured in `pyproject.toml`
- Runs on every push to a branch (tags are not linted separately — the Stage 3 test gate covers them).
- Findings are never fixed by CI; the gate simply fails and developers fix locally (optionally via `./dev lint --fix`).
- Developers could use pre-commit (config supplied by repo) or IDE linting features to automate linting

## 7. Build & Push (Stage 3)

- **Single Docker image**: frontend is built as static assets and served by the image
- **Registry:** GitHub Container Registry — `ghcr.io/lukeMitDemHut/moderne-softwareentwicklung`. Authenticated via `GITHUB_TOKEN` with `packages: write`; no third-party secrets.
- **Tags per release:**
  - `vX.Y.Z` — immutable, mirrors the git tag
  - `latest` — rolling, points at the newest successful release
- Image builds use layer caching so releases stay fast even with infrequent publishing.


## 8. GitHub Release
- `./dev release` tags the current commit and pushes the tag. Stage 3 then runs unattended: test gate → build → push → GitHub Release.
- Each `v*.*.*` tag creates a GitHub Release with auto-generated changelog notes (derived from commits since the previous tag).
- The Release is created **only after** the test gate and image push succeeded — a failed pipeline never yields a published release or published image being advertised as released.
- Retrying a failed release means deleting the tag and re-tagging; unsuccessful releases are treated as candidates.
