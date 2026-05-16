# AGENTS.md

This file provides guidance to AI coding assistants when working with code in this repository.

This repository is primarily built for the **IBM Bob Hackathon**, but this file is intentionally agent-agnostic and can be used by:

- IBM Bob
- Claude Code
- OpenAI Codex
- GitHub Copilot
- Cursor
- Windsurf
- Other AI coding assistants

If tool-specific files exist, such as `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules`, or `.bob/skills/`, they must extend this file and must not contradict it.

---

## Project Overview

**RepoTwin by Bob** is a comprehensive AI-driven developer intelligence platform built for the IBM Bob Hackathon.

The project transforms natural-language change requests into a **Shadow PR**, allowing developers to simulate the impact of a code change before implementation.

Core tagline:

> Simulate the blast radius of a code change before writing code.

RepoTwin helps developers understand:

- Which files and modules are affected by a proposed change
- What risks and regressions may appear
- What tests should be created
- What implementation order is safest
- What the Pull Request brief should contain
- How IBM Bob can reason over repository context to support safer development

The goal is not to build a generic AI code generator or repository chatbot. The goal is to demonstrate how IBM Bob can help developers understand the consequences of changes before they write code.

---

## IBM Bob Hackathon Context

This project must clearly demonstrate meaningful use of IBM Bob.

IBM Bob should be used to:

- Understand repository context
- Analyze code structure
- Identify affected files and modules
- Generate implementation plans
- Generate regression tests
- Generate documentation
- Generate PR briefs
- Help build the RepoTwin platform itself

The final repository must include:

```txt
bob_sessions/
```

This folder must contain exported IBM Bob task session reports and screenshots required for judging.

Do not commit:

- IBM credentials
- API keys
- Tokens
- Passwords
- Personal information
- Private company data
- Confidential data

---

## Main Demo Scenario

Default demo repository:

```txt
UniMarket
```

Default change request:

```txt
Add reservation flow before purchase.
```

The analysis should show that this change affects:

- Listing state model
- Transaction lifecycle
- Buyer/seller permissions
- Android UI
- Backend API
- Analytics events
- Offline cache
- Regression tests
- Documentation

Main demo insight:

> A feature that sounds simple can secretly affect the entire system.

---

## Package Manager Policy

This project uses **pnpm** as the only package manager.

Never use:

```bash
npm install
npm i
yarn install
```

Always use:

```bash
pnpm install
pnpm add <package>
pnpm add -D <package>
pnpm dev
pnpm build
pnpm lint
pnpm test
```

If any generated instruction suggests `npm install`, replace it with:

```bash
pnpm install
```

If any generated instruction suggests `npm run <script>`, prefer:

```bash
pnpm <script>
```

Examples:

```bash
pnpm dev
pnpm build
pnpm lint
```

The repository should keep a `pnpm-lock.yaml` file. Do not commit `package-lock.json` or `yarn.lock`.

---

## Project Documentation Conventions

All new documentation or task files must be saved under the `docs/` folder.

Examples:

- Tasks and TODOs:
  - `docs/2026_05_15/tasks/BackendRedisTodo.md`
  - `docs/2026_05_15/tasks/DashboardTodo.md`

- Requirements and specs:
  - `docs/2026_05_15/specs/ShadowPRRequirements.md`
  - `docs/2026_05_15/specs/ApiContract.md`

- Design docs:
  - `docs/2026_05_15/design/ArchitectureOverview.md`
  - `docs/2026_05_15/design/BlastRadiusMap.md`

- Hackathon docs:
  - `docs/api-contract.md`
  - `docs/architecture.md`
  - `docs/bob-usage.md`
  - `docs/demo-script.md`
  - `docs/submission-checklist.md`

Code files should follow the project structure.

Tests should go under the proper test folder for each module.

Important:

When creating a new file, ensure the directory exists or create it. Never default to the root directory for documentation, tasks, or planning files.

Root markdown files should be limited to standard project files:

```txt
README.md
AGENTS.md
CLAUDE.md
LICENSE
```

