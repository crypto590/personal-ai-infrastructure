# Self-Optimizing Agent Patterns for Mastra

Based on [AutoAgent](https://github.com/kevinrgu/autoagent) — the first open source library for autonomously improving agents. Patterns extracted from the actual implementation and mapped to Mastra's agent/workflow primitives.

## Architecture: How AutoAgent Actually Works

AutoAgent is not a framework — it's a constraint system. The entire mutable surface is a single file with module-level constants. A meta-agent (Claude Code on the host) edits the file, rebuilds a container, reruns a task suite, reads a results ledger, and decides keep/discard. That's the whole loop.

The key insight for Mastra: **the power comes from the constraints, not the code.**

---

## Pattern 1: Fixed Boundary — Mutable Config vs Immutable Adapter

AutoAgent splits its agent file at a marked comment. Everything above = mutable (meta-agent can edit). Everything below = immutable (Harbor adapter, never touched).

### How AutoAgent Does It

```python
# AGENT CONFIG — meta-agent modifies this section
SYSTEM_PROMPT = """..."""
CUSTOM_TOOLS = []
SUBAGENTS = None
MODEL = "haiku"
MAX_TURNS = 30

# ============================================================================
# FIXED ADAPTER BOUNDARY: do not modify unless the human explicitly asks.
# ============================================================================
class AutoAgent(BaseAgent): ...  # immutable harness
```

### Mastra Translation

Separate the mutable agent config from the immutable execution harness:

```typescript
// ─── MUTABLE CONFIG (meta-agent edits this) ─────────────────────────
interface AgentConfig {
  instructions: string;
  model: string;
  tools: Record<string, Tool>;
  maxSteps: number;
  thinkingBudget?: number;
}

const config: AgentConfig = {
  instructions: `You are a specialist in [domain]...`,
  model: "anthropic/claude-sonnet-4-5",
  tools: { /* domain tools */ },
  maxSteps: 30,
};

// ─── FIXED BOUNDARY (never modified by meta-agent) ──────────────────
function buildTaskAgent(cfg: AgentConfig): Agent {
  return new Agent({
    name: "task-agent",
    model: cfg.model,
    instructions: cfg.instructions,
    tools: cfg.tools,
  });
}
```

The meta-agent mutates the `AgentConfig` object — never the agent construction logic. Store configs in Mastra storage (Postgres/LibSQL) so you have a history of every version.

```typescript
const mutateConfig = createTool({
  id: "mutate-agent-config",
  description: "Apply a targeted change to the task agent's config",
  inputSchema: z.object({
    field: z.enum(["instructions", "model", "tools", "maxSteps"]),
    change: z.string().describe("What to change and why"),
    newValue: z.any(),
  }),
  execute: async ({ context }) => {
    // Store previous config version before mutating
    // This creates the results ledger equivalent
    const prevConfig = await storage.get("current-config");
    await storage.set(`config-history/${Date.now()}`, prevConfig);
    await storage.set("current-config", { ...prevConfig, [context.field]: context.newValue });
    return { applied: true, field: context.field };
  },
});
```

---

## Pattern 2: Hill-Climbing Protocol

AutoAgent's `program.md` defines the entire optimization loop. The rules are:

1. **Baseline first** — Run the full suite before changing anything. You need a score to beat.
2. **One change at a time** — Never batch mutations. You can't attribute improvement if you changed 3 things.
3. **Keep/discard based on `passed` count** — Not average score. Binary pass count is the primary metric.
4. **Simplicity as tiebreaker** — Same `passed` count + simpler code = keep the simpler version.
5. **Value discarded runs** — Failed experiments reveal which tasks regressed and what capabilities are missing.
6. **NEVER STOP** — The loop runs indefinitely until the human stops it.

### Mastra Translation

```typescript
const hillClimb = new Workflow({
  name: "hill-climbing-optimization",
  triggerSchema: z.object({
    taskSuite: z.array(z.object({ id: z.string(), input: z.any(), verifier: z.function() })),
    maxIterations: z.number().default(100),
  }),
});

// Step 1: Establish baseline
const baseline = new Step({
  id: "baseline",
  execute: async ({ context }) => {
    const config = await storage.get("current-config");
    const agent = buildTaskAgent(config);
    const results = await runSuite(agent, context.triggerData.taskSuite);
    const passed = results.filter((r) => r.passed).length;
    await storage.set("baseline", { config, passed, results });
    return { passed, total: results.length };
  },
});

// Step 2: Meta-agent proposes ONE change
const propose = new Step({
  id: "propose-single-change",
  execute: async ({ context }) => {
    const baseline = await storage.get("baseline");
    const traces = await storage.get("latest-traces");
    const result = await metaAgent.generate([{
      role: "user",
      content: `Current score: ${baseline.passed}/${baseline.results.length}
        
        Failed task traces:
        ${JSON.stringify(traces.filter((t) => !t.passed))}
        
        Propose exactly ONE change to the agent config.
        Explain WHY this change addresses a class of failures (not a single task).
        
        TOOL DESIGN > PROMPT TUNING. Adding a specialized tool reduces
        failure modes more reliably than rewriting instructions.
        
        Overfitting test: "If this exact task disappeared, would this
        still be a worthwhile improvement?" If no, reject it.`,
    }]);
    return { proposal: result.text };
  },
});

