# Multi-Agent Swarm System

> Level: Expert | File: `multi-agent-swarm.md`
> 
> Design and orchestration of AI agent swarms for parallel software development:
> task decomposition, inter-agent communication, conflict resolution, self-healing,
> and emergent behavior management.

---

## Table of Contents
1. [Swarm Architecture](#1-swarm-architecture)
2. [Agent Roles & Communication](#2-agent-roles--communication)
3. [Task Decomposition & Allocation](#3-task-decomposition--allocation)
4. [Inter-Agent Communication Protocol](#4-inter-agent-communication-protocol)
5. [Conflict Resolution & Consensus](#5-conflict-resolution--consensus)
6. [Self-Healing Agent](#6-self-healing-agent)
7. [Scalability: From 3 to 100 Agents](#7-scalability-from-3-to-100-agents)
8. [Quality Assurance in Swarms](#8-quality-assurance-in-swarms)
9. [Bounty System (L2 Escalation)](#9-bounty-system-l2-escalation)
10. [Telemetry & Observability](#10-telemetry--observability)

---

## 1. Swarm Architecture

### 1.1 Topology

```
High-Level Swarm:
┌─────────────────────────────────────────────────────────┐
│                     Orchestrator (Coordinator)              │
│  Task decomposition, quality gates, bounties              │
└──────┬──────────────┬──────────────┬────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ Frontend  │  │ Backend   │  │  Database  │
│  Agent    │  │  Agent    │  │   Agent    │
│ (React)   │  │ (API)     │  │ (Schema)   │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │               │              │
      └───────────────┼──────────────┘
                      │
              ┌───────┴───────┐
              │  Self-Healing │
              │    Agent      │
              │  (Diagnose +  │
              │   Auto-fix)   │
              └───────────────┘

Cross-cutting agents (run in parallel):
  ┌──────────────┐  ┌──────────┐  ┌──────────┐
  │  Test Agent  │  │Security  │  │  Docs    │
  │ (Unit+E2E)   │  │Agent     │  │  Agent   │
  └──────────────┘  └──────────┘  └──────────┘
```

### 1.2 Agent Types

| Role | Responsibility | Output | Parallelism |
|------|---------------|--------|-------------|
| **Orchestrator** | Task decomposition, quality gate, bounty dispatch | Task graph, acceptance verdict | Singleton |
| **Coding Agent** | Write implementation | Source code (files) | N (one per module) |
| **Test Agent** | Write and run tests | Test files + coverage report | N (one per module) |
| **Review Agent** | Code review + quality score | Review comments + score | N |
| **Security Agent** | Vulnerability scan, input validation | Security report | 1 (cross-cutting) |
| **Documentation Agent** | API docs, README, changelog | Doc files | 1 (aggregator) |
| **Self-Healing Agent** | Diagnose failures, generate fixes | Fix patches | 1 (reactive) |
| **Orchestration Agent** | Monitor progress, reassign tasks | Status reports | 1 (coordinator) |

### 1.3 Orchestrator State Machine

```
                    ┌─────────────┐
                    │  IDLE       │
                    └──────┬──────┘
                           │ New task arrives
                           ▼
                    ┌─────────────┐
                    │ DECOMPOSE   │  Break down PRD into subtasks
                    └──────┬──────┘
                           │ Task graph ready
                           ▼
                    ┌─────────────┐
              ┌────►│  ALLOCATE   │  Assign to coding agents
              │     └──────┬──────┘
              │            │ Agents dispatched
              │            ▼
              │     ┌─────────────┐
              │     │  EXECUTE    │  Agents work in parallel
              │     └──────┬──────┘
              │            │ Any agent completes
              │            ▼
              │     ┌─────────────┐
              │     │  VERIFY     │  Review + test gate
              │     └──────┬──────┘
              │         ╱       ╲
              │    Pass          Fail (<3)
              │      │              │
              │      ▼              ▼
              │  ┌────────┐  ┌──────────────┐
              │  │ MERGE  │  │ SELF-HEAL    │  Auto-fix attempt
              │  └────────┘  └──────┬───────┘
              │                     │
              │                Fail (>=3) → BOUNTY
              │                     │
              │                     ▼
              │              ┌──────────────┐
              └──────────────│ BOUNTY (L2)  │  Escalate to human
                             └──────────────┘
```

---

## 2. Agent Roles & Communication

### 2.1 Agent Contract

```typescript
interface Agent {
  id: string;
  role: AgentRole;
  status: 'idle' | 'working' | 'blocked' | 'done' | 'failed';
  capabilities: string[];
  context: AgentContext;
  
  // Core methods
  async acceptTask(task: Task): Promise<AcceptResult>;
  async execute(): Promise<ExecutionResult>;
  async reportProgress(): Promise<Progress>;
  async processMessage(msg: Message): Promise<void>;
}

interface AgentContext {
  workingDirectory: string;   // Isolated workspace per agent
  environment: string[];     // Language, framework, dependencies
  sharedMemory: string;      // Path to shared context file
  taskDefinition: Task;      // The task this agent owns
}
```

### 2.2 Shared Context Protocol

```typescript
// Every agent reads/writes to a shared context file
// Communication is file-system based (no need for complex RPC)

interface SharedContext {
  // Architecture decisions
  decisions: ArchitectureDecision[];
  
  // Current state of the codebase
  codebase: {
    files: CodeFile[];
    testFiles: CodeFile[];
    configFiles: CodeFile[];
  };
  
  // Known constraints
  constraints: Constraint[];
  
  // Blockers for other agents
  blockers: Blocker[];
  
  // Interface contracts
  contracts: Contract[];  // e.g., "Order API returns { id, total, status }"
}
```

### 2.3 Contract File (The Glue)

```
Every agent writes a CONTRACT.md into the shared directory:

# CONTRACT: Order Service API

## Endpoints
POST /api/v1/orders
  Request: { userId, items: [{ productId, quantity }] }
  Response: { id, status: "pending", total }
  Error: { error: { code, message } }

GET /api/v1/orders/:id
  Response: { id, userId, items, total, status, createdAt }

## Data Types
Order {
  id: string (ULID),
  userId: string,
  items: OrderItem[],
  total: Money,
  status: "pending" | "paid" | "shipped" | "cancelled",
  createdAt: ISO8601
}

## States
pending → paid → shipped
pending → cancelled

## Consumer Responsibilities
- Payment agent: after charging, POST /api/v1/orders/:id/pay
- Inventory agent: after shipping, POST /api/v1/orders/:id/ship
```

---

## 3. Task Decomposition & Allocation

### 3.1 Task Decomposition from PRD

```typescript
class TaskDecomposer {
  decompose(prd: PRDDocument): TaskGraph {
    const tasks: Task[] = [];
    
    // 1. Domain analysis
    const entities = this.extractEntities(prd);
    const useCases = this.extractUseCases(prd);
    
    // 2. Create tasks per bounded context
    for (const entity of entities) {
      tasks.push(this.createModelTask(entity));
    }
    for (const uc of useCases) {
      tasks.push(this.createUseCaseTask(uc));
    }
    
    // 3. Identify dependencies
    const graph = this.buildDependencyGraph(tasks);
    
    return graph;
  }
  
  private extractEntities(prd: PRDDocument): Entity[] {
    // Pattern: find nouns that persist (User, Order, Product)
    return prd.content
      .split('\n')
      .filter(line => line.match(/^(#|\*|-) \w+[Ee]ntity|Model|Table/))
      .map(/* ... NLP or regex extract */);
  }
}
```

### 3.2 Allocation Algorithm

```typescript
function allocateTasks(tasks: Task[], agents: Agent[]): AllocationPlan {
  // 1. Sort tasks by priority and dependencies
  const sorted = topologicalSort(tasks);
  
  // 2. Match tasks to best-fit agent
  const plan: AllocationPlan = { assignments: [] };
  
  for (const task of sorted) {
    const bestAgent = agents
      .filter(a => a.status === 'idle')
      .filter(a => a.capabilities.some(c => task.requires.includes(c)))
      .sort((a, b) => scoreAgent(a, task) - scoreAgent(b, task))
      .pop();  // worst score first (we want best, so pop)
    
    if (!bestAgent) {
      plan.pendingTasks.push(task);  // Queue for available agent
      continue;
    }
    
    plan.assignments.push({ agent: bestAgent.id, task: task.id });
  }
  
  return plan;
}

function scoreAgent(agent: Agent, task: Task): number {
  let score = 0;
  // Language match: +10
  if (task.language && agent.context.environment.includes(task.language)) score += 10;
  // Domain match: +5
  if (task.domain && agent.capabilities.includes(task.domain)) score += 5;
  // Current load: -load
  score -= agent.currentLoad;
  return score;
}
```

### 3.3 Task Template

```yaml
task:
  id: "task-004-order-api"
  type: "backend-endpoint"
  priority: 1
  dependsOn: ["task-001-order-model"]  # Must finish first
  estimatedEffort: "2h"
  maxAttempts: 3
  
  spec:
    endpoint: "POST /api/v1/orders"
    method: create
    description: |
      Create a new order from a user's cart.
      Accepts items array, calculates total from product prices.
      Returns order with "pending" status.
    contracts: 
      - "CONTRACT: Order Model"
      - "CONTRACT: Product Pricing"
    
    acceptance:
      - "Given valid cart, when POST /orders, returns 201 with order"
      - "Given empty cart, when POST /orders, returns 400"
      - "Given invalid product ID, when POST /orders, returns 404"
      - "Order total must equal sum (price * quantity) of all items"
    
    output:
      files:
        - "src/routes/orders.ts"
        - "src/controllers/orderController.ts"
      testFiles:
        - "tests/routes/orders.test.ts"
```

---

## 4. Inter-Agent Communication Protocol

### 4.1 Message Format

```typescript
interface Message {
  id: string;
  from: string;              // Agent ID
  to: string | 'broadcast';  // Recipient or all
  type: MessageType;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: number;
  
  // Payload by type
  payload: 
    | ContractChange     // "I changed the API contract"
    | Blocker           // "I'm stuck on this"
    | Question          // "How do you return this?"
    | Answer            // "Return { id, status }"
    | Status            // "I'm 70% done"
    | Error             // "My tests are failing"
    | MergeRequest      // "Ready for merge, please review"
    | HealthCheck;      // "Are you alive?"
}

type MessageType = 
  | 'contract_change'
  | 'blocker'
  | 'question' 
  | 'answer'
  | 'status'
  | 'error'
  | 'merge_request'
  | 'health_check';
```

### 4.2 Communication Rules

```
1. Agents do NOT talk directly to each other
   They communicate through the Shared Context (file-based)

2. Contract changes must be broadcast
   Any agent changing a shared interface, data type, or API signature
   MUST write to the shared context AND mark as `contract_change`

3. Blockers are escalated after 30 seconds
   Agent stuck → wait 30s → broadcast blocker
   If another agent doesn't unblock within 30s → Orchestrator intervenes

4. Health check every 60 seconds
   Agents MUST respond to health check within 5s
   Dead agent → Orchestrator reassigns task
```

### 4.3 File-Based Communication Implementation

```typescript
class FileBasedMessageBus implements MessageBus {
  private readonly basePath = '/tmp/swarm/messages/';
  
  async send(message: Message): Promise<void> {
    const path = `${this.basePath}/${message.to}/${message.id}.json`;
    await fs.writeFile(path, JSON.stringify(message));
  }
  
  async poll(agentId: string): Promise<Message[]> {
    const dir = `${this.basePath}/${agentId}/`;
    const files = await fs.readdir(dir);
    const messages = await Promise.all(
      files.map(f => fs.readFile(`${dir}/${f}`, 'utf-8').then(JSON.parse))
    );
    // Remove processed messages
    for (const f of files) await fs.unlink(`${dir}/${f}`);
    return messages;
  }
}
```

---

## 5. Conflict Resolution & Consensus

### 5.1 Types of Conflicts

```
Schema conflict:
  Agent A: "User model has email as required"
  Agent B: "User model has email as optional"
  → Both look at PRD → PRD says required → A wins

Interface conflict:
  Agent A: "Orders API returns { id, total }"
  Agent B expects: "Orders API returns { id, items, total }"
  → Check CONTRACT.md → If not defined, do minimum union

Code conflict:
  Both agents modify the same file (rare in well-decomposed tasks)
  → Orchestrator coordinates merge, runs diff, asks for conflict resolution
  
Priority conflict:
  Agent A needs Agent B's output but B is blocked
  → Orchestrator reprioritizes
```

### 5.2 Consensus Protocol

```typescript
class ConsensusResolver {
  async resolve(conflict: Conflict): Promise<Resolution> {
    // Step 1: Check PRD authority
    const prdAnswer = this.checkPRD(conflict);
    if (prdAnswer) return { ...prdAnswer, source: 'prd' };
    
    // Step 2: Check CONTRACT.md authority
    const contractAnswer = this.checkContract(conflict);
    if (contractAnswer) return { ...contractAnswer, source: 'contract' };
    
    // Step 3: Vote among agents
    const votes = await this.collectVotes(conflict, relevantAgents);
    const majority = this.findMajority(votes);
    if (majority) return { ...majority, source: 'vote' };
    
    // Step 4: Escalate to orchestrator default
    return { 
      resolution: this.defaultResolution(conflict),
      source: 'orchestrator_default'
    };
  }
  
  private checkPRD(conflict: Conflict): Resolution | null {
    // Heuristic: check if PRD text mentions this exact topic
    for (const [topic, text] of Object.entries(this.prd.topics)) {
      if (conflict.topic.includes(topic)) {
        return { resolution: text, confidence: 0.9 };
      }
    }
    return null;
  }
}
```

### 5.3 Orchestrator Conflict Mediation

```typescript
// Orchestrator's mediation process
async function mediateConflict(conflict: Conflict): Promise<void> {
  console.log(`[ORCHESTRATOR] Conflict detected between ${conflict.agentA} 
               and ${conflict.agentB}: ${conflict.description}`);
  
  // 1. Pause both agents
  await pauseAgent(conflict.agentA);
  await pauseAgent(conflict.agentB);
  
  // 2. Present both sides
  await broadcastToAgents(conflict.agentA, {
    type: 'conflict_presentation',
    theirArgument: conflict.argumentB,
    yourArgument: conflict.argumentA,
  });
  await broadcastToAgents(conflict.agentB, {
    type: 'conflict_presentation',
    theirArgument: conflict.argumentA,
    yourArgument: conflict.argumentB,
  });
  
  // 3. Expect resolution within 3 rounds of negotiation
  for (let round = 0; round < 3; round++) {
    const responses = await Promise.all([
      getNegotiationResponse(conflict.agentA),
      getNegotiationResponse(conflict.agentB),
    ]);
    
    if (responses[0].agrees && responses[1].agrees) {
      console.log(`[ORCHESTRATOR] Conflict resolved in round ${round + 1}`);
      return;
    }
  }
  
  // 4. Timeout → Orchestrator picks based on heuristic
  const decision = this.consensusResolver.defaultResolution(conflict);
  console.log(`[ORCHESTRATOR] Conflict unresolved after 3 rounds. 
               Applying default: ${decision}`);
}
```

---

## 6. Self-Healing Agent

### 6.1 Diagnostic Loop

```typescript
class SelfHealingAgent {
  private maxAttempts = 3;
  private healHistory: HealingRecord[] = [];
  
  async diagnoseAndHeal(failedTask: Task, error: Error): Promise<HealResult> {
    const diagnostics = await this.runDiagnostics(failedTask, error);
    
    for (let attempt = 1; attempt <= this.maxAttempts; attempt++) {
      const patch = await this.generatePatch(diagnostics, attempt);
      if (!patch) break;
      
      const result = await this.applyAndVerify(failedTask, patch);
      
      this.healHistory.push({
        taskId: failedTask.id,
        attempt,
        diagnostics,
        patch,
        success: result.success,
      });
      
      if (result.success) {
        return { status: 'healed', attempts: attempt, logs: this.healHistory };
      }
    }
    
    // Escalate to bounty
    return { 
      status: 'bounty', 
      attempts: this.maxAttempts, 
      logs: this.healHistory,
      bounty: await this.createBounty(failedTask, this.healHistory),
    };
  }
  
  private async runDiagnostics(task: Task, error: Error): Promise<Diagnostics> {
    const diagnostics: Diagnostics = {
      taskId: task.id,
      error: { message: error.message, stack: error.stack },
      compilationErrors: [],
      testFailures: [],
      lintViolations: [],
      symptoms: [],
    };
    
    // Compilation check
    try {
      const compileResult = await exec(`cd ${task.directory} && npm run build 2>&1`);
      diagnostics.compilationErrors = this.parseCompilationErrors(compileResult.stderr);
    } catch (e) {}
    
    // Test failures
    try {
      const testResult = await exec(`cd ${task.directory} && npm test 2>&1`);
      diagnostics.testFailures = this.parseTestFailures(testResult.stdout);
    } catch (e) {}
    
    // Lint
    try {
      const lintResult = await exec(`cd ${task.directory} && npm run lint 2>&1`);
      diagnostics.lintViolations = this.parseLintViolations(lintResult.stdout);
    } catch (e) {}
    
    return diagnostics;
  }
}
```

### 6.2 Heal Patterns by Error Type

```
Compilation Error:
  1. Missing import → add import
  2. Type mismatch → cast or fix type definition
  3. Syntax error → fix syntax (usually the AI generates invalid code)

Runtime Error:
  1. Null/undefined → add null check
  2. Infinite loop → add max iteration guard
  3. Network timeout → increase timeout, add retry

Test Failure:
  1. Assertion mismatch → check if test or implementation is wrong
  2. Missing mock → add mock for dependency
  3. Flaky test → add retry or fix timing

Lint Error:
  1. Unused variable → remove or prefix with underscore
  2. Wrong quotes → auto-fix with linter
  3. Missing type annotation → add type
```

### 6.3 Heal Attempt Log

```json
{
  "taskId": "task-004-order-api",
  "agentId": "agent-backend-02",
  "timeline": [
    {
      "time": "2026-05-02T14:30:00Z",
      "event": "agent_completed",
      "detail": "Agent finished writing code"
    },
    {
      "time": "2026-05-02T14:30:05Z",
      "event": "test_failure",
      "detail": "3 tests failed: 2 assertion errors, 1 compilation"
    },
    {
      "time": "2026-05-02T14:30:10Z",
      "event": "heal_attempt_1",
      "detail": "Fixed type error: number vs string on amount field"
    },
    {
      "time": "2026-05-02T14:30:20Z",
      "event": "heal_attempt_2",
      "detail": "Fixed test assertion: expected total was wrong"
    },
    {
      "time": "2026-05-02T14:30:25Z",
      "event": "all_tests_pass",
      "detail": "12/12 tests pass, coverage 87%"
    }
  ],
  "finalStatus": "healed"
}
```

---

## 7. Scalability: From 3 to 100 Agents

### 7.1 Architecture Scaling Path

```
Small (3-10 agents): Single orchestrator, shared filesystem
  ├── 1 Orchestrator
  ├── 2-5 Coding agents
  ├── 1 Test agent
  ├── 1 Review agent
  └── File-based context

Medium (10-30 agents): Hierarchical orchestrators
  ├── Meta-Orchestrator (project-level)
  ├── Sub-Orchestrators per domain
  │   ├── Orders Sub-orch → 5 agents
  │   ├── Payments Sub-orch → 3 agents
  │   └── Frontend Sub-orch → 5 agents
  ├── Cross-functional (Test, Security, Docs) → 3 agents each
  └── Redis/DB-based context

Large (30-100+ agents): Full hierarchy + service mesh
  ├── Meta-Orchestrator + Dashboard
  ├── Domain clusters (each 10-20 agents)
  ├── Message queue (NATS/Kafka) for inter-agent
  ├── Centralized log (Loki/Elastic)
  └── Dynamic scaling (add agents by demand)
```

### 7.2 Agent Pool Management

```typescript
class AgentPool {
  private agents: Agent[] = [];
  private maxConcurrent: number;
  
  async allocateTask(task: Task): Promise<string> {
    // Find best idle agent
    for (const agent of this.agents) {
      if (agent.status !== 'idle') continue;
      if (!this.matchCapabilities(agent, task)) continue;
      
      await agent.acceptTask(task);
      return agent.id;
    }
    
    // No idle agent → scale up (if under max)
    if (this.agents.length < this.maxConcurrent) {
      const newAgent = await this.spawnAgent();
      await newAgent.acceptTask(task);
      return newAgent.id;
    }
    
    // Queue task
    this.taskQueue.push(task);
    return 'queued';
  }
  
  async scaleUp(count: number): Promise<void> {
    for (let i = 0; i < count; i++) {
      const agent = await this.spawnAgent();
      this.agents.push(agent);
    }
  }
  
  async scaleDown(idleThreshold: number): Promise<void> {
    const idleAgents = this.agents
      .filter(a => a.status === 'idle')
      .filter(a => a.idleSince < Date.now() - idleThreshold);
    
    for (const agent of idleAgents) {
      await this.terminateAgent(agent.id);
      this.agents = this.agents.filter(a => a.id !== agent.id);
    }
  }
}
```

---

## 8. Quality Assurance in Swarms

### 8.1 Automated Quality Gates

```
Gate 1: Static Analysis (immediate)
  - No syntax errors
  - All imports resolve
  - Lint passes (strict mode)

Gate 2: Unit Tests (per agent)
  - > 80% coverage on new code
  - All tests pass (no flaky tests)
  - No test file with 0 assertions

Gate 3: Integration (cross-agent)
  - Contracts match (A's output → B's input)
  - API endpoints respond correctly
  - Database schema migrations run without conflicts

Gate 4: E2E (critical paths)
  - Happy path: full user flow
  - Error paths: empty data, invalid input, timeout
  - Performance: response < 500ms p95
```

### 8.2 Review Agent Scoring

```typescript
class ReviewAgent {
  async review(code: CodeFile, context: SharedContext): Promise<ReviewVerdict> {
    const issues: ReviewIssue[] = [];
    
    // 1. Contract compliance
    const contractViolations = this.checkContracts(code, context.contracts);
    issues.push(...contractViolations.map(v => ({
      severity: 'error',
      message: `Contract violation: ${v.description}`,
      file: v.file,
      line: v.line,
    })));
    
    // 2. Code quality
    const qualityIssues = this.checkCodeQuality(code);
    issues.push(...qualityIssues);
    
    // 3. Test coverage on new code
    if (context.task.type !== 'test-only') {
      const uncoveredLines = this.findUncoveredLines(code);
      if (uncoveredLines.length / code.totalLines > 0.2) {
        issues.push({
          severity: 'warning',
          message: `Low coverage: ${covered}% new code uncovered`,
        });
      }
    }
    
    // 4. Security scan
    const securityIssues = this.securityScan(code);
    issues.push(...securityIssues);
    
    const score = this.calculateScore(issues);
    const passed = score >= 0.8;  // 80% threshold
    
    return { passed, score, issues, recommendations: this.suggestFixes(issues) };
  }
  
  private calculateScore(issues: ReviewIssue[]): number {
    const weights = { error: -10, warning: -3, info: -1 };
    const penalty = issues.reduce((sum, i) => sum + (weights[i.severity] || 0), 0);
    return Math.max(0, Math.min(1, 1 + penalty / 100));
  }
}
```

---

## 9. Bounty System (L2 Escalation)

### 9.1 When to Create a Bounty

```
Conditions:
  1. Self-healing agent fails 3 attempts → auto bounty
  2. Conflict resolution fails (3 rounds) → manual bounty  
  3. Task exceeds time estimate by 2x → review → bounty
  4. Code review score < 0.6 after 2 heal cycles → bounty
  5. Cross-agent integration fails and cause unknown → bounty
```

### 9.2 Bounty Package Format

```yaml
bounty:
  id: "bounty-20260502-001"
  title: "Fix order API test failures (idempotency)"
  createdAt: "2026-05-02T15:30:00Z"
  severity: "medium"
  estimatedEffort: "2h"
  reward: "500 credits"

  problem:
    description: |
      Order creation endpoint fails when idempotency key is reused.
      First call succeeds, second call returns 500 instead of 200 (cached result).
    stepsToReproduce:
      - "POST /api/v1/orders with Idempotency-Key: test1"
      - "POST /api/v1/orders with Idempotency-Key: test1 (same key)"
      - "Second request returns 500 Internal Server Error"

  context:
    failedAttempts: 3
    diagnosticLogs: "logs/bounty-20260502-001.json"
    relevantFiles:
      - "src/middleware/idempotency.ts"
      - "src/routes/orders.ts"
      - "tests/idempotency.test.ts"
    sharedContextVersion: "sha256:abc123"
  
  acceptance:
    - "Two identical requests with same idempotency key → both return same result"
    - "First request status: 201, second: 200"
    - "No data duplication in database"
    - "Existing tests don't break"
```

### 9.3 Bounty Lifecycle

```
Create: Auto-generated on 3rd heal failure
  → Store in bounty registry
  → Classify by domain and complexity
  → Assign reward (based on estimated effort)

Assign: Available for assignment
  → Notify available senior agents
  → First claim gets the bounty
  → Lock the bounty (no parallel work)

Execute: Agent works on the bounty
  → Has wider context than regular tasks
  → Can modify any file
  → Must pass same quality gates

Verify: Bounty solution reviewed
  → Orchestrator runs full pipeline
  → If passes: mark solved, award credits
  → If fails: return to available pool

Archive: Solved or expired
  → Store solution for future reference
  → Update heal pattern library
  → If expired (48h): escalate to human
```

---

## 10. Telemetry & Observability

### 10.1 Metrics to Monitor

```
Agent-level:
  - Task completion rate (per agent type)
  - Average task duration
  - Heal success rate
  - Code quality score (per agent)
  - Conflicts caused (per agent)
  - Idle time / Working time ratio

Swarm-level:
  - Total throughput (tasks/hour)
  - Bottleneck detection (which stage queues up?)
  - Heal rate (% of tasks needing heal vs straight pass)
  - Bounty rate (% of tasks escalated)
  - Agent utilization (how many agents are working vs idle)
  - Cross-module integration failure rate

Cost:
  - Token usage per task
  - Total tokens per project
  - Cost per successful task
```

### 10.2 Dashboard Layout

```
Row 1: Swarm health
  [Active tasks] [Queued tasks] [Completion rate] [Bounty rate]
  
Row 2: Agent utilization  
  [Agent pool size] [Idle %] [Working %] [Healing %]

Row 3: Quality metrics
  [Avg review score] [Test pass rate] [Coverage avg] [Heal rate]
  
Row 4: Bottleneck
  [Slowest stage] [Blocked agents] [Pending dependencies]
```

### 10.3 Telemetry Data Structure

```json
{
  "swarm": {
    "projectId": "order-service-v2",
    "activeTasks": 7,
    "queuedTasks": 2,
    "completedTasks": 23,
    "bountyTasks": 1,
    "totalDuration": "45m"
  },
  "agents": [
    {
      "id": "agent-be-03",
      "role": "backend",
      "status": "working",
      "currentTask": "task-007",
      "tasksCompleted": 4,
      "avgReviewScore": 0.87,
      "healAttempts": 2,
      "healSuccess": 2
    }
  ],
  "quality": {
    "avgCoverage": 84.3,
    "testPassRate": 0.97,
    "avgScore": 0.82,
    "healRate": 0.15
  }
}
```