---

## Common Development Commands

### Frontend

```bash
# Install dependencies
pnpm install

# Run frontend development server
pnpm dev

# Build frontend
pnpm build

# Run linting
pnpm lint

# Run tests if configured
pnpm test
```

### Backend

The backend may use FastAPI, Node.js, or the stack already created by the backend teammate.

The backend must expose at minimum:

```txt
GET /api/health
POST /api/analyze
```

If the backend supports job-based analysis:

```txt
POST /api/analyses
GET /api/analyses/:id/status
GET /api/analyses/:id/result
```

If the backend uses Node.js, use pnpm commands only:

```bash
pnpm install
pnpm dev
pnpm build
pnpm test
```

If the backend uses Python/FastAPI, follow the backend-specific dependency manager already configured by the backend teammate.

Do not introduce a second JavaScript package manager.

### Redis

Redis should be used for real orchestration value, not just for show.

Recommended local command:

```bash
docker run --name repotwin-redis -p 6379:6379 -d redis:latest
```

Recommended environment variable:

```env
REDIS_URL=redis://localhost:6379
```

If Redis is unavailable, the backend should gracefully fall back to in-memory job storage for local development.

---

## Workflow Execution

### Complete Workflow

Use this workflow for large tasks:

```txt
First analyze requirements → then update architecture/API contract → then implement backend or frontend → then test → then validate hackathon evidence.
```

### Phase-Specific Execution

Use phase-specific work when possible:

```txt
Use Product Intelligence phase: refine Shadow PR data and Bob evidence
Use Backend phase: implement Redis-backed analysis API
Use Frontend phase: implement Shadow PR dashboard
Use QA phase: validate demo, docs, and submission readiness
```

### IBM Bob Usage Workflow

When using IBM Bob:

1. Use `AGENTS.md` as project context.
2. Use `.bob/skills/` for repeatable workflows.
3. Ask Bob for focused implementation tasks.
4. Avoid repeating long context in every prompt.
5. Export task session reports into `bob_sessions/`.

---

## System Architecture

### Multi-Phase Workflow Design

The system follows a three-phase approach with quality gates.

---

## 1. Planning Phase

Purpose:

- Define product requirements
- Define Shadow PR contract
- Define backend/frontend API contract
- Define Redis job lifecycle
- Define IBM Bob evidence strategy

Outputs:

```txt
docs/api-contract.md
docs/architecture.md
docs/bob-usage.md
types/shadow-pr.ts
data/sample-shadow-pr.json
```

Quality Gate 1:

- Shadow PR contract is stable
- Backend and frontend agree on field names
- Demo scenario is clear
- IBM Bob usage is documented

---

## 2. Development Phase

Purpose:

- Implement backend API
- Implement Redis job storage
- Implement frontend dashboard
- Implement typed API client
- Implement demo flow

Outputs:

```txt
backend/
app/
components/
lib/api.ts
data/sample-shadow-pr.json
```

Quality Gate 2:

- Frontend can render sample Shadow PR
- Backend can return analysis response
- Redis job status works or falls back to memory
- Demo flow works from input to results

---

## 3. Validation Phase

Purpose:

- Validate UI
- Validate API response shape
- Validate IBM Bob evidence
- Validate README and docs
- Validate deployment
- Prepare final submission

Outputs:

```txt
README.md
docs/demo-script.md
docs/submission-checklist.md
bob_sessions/
deployed demo URL
```

Quality Gate 3:

- App is deployed
- Public GitHub repository is ready
- `bob_sessions/` is not empty
- No secrets are committed
- Demo can be presented in 3 minutes

---

## Agent Categories

These are logical roles. They can be executed by IBM Bob, Claude, Codex, Copilot, Cursor, or human team members.

---

## Workflow Agents

### spec-orchestrator

Coordinates the project workflow and makes sure the team does not skip the contract, evidence, or submission requirements.

Responsibilities:

- Coordinate phases
- Track quality gates
- Prevent scope creep
- Ensure IBM Bob evidence is included
- Ensure final submission assets are ready

