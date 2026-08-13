# Roadmap

Current Development Plan

---

## Phase 1

Foundation

- [x] Dependency Injection
- [x] Runtime
- [x] Middleware
- [x] Execution Engine
- [x] Coordinator

---

## Phase 2

Workflow Engine

- [x] Workflow Executor (RuleBasedWorkflowExecutor)
- [x] Scheduler (RuleBasedWorkflowScheduler — dependency-aware batching)
- [x] Validation (graph cycle validation)
- [x] Retry Policy (RuleBasedRetryPolicy + FailureClassifier)
- [x] Resilience / Recovery (DefaultWorkflowResilience, DefaultWorkflowRecovery, checkpoints)
- [ ] Planner (workflow-level planner beyond task graph construction)
- [ ] Parallel Execution (scheduler groups are parallel-safe; executor
      still runs each group's tasks sequentially — see STATUS.md)

---

## Phase 3

Task Engine

- [ ] Task Executor
- [ ] Task Retry
- [ ] Task Cancellation
- [ ] Task Timeout

---

## Phase 4

Memory

- [ ] Working Memory
- [ ] Long-term Memory
- [ ] Knowledge Store
- [ ] Semantic Search

---

## Phase 5

Tool System

- [ ] Tool Registry
- [ ] Tool Execution
- [ ] Tool Discovery
- [ ] Permissions

---

## Phase 6

Browser Runtime

- [ ] Browser Manager
- [ ] DOM Interaction
- [ ] Navigation
- [ ] Downloads
- [ ] Authentication

---

## Phase 7

Desktop Runtime

- [ ] Windows
- [ ] Linux
- [ ] macOS

---

## Phase 8

Multi-Agent Runtime

- [ ] Agent Collaboration
- [ ] Delegation
- [ ] Shared Memory
- [ ] Coordination

---

## Phase 9

Production

- [ ] REST API
- [ ] Dashboard
- [ ] Monitoring
- [ ] Deployment