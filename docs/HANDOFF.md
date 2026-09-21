# Autonomy Engine — Project Handoff

Last updated: 2026-09-20

This is the working handoff for the autonomy-engine project. It
supersedes the original ChatGPT handoff (which is still accurate as
*architectural intent*, but its status claims are long out of date).

Treat the repository as the source of truth and this document as
context.

---

## 1. What this is

A production-grade autonomous AI execution platform in Python. Give
an agent a task; it reasons, plans, executes actions across
browser/desktop/tools, maintains state and memory, recovers from
failures, and produces a reliable result.

Built as a **kernel/runtime platform**, not one giant agent class.
Every subsystem sits behind an explicit contract:

```
Request -> Coordinator -> Reasoning -> Planning -> Workflow
        -> Scheduler -> Runtime Pipeline -> Browser/Desktop/Tools
```

Stack: FastAPI, Playwright, pywinauto + PyAutoGUI, LangChain/LangGraph
(kept out of core domain objects), ruff, mypy (strict), pytest.

---

## 2. Current state

### Quality baseline

| Metric | Value |
|---|---|
| Tests | 325 passing (last full run) |
| Ruff | clean |
| Mypy (strict) | clean, 464 source files |

**Caveat:** the most recent work (Tasks capability resolution) was
verified against scoped suites only — Tasks + Tools (38 passed) and
dependent suites workflows/agents/capabilities/planning (131 passed)
— at the user's request. **Run the full suite before merging**, since
that change touched `ToolExecutor`, which is shared infrastructure.

### Subsystem status

| Subsystem | % | State |
|---|---|---|
| Dependency Injection | 100 | Done |
| Runtime | 95 | Done |
| Workflow Engine | 95 | Done |
| Tasks | 85 | Solid |
| Browser Runtime | 80 | Solid |
| Agents | 75 | Solid |
| Desktop Runtime | 65 | Working |
| Memory | 50 | Working, lexical-only search |
| Infrastructure | 45 | Filesystem done; persistence not started |

Roughly **~78% overall**. Every subsystem has been live-verified, not
just unit-tested.

---

## 3. Git state — READ THIS FIRST

`origin/main` is at `0f76672`. **Seven commits are unmerged**, and
the branches are **stacked** — each was cut from the previous branch
rather than from `main`:

```
d903bca feat(tasks): resolve capabilities to real tools
d5a14bf feat(infrastructure): filesystem sandbox + CLI entry point
be3548b feat(agents): wire agents to the real tool ecosystem
292566f feat(desktop): implement Desktop Runtime from scratch
8050672 feat(browser): wire real engine config into Playwright provider
caa5d35 feat(browser): implement Browser Runtime with Playwright
aeb6ff5 feat(memory): wire real semantic search
```

Consequences:

- The open PRs are **not independent**. Merging them out of order, or
  merging one and expecting the others to shrink, will not behave
  the way separate feature PRs normally do.
- The newest branch (`feat/tasks-capability-resolution`) contains
  **all seven** commits.

Simplest resolution: merge `feat/tasks-capability-resolution` into
`main` once (it carries everything), then delete the other six
branches. Alternatively merge oldest-to-newest in the order listed
above, bottom-up.

---

## 4. How to run it

### CLI (`run.py`) — the normal way

```powershell
cd C:\Users\Windows\Desktop\autonomy-engine

# list all 37 registered tools
.venv\Scripts\python.exe run.py tool --list

# call a tool directly (recommended for real work)
.venv\Scripts\python.exe run.py tool browser_scrape --args-file scrape_args.json

# natural-language goal through the planning agent (experimental)
.venv\Scripts\python.exe run.py goal "navigate browser to a URL" --meta-file goal.json
```

**On Windows, always use `--args-file`, not `--args`.** PowerShell and
cmd both mangle inline JSON quoting badly enough that it is not worth
fighting.

Example `scrape_args.json`:

```json
{
  "url": "https://www.jumia.co.ke/smartphones/",
  "max_pages": 3
}
```

### HTTP API

`POST /agents/execute` exists on the FastAPI app. See
`examples/execute_goal.py`. Note: **no test coverage yet** — it was
picked up as pre-existing uncommitted work and verified only manually.