### spec-analyst

Analyzes the product idea and translates it into concrete requirements.

Responsibilities:

- Define user stories
- Define MVP requirements
- Define demo narrative
- Define business value
- Define judging criteria alignment

### spec-architect

Designs the technical architecture.

Responsibilities:

- Define frontend/backend architecture
- Define API contract
- Define Redis usage
- Define fallback strategy
- Define Shadow PR data contract
- Define deployment architecture

### spec-planner

Breaks work into tasks.

Responsibilities:

- Split work by team member
- Define branch names
- Define milestones
- Define acceptance criteria
- Define must-have vs nice-to-have

### spec-developer

Implements features following the specs.

Responsibilities:

- Implement backend API
- Implement Redis layer
- Implement frontend dashboard
- Implement typed API client
- Keep code clean and focused

### spec-tester

Creates and validates tests.

Responsibilities:

- Validate API endpoints
- Validate frontend rendering
- Validate Shadow PR schema
- Validate Redis fallback
- Validate demo flow

### spec-reviewer

Reviews code and project quality.

Responsibilities:

- Review code organization
- Check consistency with `AGENTS.md`
- Check for secrets
- Check UI quality
- Check documentation quality

### spec-validator

Performs final validation.

Responsibilities:

- Confirm all quality gates pass
- Confirm final demo works
- Confirm `bob_sessions/` exists
- Confirm README explains IBM Bob usage
- Confirm submission checklist is complete

---

## Domain Specialists

### senior-frontend-architect

Expert in Next.js, TypeScript, Tailwind, shadcn/ui, and dashboard UX.

Responsibilities:

- Landing page
- Demo input page
- Loading page
- Results dashboard
- Responsive design
- UI polish
- Shadow PR visualization
- Blast radius map

### senior-backend-architect

Expert in backend APIs, Redis, job orchestration, and typed contracts.

Responsibilities:

- Health endpoint
- Analyze endpoint
- Analysis job creation
- Redis-backed job state
- Result caching
- Error handling
- API contract compliance

### product-intelligence-agent

Expert in RepoTwin product logic and IBM Bob usage.

Responsibilities:

- Shadow PR data
- Risk scoring logic
- Regression pack structure
- Implementation contract quality
- IBM Bob prompts
- IBM Bob evidence strategy
- Hackathon narrative coherence

### ui-ux-master

Expert in creating a professional developer-tool interface.

Responsibilities:

- Visual hierarchy
- Risk badges
- Impact badges
- Empty states
- Loading states
- Presentation quality
- Demo clarity

### refactor-agent

Expert in code quality and maintainability.

Responsibilities:

- Simplify components
- Remove duplication
- Improve naming
- Improve types
- Keep project clean

---

## Quality Framework

Each phase includes quality gates.

---

## Gate 1: Planning Quality

Threshold: 95%

Criteria:

- Product idea is clear
- Demo scenario is clear
- Shadow PR contract is defined
- API contract is documented
- Team roles are defined
- IBM Bob evidence strategy is defined
- Package manager is pnpm

Required artifacts:

```txt
AGENTS.md
docs/api-contract.md
docs/architecture.md
docs/bob-usage.md
types/shadow-pr.ts
data/sample-shadow-pr.json
pnpm-lock.yaml
```

---

## Gate 2: Development Quality

Threshold: 80%

Criteria:

- Frontend flow works
- Backend API works
- Redis job lifecycle works or has fallback
- Dashboard renders data
- TypeScript types are consistent
- No major broken states
- No `package-lock.json`
- No `yarn.lock`
- No npm commands in documentation

Required functionality:

```txt
Landing → Demo Input → Analyzing → Results Dashboard
```

Required endpoints:

```txt
GET /api/health
POST /api/analyze
```

Optional endpoints:

```txt
POST /api/analyses
GET /api/analyses/:id/status
GET /api/analyses/:id/result
```

---

## Gate 3: Production Readiness

Threshold: 85%

Criteria:

- App is deployed
- README is complete
- Demo script exists
- IBM Bob evidence exists
- Public GitHub repository is ready
- No credentials are committed
- Final submission checklist is complete
- Commands use pnpm consistently

Required artifacts:

```txt
README.md
docs/demo-script.md
docs/submission-checklist.md
bob_sessions/
```

---

## Agent Communication Protocol

Agents and team members communicate through structured artifacts.

Each phase should produce specific files:

```txt
docs/requirements.md
docs/architecture.md
docs/api-contract.md
docs/bob-usage.md
docs/demo-script.md
types/shadow-pr.ts
data/sample-shadow-pr.json
```

Rules:

- The next agent or team member must use previous outputs as input.
- Do not invent a new contract if one already exists.
- Do not change the Shadow PR schema without updating all affected files.
- Do not bypass the API contract.
- Do not create random files in root.
- Do not leave undocumented architectural decisions.
- Do not introduce npm, yarn, package-lock, or yarn.lock.

---

## Expected Output Structure

```txt
repotwin-by-bob/
├── app/
│   ├── page.tsx
│   ├── demo/
│   │   ├── page.tsx
│   │   ├── analyzing/
│   │   │   └── page.tsx
│   │   └── results/
│   │       └── page.tsx
│   └── globals.css
│
├── components/
│   ├── layout/
│   ├── shadow-pr/
│   ├── shared/
│   └── ui/
│
├── backend/
│   ├── src/
│   └── tests/
│
├── data/
│   ├── sample-shadow-pr.json
│   └── demo-scenarios.json
│
├── lib/
│   ├── api.ts
│   ├── data-loader.ts
│   └── utils.ts
│
├── types/
│   ├── shadow-pr.ts
│   └── api.ts
│
├── docs/
│   ├── api-contract.md
│   ├── architecture.md
│   ├── bob-usage.md
│   ├── demo-script.md
│   └── submission-checklist.md
│
├── bob_sessions/
│
├── .bob/
│   └── skills/
│
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── package.json
├── pnpm-lock.yaml
└── .env.example
```

Preserve the existing backend structure if it already exists.

Do not rewrite a working backend structure unless necessary.

---

## Key Integration Points

### Frontend to Backend

The frontend should use a typed API client.

Recommended file:

```txt
lib/api.ts
```

The frontend should support:

- Demo mode using local JSON
- Backend mode using API
- Fallback mode if the backend fails

### Backend to Redis

Redis should be used for:

- Analysis job status
- Progress messages
- Cached Shadow PR results
- Temporary analysis sessions
- Optional rate limiting
- Optional analysis history

Recommended Redis keys:

```txt
analysis:{analysisId}:status
analysis:{analysisId}:result
analysis:{analysisId}:progress
analysis:{analysisId}:metadata
repo:{repoName}:summary
demo:unimarket:reservation-flow
```

Add TTL to temporary keys.

Do not store secrets in Redis.

### IBM Bob Integration

IBM Bob is used as:

1. Development-time intelligence:
   - Building the app
   - Generating analysis
   - Improving code
   - Creating docs

2. Product-level intelligence:
   - Generating Shadow PR examples
   - Producing affected file analysis
   - Producing risk explanations
   - Producing regression packs
   - Producing implementation contracts

All relevant IBM Bob task sessions must be exported into:

```txt
bob_sessions/
```

---

## API Contract

The backend must return a Shadow PR response compatible with:

```txt
types/shadow-pr.ts
```

Main response shape:

```json
{
  "id": "shadow-pr-unimarket-reservations-001",
  "repository": {},
  "changeRequest": {},
  "analysis": {},
  "summary": {},
  "affectedFiles": [],
  "blastRadiusMap": {},
  "riskScore": {},
  "regressionPack": {},
  "implementationContract": {},
  "prBrief": {}
}
```

Do not change field names unless all affected frontend, backend, docs, and sample data files are updated together.

---

## Backend Requirements

The backend must support two modes.

### Demo Mode

Returns a stable, high-quality IBM Bob-assisted sample analysis.

Example request:

```json
{
  "repositoryName": "UniMarket",
  "changeRequest": "Add reservation flow before purchase.",
  "mode": "demo"
}
```

### Live Mode

Creates an analysis job and returns an analysis ID.

Example request:

```json
{
  "repositoryName": "UniMarket",
  "changeRequest": "Add reservation flow before purchase.",
  "mode": "live"
}
```

Minimum backend functionality:

```txt
GET /api/health
POST /api/analyze
```

Recommended job-based functionality:

```txt
POST /api/analyses
GET /api/analyses/:id/status
GET /api/analyses/:id/result
```

If live analysis is not fully implemented, simulate live mode using Redis and precomputed IBM Bob-assisted data.

---

## Frontend Requirements

Required pages:

```txt
/
  Landing page

/demo
  Change request input

/demo/analyzing
  Analysis progress page

/demo/results
  Shadow PR dashboard
```

Required dashboard sections:

1. Repo Summary
2. Shadow PR Summary
3. Blast Radius Map
4. Affected Files
5. Risk Score
6. Regression Pack
7. Safe Implementation Contract
8. Pull Request Brief
9. IBM Bob Evidence

UI style:

- Dark developer-tool aesthetic
- IBM-inspired blue/purple accents
- Clean cards
- Risk badges
- Impact badges
- Strong typography
- Responsive layout
- Minimal polished animations

Avoid:

- Toy-looking UI
- Random colors
- Excessive animations
- Unclear IBM Bob attribution

---

## Redis Requirements

Redis must have a real purpose.

Minimum Redis-backed flow:

1. Frontend sends an analysis request.
2. Backend creates `analysisId`.
3. Backend stores job status in Redis.
4. Backend stores progress messages in Redis.
5. Backend stores final Shadow PR result in Redis.
6. Frontend polls status/result endpoint.
7. Results dashboard renders final result.

Example status response:

```json
{
  "analysisId": "analysis_123",
  "status": "processing",
  "progress": 65,
  "message": "Calculating blast radius with IBM Bob-assisted analysis."
}
```

Example final response:

```json
{
  "analysisId": "analysis_123",
  "status": "completed",
  "result": {}
}
```

If Redis is unavailable, use in-memory storage for local development.

---

## Team Roles

### Member 1: Backend and Redis

Branch:

```txt
feature/backend-redis-analysis
```

Responsible for:

- Backend API
- Redis integration
- Analysis job lifecycle
- Health checks
- API contract compliance
- Backend fallback behavior

### Member 2: Frontend Dashboard

Branch:

```txt
feature/frontend-shadow-dashboard
```

Responsible for:

- Landing page
- Demo input page
- Analyzing page
- Results dashboard
- UI polish
- API integration

### Member 3: IBM Bob Workflow and Product Intelligence

Branch:

```txt
feature/bob-workflow-product-intelligence
```

Responsible for:

- `AGENTS.md`
- `.bob/skills/`
- Shadow PR sample data
- IBM Bob prompts
- Bob evidence docs
- API contract alignment
- Final narrative coherence

### Member 4: QA, Docs, Demo and Submission

Branch:

```txt
feature/demo-docs-submission
```

Responsible for:

- README
- Architecture docs
- Demo script
- Submission checklist
- Deployment checks
- Video/presentation support
- Final review

---

## Recommended Development Order

### Phase 1: Foundation

1. Define `types/shadow-pr.ts`.
2. Define `data/sample-shadow-pr.json`.
3. Define `docs/api-contract.md`.
4. Confirm backend endpoint shape.
5. Confirm frontend can render sample data.

### Phase 2: Backend and Redis

1. Add health endpoint.
2. Add analyze endpoint.
3. Add analysis job creation.
4. Add Redis-backed status/result storage.
5. Add fallback to in-memory storage.
6. Add backend documentation.

### Phase 3: Frontend Dashboard

1. Build landing page.
2. Build demo input.
3. Build analyzing page.
4. Build results dashboard.
5. Connect to backend or mock API.
6. Polish UI.

### Phase 4: IBM Bob Evidence