// Step 3: Apply change and re-run
const evaluate = new Step({
  id: "evaluate",
  execute: async ({ context }) => {
    const newConfig = await storage.get("current-config");
    const agent = buildTaskAgent(newConfig);
    const results = await runSuite(agent, context.triggerData.taskSuite);
    const passed = results.filter((r) => r.passed).length;
    return { passed, total: results.length, results };
  },
});

// Step 4: Keep or discard
const decide = new Step({
  id: "keep-or-discard",
  execute: async ({ context }) => {
    const baseline = await storage.get("baseline");
    const evaluation = context.getStepResult("evaluate");
    
    if (evaluation.passed > baseline.passed) {
      // Improved — keep and update baseline
      await storage.set("baseline", { passed: evaluation.passed, results: evaluation.results });
      await appendLedger({ status: "keep", passed: evaluation.passed, description: "..." });
      return { decision: "keep" };
    } else if (evaluation.passed === baseline.passed) {
      // Tie — keep only if simpler (fewer instructions, fewer tools)
      const simpler = isSimpler(await storage.get("current-config"), baseline.config);
      if (simpler) {
        await appendLedger({ status: "keep", passed: evaluation.passed, description: "simpler, same score" });
        return { decision: "keep-simpler" };
      }
      await rollbackConfig();
      await appendLedger({ status: "discard", passed: evaluation.passed, description: "no improvement" });
      return { decision: "discard" };
    } else {
      // Regressed — rollback
      await rollbackConfig();
      await appendLedger({ status: "discard", passed: evaluation.passed, description: "regression" });
      return { decision: "discard" };
    }
  },
});

hillClimb
  .step(baseline)
  .then(propose)
  .then(evaluate)
  .then(decide)
  // Loop back to propose for next iteration
  .commit();
```

---

## Pattern 3: ATIF Trajectory Capture

AutoAgent uses ATIF (Agent Trajectory Interface Format) to serialize every agent execution — full step-by-step traces with tool calls, observations, and reasoning.

### AutoAgent's ATIF Schema

```json
{
  "schema_version": "ATIF-v1.6",
  "session_id": "...",
  "agent": { "name": "autoagent", "version": "0.1.0", "model_name": "claude-sonnet-4-5" },
  "steps": [
    {
      "step_id": 1,
      "timestamp": "...",
      "source": "agent",
      "message": "Tool: run_shell",
      "tool_calls": [{ "tool_call_id": "...", "function_name": "run_shell", "arguments": {} }],
      "observation": { "results": [{ "source_call_id": "...", "content": "..." }] }
    }
  ],
  "final_metrics": {
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_cost_usd": null,
    "total_steps": 0,
    "extra": { "duration_ms": 0, "num_turns": 0 }
  }
}
```

Key detail: AutoAgent tracks **pending tool calls by ID** and pairs them back when results arrive. This is the matching pattern.

### Mastra Translation

```typescript
import { createTool } from "@mastra/core/tools";
import { z } from "zod";

