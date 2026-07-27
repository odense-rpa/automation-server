# Changelog

All notable changes to the Automation Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-07-08

### Security

- **Dependency upgrades across all components** patching ~135 advisories rooted in stale lockfiles ([344b99b](https://github.com/odense-rpa/automation-server/commit/344b99b)):
  - Backend: h11 0.16.0 (request smuggling, CVE-2025-43859), python-multipart 0.0.32 (arbitrary file write, CVE-2026-24486), starlette 1.3.1 via FastAPI 0.139.0 (7 CVEs), urllib3 2.7.0 (decompression-bomb DoS)
  - Worker: gitpython 3.1.50 (4 RCE-class CVEs in clone/config paths), urllib3 2.7.0, requests 2.34.2
  - Frontend: axios 1.16.x (25 advisories), form-data boundary randomness fix (critical), vite 5.4.21, tar chain
  - Website: shell-quote 1.9.0 (command injection), babel/fast-uri/ws updates
- **Docker base images**: node 20 (EOL) → 24, nginx 1.25 → 1.30, uv image pinned to 0.11.28 (was `:latest`); `.env*` excluded from worker image via `.dockerignore`

### Internal

- Migrated to trunk-based development: `main` is the only long-lived branch, protected with required CI checks; releases are marked by `v*` tags
- Added CI workflow running backend tests/lint and frontend lint/build on all pull requests
- Added nightly Docker build workflow

---

## [0.4.0] - 2026-05-20

### Changed

- **Full async I/O migration**: All database sessions, repositories, services, API endpoints, and the scheduler now use `async`/`await`. The database engine is replaced with `asyncpg`-backed `AsyncSession`; `AbstractUnitOfWork` is now an async context manager. This eliminates thread-blocking DB calls and reduces latency under concurrent load.
- **Async scheduler**: The automation scheduler loop runs entirely async, using `AsyncSession` directly rather than wrapping a sync session generator.
- **Async test suite**: All API and service tests ported to `pytest-asyncio` with `AsyncClient`.

### Added

- **Locust benchmark harness** (`backend/benchmarks/`): load-test scripts and seed data for comparing async vs sync throughput. Run with `locust -f backend/benchmarks/locustfile.py`.

### Fixed

- `release.sh` branch guard updated from `master` to `main`.

### Internal

- Added `asyncpg>=0.30.0` runtime dependency.
- Added `locust>=2.0` and `ruff>=0.9.0` as dev dependencies.
- Sync `engine` retained solely for Alembic migrations; application uses `async_engine`.

---

## [0.3.1] - 2026-04-15

### Added

- **Copy buttons in workitem views**: `JsonView`, `WorkitemInfo`, and `WorkItemRow` components now include copy-to-clipboard buttons for JSON data and workitem references ([19a9004](https://github.com/odense-rpa/automation-server/commit/19a9004))
- **Documentation website**: New Docusaurus-based documentation site in `website/` with structured sections for getting started, architecture, and guides ([b1dd1bc](https://github.com/odense-rpa/automation-server/commit/b1dd1bc))
- **Docs deploy workflow**: GitHub Actions workflow to automatically deploy the documentation site ([deploy-docs.yml](https://github.com/odense-rpa/automation-server/blob/development/.github/workflows/deploy-docs.yml))

### Changed

- **Incident age filtering**: Incident creation now filters failed sessions by age — only recent failures trigger new incidents, preventing historical sessions from generating noise ([6ce8c14](https://github.com/odense-rpa/automation-server/commit/6ce8c14), [57f470f](https://github.com/odense-rpa/automation-server/commit/57f470f))
- **Workitem JSON display**: Improved layout and column handling in `JsonView`, `WorkitemInfo`, and `WorkitemsTable` components ([26063ba](https://github.com/odense-rpa/automation-server/commit/26063ba))
- **Documentation restructured**: Docs reorganized into `getting-started/`, `architecture/`, and `guides/` sections; obsolete pages removed ([98a360f](https://github.com/odense-rpa/automation-server/commit/98a360f), [ef69a71](https://github.com/odense-rpa/automation-server/commit/ef69a71))

### Testing

- Added age-based session filtering tests for incident creation in `test_incidents.py` ([57f470f](https://github.com/odense-rpa/automation-server/commit/57f470f))

---

## [0.3.0] - 2026-03-30

### Added

- **Incident management**: Failed sessions automatically create incidents. Incidents can be resolved, dismissed individually or in bulk, and viewed on the dashboard. Includes full API, service, repository, and frontend component ([20720f0](https://github.com/odense-rpa/automation-server/commit/20720f0), [26d69cf](https://github.com/odense-rpa/automation-server/commit/26d69cf), [13d738d](https://github.com/odense-rpa/automation-server/commit/13d738d), [999225b](https://github.com/odense-rpa/automation-server/commit/999225b))
- **Process activity summary**: Dashboard component and API endpoint showing session counts (completed/failed/in-progress/new) per process over a configurable time window ([994126a](https://github.com/odense-rpa/automation-server/commit/994126a), [08f721b](https://github.com/odense-rpa/automation-server/commit/08f721b))
- **Sessions view**: Dedicated page for browsing sessions with search and pagination ([c20dd3c](https://github.com/odense-rpa/automation-server/commit/c20dd3c))
- **Workqueue detail view**: Read-only workqueue detail page split from the edit view ([03e998e](https://github.com/odense-rpa/automation-server/commit/03e998e))
- **Workqueue lookup by name**: New API endpoint `GET /workqueues/by_name/{name}` ([5382db5](https://github.com/odense-rpa/automation-server/commit/5382db5))
- **Light/dark mode**: Toggle added to navigation with custom "automation" DaisyUI theme ([c8ff840](https://github.com/odense-rpa/automation-server/commit/c8ff840), [7811f90](https://github.com/odense-rpa/automation-server/commit/7811f90))
- **Optional message on work item status update**: `WorkItemStatusUpdate` schema accepts an optional `message` field
- **Playwright browser installation in runner**: Python runner installs Playwright browsers at runtime ([d0786b7](https://github.com/odense-rpa/automation-server/commit/d0786b7))
- **Release and version bump scripts**: `scripts/release.sh` and `scripts/bump-version.sh` for managing releases ([e1af60f](https://github.com/odense-rpa/automation-server/commit/e1af60f))

### Changed

- **Dashboard layout**: Incidents list at the top, process activity summary replaces the session list
- **Credentials**: Refactored from modal-based to dedicated create/edit views following the list→edit pattern ([f81fbed](https://github.com/odense-rpa/automation-server/commit/f81fbed))
- **Search and pagination**: Extracted into a reusable `SearchInput` component and a `tableStateStore` (Pinia) that persists state across views ([d47690d](https://github.com/odense-rpa/automation-server/commit/d47690d), [27027be](https://github.com/odense-rpa/automation-server/commit/27027be))
- **Workqueue information endpoint**: Replaced N+1 per-queue count queries with a single batch query; added composite index on `(workqueue_id, status)` ([7f4905b](https://github.com/odense-rpa/automation-server/commit/7f4905b))
- **Workqueues and credentials sorted server-side** by name ([3fc00b2](https://github.com/odense-rpa/automation-server/commit/3fc00b2))
- **Process creation**: Redirects to edit view after creation ([a3edc88](https://github.com/odense-rpa/automation-server/commit/a3edc88))
- **AlertFlasher**: Relocated to bottom-right of screen
- **Favicon**: Replaced `.ico` with `.svg`
- **Version**: Read dynamically via `importlib.metadata`; handles missing package gracefully ([cd4bb13](https://github.com/odense-rpa/automation-server/commit/cd4bb13))
- **Auto-refresh interval**: Changed to 15 seconds ([0539639](https://github.com/odense-rpa/automation-server/commit/0539639))
- **Worker Docker setup**: Simplified to single stage; Playwright installation moved into the runner ([a7754c9](https://github.com/odense-rpa/automation-server/commit/a7754c9))
- **Docker Compose**: Split into production base (`docker-compose.yml`) and development override (`docker-compose.override.yml`). Production uses pre-built GHCR images; development builds locally with hot-reload and volume mounts ([072e8dd](https://github.com/odense-rpa/automation-server/commit/072e8dd))
- **PostgreSQL**: Configured with ICU locale (`da-DK`) for correct collation on new installations

### Fixed

- Fix #3: Clone git repositories with `--recurse-submodules` ([15f4f1b](https://github.com/odense-rpa/automation-server/commit/15f4f1b))
- Fix #8: Configurable time window on Up Next display ([fc3328b](https://github.com/odense-rpa/automation-server/commit/fc3328b))
- Fix #12: Auto-focus parameters input on open, trigger session on Enter, show parameter suggestions ([cc2d661](https://github.com/odense-rpa/automation-server/commit/cc2d661))
- Session search now filters on status in addition to process name ([d54d3fa](https://github.com/odense-rpa/automation-server/commit/d54d3fa))

### Testing

- Added `test_incidents.py` with comprehensive incident lifecycle coverage
- Added workqueue by-name lookup tests to `test_workqueue.py`

---

## [0.2.0] - 2025-07-25

### Added

- **Upcoming executions**: View upcoming scheduled executions with API and UI component ([4f59257](https://github.com/odense-rpa/automation-server/commit/4f59257), [d83e9fd](https://github.com/odense-rpa/automation-server/commit/d83e9fd))
- **Work duration tracking**: WorkItem model tracks work duration with tests ([243f00a](https://github.com/odense-rpa/automation-server/commit/243f00a), [03a9d94](https://github.com/odense-rpa/automation-server/commit/03a9d94))
- **Session parameters**: Optional parameters input for session creation in InstantSchedule ([11ea9fb](https://github.com/odense-rpa/automation-server/commit/11ea9fb))
- **Trigger deduplication**: Prevents multiple trigger activations within the same minute ([8c31b17](https://github.com/odense-rpa/automation-server/commit/8c31b17))
- **Work item reference API**: Endpoint to retrieve work items by reference with optional status filter ([27d2c6f](https://github.com/odense-rpa/automation-server/commit/27d2c6f), [33672fc](https://github.com/odense-rpa/automation-server/commit/33672fc))
- **Health check endpoints**: Integrated into FastAPI application ([fa668fd](https://github.com/odense-rpa/automation-server/commit/fa668fd))
- **Audit logging**: Refactored session logging to audit logging with new schema ([5ff9a35](https://github.com/odense-rpa/automation-server/commit/5ff9a35), [b9ce07e](https://github.com/odense-rpa/automation-server/commit/b9ce07e), [727e8e1](https://github.com/odense-rpa/automation-server/commit/727e8e1))
- **Docker release workflow**: Automated image building and pushing ([6240b75](https://github.com/odense-rpa/automation-server/commit/6240b75))
- **Playwright Docker support**: Compose and Docker configuration for Playwright workers ([7c0a63b](https://github.com/odense-rpa/automation-server/commit/7c0a63b))
- **Testing infrastructure**: Docker PostgreSQL container fixture for integration tests ([4a42787](https://github.com/odense-rpa/automation-server/commit/4a42787))
- **Delete workqueue**: Added delete workqueue functionality to the frontend ([4f25702](https://github.com/odense-rpa/automation-server/commit/4f25702))
- **CLAUDE.md**: Project guidance and development instructions ([054e578](https://github.com/odense-rpa/automation-server/commit/054e578))

### Changed

- **Scheduler**: Refactored to modular architecture using the Strategy pattern with date, cron, and workqueue trigger processors ([da6b972](https://github.com/odense-rpa/automation-server/commit/da6b972), [7df783e](https://github.com/odense-rpa/automation-server/commit/7df783e), [ac195f3](https://github.com/odense-rpa/automation-server/commit/ac195f3))
- **CronSim**: Migrated to CronSim for cron expression handling ([ec7d362](https://github.com/odense-rpa/automation-server/commit/ec7d362))
- **Worker Dockerfile**: Multi-stage build with Playwright stage ([52b4052](https://github.com/odense-rpa/automation-server/commit/52b4052))
- **Docker Compose**: Uses pre-built images; API URL configurable via environment variable ([c9f0101](https://github.com/odense-rpa/automation-server/commit/c9f0101), [a5d014c](https://github.com/odense-rpa/automation-server/commit/a5d014c))
- **Alphabetical sorting**: Lists and tables sorted alphabetically ([6d4a049](https://github.com/odense-rpa/automation-server/commit/6d4a049))
- **Active route highlighting**: Navigation highlights the current route ([90354ee](https://github.com/odense-rpa/automation-server/commit/90354ee))
- **Work item concurrency**: `get_next_workitem` uses `skip_locked` for better concurrency ([04bf0ef](https://github.com/odense-rpa/automation-server/commit/04bf0ef))
- **Schemas**: Data types use `Dict` instead of `str` ([8389641](https://github.com/odense-rpa/automation-server/commit/8389641))

### Fixed

- Token list no longer sorted, preserving original order ([9727d65](https://github.com/odense-rpa/automation-server/commit/9727d65))
- Case-insensitive session log search; pagination improvements ([40b54f2](https://github.com/odense-rpa/automation-server/commit/40b54f2), [51cf9f3](https://github.com/odense-rpa/automation-server/commit/51cf9f3))
- `scalar_one` query result handling ([d06f88d](https://github.com/odense-rpa/automation-server/commit/d06f88d))
- Paginated workitem count ([e9cc2c8](https://github.com/odense-rpa/automation-server/commit/e9cc2c8))
- JSON handling in credential create/edit components ([9e007fe](https://github.com/odense-rpa/automation-server/commit/9e007fe))
- Form fields use `null` instead of `0` for empty state ([3e699ce](https://github.com/odense-rpa/automation-server/commit/3e699ce))
- Docker entrypoint script ([fdc6534](https://github.com/odense-rpa/automation-server/commit/fdc6534))
- API docs URL when running in Docker ([0d40ab8](https://github.com/odense-rpa/automation-server/commit/0d40ab8))

### Testing

- Validation tests for workitem update endpoint ([b31b20f](https://github.com/odense-rpa/automation-server/commit/b31b20f))
- Pagination tests for workitems with and without search ([9e427c4](https://github.com/odense-rpa/automation-server/commit/9e427c4))

---

## [0.1.0] - 2025-05-19

### Initial Release

- Core automation server functionality
- Basic Docker Compose setup for development
- Foundation for web-based automation management