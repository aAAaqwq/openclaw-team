# Open Source Architecture (OSA)

> Level: Expert | File: `open-source-architecture.md`
> 
> Deep pattern analysis of top open source projects: how they're structured, how they
> evolved, architecture decisions that mattered, and how to replicate the patterns.

---

## Table of Contents
1. [How to Read Open Source Code](#1-how-to-read-open-source-code)
2. [Top 10 Architecture Patterns in Open Source](#2-top-10-architecture-patterns-in-open-source)
3. [Project Deep Dives](#3-project-deep-dives)
4. [Repository Structure Signals](#4-repository-structure-signals)
5. [Evolution Trajectory Analysis](#5-evolution-trajectory-analysis)
6. [Contributing & Forking Strategy](#6-contributing--forking-strategy)
7. [OSS Adoption Qualification](#7-oss-adoption-qualification)
8. [Building Your Own OSS Project](#8-building-your-own-oss-project)
9. [ClawHub Platform Intelligence](#9-clawhub-platform-intelligence)
10. [Architecture Reconstruction](#10-architecture-reconstruction)

---

## 1. How to Read Open Source Code

### 1.1 The Reading Order

```
Step 1: README (5 min)
  - What does it do? One sentence.
  - What's the architecture diagram?
  - What's the one unique thing?

Step 2: Architecture docs / ADR / design docs (15 min)
  - Any DESIGN.md, ARCHITECTURE.md, ADR-*
  - Contribute.md for conventions
  - RFCs if available

Step 3: Top-level directory structure (2 min)
  - src/ structure = domain or technical layers?
  - Monorepo or polyrepo?
  - Package structure = service boundaries?

Step 4: Core data model + interfaces (15 min)
  - Find the main type/entity definitions
  - Find the main interfaces/abstract classes
  - Primary key, foreign key, relationships

Step 5: Main entry point + key flow (20 min)
  - main.go / index.ts / main.py → trace one request
  - How does a request flow through the system?
  - Error handling pattern

Step 6: Test strategy (10 min)
  - Are there test files? Coverage?
  - Test patterns: mocks vs real instances?
  - Integration tests?

Step 7: The CHANGELOG / release notes (5 min)
  - How did it evolve?
  - Major milestones
  - Breaking changes
```

### 1.2 Reading Toolchain

```bash
# Clone a repo
git clone --depth 1 https://github.com/user/repo.git
cd repo

# Quick overview
ls -la
cat README.md | head -50

# Biggest files = core logic
find . -name "*.go" -o -name "*.ts" -o -name "*.py" | \
  xargs wc -l | sort -rn | head -20

# Most complex functions (longest)
grep -r "^func " --include="*.go" | \
  awk '{print length, $0}' | sort -rn | head -20

# Test method vs production code ratio
find . -name "*_test.go" | xargs wc -l
find . -name "*.go" ! -name "*_test.go" | xargs wc -l

# See evolution: look at releases
git tag | sort -V | tail -10

# Compare first commit vs current
git log --reverse --oneline | head -5
git log --oneline | head -5
```

### 1.3 Signal vs Noise

```
Look for (signals):
  - ADR files (organization, design maturity)
  - DESIGN.md (deliberate architecture decisions)
  - PROFILING.md (performance-aware project)
  - POSTMORTEM.md (learning culture)
  - Extensive test file coverage (engineering discipline)
  - Monorepo with clear package boundaries (clean architecture)

Ignore (noise):
  - Number of GitHub stars (popularity ≠ quality)
  - Recent commit count (can be from one person)
  - CI green checkmarks (usually pass)
  - .github/ directory size (process ≠ engineering)
  - Linter configuration size (can be generated)
```

---

## 2. Top 10 Architecture Patterns in Open Source

### 2.1 Plugin Architecture

```
Components: Core + Extension Points + Plugins

Projects: VS Code, Helm, Terraform, Grafana, Kong

Structure:
  core/
    extensions/
  plugins/          ← Each plugin is a Go module
  examples/

Key Pattern:
  - Define interface in core
  - Plugins implement the interface at compile or runtime
  - Go: hashicorp/go-plugin (gRPC-based, hot reload)
  - JS: webpack plugin API, ESLint plugins
  
When to use: need extensibility without modifying core
```

### 2.2 Clean/Hexagonal in Go

```
Components: Domain + Ports + Adapters

Projects: Kubernetes, Docker, HashiCorp tools, Prometheus

Structure:
  pkg/              ← Reusable library code
    controller/
    apiserver/
  internal/         ← Shouldn't be imported externally
    registry/
    storage/

Key Go pattern:
  - Interface defined where it's USED, not where it's IMPLEMENTED
  - Kubernetes: client-go has interfaces, server implements
  - HashiCorp: go-multierror, go-msgpack, go-plugin as separate modules
```

### 2.3 Monorepo with Microservices

```
Components: apps/ + packages/ + services/

Projects: Google (internal), Uber, Monzo, all large SDK projects

Structure:
  apps/
    web/
    mobile/
    cli/
  packages/
    shared-types/
    ui-components/
    eslint-config/
  services/
    api-gateway/
    order-service/
    user-service/
  tools/
    scripts/
```

### 2.4 Event-Driven / CQRS

```
Components: Producer + Event Bus + Consumer + Read Model + Write Model

Projects: Temporal, Camunda, EventStoreDB, Axon Framework

Pattern:
  - Commands (do something) in Producer
  - Events (something happened) on Event Bus
  - Projectors build Read Models
  - Sagas coordinate long-running transactions
```

### 2.5 Layered with Adapters

```
Components: Handler → Service → Repository → DB

Projects: ent (prisma-like Go ORM), GORM, most web frameworks

Structure:
  handler/     ← HTTP layer
  service/     ← Business logic
  repository/  ← Data access
  model/       ← Domain types
  
Key Pattern: in Go, top-level handler imports service, service imports repository
```

### 2.6 State Machine Architecture

```
Components: State Store + Transitions + Triggers + Side Effects

Projects: Temporal, Cadence, Kubernetes controllers, Ansible

Structure:
  controller/
    reconciler/
    watcher/
  state/
  transitions/
```

### 2.7 Virtual Filesystem

```
Components: VFS Layer + Backends

Projects: Go (io/fs), bazel, webpack, Vite

Structure:
  fs/
    local/
    s3/
    inmemory/
    overlay/
```

### 2.8 Middleware Pipeline

```
Components: Chain of handlers

Projects: Express, Koa, Fastify, Gin, Echo, http.Handler middleware

Pattern:
  type Middleware func(ctx Context, next NextFunc) error
  
  Example: auth → rate-limit → logger → handler
```

### 2.9 Interface Segregation in Practice

```
Projects: Kubernetes (client-go), Terraform Provider SDK

Pattern: One interface per responsibility, not one giant interface.

Kubernetes example:
  type Lister interface { List() }
  type Getter interface { Get(name string) }
  type Creator interface { Create(obj Object) }
  type Updater interface { Update(obj Object) }
  
  Not: type CRUD interface { List, Get, Create, Update, Delete }
  
  Why: consumers only implement what they need
```

### 2.10 Versioned API + Compatibility

```
Projects: Kubernetes, AWS SDK, Terraform

Pattern:
  apis/
    v1/
    v2/
  conversion/
  
  v1 and v2 exist simultaneously.
  Storage version is one (v2). v1 automatically converts to v2 on read/write.
  Internal version is separate: avoids direct v1→v2 mapping.
```

---

## 3. Project Deep Dives

### 3.1 Kubernetes

```
Total: ~3M lines (Go)

Architecture:
  etcd (Raft) ← API Server ← Scheduler ← Kubelet ← Pod
                      ↓                                   
                 Controller Manager                        
                      ↓                                   
                 Cloud Controller Manager                  

Key patterns:
  1. Controller pattern: reconcile desired vs actual state
  2. API versioning: v1, v1beta1, v1alpha1 with conversion
  3. Interface segregation: client-go has 30+ small interfaces
  4. Plugin architecture: CSI, CNI, CRI, device plugins
  5. Work queue: handle retries with rate limiting

Extracting K8s for your project:
  - Tak: Use controller-runtime for custom controllers
  - Don't: Copy the directory structure (it's special-cased for K8s)

Go module structure:
  staging/
    src/k8s.io/
      api/          ← API types (ObjectMeta, Pod, etc.)
      apimachinery/ ← Runtime, conversion, scheme
      client-go/    ← Go client library
      component-base/ ← Logging, metrics, flags
  pkg/
    controller/
      namespace/
      deployment/
```

### 3.2 Docker / Moby

```
Total: ~200K lines (Go)

Architecture:
  Client (Docker CLI) → Daemon (dockerd) → containerd → runc
  
Key patterns:
  1. Client-Server architecture (REST API between CLI and Daemon)
  2. Plugin via containerd (CRI interface)
  3. Builder pattern: Dockerfile → buildkit → image layers
  4. Graph driver (AUFS, overlay2, devicemapper) — deprecated now

Structure:
  cli/         ← docker CLI (separate repo now)
  daemon/      ← dockerd
  builder/     ← BuildKit
  distribution/ ← Image registry client
  layer/       ← Union filesystem management
  volume/      ← Volume drivers
```

### 3.3 Terraform / OpenTofu

```
Total: ~500K lines (Go)

Architecture:
  Core (HCL parsing, state management, plan/apply)
    ├── Provider plugins (gRPC)
    │   ├── aws
    │   ├── azurerm
    │   └── google
    ├── State backends
    │   ├── s3
    │   ├── consul
    │   └── terraform cloud
    └── Provisioners (file, local-exec, remote-exec)

Key patterns:
  1. Plugin via gRPC (hashicorp/go-plugin)
  2. Plugin registration via goog's proto schema + SDK
  3. State machine: Refresh → Plan → Apply → Destroy
  4. Terraform provider SDK v2 / framework: CRUD interface

Provider structure:
  terraform-provider-aws/
    aws/        ← Provider implementation
      internal/
        service/
          ec2/
          s3/
          iam/
```

### 3.4 Prometheus

```
Total: ~150K lines (Go)

Architecture:
  Scrapers (Pull model) → TSDB (local) + Remote Write

PromQL engine:
  AST → PromQL parser → Evaluator → Range/Instant vectors

Structure:
  tsdb/          ← Time-series database
  promql/        ← Query language
  rules/         ← Recording & alerting rules
  scrape/        ← Scrape manager
  discovery/     ← Service discovery (k8s, file, dns)
  storage/       ← Storage interface (TSDB implements, remote write implements)
  web/           ← Web UI + API
  
Lessons:
  - TSDB is a standalone library (used by Thanos, Cortex, VictoriaMetrics)
  - Service discovery is pluggable
  - Storage is an interface (can be local TSDB or remote)
  - PromQL is a full programming language (AST → evaluation)
```

### 3.5 ClickHouse

```
Total: ~700K lines (C++)

Architecture:
  Columnar storage engine (MergeTree) + Vectorized execution (SIMD)

Structure:
  src/
    Core/        ← Foundation: types, error handling, logging
    IO/          ← I/O abstraction
    DataTypes/   ← Column types
    Columns/     ← Column data structures
    Storages/    ← MergeTree, Memory, Distributed
    Interpreters/ ← SQL → QueryPlan
    Processors/   ← Data stream processing pipeline
    Functions/    ← SQL functions (scalar, aggregate, window)

Key patterns:
  1. Compile-time metaprogramming (C++ templates for data type dispatch)
  2. Vectorized execution: loop over columns, not rows
  3. MergeTree: sorted by primary key, partitioned by expression
  4. Distributed table: read from all shards, merge results

Lessons for columnar stores:
  - DataType + Column: type erasure via virtual dispatch
  - IBlock: a set of columns, processed as a batch
  - IProcessor: connected in a directed acyclic graph
```

### 3.6 Golang Standard Library

```
Total: ~700K lines (Go itself ~300K, net ~200K, crypto ~100K)

Structure (selected):
  net/
    http/           ← HTTP client + server (most used package)
      httptest/     ← Testing utilities
      httputil/     ← Reverse proxy, etc
    url/
  context/          ← Context (cancel, deadline, values)
  sync/             ← Mutex, WaitGroup, Pool, Map
    atomic/
  database/sql/     ← SQL driver interface (< 2000 lines!)
  encoding/         ← JSON, XML, protobuf, etc
  flag/             ← Command-line flag parsing (< 2000 lines!)

Lessons from Go stdlib:
  - database/sql is the best interface design in Go: < 2000 lines, 
    supports any SQL DB through driver interface
  - httptest.Server: simple but revolutionary for testing HTTP
  - sync.Pool: brilliant for reducing GC pressure
  - context: "cancel propagation" design pattern
```

### 3.7 Vite / esbuild

```
Vite (TypeScript): ~100K lines
esbuild (Go): ~100K lines

Architecture:
  Vite dev server (esbuild pre-bundling) 
    → On-demand file serving (native ESM)
    → HMR websocket

esbuild:
  Parser (Go) → AST → Bundler → Minifier → Source map

Key patterns:
  1. esbuild: single binary, no npm dependencies, 10-100x faster than Node bundlers
  2. Vite: "unbundle during dev, bundle for prod" — best of both
  3. HMR via websocket: only send changed modules
  4. Pre-bundling: convert CommonJS dependencies to ESM ahead of time

Lessons:
  - Performance > features (esbuild doesn't have TypeScript compiler, 
    just strips types)
  - Python/Node bundlers hit JS performance wall → Go/Rust replacement
```

---

## 4. Repository Structure Signals

### 4.1 Signals of Well-Maintained Projects

```
Signals:
  - ADR/ directory or ARCHITECTURE.md → deliberate architecture
  - CHANGELOG.md maintained → disciplined releases
  - CONTRIBUTING.md with decision process → community management
  - test/ and integration/ → testing culture
  - google/wire or fx (Go) → dependency injection
  
Anti-signals:
  - No README → run
  - README only has "Hello World" and 5-year-old screenshots
  - vendor/ in git (Go pre-modules), or massive .gitignore
```

### 4.2 Common Directory Layouts in Open Source

```yaml
Go (backend-heavy):
  cmd/                # Main programs (one per binary)
    server/
    cli/
  internal/           # Shouldn't be imported externally
  pkg/                # Reusable library code
  api/                # API types, protobuf definitions
  config/             # Configuration structures
  docs/
  
TypeScript (full-stack):
  apps/               # Applications
  packages/           # Shared packages
  services/           # Microservices
  libs/               # Internal libraries (NX monorepo)
  tools/              # Build scripts, generators
  
Python (data/ML):
  src/
    [project_name]/
      models/
      services/
      api/
  tests/
  notebooks/
  scripts/
  Dockerfile
```

### 4.3 Monorepo vs Polyrepo Decision

```
Monorepo advantages:
  - Atomic changes across packages
  - Single version (no version hell)
  - Easier refactoring
  - Reuse is natural
  
Polyrepo advantages:
  - Independent versioning
  - Independent deployment
  - Different teams have autonomy
  - Not-all-code-fits-in-one-tool

Signal: Which do top projects use?
  - Google/Meta/Uber: Monorepo (hundreds of millions of lines)
  - Kubernetes: Monorepo in staging/ tree
  - Most 10-100K line projects: single repo with clear package boundaries
  - AWS SDKs (multiple languages): polyrepo, one per language
```

---

## 5. Evolution Trajectory Analysis

### 5.1 How K8s Evolved

```
Phase 1 (2014-2015): Simple container scheduler
  - Single binary, few controllers, etcd as backend
  
Phase 2 (2016-2017): Extensibility
  - CRDs (2017), CSI, CNI, CRI — plugin everything
  
Phase 3 (2018-2020): Production hardening
  - Stability: pod priority, taints/tolerations, topology spread
  - RBAC, PSP → PSA
  - HPA v2
  
Phase 4 (2021-2024): Efficiency
  - In-place pod resize, NUMA-aware scheduling
  - DRA (Dynamic Resource Allocation)

Lesson: Start simple, plugin the extensibility points, 
        then harden. Don't design for all scales from day 1.
```

### 5.2 How Prometheus Evolved

```
Phase 1 (2012): SoundCloud internal tool
  - In-memory TSDB, YAML config, no alerting
  
Phase 2 (2014): CNCF incubation
  - Local disk TSDB (mmap-based), AlertManager, recording rules
  
Phase 3 (2016-2019): Production TSDB
  - Compression innovations (xor for floats, delta-of-delta for timestamps)
  - Remote write for long-term storage
  
Phase 4 (2020+): Ecosystem
  - Thanos/Cortex handle HA and long-term
  - OpenMetrics standard
  - Prometheus becomes "the metrics system" (not just a single binary)
```

### 5.3 Pattern: Spinoff / Extraction

```
Many projects start as internal tools, then get spinned out:

Internal → Spinoff → Stars
  Google MapReduce → Hadoop → 10K+
  Google GFS → HDFS → 10K+
  Google BigTable → HBase → 10K+  
  Google Borg → Kubernetes → 100K+
  SoundCloud Prometheus → Prometheus → 50K+
  HashiCorp Terraform → OpenTofu → 30K+
  InfluxDB IOx → InfluxDB 3.0 → 10K+

Pattern: Internal solves real need → Extract as oss → Community takes over
```

---

## 6. Contributing & Forking Strategy

### 6.1 Quick Start to Contributing

```markdown
Step 1: Find your entry point
  - Good First Issue label
  - Help Wanted label
  - Documentation improvements (always needed, low friction)

Step 2: Understand the build system
  - Go: go build . 
  - TypeScript: npm install && npm run build
  - Rust: cargo build

Step 3: Run the tests
  - Go: go test ./...
  - TypeScript: npm test
  - Rust: cargo test

Step 4: Make a small fix
  - Fix a typo in docs
  - Add a test case
  - Fix a CLI help message

Step 5: Submit PR
  - Follow CONTRIBUTING.md
  - Include test
  - Sign DCO (if required)
```

### 6.2 Forking Strategy for Adoption

```markdown
When to fork:
  - Project is unmaintained (no commits > 1 year)
  - License change (e.g., Terraform BSL → OpenTofu fork)
  - Need features that won't be accepted upstream
  - Need to customize for internal use

Forking responsibly:
  - Keep upstream sync (rebasing periodically)
  - Add .patch files documenting changes from upstream
  - Make the fork usable: CI, releases, documentation
  - If changes are valuable: still attempt to upstream them

OpenTofu fork example:
  - Forked from Terraform after BSL license change
  - 30+ contributors, weekly releases, maintained
  - Continues to sync some changes from upstream
```

---

## 7. OSS Adoption Qualification

### 7.1 Decision Matrix

```
| Factor                 | High Risk | Low Risk |
|------------------------|-----------|----------|
| License                | AGPL, BSL | Apache 2.0, MIT, BSD |
| Community              | Single maintainer | Foundation-backed |
| Backward compat        | Breaking every release | API stability guarantee |
| Release cadence       | > 6 months | Monthly or quarterly |
| Test coverage          | < 50%     | > 80% |
| Security process       | None      | Security.md, CVE, disclosure |
| Ecosystem lock-in      | Proprietary config | Standards-based |
```

### 7.2 Due Diligence Checklist

```
□ License compatible with your use case (Apache 2.0 vs GPL vs BSL)
□ Community health: > 5 active committers, > 3 companies contributing
□ Release cadence: at least quarterly releases
□ API maturity: 1.x+ (not 0.x)
□ Security process: security.txt or SECURITY.md, past CVE track record
□ Backward compatibility commitment: README or ADR mentions it
□ Dependency size: npm audit / go mod why / cargo audit
```

---

## 8. Building Your Own OSS Project

### 8.1 Minimum Viable OSS Structure

```
my-project/
├── README.md           # 1-paragraph explanation + quick start
├── LICENSE             # Apache 2.0 or MIT
├── CONTRIBUTING.md     # How to contribute
├── CODE_OF_CONDUCT.md  # Required by CNCF
├── Makefile            # build, test, lint, fmt
├── .github/
│   ├── workflows/
│   │   └── ci.yml      # Build + test on push and PR
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
└── src/
```

### 8.2 OSS Growth Phases

```
Phase 1 (0-100 stars): Personal project
  - Just make it work, write docs
  - 1 maintainer

Phase 2 (100-1000 stars): Community starts
  - Add CONTRIBUTING.md, issue templates
  - Start getting contributions (documentation, tests)
  - 1-3 maintainers

Phase 3 (1000-10000 stars): Scaling
  - Formal RFC/ADR process
  - Dedicated maintainers (may be employed)
  - Governance: committers, maintainers, PMC

Phase 4 (10000+): Foundation
  - CNCF/GitHub Foundation
  - Full time maintainers
  - Marketing, events, certification
```

---

## 9. ClawHub Platform Intelligence

### 9.1 What ClawHub Teaches

```
ClawHub ecosystem:
  - OpenClaw: the Agent OS — runtime + skills + agents
  - ClawHub.ai: marketplace for skills, plugins, agents
  - Skills API: skill specification, versioning, dependency management

Architecture inferences:
  1. Plugin architecture (skills are plugins)
     → Skills are self-contained modules
     → Skill discovery: skills directory or marketplace
     → Skill isolation: each skill runs independently

  2. Runtime aspect: 
     → Skills loaded at runtime
     → Model routing per skill
     → Tool exposure per skill
  3. Versioned ecosystem:
     → Skill versions (semver)
     → Dependency between skills
```

### 9.2 ClawHub Skill Architecture Pattern

```markdown
Skill anatomy:
  - SKILL.md: metadata (name, description, provider, version)
  - skill.ts / skill.js: implementation
  - references/: supporting files
  - tests/: test fixtures

This is essentially a plugin architecture:
  ┌─────────────────────────────────┐
  │          Agent Runtime          │
  │  (OpenClaw)                     │
  │     │ Loads skills at startup    │
  │     │ Routes messages to skills  │
  │     │ Exposes tools to skills    │
  └─────────────┬───────────────────┘
                │
        ┌───────┴───────┐
        │   Skill 1     │
        │   Skill 2     │
        │   Skill N     │
        └───────────────┘
```

---

## 10. Architecture Reconstruction

### 10.1 How to Reverse-Engineer an Unknown System

```
Running system (no docs):
  1. Find the entry point (main function, startup script)
  2. Find the first request handler
  3. Trace one request from start to finish
  4. Document: components, data flow, dependency graph

Code only (no running system):
  1. Config files → discoverable capabilities
  2. Test files → expected behavior
  3. Repository structure → architectural decisions
  4. Imports/dependencies → integration surface area

Mental model:
  Draw on a whiteboard (or Miro):
  ┌─────────┐     ┌─────────┐     ┌─────────┐
  │ Entry   │────▶│ Handler │────▶│ Service │
  └─────────┘     └─────────┘     └────┬────┘
                                       │
                                  ┌────▼────┐
                                  │  DB     │
                                  └─────────┘
```

### 10.2 Architecture Reconstruction Template

```markdown
# Architecture Reconstruction: [Project Name]

## System Overview (1 sentence)
[What it does, in one line]

## Key Components
- Component 1: [responsibility, interface in/out]
- Component 2: [responsibility, interface in/out]

## Data Flow
```
User → Component A → Component B → DB
                                          ↕
                                    Component C (cache)
```

## Architecture Style
[Monolith / Microservices / Event-driven / Plugin / etc]

## Key Design Decisions
1. [Decision 1]: [Rationale]
2. [Decision 2]: [Rationale]

## What I Would Change
1. [Improvement 1]
2. [Improvement 2]

## Lessons for My Project
1. [Lesson extracted]
```

### 10.3 Top 10 OSS Lessons

```
1. Interface segregation: small interfaces > one big interface
2. Plugin everything: extensibility beats completeness
3. Test your API, not your implementation: contract tests, not mocks
4. Start simple, extract later: monolith → microservice is easier than reverse
5. Design docs matter: ADR saves future-you
6. Tooling is code: Makefile, CI scripts, code gen are as important as src/
7. Backward compatibility is a feature: your users depend on it
8. CLI first, GUI second: every great OSS project has a CLI
9. One version at a time: sleep well knowing there's only ONE version
10. Performance matters at scale: but don't optimize before you have users
```