// ATIF step schema
const atifStepSchema = z.object({
  stepId: z.number(),
  timestamp: z.string(),
  source: z.enum(["agent", "user", "system"]),
  message: z.string(),
  toolCalls: z.array(z.object({
    toolCallId: z.string(),
    functionName: z.string(),
    arguments: z.record(z.any()),
  })).optional(),
  observation: z.object({
    results: z.array(z.object({
      sourceCallId: z.string(),
      content: z.string(),
    })),
  }).optional(),
  reasoning: z.string().optional(), // extended thinking content
});

const atifTraceSchema = z.object({
  schemaVersion: z.literal("ATIF-v1.6"),
  sessionId: z.string(),
  agent: z.object({ name: z.string(), model: z.string() }),
  steps: z.array(atifStepSchema),
  finalMetrics: z.object({
    totalPromptTokens: z.number(),
    totalCompletionTokens: z.number(),
    totalCostUsd: z.number().nullable(),
    totalSteps: z.number(),
    durationMs: z.number(),
  }),
  outcome: z.enum(["success", "partial", "failure"]),
});

// Wrap any agent execution to produce an ATIF trace
async function executeWithTrace(
  agent: Agent,
  messages: CoreMessage[],
  taskId: string,
): Promise<{ result: GenerateReturn; trace: z.infer<typeof atifTraceSchema> }> {
  const startTime = Date.now();
  const result = await agent.generate(messages);

  // Build ATIF trace from result
  // Mastra's generate() returns steps with tool calls — map to ATIF format
  const steps = result.steps?.map((step, i) => ({
    stepId: i + 1,
    timestamp: new Date().toISOString(),
    source: "agent" as const,
    message: step.toolCalls?.[0]
      ? `Tool: ${step.toolCalls[0].toolName}`
      : step.text?.slice(0, 100) ?? "",
    toolCalls: step.toolCalls?.map((tc) => ({
      toolCallId: tc.toolCallId,
      functionName: tc.toolName,
      arguments: tc.args,
    })),
    observation: step.toolResults
      ? { results: step.toolResults.map((tr) => ({
          sourceCallId: tr.toolCallId,
          content: JSON.stringify(tr.result),
        })) }
      : undefined,
  })) ?? [];

  const trace = {
    schemaVersion: "ATIF-v1.6" as const,
    sessionId: taskId,
    agent: { name: agent.name, model: agent.model.toString() },
    steps,
    finalMetrics: {
      totalPromptTokens: result.usage?.promptTokens ?? 0,
      totalCompletionTokens: result.usage?.completionTokens ?? 0,
      totalCostUsd: null,
      totalSteps: steps.length,
      durationMs: Date.now() - startTime,
    },
    outcome: "success" as const, // determined by verifier
  };

  return { result, trace };
}
```

**Why traces matter**: AutoAgent found that scores without trajectories produce dramatically lower improvement rates. The meta-agent needs to see *how* the task-agent reasoned, not just *whether* it passed.

---

## Pattern 4: Verification Sub-Agent

AutoAgent's `program.md` explicitly calls out a verification sub-agent as a high-leverage improvement. In AutoAgent, this is implemented via `agent.as_tool()`:

```python
verifier = Agent(name="verifier", instructions="Check output against requirements...")
tools.append(verifier.as_tool(tool_name="verify_output", tool_description="..."))
```

### Mastra Translation

```typescript
// Verification agent as a tool available to the task agent
const verifierAgent = new Agent({
  name: "verifier",
  model: "anthropic/claude-sonnet-4-5", // same model — model empathy
  instructions: `You verify outputs against task requirements.
    Check for: correctness, completeness, hallucinations, edge cases.
    Be harsh. Return { passed: boolean, issues: string[] }`,
});