1. Export Bob task reports.
2. Add screenshots.
3. Update `docs/bob-usage.md`.
4. Add IBM Bob attribution in README and UI.

### Phase 5: Final Submission

1. Deploy app.
2. Test full demo.
3. Record video.
4. Create slides.
5. Verify public GitHub repo.
6. Verify `bob_sessions/`.
7. Submit to lablab.

---

## Best Practices

### For Working with Agents

- Start with the orchestrator role for complete project work.
- Use domain specialists for specific areas.
- Let each phase produce artifacts before moving forward.
- Trust quality gates for consistency.
- Review artifacts between phases.
- Keep prompts focused to avoid unnecessary token or Bobcoin usage.
- Require pnpm commands in all generated instructions.

### For Project Setup

- Create `AGENTS.md` as the source of truth.
- Keep `CLAUDE.md` small and pointing to `AGENTS.md`.
- Use `.bob/skills/` for IBM Bob reusable workflows.
- Keep documentation under `docs/`.
- Keep the Shadow PR contract stable.
- Use pnpm only.

### For Customization

- Adjust quality thresholds depending on time.
- Skip complex features only if the demo is at risk.
- Prefer working software over perfect architecture.
- Add Redis only where it supports job state, progress, or caching.
- Avoid building a generic chatbot.

---

## Troubleshooting

### Common Issues

**Agent ignores project scope**

Ask it to read `AGENTS.md` again and make focused edits only.

**Agent suggests npm commands**

Replace them with pnpm commands and remind the agent:

```txt
This project uses pnpm only. Never use npm install, npm i, or npm run.
```

**Backend response breaks frontend**

Check:

```txt
types/shadow-pr.ts
docs/api-contract.md
data/sample-shadow-pr.json
```

**Redis unavailable**

Use in-memory fallback and log a warning.

**Demo fails**

Use local sample data fallback.

**IBM Bob evidence missing**

Export Bob task sessions immediately and place them in:

```txt
bob_sessions/
```

**Quality gate fails**

Review the specific gate and fix only the failing area.

---

## Integration with External Systems

The system can integrate with:

- IBM Bob IDE
- IBM Bob task session exports
- Redis
- GitHub
- Vercel
- Optional watsonx services
- Optional CI/CD validation

However:

- IBM Bob IDE usage is central for judging.
- watsonx is optional.
- Do not depend on external services for the demo unless fallback exists.
- Do not expose credentials.
- Do not introduce npm or yarn.

---

## What Not To Do

Do not:

- Build a generic chatbot.
- Hide IBM Bob usage.
- Commit credentials.
- Leave `bob_sessions/` empty in the final submission.
- Let frontend invent a different response shape.
- Let backend return unstable JSON.
- Add Redis without using it for job state or caching.
- Spend too much time on deep static analysis before the demo works.
- Rewrite working backend code without reason.
- Create random documentation files in root.
- Change the Shadow PR contract without updating related files.
- Use `npm install`.
- Use `npm i`.
- Use `npm run`.
- Commit `package-lock.json`.
- Commit `yarn.lock`.

---

## Response Rules for AI Assistants

When working on this repository:

1. Read `AGENTS.md` first.
2. Inspect existing files before editing.
3. Make focused changes.
4. Do not rewrite unrelated files.
5. Prefer code changes over long explanations.
6. Preserve existing project structure unless explicitly asked to reorganize.
7. Use pnpm commands only.
8. After changes, return:
   - files changed
   - what was implemented
   - commands to run
   - next recommended task

For large tasks, split the work into safe phases and implement one phase at a time.

---

## Current Product Priority

The priority is to build a complete, impressive MVP, not a tiny mockup.

The ideal MVP includes:

- Next.js frontend
- Backend API
- Redis-backed analysis jobs
- Static IBM Bob-assisted analysis fallback
- Shadow PR dashboard
- Blast radius visualization
- Risk score
- Regression pack
- Implementation contract
- PR brief
- IBM Bob evidence
- Public deployment

The project should feel like a serious developer tool, not a static landing page.