# Current Status

Last Updated

2026-08-13

---

## Quality Baseline

- Tests: 178 passed, 0 failed
- Ruff: PASS
- Mypy (strict): PASS — 434 source files

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

35%

Completed

- MemoryEntry (immutable record), MemoryQuery, MemoryResult
- MemoryStore (in-memory provider: store/query/delete/clear/size,
  substring search)
- MemoryService (thin service wrapper around a MemoryProvider) —
  already registered in the container before this session
- ExperienceRecorder (converts agent execution outcomes into
  MemoryEntry objects)
- ExecutionMemory (per-run scratch space: retrieved + generated
  memories, variables)
- Wired for the first time this session: `AgentService.execute()` —
  a new method, now the recommended entry point instead of calling
  `manager.execute()` directly — auto-attaches an `ExecutionMemory`
  to the context before running, and persists everything the agent
  generated to `MemoryService` afterward. Verified end-to-end via a
  live bootstrap run: executed a goal, then queried MemoryService
  and got the generated experience back.

### Gap found and fixed this session

The entire experience-recording pipeline was built and exercised
(`Agent.execute()` already called `context.memory.remember(...)` on
success/failure) but **nothing ever persisted it anywhere**.
`ExecutionMemory.remember()` only appends to a local in-memory list;
its own docstring says "Persistence is handled later by
MemoryService" — but nothing did that. `AgentManager.execute()`
passed `context` straight through untouched, and no caller anywhere
in the codebase ever attached an `ExecutionMemory` to `AgentContext`
in the first place. So every goal ever executed silently generated
zero durable memory, indistinguishable from working correctly since
nothing raised an error.

Fixed by adding `AgentService.execute()`, which:
1. auto-creates `ExecutionMemory()` on the context if not already
   present (so recording during the run has somewhere to land)
2. after execution, flushes every generated `MemoryEntry` through
   `MemoryService.store()`

This does not change `Agent`/`AgentManager` at all — `Agent.execute()`
already did the right thing on its side; the gap was purely in
"nobody constructs the context correctly and nobody flushes it
afterward," which is exactly what a service-layer orchestration
method is for (matching how `TaskService`/`ToolService`/
`WorkflowService` each own their subsystem's top-level orchestration).

Remaining

- `MemoryRegistry` (multi-provider registry), `VectorMemory`,
  `VectorStore`, `EpisodicMemory`, `SemanticSearch`,
  `EmbeddingService`/`EmbeddingProvider`, `MemoryConsolidator`,
  `MemoryRanker`, `MemoryImportance` — all fully built but referenced
  nowhere outside their own files. `MemoryService` only ever uses the
  single flat `MemoryStore` (substring search); none of the
  vector/semantic/episodic infrastructure is connected to it
- `MemoryStore.query()` is substring matching only — no ranking,
  importance weighting, or semantic search despite those components
  existing
- No memory retrieval happens before an agent plans — experience is
  now persisted, but nothing yet calls `memory_service.query()` to
  feed past experience back into planning/reasoning
- `AgentMemory` (`backend/core/agents/memory.py`) is a separate,
  unrelated key/value scratch class that is not used by
  `AgentContext` at all (`AgentContext.memory` is `ExecutionMemory`,
  a different type) — likely leftover from an earlier design; not
  touched this session since nothing references it either way

---

## Browser Runtime

Status

15%

---

## Desktop Runtime

Status

5%

---

## Infrastructure

Status

20%

---
