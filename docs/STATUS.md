# Current Status

Last Updated

2026-08-13

---

## Quality Baseline

- Tests: 295 passed, 0 failed
- Ruff: PASS
- Mypy (strict): PASS — 470 source files

---

## Dependency Injection

Status

100%

Completed

- Container
- Providers
- Resolver
- Wiring
- Runtime Registration

---
## Runtime

Status

95%

Completed

- Execution Engine
- Execution Pipeline
- Coordinator
- Middleware
- Runtime Scheduler (session queue)

Remaining

- Distributed/priority scheduling refinements

---

## Workflow Engine

Status

95%

Completed

- Workflow / Graph / Nodes / Edges
- WorkflowRuntimePipeline (orchestration: validate -> schedule ->
  monitor -> resilience -> monitor.finish -> recovery -> report) —
  now inherits WorkflowRuntime and is the LIVE registered runtime
  (see "Critical fix" below)
- RuleBasedWorkflowScheduler (dependency-aware wave/batch scheduling)
- RuleBasedWorkflowExecutor (batch-parallel via asyncio.gather within
  a scheduling group; groups still run in order)
- DefaultWorkflowResilience (retry + failure classification, reuses
  a single SchedulingPlan across retries)
- RetryPolicy / RuleBasedRetryPolicy (exponential backoff)
- FailureClassifier / RuleBasedFailureClassifier
- DefaultWorkflowRecovery (checkpoint-based)
- DefaultWorkflowMonitor now opens a real ExecutionTrace/TraceSpan
  through the shared Tracing service (previously only a disconnected
  flat WorkflowTrace)
- WorkflowRuntimePipeline logs through context.logger at every
  lifecycle stage (started/scheduled/executed/recovery/finished)
- WorkflowEventBus, WorkflowExecutionContext
- Removed: orphaned legacy executor.py/scheduler.py/result.py trio
  (duplicate class names, unused) and default_workflow_runtime.py
  (superseded, see below)

### Critical fix this session

`WorkflowService` — the actual live service the rest of the system
calls — was wired to `DefaultWorkflowRuntime`, a bare
scheduler-then-executor runtime with **no monitoring, no resilience/
retry, no recovery, and no event bus**. `WorkflowRuntimePipeline`
(everything above) was fully built and fully tested but never
actually ran in production. Fixed by:

- Making `WorkflowRuntimePipeline` inherit `WorkflowRuntime`
- Registering it (not `DefaultWorkflowRuntime`) as the container's
  `WorkflowRuntime` implementation in `workflow_services.py`
- Fixing `KernelBootstrap`: `Tracing` was constructed but never
  registered in the container, and was registered too late (after
  `WorkflowService` had already resolved) — moved earlier
- Deleting `default_workflow_runtime.py` (no longer referenced
  anywhere)
- `WorkflowService`'s standalone fallback (used when constructed
  outside the DI container, e.g. in isolated tests) now builds a
  fully wired `WorkflowRuntimePipeline` instead of the old bare
  runtime, so that path is never quietly weaker than the DI path

Remaining

- Checkpoint replay / partial recovery / resumption
- Circuit breakers, adaptive retry, timeout/cancellation policies
- Event bus has zero subscribers (WorkflowEventHistory /
  WorkflowEventListener exist but nothing subscribes them — would
  need an async wiring point, e.g. WorkflowService.on_start())

---
## Tasks

Status

60%

Completed

- Task base class (execute() lifecycle: cancellation check -> RUNNING
  -> run() -> COMPLETED/FAILED, with task.started/completed/failed
  events published throughout)
- TaskQueue (priority heap, FIFO within a priority tier), TaskExecutor,
  TaskScheduler, TaskPipeline (queue+scheduler wrapper), TaskWorker
  (background polling loop primitive, available but not auto-started)
- PlaceholderTask, ToolTask, RuleBasedTaskFactory
- New: TaskService — Tasks previously had no service and was never
  registered in the container at all (unlike Tool/Agent/Workflow).
  Built TaskService following the same pattern as the other three,
  registered it in `register_runtime_services()`, and wired it into
  `KernelBootstrap`, `ServiceLocator`, and `Application` alongside
  the existing three services
- Verified end-to-end via a live bootstrap run: submit a task through
  `bootstrap.task_service`, run it, get a real `TaskResult` back
