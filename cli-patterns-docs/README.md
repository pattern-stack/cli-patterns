# CLI Patterns Documentation

## Overview

This directory contains the complete documentation for the CLI Patterns system - a type-safe, wizard-based command-line interface framework designed for Pattern Stack projects.

## Documentation Structure

```
cli-patterns-docs/
├── README.md                 # This file
├── PRD.md                   # Product Requirements Document
├── adrs/                    # Architecture Decision Records
│   ├── ADR-001-stateless-execution.md
│   ├── ADR-002-hybrid-definitions.md
│   ├── ADR-003-subprocess-execution.md
│   ├── ADR-004-branch-ui-protocol.md
│   └── ADR-005-type-system.md
├── session-logs/            # Development session logs
│   ├── 001-context-gathering.md
│   └── 002-synthesis-refinement.md
└── implementation/          # Implementation guides (future)
```

## Key Documents

### Product Requirements Document (PRD)
[PRD.md](./PRD.md) - Complete specification for CLI Patterns MVP including:
- Vision and goals
- Key features
- Architecture overview
- User stories
- Technical requirements
- Success metrics

### Architecture Decision Records (ADRs)
Documenting key architectural decisions:
- [ADR-001](./adrs/ADR-001-stateless-execution.md): Stateless Execution Model
- [ADR-002](./adrs/ADR-002-hybrid-definitions.md): Hybrid Definition System
- [ADR-003](./adrs/ADR-003-subprocess-execution.md): Subprocess for Shell Execution
- [ADR-004](./adrs/ADR-004-branch-ui-protocol.md): Branch-Level UI Protocol
- [ADR-005](./adrs/ADR-005-type-system.md): Type System Design

### Session Logs
Development process documentation:
- [Session 001](./session-logs/001-context-gathering.md): Context Gathering Phase
- [Session 002](./session-logs/002-synthesis-refinement.md): Synthesis and Refinement Phase

## Development Phases

### Phase 1: Context Gathering ✅
- Reviewed Pattern Stack architecture
- Studied existing CLI implementations
- Identified patterns and principles

### Phase 2: Synthesis/Refinement ✅
- Combined original spec with Pattern Stack context
- Created refined architecture
- Documented decisions in ADRs

### Phase 3: Execution (Next)
- Implement core type system
- Build definition loaders
- Create execution engine
- Develop CLI entry point

## Quick Start

### Example YAML Wizard
```yaml
name: quick-setup
version: 1.0.0
entry_branch: main

branches:
  - id: main
    name: Quick Setup
    actions:
      - id: check
        type: bash
        command: echo "System OK"
```

### Example Python Wizard
```python
@wizard(name="advanced-setup", version="1.0.0")
class AdvancedWizard:
    @branch(id="main", entry=True)
    class MainBranch:
        @action(id="validate")
        async def validate(self, state: SessionState) -> ActionResult:
            return ActionResult(success=True)
```

## Core Concepts

### 1. Wizard-Based Navigation
Tree-structured command organization with branches, actions, options, and menus.

### 2. Type Safety
Full MyPy strict mode compliance with semantic types, discriminated unions, and runtime protocols.

### 3. Hybrid Definitions
Support for both YAML (simple) and Python (complex) wizard definitions.

### 4. Stateless Execution
Each run is independent with optional session persistence.

### 5. Protocol-Based Design
Clear boundaries between core logic and implementations (UI, storage, execution).

## Design Principles

1. **Sophisticated Simplicity**: Complex type system, simple runtime behavior
2. **Type Safety First**: Everything fully typed with validation
3. **Stateless by Default**: Persistence is optional
4. **Protocol Boundaries**: Clean interfaces between layers
5. **Future-Proof**: Designed for eventual Rust migration

## Implementation Status

- ✅ Requirements documented
- ✅ Architecture designed
- ✅ Decisions recorded
- ⏳ Implementation pending
- ⏳ Testing pending
- ⏳ Documentation pending

## Contributing

When contributing to CLI Patterns:
1. Follow the type system defined in the spec
2. Maintain MyPy strict mode compliance
3. Document significant decisions as ADRs
4. Keep session logs for major development efforts
5. Ensure all code aligns with documented principles

## References

- [Pattern Stack Architecture](../pattern_stack/atoms/shared/INFRASTRUCTURE-SUBSYSTEMS.md)
- [Atomic Architecture v2.5.1](../.claude/ai-docs/architecture-v2.5.1.md)
- [Original CLI Patterns Spec](../.claude/specs/cli-pattern-plan.md)

---

**Version**: 1.0.0
**Last Updated**: 2024-01-18
**Status**: Design Complete, Implementation Pending