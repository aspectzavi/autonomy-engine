# Autonomy Engine Architecture

> Source of Truth

This document defines the architecture of the Autonomy Engine.

Every subsystem must follow this document. When code and documentation
conflict, this document takes precedence until an architectural decision
record (ADR) updates it.

---

# Vision

Autonomy Engine is a production-grade autonomous AI operating system capable of:

- reasoning
- planning
- workflow generation
- browser automation
- desktop automation
- tool execution
- long-term memory
- multi-agent collaboration

The system is designed around clean architecture, dependency injection,
and event-driven execution.

---

# High-Level Architecture

```
                API
                 │
                 ▼
        Application Layer
                 │
                 ▼
             Runtime
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
 Workflow Engine      Agent System
      │                     │
      └──────────┬──────────┘
                 ▼
           Task Execution
                 │
                 ▼
           Tool Execution
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
 Browser Runtime      Desktop Runtime
```

---

# Layer Responsibilities

## backend/app

Application composition.

Responsibilities

- Dependency Injection
- Bootstrap
- Configuration
- Wiring
- Startup

Must NOT contain business logic.

---

## backend/core

Core autonomous intelligence.

Contains:

- Runtime
- Agents
- Planning
- Workflows
- Tasks
- Memory
- Tools
- Events
- Observability

Must not depend on infrastructure.

---

## backend/infrastructure

External integrations.

Contains

- Browser automation
- Desktop automation
- LLM providers
- Databases
- Storage
- Network

Infrastructure never contains business rules.

---

# Dependency Rules

Allowed

```
API
↓

Application
↓

Core
↓

Infrastructure
```

Forbidden

Infrastructure → Core

Agents → Browser

Tasks → Playwright

Everything must execute through Tools.

---

# Runtime

Execution flow

```
ExecutionRequest

↓

ExecutionPipeline

↓

Middleware

↓

ExecutionEngine

↓

RuntimeCoordinator

↓

WorkflowExecutor

↓

TaskExecutor

↓

ToolExecutor
```

---

# Workflow Engine

Workflow execution is graph-based.

NOT linear.

```
Workflow

↓

WorkflowGraph

↓

WorkflowNode

↓

WorkflowEdge
```

WorkflowExecutor executes nodes whose dependencies have completed.

---

# Agent System

Agents never execute tools directly.

Flow

```
Goal

↓

Planner

↓

Workflow

↓

Runtime

↓

Result
```

---

# Dependency Injection

The DI container is the only mechanism for service construction.

Rules

- constructor injection only
- no service locator pattern
- no global state
- singleton only when required

---

# Observability

Everything should emit:

- logs
- events
- traces

No subsystem is allowed to silently fail.

---

# Design Principles

- SOLID
- Composition over inheritance
- Dependency Injection
- Immutable data models
- Event-driven communication
- Async-first execution
- Testable components
- Clear ownership