// Make verifier available as a tool to the task agent
const verifyOutput = createTool({
  id: "verify-output",
  description: "Have the verifier agent check your output before finalizing",
  inputSchema: z.object({
    taskRequirements: z.string(),
    producedOutput: z.string(),
  }),
  outputSchema: z.object({ passed: z.boolean(), issues: z.array(z.string()) }),
  execute: async ({ context }) => {
    const result = await verifierAgent.generate([{
      role: "user",
      content: `Requirements: ${context.taskRequirements}\n\nOutput: ${context.producedOutput}\n\nVerify.`,
    }]);
    return JSON.parse(result.text);
  },
});

// Add to task agent's tool set
const taskAgent = new Agent({
  name: "task-agent",
  model: "anthropic/claude-sonnet-4-5",
  instructions: `...
    ALWAYS call verify-output before finalizing your answer.`,
  tools: { verifyOutput, /* other tools */ },
});
```

---

## Pattern 5: Results Ledger

AutoAgent tracks every iteration in a TSV ledger:

```
commit  avg_score  passed  task_scores  cost_usd  status  description
abc123  0.34       20/58   [1,0,1,...]  $2.40     keep    added file-check tool
def456  0.31       18/58   [1,0,0,...]  $2.10     discard prompt rewrite regressed
```

### Mastra Translation

```typescript
const ledgerSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  configVersion: z.string(),
  avgScore: z.number(),
  passed: z.string(), // "20/58" format
  costUsd: z.number().nullable(),
  status: z.enum(["keep", "discard", "crash"]),
  description: z.string(),
  // What changed vs previous
  delta: z.object({
    newlySolved: z.array(z.string()),  // task IDs that now pass
    regressed: z.array(z.string()),     // task IDs that now fail
    unchanged: z.number(),
  }),
});

