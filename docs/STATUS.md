# Current Status

Last Updated

2026-08-13

---

## Quality Baseline

- Tests: 160 passed, 0 failed
- Ruff: PASS
- Mypy (strict): PASS — 441 source files

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

30%

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

10%

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