### Python

```python
import asyncio
from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.tools.context import ToolContext

async def main():
    bootstrap = KernelBootstrap()
    await bootstrap.runtime.start()
    tool = bootstrap.tool_service.registry.get("browser_scrape")
    result = await tool.execute(ToolContext(arguments={"url": "...", "max_pages": 3}))
    print(result.output)
    await bootstrap.runtime.stop()

asyncio.run(main())
```

### Checks

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check backend tests
.venv\Scripts\python.exe -m mypy backend
```

---

## 5. The single most important lesson: the recurring bug class

**Nearly every subsystem in this project had solid, well-tested code
that was never actually connected to anything that ran.** Tests
passed. Nothing errored. The features simply did not exist at
runtime. This happened seven-plus times and is the defining
characteristic of this codebase's history.

### Pattern A: the falsy-empty-collection footgun

```python
self._registry = registry or Registry()   # WRONG
self._registry = registry if registry is not None else Registry()  # RIGHT
```

Any class defining `__len__` is **falsy when empty**. An
injected-but-empty collection gets silently discarded and replaced
with a new, disconnected one. Since most registries are empty at
construction time (populated later in `on_start()`), `or` discarded
the correct object essentially every time.

Found and fixed in: `AgentManager`, `ToolManager`, `TaskScheduler`,
`ToolExecutor`. The `ToolExecutor` instance was the worst — it meant
**every single tool execution raised `ToolNotFoundError`**.

### Pattern B: resolution-order bugs

A service resolved from the DI container *before* its dependencies
were registered silently auto-constructs its own private, empty
version. Fixed in `KernelBootstrap` for `AgentService` (booted with
zero agents, every time) and `Tracing`.

### Pattern C: concrete dataclasses in DI

An unregistered **ABC** fails loudly. An unregistered **concrete
dataclass** does not — the container auto-constructs it, recursively
"resolving" its primitive fields, and bare `str()`/`bool()` succeed
trivially. Result: `encoding=''`, every bool `False`, real defaults
silently overridden. Fixed for `FilesystemConfig` by registering a
real instance.

### Pattern D: two halves that never met

Built, correct, tested — but nothing joined them:
- `CapabilityRegistry` existed but was never populated with the 37
  real tools → agents could not reach any tool
- `RuleBasedTaskFactory` returned a placeholder for every capability
  and was never constructed at all
- `ExecutionMemory.remember()` wrote to a throwaway list; nothing
  ever persisted it
- `WorkflowRuntimePipeline` (monitored, resilient, recoverable) was
  fully built while `WorkflowService` ran a bare fallback runtime

### The working rule that came out of this

**Never trust "it type-checks" or "tests pass" as evidence a feature
works.** Boot the real system through `KernelBootstrap`, call the
real entry point, and confirm real output. Every genuine bug above
was found that way and would have shipped otherwise.

---

## 6. Subsystem detail

### Workflow Engine (95%)
`WorkflowRuntimePipeline` orchestrates validate → schedule → monitor
→ resilience → recovery → report. Dependency-aware wave scheduling;
`RuleBasedWorkflowExecutor` runs a group's tasks concurrently via
`asyncio.gather`. Retry + failure classification reuse a single
`SchedulingPlan` across attempts.

Remaining: checkpoint replay/resumption, circuit breakers, adaptive
retry, timeout/cancellation policies. Event bus has zero subscribers.

### Browser Runtime (80%)
`PlaywrightBrowserProvider` + `BrowserSessionManager` + 13 tools.
Deterministic by design — **no LLM call per action** — to keep token
cost near zero.

Multi-page scraping: `WebScraper` + two pagination strategies
(`NextLinkPaginationStrategy`, `UrlPatternPaginationStrategy`) with
max-pages cutoff, cycle detection, and failure handling. One
`browser_scrape` call crawls N pages. Generic DOM extraction works
on any site, no per-site selectors. **Verified against real Jumia
and books.toscrape.com.**

Remaining: `browser_use_provider.py` / `browser_use_adapter.py`
already contain substantial code but are unwired — that is the
deliberately deferred "incorporate browser-use later" piece. Also:
multi-session support, selector discovery, and a third orphaned
`BrowserSettings` config path under `backend/app/config/sections/`.

### Desktop Runtime (65%)
`PywinautoDesktopProvider` (structured UI Automation) + PyAutoGUI
(coordinate fallback) + 14 tools. All sync calls wrapped in
`asyncio.to_thread()`.

Note: `launch()` matches windows by **handle diff before/after**, not
PID — Windows 11's packaged Notepad launches via a shim whose PID
never matches the window's owner, so PID matching failed every time.

Remaining: no `EngineConfig.desktop` section (hardcoded defaults), no
image/template matching, no OCR, Windows-only.

### Agents (75%)
`PlanningAgent` + `AgentManager`/`AgentRegistry`/`AgentFactory`.
`ToolCapabilityProvider` exposes all 37 tools as capabilities;
`RegistryAwareCapabilitySelector` keyword-matches a goal to a real
capability, falling back to the abstract placeholder set.
`goal.metadata` flows through as tool arguments.

Remaining: only one concrete agent exists. Keyword matching is token
overlap, **not intent understanding** — a goal must share literal
words with a tool's name/description. No argument extraction from
free text.

### Tasks (85%)
Queue (priority heap, FIFO within tier), executor, scheduler,
pipeline, worker. `RuleBasedTaskFactory` resolves a capability to a
real `ToolTask` when it matches a registered tool, else a
`PlaceholderTask`. `TaskService.create()` / `submit_capability()`.

Remaining: `TaskWorker` (background polling) is built but not wired
into `on_start()` — left on-demand deliberately.

### Memory (50%)
`VectorMemory` embeds every entry and answers queries via cosine
similarity. `AgentService.execute()` persists generated experience.

**Be honest about this one:** `HashingEmbeddingProvider` captures
**shared vocabulary, not meaning**. "feline" will not match "cat".
This is lexical/keyword search with ranking, not semantic retrieval.
The abstraction exists so a real model-backed provider can drop in.

Remaining: real embedding model; `MemoryRegistry`, `EpisodicMemory`,
`MemoryConsolidator`, `MemoryRanker` all built but unwired; no
retrieval feeds back into planning.

### Infrastructure (45%)
Filesystem: 8 sandboxed tools (workspace jail — no absolute paths, no
symlinks, every path resolved against the root). `run.py` CLI.

**Remaining — the biggest gap:** persistence. Everything is
in-memory-only. `InMemoryCheckpointStore` and `InMemoryVectorStore`
both vanish on process exit. A SQLite-backed implementation of each
(swapping the registered implementation, same pattern as
`MemoryStore` → `VectorMemory`) is the clear next task. Cache and
database are untouched by design — no consumer needs them.

---

## 7. Suggested next steps

1. **Resolve the branch situation** (section 3) and run the full
   suite before merging.
2. **SQLite persistence** — highest-value remaining work. Durable
   checkpoints and durable memory.
3. **A real embedding provider** — unlocks actual semantic memory.
4. **Structured product extraction** for scraping — the generic
   extractor returns raw link text; a typed name/price/rating
   extractor would make the Jumia use case much cleaner.
5. **Test coverage for `POST /agents/execute`.**
6. **Wire the workflow event bus** to its existing (unused)
   subscribers.

---

## 8. Working conventions

- Every optional injected dependency uses `is None`, never `or`.
- Swap implementations at the **container registration** level; keep
  abstractions untouched (`MemoryStore` → `VectorMemory`,
  `WorkflowRuntime` → `WorkflowRuntimePipeline`).
- New behavior subclasses existing behavior and falls back to it, so
  a change is a strict superset, never a regression.
- Deterministic "RuleBased" components by default; no LLM call in a
  hot loop. Token cost is an explicit design constraint.
- Conventional Commits. Atomic. No secrets.
- After meaningful changes: `ruff check backend tests`,
  `mypy backend`, `pytest`. A change is not done until all three are
  clean.
- Delete empty duplicate-name stub files on sight — several caused
  real shadowing bugs.
- **Live-verify through `KernelBootstrap` before claiming something
  works.**
