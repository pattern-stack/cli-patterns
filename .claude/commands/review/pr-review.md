---
description: Comprehensively review pull requests following Pattern Stack standards with TDD validation
argument-hint: [pr-number] or leave blank to review current branch's PR
allowed-tools: Task, Bash, Read, MultiEdit, Glob, Grep, WebFetch
---

# Pattern Stack PR Review Process

## Reference Context
First, load these key files to understand the project context:
- @CLAUDE.md - Project overview and development commands
- @.claude/commands/plan/refine-issue.md - How we refine and plan issues
- @Makefile - Available test and validation commands
- @src/cli_patterns/core/ - Core type definitions and protocols

For backend-patterns reviews, also load:
- @../backend-patterns/CLAUDE.md - Backend patterns architecture
- @../backend-patterns/.claude/commands/atomic-commit-workflow.md - Commit standards

You are conducting a comprehensive pull request review for the Pattern Stack ecosystem. This review process ensures code quality, architectural compliance, and alignment with our development methodology.

## Phase 1: Context Discovery & Analysis

### Step 1.1: Identify the PR
$ARGUMENTS

If a PR number was provided, fetch details:
```bash
gh pr view $1
```

If no PR specified, find current branch's PR:
```bash
gh pr status
```

### Step 1.2: Understand the Task Context
Use task patterns to understand what was implemented:
```bash
# Get the Linear issue details from PR description or branch name
tp show [issue-id]
```

Also review:
- @cli-patterns-docs/adrs/ - Any relevant ADRs for architectural decisions
- @tests/ - Test structure to understand testing patterns

Look for:
- Original requirements and acceptance criteria
- Related issues in the hierarchy (parent epics, dependencies)
- Comments showing refinement decisions
- Any ADRs referenced

### Step 1.3: Fetch and Analyze Changes
Launch a subagent to comprehensively analyze the changes:

**Task Tool Usage:**
```
Task: "Analyze PR changes comprehensively"
Prompt: "
1. Use 'gh pr diff [pr-number]' to get the full diff
2. Identify all files changed and categorize them by:
   - Layer (for backend-patterns: atoms/features/molecules/organisms)
   - Component (for cli-patterns: core/execution/ui/parser)
   - Type (implementation/tests/docs)
3. Create a change summary including:
   - Total lines added/removed
   - Test file ratio (test files vs implementation files)
   - Component boundaries crossed
4. Check commit history with 'git log --oneline [base]..HEAD'
5. Verify atomic commit practices
"
Subagent: general-purpose
```

## Phase 2: Multi-Dimensional Review

### Step 2.1: Architecture Compliance Review
Launch architecture review agent:

**Task Tool Usage:**
```
Task: "Review architectural compliance"
Prompt: "
Review the PR for Pattern Stack architectural compliance:

FOR BACKEND-PATTERNS:
1. Verify Atomic Architecture v2.1 compliance:
   - Unidirectional dependencies (Organisms → Molecules → Features → Atoms)
   - Features handle ONE model only
   - No cross-feature imports
   - Clean boundaries (no business logic in models, no permissions in services)
2. Check import directions using 'make validate' if available
3. Verify infrastructure subsystem usage (cache, rate_limit patterns)

FOR CLI-PATTERNS:
1. Verify protocol-based architecture:
   - Review @src/cli_patterns/core/types.py for semantic types (BranchId, ActionId, OptionKey)
   - Check @src/cli_patterns/core/protocols.py for protocol contracts
   - Stateless execution maintained
2. Check MyPy strict mode compliance with 'make type-check'
3. Verify design token usage - review @src/cli_patterns/ui/design/tokens.py

Report any architectural violations found.
"
Subagent: general-purpose
```

### Step 2.2: Test Coverage & TDD Validation
Launch test validation agent:

**Task Tool Usage:**
```
Task: "Validate test coverage and TDD practices"
Prompt: "
1. Run full test suite: 'make test'
2. Check coverage: 'make test-coverage'
3. Verify 80% minimum coverage for backend-patterns
4. For each implementation file, verify corresponding test file exists
5. Run tests in isolation to verify no interdependencies:
   - Unit tests: 'make test-unit'
   - Integration tests: 'make test-integration'
6. Check for:
   - Proper use of test markers (@pytest.mark.unit, @pytest.mark.integration)
   - Test fixtures and factories usage
   - Edge case coverage
   - Performance benchmarks where applicable
7. Verify tests were written BEFORE implementation (check commit order)
"
Subagent: general-purpose
```

### Step 2.3: Code Quality & Standards Review
Launch code quality agent:

**Task Tool Usage:**
```
Task: "Review code quality and standards"
Prompt: "
Perform comprehensive code quality checks:

1. Linting: 'make lint' or 'make ci'
2. Formatting: Verify 'make format' produces no changes
3. Type checking: 'make typecheck' passes without errors
4. For Python code verify:
   - Type hints on all functions
   - Async-first design where appropriate
   - Proper error handling with structured exceptions
   - No hardcoded secrets or credentials
5. For TypeScript/JavaScript:
   - Proper typing (no 'any' without justification)
   - Consistent import style
6. Check documentation:
   - Docstrings for public APIs
   - Updated README if new features added
   - CLAUDE.md updates if development patterns changed
"
Subagent: general-purpose
```

### Step 2.4: Pattern Stack Integration Opportunities
Launch pattern enhancement agent:

**Task Tool Usage:**
```
Task: "Identify Pattern Stack enhancement opportunities"
Prompt: "
Review the code for opportunities to enhance with Pattern Stack packages:

1. Check if any implemented patterns could use:
   - pattern_stack.atoms.cache for caching needs
   - pattern_stack.atoms.security for auth/JWT
   - pattern_stack.atoms.validators for field validation
   - pattern_stack.core.loader for auto-discovery
   - pattern_stack.core.registry for component tracking

2. For CLI implementations, check if they could benefit from:
   - Composable parser system for command handling
   - Design token system for consistent theming
   - Protocol-based implementations for extensibility

3. Identify any code that reimplements existing Pattern Stack functionality

4. Look for opportunities to extract reusable patterns into:
   - Atoms (domain-agnostic utilities)
   - Features (data services)
   - Molecules (domain entities)

Report enhancement opportunities without being prescriptive.
"
Subagent: general-purpose
```

### Step 2.5: Security & Performance Review
Launch security and performance agent:

**Task Tool Usage:**
```
Task: "Review security and performance implications"
Prompt: "
Conduct security and performance review:

SECURITY:
1. Check for exposed credentials or API keys
2. Verify proper input validation and sanitization
3. Review authentication/authorization logic
4. Check for SQL injection vulnerabilities
5. Verify secure password handling (if applicable)
6. Check for proper error messages (no stack traces to users)

PERFORMANCE:
1. Look for N+1 query problems
2. Check for unnecessary database calls
3. Verify proper use of caching where appropriate
4. Check for memory leaks or unbounded growth
5. Review async/await usage for I/O operations
6. Run benchmarks if available: 'make test-benchmark'

Report any concerns found.
"
Subagent: general-purpose
```

## Phase 3: Atomic Commit Validation

### Step 3.1: Review Commit Granularity
Analyze the commit history for atomic commit practices:

```bash
# Get detailed commit history
git log --stat [base-branch]..HEAD

# Check each commit builds independently
for commit in $(git rev-list [base-branch]..HEAD); do
    git checkout $commit
    make test  # or appropriate test command
done
```

Verify:
- Each commit represents ONE logical change
- Commits maintain working state (build and tests pass)
- Proper commit message format: `type(scope): description (ticket)`
- No "WIP" or "fix typo" commits (should be squashed)

## Phase 4: Collaborative Feedback

### Step 4.1: Synthesize Findings
Compile all agent findings into structured feedback:

1. **Critical Issues** (must fix before merge)
   - Architectural violations
   - Failing tests or insufficient coverage
   - Security vulnerabilities
   - Breaking changes without migration path

2. **Important Suggestions** (should address)
   - Code quality improvements
   - Performance optimizations
   - Missing documentation
   - Pattern Stack enhancement opportunities

3. **Minor Notes** (nice to have)
   - Style improvements
   - Refactoring opportunities
   - Additional test cases

### Step 4.2: Create Review Comments
Based on the findings, create constructive feedback:

```markdown
## PR Review for #[PR-NUMBER]: [PR Title]

### ✅ Strengths
- [What was done well]
- [Good patterns observed]

### 🔴 Critical Issues
[List critical issues that block merge]

### 🟡 Suggestions for Improvement
[List important but non-blocking items]

### 💡 Pattern Stack Opportunities
[Opportunities to leverage Pattern Stack packages]

### 📊 Metrics
- Test Coverage: X%
- Files Changed: X
- Tests Added: X
- Atomic Commits: X/Y follow standards

### 📝 Detailed Feedback
[Specific file-level comments]
```

### Step 4.3: Provide Actionable Next Steps
Create a clear action plan:

```markdown
## Recommended Actions

1. **Immediate fixes needed:**
   - [ ] Fix failing test in test_parser.py
   - [ ] Add missing type hints in executor.py
   - [ ] Update coverage to meet 80% minimum

2. **Before final approval:**
   - [ ] Add integration tests for new parser pipeline
   - [ ] Update CLAUDE.md with new development pattern
   - [ ] Consider extracting validation logic to atoms layer

3. **Future improvements (create tickets):**
   - [ ] Implement caching for expensive operations
   - [ ] Add performance benchmarks
```

## Phase 5: Documentation & Learning

### Step 5.1: Update Project Knowledge
If the review revealed important patterns or decisions:

1. Create or update ADRs for architectural decisions
2. Update CLAUDE.md with new patterns or anti-patterns discovered
3. Add examples to documentation if novel solutions were implemented

### Step 5.2: Track Review Patterns
Document recurring issues for team improvement:

```bash
# Add comment to Linear ticket about review findings
tp comment [issue-id] "PR Review completed. Key findings: ..."
```

## Important Review Principles

### Be Constructive
- Acknowledge good work before criticizing
- Provide specific examples and solutions
- Explain the "why" behind suggestions

### Consider Context
- Understand the task requirements from Linear
- Review previous refinement decisions
- Consider timeline and scope constraints

### Think System-Wide
- How does this change affect other components?
- Does it maintain backward compatibility?
- Will it scale with future requirements?

### Foster Learning
- Explain Pattern Stack patterns when suggesting changes
- Share relevant documentation links
- Provide code examples for complex suggestions

## Review Checklist

Before completing the review, ensure:
- [ ] All tests pass locally
- [ ] Architecture compliance verified
- [ ] Test coverage meets requirements
- [ ] Code quality checks pass
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Documentation updated as needed
- [ ] Commit history follows atomic practices
- [ ] Pattern Stack opportunities identified
- [ ] Linear ticket will be updated with findings

## Completion

After review:
1. Post review comments on GitHub PR
2. Update Linear ticket with review summary
3. Set appropriate PR labels (needs-work, approved, etc.)
4. Notify PR author of review completion

Remember: The goal is not just to find problems, but to ensure the code advances Pattern Stack's goals of composability, type safety, and maintainability while helping the team grow and improve.