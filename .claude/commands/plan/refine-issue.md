---
description: Collaboratively refine and plan a development issue through iterative exploration
argument-hint: [issue-id] or leave blank to choose from available issues
allowed-tools: Bash(tp:*), Read, Write, MultiEdit, Glob, Grep, WebFetch
---

# Issue Refinement Process

You are beginning an iterative refinement session for a development issue. This is a collaborative exploration where you'll work with the user to deeply understand requirements, explore options, and make implementation decisions together.

## Phase 1: Context Gathering

### Step 1.1: Identify the Issue
$ARGUMENTS

If an issue ID was provided (e.g., CLI-8), use:
```bash
tp show $1
```

If no issue specified, show available work:
```bash
tp c
```

**Important:** Check the team context in the output. Use the correct team filter if needed (e.g., `teams: CLI`).

### Step 1.2: Read Related Issues
If there's a clear task hierarchy or related issues mentioned, read them to understand the broader context:
- Look for dependencies mentioned in the ticket
- Check for "blocked by" or "blocks" relationships
- Review any parent epics or related work

### Step 1.3: Explore Existing Code
Based on the issue context, explore relevant code:
- Use `Glob` to find related files
- Use `Read` to understand current implementation
- Look for patterns already established in the codebase

## Phase 2: Initial Understanding

### Step 2.1: Summarize Your Understanding
Present to the user:
1. **What you understand** the issue is asking for
2. **What questions** you have about requirements
3. **What context** you might be missing

**Be honest about uncertainties.** Say things like:
- "I'm not sure if this means X or Y..."
- "Should we consider..."
- "I notice the ticket mentions X but I don't see where that fits..."

### Step 2.2: Wait for User Input
**PAUSE HERE** - Let the user provide additional context, corrections, or guidance.

## Phase 3: Iterative Exploration

### Step 3.1: Present Options
Based on user feedback, present different approaches:

**Start simple and high-level:**
```
"So we could approach this in a few ways:

Option A: [Simple approach]
- Pros: Quick to implement, easy to understand
- Cons: Limited flexibility

Option B: [More complex approach]
- Pros: More powerful, extensible
- Cons: Takes longer, more complexity

What resonates with you?"
```

### Step 3.2: Drill Down Gradually
As the user expresses preferences, go deeper:
1. Start with conceptual choices
2. Move to architectural decisions
3. Then implementation details
4. Finally, specific code patterns

**Example progression:**
- "Should this be interactive or command-based?"
- "Would you prefer a class-based or functional approach?"
- "Should we use Python's shlex for parsing or write our own?"

### Step 3.3: Show Code Examples
When discussing options, provide small, concrete examples:
```python
# "Here's what Option A might look like:"
def simple_parse(input):
    return input.split()

# "Versus Option B:"
class Parser:
    def parse(self, input):
        # More sophisticated parsing
```

## Phase 4: Convergence

### Step 4.1: Confirm Understanding
Once you've explored options together, summarize:
- The approach you've agreed on
- Key decisions made
- Any remaining open questions

### Step 4.2: Create Refinement Plan
Write out a clear implementation plan with:
1. **Phases** - Logical chunks of work
2. **Components** - What needs to be built
3. **Examples** - How it will be used
4. **Acceptance Criteria** - How we'll know it's done

## Phase 5: Documentation

### Step 5.1: Create ADR if Needed
If you made significant architectural decisions, create an ADR:
```bash
Write cli-patterns-docs/adrs/ADR-XXX-[decision-name].md
```

Include:
- Context of the decision
- Options considered
- Decision made and rationale
- Consequences

### Step 5.2: Update the Issue
Add a comment to the issue (if using Linear/GitHub) summarizing:
- Decisions made during refinement
- Updated implementation plan
- Any new acceptance criteria
- Links to ADRs created

### Step 5.3: Update Project Documentation
If this refinement revealed important context:
- Update CLAUDE.md if it affects how to work with the codebase
- Add to relevant documentation
- Create examples if helpful

## Important Principles

### Go Slow
- Don't jump to implementation details
- Start with understanding the problem
- Build context gradually

### Be Collaborative
- Present options, don't prescribe solutions
- Ask "What do you think?" frequently
- Admit when you're unsure

### Think About the System
Remember: CLI Patterns is a system for building CLI systems. Consider:
- How this feature enables different interaction paradigms
- Whether components can be composable/reusable
- How different users might combine features

### Document Thinking
- Capture not just what was decided, but why
- Note alternatives considered
- Record constraints and trade-offs

## Example Session Flow

```
1. "Let me look at CLI-8... [reads ticket]"
2. "So this is about parsing commands. I see we currently have basic splitting. What kind of command styles do you envision supporting?"
3. [User explains]
4. "Interesting! So we need multiple paradigms. Let me show you some options..."
5. [Explore together]
6. "OK, so we're going with a composable parser system. Let me document this..."
7. [Create ADR, update issue]
```

## Completion Checklist

Before ending the refinement session, ensure:
- [ ] Issue requirements are clear
- [ ] Implementation approach is agreed upon
- [ ] Key decisions are documented in ADRs
- [ ] Issue is updated with refinement outcomes
- [ ] Any new context is added to project docs
- [ ] Next steps are clear

Remember: The goal is not just to refine the issue, but to build shared understanding through collaborative exploration.