// Append after every evaluation run
async function appendLedger(entry: z.infer<typeof ledgerSchema>) {
  const ledger = await storage.get("results-ledger") ?? [];
  ledger.push(entry);
  await storage.set("results-ledger", ledger);
}
```

The ledger is critical for the meta-agent — it sees the full history of what was tried, what worked, and what regressed.

---

## Pattern 6: Overfitting Prevention

AutoAgent uses one concrete heuristic:

> **"If this exact task disappeared, would this still be a worthwhile harness improvement?"**
> If the answer is no, it is probably overfitting.

Additional structural constraints from `program.md`:

- **`passed` count, not per-task score** — Single-task wins don't change the aggregate
- **Simplicity is a tiebreaker** — Same `passed` + simpler code = keep the simpler version
- **Prefer class fixes over task fixes** — "Fix a class of failures, not a single task"
- **Discarded runs have value** — They reveal missing capabilities and regression patterns

### Meta-Agent Anti-Overfit Instructions

```typescript
const META_AGENT_CONSTRAINTS = `
OPTIMIZATION RULES:
1. Propose exactly ONE change per iteration. Never batch.
2. Tool design > prompt tuning. Adding a specialized tool reduces
   failure modes more reliably than rewriting instructions.
3. Overfitting test: "If this task disappeared, would this still
   be worthwhile?" If no, reject the change.
4. Never add "make sure to include X" where X maps to a rubric item.
5. Prefer changes that fix a CLASS of failures, not a single task.
6. Same score + simpler code = keep the simpler version.
7. Value failed experiments — they reveal what's missing.
`;
```

---

## Pattern 7: Tool Design Over Prompt Tuning

From `program.md`:

> "Prompt tuning alone has diminishing returns. Adding specialized tools is a high-leverage improvement axis."

When the meta-agent analyzes failure traces, it should prefer creating new tools over rewriting instructions:

```typescript
const createToolFromFailure = createTool({
  id: "design-new-tool",
  description: "Design a new tool to address a class of task-agent failures",
  inputSchema: z.object({
    failurePattern: z.string().describe("The class of failures this tool addresses"),
    toolSpec: z.object({
      id: z.string(),
      description: z.string(),
      inputSchema: z.record(z.any()),
      implementation: z.string().describe("TypeScript implementation of execute()"),
    }),
  }),
  execute: async ({ context }) => {
    // Meta-agent designs a tool, which gets added to the task agent's config
    const config = await storage.get("current-config");
    // Add tool spec to config.tools — will be built on next agent construction
    config.pendingTools = [...(config.pendingTools ?? []), context.toolSpec];
    await storage.set("current-config", config);
    return { added: context.toolSpec.id };
  },
});
```

---

## Composing Patterns: Complete Self-Optimizing Pipeline

```
┌─────────────────────────────────────────────────┐
│ 1. BASELINE                                      │
│    Build agent from current config               │
│    Run full task suite                           │
│    Record passed count + all traces (ATIF)       │
├─────────────────────────────────────────────────┤
│ 2. ANALYZE (meta-agent)                          │
│    Read failure traces (not just scores)         │
│    Identify failure CLASSES, not instances        │
│    Check results ledger for past attempts        │
├─────────────────────────────────────────────────┤
│ 3. PROPOSE (meta-agent)                          │
│    Exactly ONE change                            │
│    Prefer tool design over prompt tuning         │
│    Apply overfitting heuristic                   │
├─────────────────────────────────────────────────┤
│ 4. EVALUATE                                      │
│    Apply change to config                        │
│    Rebuild agent, rerun full suite               │
│    Capture new traces                            │
├─────────────────────────────────────────────────┤
│ 5. DECIDE                                        │
│    passed↑ → keep, update baseline               │
│    passed= + simpler → keep                      │
│    passed= or passed↓ → discard, rollback        │
│    Record in ledger (keep/discard + delta)       │
├─────────────────────────────────────────────────┤
│ 6. LOOP → back to step 2                        │
│    Never stop. Human decides when to halt.       │
└─────────────────────────────────────────────────┘
```

---

## Key Principles (from actual implementation)

| Principle | AutoAgent Rule | Mastra Application |
|---|---|---|
| Fixed boundary | Mutable config above a comment line, immutable adapter below | Separate `AgentConfig` type from `buildTaskAgent()` |
| One change at a time | Never batch mutations — can't attribute improvement | Each workflow iteration proposes exactly one change |
| Tool design > prompts | "Prompt tuning has diminishing returns" | Meta-agent has `design-new-tool` capability |
| Model empathy | Same model for meta + task agent | Both use `anthropic/claude-sonnet-4-5` |
| Traces over scores | ATIF trajectory capture on every run | `executeWithTrace()` wrapper returns full ATIF |
| Simplicity tiebreaker | Same passed + simpler = keep simpler | `isSimpler()` check in decide step |
| Overfitting heuristic | "If this task disappeared, would this still be worthwhile?" | Baked into meta-agent constraints |
| Ledger everything | TSV with commit, passed, status, description | Structured ledger in Mastra storage |
| Value failures | Discarded runs reveal missing capabilities | Ledger tracks `newlySolved` and `regressed` per run |
| Never stop | Loop runs until human halts it | Workflow loops back to analyze step |

## When to Use

- **Building agent fleets** — Many workflows to automate, can't hand-tune each one
- **Production agents** — Need continuous improvement without manual intervention
- **Complex multi-step tasks** — Where single-shot execution has high failure rates
- **Evaluation-driven development** — When you have clear success criteria to optimize against

## References

- [AutoAgent GitHub](https://github.com/kevinrgu/autoagent)
- [AutoAgent `program.md`](https://github.com/kevinrgu/autoagent/blob/main/program.md) — The complete meta-agent directive
- [AutoAgent `agent-claude.py`](https://github.com/kevinrgu/autoagent/blob/main/agent-claude.py) — Claude SDK harness with fixed boundary
- [Harbor Framework](https://github.com/harbor-framework/harbor) — Evaluation infrastructure AutoAgent uses
- [ATIF Spec](https://github.com/kevinrgu/autoagent/blob/main/agent.py) — Trajectory serialization format