- Deleted 8 empty duplicate-name stub files (task_context.py,
  task_executor.py, task_queue.py, task_result.py, task_scheduler.py,
  task_status.py, ids.py, task_id.py) — same clutter pattern seen in
  workflows/runtime, harmless here since they were empty, but same
  landmine shape as the earlier real bugs
- tests/tasks/ added (was empty/nonexistent before this session):
  queue ordering, scheduler, service lifecycle, bootstrap wiring

### Bug fixed this session (same class, found proactively)

`TaskScheduler.__init__` used `queue or TaskQueue()`. `TaskQueue`
defines `__len__`, so an injected-but-empty queue would be silently
discarded — the identical bug fixed in `AgentManager` and
`ToolManager`. Fixed with an explicit `is None` check before it could
cause a live failure (nothing yet resolves `TaskQueue` independently
the way `create_agent_factory()` does for `AgentRegistry`, so this
was a landmine, not yet an active bug — same as the `ToolManager` fix).

Remaining

- `backend/agents/execution/` (engine, scheduler, runner, retry,
  checkpoint, session) is entirely empty stub files — a
  higher-level orchestration layer above tasks that doesn't exist yet
- `TaskWorker` (continuous background polling) is built but not
  wired into `TaskService.on_start()` — deliberately left on-demand
  (`submit()` + `run_all()`) to match the synchronous, non-background
  pattern the other three services use; revisit if background
  processing is actually needed
- No concrete tasks exist yet beyond `PlaceholderTask`/`ToolTask` —
  `RuleBasedTaskFactory` resolves every capability to a placeholder

---

## Agents

Status

55%

Completed

- Agent base class (reason -> plan -> optimize -> compile -> execute,
  state transitions, experience recording on success/failure)
- AgentRegistry, AgentManager, AgentFactory
- PlanningAgent (concrete built-in agent) + RuleBasedAgentPlanner
- AgentContext, Goal, AgentResult, AgentState
- Verified end-to-end: bootstrap -> agent_service -> manager.execute()
  -> reasoning pipeline -> planning -> optimization -> compilation ->
  workflow execution now genuinely runs (previously did not, see
  critical fix below)
- tests/agents/, tests/bootstrap/ now have real coverage (both were
  empty stub files before this session — zero lines of test code
  existed for the composition root or for AgentManager)

### Critical fix this session

`AgentService` — the live service everything calls — booted with
**zero registered agents**, every time, silently. Root causes (two
separate bugs, both in the same class as the earlier WorkflowRuntime
fix):

1. `KernelBootstrap.__init__` resolved `AgentService` before
   `register_agents()` / `create_agent_factory()` ever ran, so
   `AgentService` auto-constructed its own private, disconnected,
   empty `AgentManager`. Fixed by moving agent registration +
   built-in agent construction before `AgentService` is resolved.
2. Even after fixing (1), agents still didn't show up:
   `AgentManager.__init__` used `registry or AgentRegistry()`.
   `AgentRegistry` defines `__len__`, so an injected-but-*empty*
   registry evaluates as falsy in Python and was silently discarded
   in favor of a brand-new, disconnected registry — even though DI
   had correctly injected the right (shared, singleton) one. Fixed
   by switching to an explicit `is None` check. Found the identical
   latent bug in `ToolManager` (currently harmless, since nothing
   else resolves `ToolRegistry` independently yet) and fixed it
   proactively too.

Confirmed via a live end-to-end run: agent count went from 0 -> 1
("planning"), and `manager.execute(agent="planning", goal=...)` ran
the full pipeline through to a real (correctly-failing-on-unknown-
capability) `AgentResult`, proving the whole chain — reasoning,
planning, optimization, compilation, workflow execution, experience
recording — is actually wired end-to-end for the first time.

Remaining

- Only one concrete agent exists (PlanningAgent). browser/, desktop/,
  memory/, reviewer/, vision/ agent subpackages are empty stubs
  (`__init__.py` only)
- backend/agents/execution/ (engine, scheduler, runner, retry,
  checkpoint, session) is entirely empty stub files
- No test coverage yet for the "unknown capability" failure path or
  for Agent.execute()'s success path with a goal that resolves to a
  real registered tool

---

## Memory

Status

50%

Completed

- MemoryEntry, MemoryQuery, MemoryResult, MemoryService,
  ExperienceRecorder, ExecutionMemory (all as before)
- `AgentService.execute()` persistence wiring (previous session)
- New this session — real semantic search, not just persistence:
  - `HashingEmbeddingProvider`: concrete `EmbeddingProvider` using
    feature hashing (the "hashing trick" — same technique behind
    scikit-learn's `HashingVectorizer`). Deterministic, fully local,
    no API key or network access needed. Produces normalized
    fixed-dimension vectors from shared vocabulary.
  - `InMemoryVectorStore`: concrete `VectorStore` — brute-force
    cosine-similarity search over stored (entry, embedding) pairs
  - `VectorMemory` (previously a documented-but-empty placeholder)
    now actually embeds every stored entry and answers `query()` via
    `SemanticSearch` (embed query -> cosine similarity search)
    instead of substring matching
  - Registered as the live `MemoryStore` implementation in
    `register_runtime_services()`: `EmbeddingProvider` ->
    `HashingEmbeddingProvider`, `VectorStore` -> `InMemoryVectorStore`,
    `MemoryStore` -> `VectorMemory`, following the exact same
    swap-the-registered-implementation pattern already used for
    `WorkflowRuntime` -> `WorkflowRuntimePipeline`
- Verified end-to-end via a live bootstrap run: stored entries with
  varying vocabulary overlap, queried with a related-but-not-identical
  phrase, confirmed entries sharing vocabulary ranked above an
  unrelated entry, confirmed `MemoryService.provider` is the exact
  same `VectorMemory` singleton the container resolves for
  `MemoryStore`
- tests/memory/ added: `HashingEmbeddingProvider` (determinism,
  dimensions, normalization, empty text, similarity ordering),
  `InMemoryVectorStore` (ranking, limit, add_many, remove/clear),
  `VectorMemory` (ranking, limit, delete/clear cascading to the
  vector index, diagnostics), plus a bootstrap-level regression test

### Important limitation — be honest about what this actually does

`HashingEmbeddingProvider` captures **shared vocabulary** (literal
token overlap), not true semantic/synonym understanding. A query for
"feline resting near a bright window" will NOT rank highly against
"the cat sat on the warm windowsill" — none of those words overlap,
so cosine similarity is near zero regardless of the obvious semantic
relationship a real embedding model would catch. This was verified
directly: an early smoke test using synonym-heavy phrasing produced
nonsensical rankings until reworded to share actual words, which then
worked correctly and predictably. This is a known, expected property
of hashing-trick embeddings, not a bug — but it means "semantic
search" here means "lexical/keyword search with fuzzy matching and
ranking," not the model-backed retrieval a production system would
eventually want. `EmbeddingProvider` is registered behind its
abstraction specifically so a real model-backed provider (OpenAI,
SentenceTransformers, Ollama, etc.) can be swapped in later without
touching `VectorMemory`, `SemanticSearch`, or `MemoryService`.

Remaining

- Swap `HashingEmbeddingProvider` for a real model-backed provider
  when true semantic/synonym understanding is needed
- `MemoryRegistry` (multi-provider registry), `EpisodicMemory`,
  `MemoryConsolidator`, `MemoryRanker`, `MemoryImportance` — still
  fully built but referenced nowhere outside their own files
- No memory retrieval happens before an agent plans — experience is
  persisted and semantically queryable, but nothing yet calls
  `memory_service.query()` to feed past experience back into
  planning/reasoning
- `AgentMemory` (`backend/core/agents/memory.py`) is a separate,
  unrelated key/value scratch class not used by `AgentContext` at
  all — likely leftover from an earlier design; still untouched
  since nothing references it either way

---

## Browser Runtime

Status

80%

Completed — config wiring finished, real multi-page scraping added
this session, on top of last session's first real implementation

- Design goal (per project owner): Playwright does the actual
  browser work deterministically — no LLM call per action — to keep
  token cost low. A separate LLM-driven provider (browser_use,
  already partially scaffolded in browser_use_provider.py /
  browser_use_adapter.py) is intended to be incorporated later,
  behind the same BrowserProvider abstraction, for tasks that
  genuinely need autonomous "figure this unfamiliar page out"
  behavior.
- `PlaywrightBrowserProvider`: concrete `BrowserProvider` covering
  navigate/back/forward/refresh, click/type/press/scroll,
  screenshot/content/text_content/current_url/title, wait_for,
  upload, download, extract_links, extract_structured. Lazy-starts
  the actual Chromium process on first use, not at construction/
  registration time.
- `BrowserSessionManager`: owns one lazily-created default session,
  reused across a sequence of tool calls so navigate -> click ->
  extract-text all act on the same page.
- 13 browser tools (`backend/tools/browser/*_tool.py`): navigate,
  click, fill, press_key, scroll, extract_text, extract_links,
  extract_structured, scrape, screenshot, wait, upload_file,
  download. Each is a thin, deterministic wrapper: one tool call in,
  one Playwright action out, no LLM involved in between.
  `extract_text` returns clean visible text (not raw HTML) and
  `screenshot` returns base64-encoded PNG, both chosen specifically
  to minimize what an LLM has to parse/pay for downstream.
- Config wiring closed out this session: found a *third* parallel
  `BrowserConfig` (`EngineConfig.browser`, a dataclass populated by
  the engine's own config loading) that never reached the
  provider — `PlaywrightBrowserProvider` always silently used
  hardcoded defaults regardless of what was configured. Added
  `BrowserConfig.from_engine_config()` and wired it through
  `BuiltinToolFactory`, so real engine config now actually reaches
  Playwright. (The separate pydantic `BrowserSettings` under
  `backend/app/config/sections/browser/` is still unconnected — see
  Remaining.)
- New this session — genuine multi-page scraping ("any site", per
  project owner's stated frequent use case):
  - Extended `BrowserProvider` with `extract_links()` and
    `extract_structured()` — generic DOM extraction (title,
    headings, visible text, links, images, tables) that works on
    any page's markup, no site-specific selectors needed.
  - New `backend/core/scraping/`: `WebScraper` (deterministic crawl
    orchestrator — no LLM call per page), `PaginationStrategy`
    abstraction with two implementations —
    `NextLinkPaginationStrategy` (generic: matches `rel="next"` or
    "Next"/"older"/chevron-style link text) and
    `UrlPatternPaginationStrategy` (for `?page={n}`-style sites).
    Handles max_pages cutoff, cycle detection (site links back to an
    already-visited page), and navigation/extraction failures
    without crashing the crawl.
  - New `browser_scrape` tool: one tool call crawls up to N pages
    and returns all structured data — an agent pays for one decision
    ("scrape this site, up to N pages") instead of one decision per
    page, which is the core token-cost win being asked for. Also
    added standalone `browser_extract_links` /
    `browser_extract_structured` tools for single-page use.
- Fixed a real resource leak found via live testing (previous
  session): `ToolService.on_stop()` never closed the browser: fixed
  by closing the session and stopping the provider in `on_stop()`.
- Verified live through the real DI container, this session: (1)
  navigated a real multi-page site (books.toscrape.com) 3 pages deep
  via generic next-link detection, zero site-specific config; (2)
  `extract_links`/`extract_structured` against example.com returned
  correct real data (title, links, headings, iana.org link found).
- tests/browser/ and new tests/scraping/ (previously nonexistent):
  `FakeBrowserProvider` for fast tool-layer tests, `BrowserSession
  Manager` lifecycle tests, 9 real-Chromium integration tests
  (including the two new extraction methods), and — critically —
  `WebScraper` crawl-loop tests against a scripted fake provider
  covering max_pages cutoff, cycle detection, and both navigation-
  and extraction-failure handling.

Remaining

- `browser_use_provider.py` / `browser_use_adapter.py` already exist
  with substantial code but are not yet wired to anything — the
  deliberately deferred "incorporate browser-use later" piece
- Multi-session support (BrowserSessionManager only tracks one
  default session; `WebScraper.scrape()` opens/closes its own
  session per call when none is supplied, but nothing runs multiple
  scrapes concurrently yet)
- No selector-discovery / accessibility-tree helper tools (an agent
  must already know the CSS selector it wants to click/fill —
  extract_structured/extract_links help here but don't replace it)
- The pydantic `BrowserSettings` under
  `backend/app/config/sections/browser/` (env-var driven,
  Launch/Context/Downloads/Tracing/Video/Screenshots/Recovery) is
  still a separate, unconnected config path from the
  `EngineConfig.browser` dataclass that's now actually wired —
  three near-duplicate `BrowserConfig`-shaped things total in this
  codebase, one of which (this one) is still fully orphaned
- No rate-limiting/politeness delay by default in `WebScraper`
  beyond the optional `delay_seconds` a caller can pass explicitly

---

## Desktop Runtime

Status

65%

Completed — first real implementation this session (was empty stub
folders: `backend/agents/desktop/`, `backend/services/desktop/`)

- Design direction (per project owner): both structured, UI-Automation-
  based control (find elements by name/automation ID/control type,
  like a CSS selector) AND coordinate-based fallback control, for
  general-purpose automation of "almost any desktop app" — not
  limited to a fixed set of known apps.
- New dependencies: `pywinauto` (Windows UI Automation) and
  `pyautogui` + `pillow` (coordinate-based mouse/keyboard/screenshot
  fallback), added to `requirements.txt`.
- `DesktopProvider` abstraction (mirrors `BrowserProvider`): window/
  app management (list_windows, connect_window, launch), structured
  element interaction (click_element, type_into_element,
  get_element_text, extract_structured), coordinate-based fallback
  (click_at, move_to, drag, scroll_at), global keyboard (type_text,
  press_key), and screenshot/current_window_title.
- `PywinautoDesktopProvider`: concrete implementation. Every call
  runs through `asyncio.to_thread()` since pywinauto/pyautogui are
  synchronous libraries, unlike Playwright's native async API.
- `extract_structured()` is the desktop equivalent of the browser
  subsystem's generic DOM extraction: dumps every control in the
  connected window's UI tree (type, name, automation ID, bounding
  rectangle) without needing to know the app's layout ahead of time.
- `DesktopSessionManager`: owns one lazily-created default session,
  mirroring `BrowserSessionManager`.
- 14 desktop tools (`backend/tools/desktop/*_tool.py`, all built
  from scratch this session): list_windows, connect_window,
  launch_app, click_element, type_into_element, get_element_text,
  extract_structured, click_at, move_mouse, drag, scroll_at,
  type_text, press_key, screenshot.
- Wired into `BuiltinToolFactory`/`ToolService` alongside the browser
  tools (30 tools total now registered). `ToolService.on_stop()`
  updated to also close the desktop session and stop its provider on
  shutdown, matching the browser cleanup fix from a previous session.

### Real-world issue found and fixed via live testing

`launch()`'s first implementation matched the newly launched
process's window by PID (`Desktop().windows(process=pid)`). Verified
against real Notepad: **failed every time** — Windows 11's packaged
Notepad launches through a shim/launcher process whose PID never
matches the actual window-owning process's PID, so PID-based matching
silently found nothing and timed out. Fixed by diffing window handles
before and after launch instead of matching by PID — works regardless
of how indirectly a given app's process actually ends up owning its
window. This is exactly the kind of thing that would have shipped
broken without live-testing against a real app rather than trusting
the implementation because it type-checked.

Verified live end-to-end through the real DI container: launched a
real Notepad instance, typed real text into its Document control via
structured element interaction, extracted its real UI tree (38
controls) and confirmed the title bar reflected the typed text
(`*Hello from the desktop runtime - Notepad`), captured a real
screenshot, and shut down cleanly.

tests/desktop/ added (previously nonexistent): a `FakeDesktopProvider`
test double for fast argument-validation/delegation tests across all
14 tools plus session-manager lifecycle tests, and — not mocked — 9
integration tests that launch real Notepad and drive it for real
(launch+type, extract_structured, screenshot PNG-signature check,
list_windows, connect_window by title pattern, click+type, launching
an unknown executable, acting without a connected window, start()
idempotency). One test initially failed due to a stray pre-existing
Notepad window (the user's own, left open from earlier manual API
exploration) confusing the window-diffing logic in `launch()` — fixed
by adding a before-test cleanup step, not by changing the
implementation, since the underlying diffing logic was correct.

Remaining

- Config wiring: unlike Browser Runtime, there's no `EngineConfig.
  desktop` section yet, so `DesktopConfig` always uses hardcoded
  defaults regardless of engine configuration
- Multi-session support (same as Browser Runtime: one default
  session tracked; the abstraction supports more, nothing above it
  uses that yet)
- No image/template-matching helper (a common PyAutoGUI pattern:
  "find this icon on screen and click it") — only raw coordinate
  actions and structured element matching exist right now
- `element_info.control_type` in `extract_structured()`'s output is
  whatever pywinauto's UIA backend reports as a raw string (e.g.
  "Button", "Edit", "Document") — no normalization/mapping layer
  over it yet
- No OCR — the original project handoff mentioned OCR/vision for
  cases where neither structured access nor known coordinates work;
  not built this session
- macOS/Linux desktop automation: `PywinautoDesktopProvider` is
  Windows-only by nature (pywinauto + the win32-flavored parts of
  pyautogui); the `DesktopProvider` abstraction itself is
  platform-neutral, but no macOS/Linux implementation exists

---

## Infrastructure

Status

20%

---
