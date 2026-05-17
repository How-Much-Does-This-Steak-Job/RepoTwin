# RepoTwin by Bob

> **Simulate the blast radius of a code change before writing code.**

RepoTwin is an AI-driven developer intelligence platform that transforms natural-language change requests into a comprehensive **Shadow PR** — allowing developers to understand the full impact of a proposed change before implementation.

Built for the **IBM Bob Hackathon** to demonstrate how IBM Bob IDE can revolutionize software development by providing deep repository context and change impact analysis.

---

## 🎯 What is RepoTwin?

RepoTwin answers the critical question every developer faces:

> "If I make this change, what else breaks?"

Instead of discovering issues after coding, RepoTwin generates a **Shadow PR** that shows:

- 📁 **Affected Files** - Which files need changes (direct and indirect)
- 💥 **Blast Radius** - How far the impact spreads across your codebase
- ⚠️ **Risk Assessment** - What can go wrong and how to mitigate it
- 🧪 **Regression Pack** - What tests need to be created or updated
- 📋 **Implementation Contract** - Safe step-by-step implementation plan
- 📝 **PR Brief** - Ready-to-use Pull Request description

---

## 🤖 Built with IBM Bob IDE

This project extensively uses **IBM Bob IDE** throughout development:

### Development-Time Intelligence
- Repository structure analysis
- Code architecture understanding
- Implementation planning
- Documentation generation
- Test strategy design

### Product-Level Intelligence
- Shadow PR generation logic
- Affected file analysis
- Risk scoring algorithms
- Regression test recommendations
- Implementation contract creation

### Runtime Enhancement (Optional)
- **watsonx.ai** integration for deeper semantic analysis
- LLM-enhanced impact prediction
- Natural language change request processing

**Evidence**: See `bob_sessions/` directory for exported IBM Bob task session reports and screenshots demonstrating Bob's usage throughout the project.

---

## 🎬 Demo Scenario

**Repository**: UniMarket (University Marketplace Android App)

**Change Request**: "Add reservation flow before purchase"

**What Sounds Simple**:
- Add a reservation button
- Store reservation in database
- Update purchase flow

**What RepoTwin Reveals**:
- 12 files affected across 5 modules
- Breaking API changes required
- State machine complexity increases from 4 to 7 states
- Android UI needs complete refactor
- Cache invalidation strategy must change
- Analytics events need updates
- 28 hours estimated implementation time
- Medium-high risk level with 6 major risk factors

**Key Insight**: A "simple" feature request secretly affects the entire system architecture.

---

## 🏗️ Architecture

### Frontend (Next.js + TypeScript)
```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── page.tsx           # Landing page
│   ├── demo/              # Demo flow
│   │   ├── page.tsx       # Change request input
│   │   ├── analyzing/     # Progress tracking
│   │   └── results/       # Shadow PR dashboard
│   └── repos/             # Repository management
├── components/
│   ├── ui/                # shadcn/ui components
│   └── repo/              # Repository components
├── lib/
│   └── api.ts             # Typed API client
└── types/
    └── api.ts             # TypeScript contracts
```

### Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── api/               # REST endpoints
│   │   ├── analysis.py    # Analysis lifecycle
│   │   ├── shadow_pr.py   # Shadow PR generation
│   │   └── repos.py       # Repository management
│   ├── core/              # Core engines
│   │   ├── code_parser.py # Tree-sitter parsing
│   │   ├── impact_engine.py # NetworkX impact analysis
│   │   ├── ibm_bob.py     # IBM watsonx client
│   │   └── risk_calculator.py # Risk scoring
│   ├── services/          # Business logic
│   │   ├── analysis_service.py
│   │   ├── shadow_pr_service.py
│   │   └── demo_service.py
│   └── redis/             # Job orchestration
│       ├── client.py      # Redis connection
│       └── store.py       # Job state management
└── tests/                 # Comprehensive test suite
```

### Key Technologies
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, Python 3.11+, Pydantic
- **Analysis**: Tree-sitter (code parsing), NetworkX (impact graph)
- **AI**: IBM watsonx.ai (optional runtime enhancement)
- **Orchestration**: Redis (job state) with in-memory fallback
- **Package Manager**: **pnpm only** (no npm/yarn)

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+
- Redis (optional, has in-memory fallback)
- IBM watsonx API key (optional, has heuristic fallback)

### Frontend Setup
```bash
cd frontend
pnpm install
pnpm dev
```

Frontend runs at `http://localhost:3000`

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

### Environment Configuration

**Backend** (`backend/.env`):
```env
# Optional: IBM watsonx.ai
WATSONX_API_KEY=your_key_here
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Optional: Redis
REDIS_URL=redis://localhost:6379

# App Config
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker Compose (Full Stack)
```bash
docker-compose up
```

---

## 📖 API Endpoints

### Analysis Lifecycle
```
POST   /api/analysis              # Create analysis job
GET    /api/analysis/{id}         # Get analysis status
GET    /api/analysis/{id}/results # Get analysis results
GET    /api/analysis/{id}/progress # Get progress updates
WS     /api/analysis/{id}/ws      # WebSocket progress stream
```

### Shadow PR
```
POST   /api/analysis/{id}/shadow-pr/preview  # Generate Shadow PR
```

### Repository Management
```
GET    /api/repos                 # List repositories
POST   /api/repos/connect         # Connect repository
GET    /api/repos/{id}/files      # List repository files
```

### Health Check
```
GET    /api/health                # Service health status
```

See `docs/api-contract.md` for detailed API documentation.

---

## 🎨 Shadow PR Dashboard

The results dashboard displays:

1. **Repository Summary** - Project context and metadata
2. **Analysis Overview** - High-level impact summary
3. **Blast Radius Visualization** - Direct/indirect/total impact metrics
4. **Risk Assessment** - Risk score gauge with mitigation strategies
5. **Affected Files** - Detailed file-by-file impact analysis
6. **Risk Factors** - Comprehensive risk breakdown
7. **Test Recommendations** - New tests needed and coverage gaps
8. **Implementation Plan** - Phase-by-phase implementation contract
9. **PR Brief** - Copy-ready Pull Request description
10. **IBM Bob Evidence** - Clear attribution of AI assistance

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
pnpm test
pnpm lint
```

---

## 📚 Documentation

- `AGENTS.md` - AI agent guidelines and project rules
- `HACKATHON_PLAN.md` - Original 48-hour implementation plan
- `docs/api-contract.md` - API specification
- `docs/architecture.md` - System architecture
- `docs/bob-usage.md` - IBM Bob usage documentation
- `docs/demo-script.md` - Presentation demo script
- `docs/submission-checklist.md` - Hackathon submission checklist

---

## 🎯 IBM Bob Hackathon Alignment

### Application of Technology (25%)
- ✅ Extensive use of IBM Bob IDE for development
- ✅ Optional watsonx.ai runtime integration
- ✅ Clear demonstration of AI-assisted development workflow
- ✅ Exported task sessions in `bob_sessions/`

### Presentation (25%)
- ✅ Clear product narrative: "Simulate blast radius before coding"
- ✅ Compelling demo with UniMarket scenario
- ✅ Professional UI with IBM-inspired design
- ✅ Strong IBM Bob branding throughout

### Business Value (25%)
- ✅ Solves real developer pain point
- ✅ Reduces regression bugs and production incidents
- ✅ Accelerates code review process
- ✅ Improves team velocity and code quality

### Originality (25%)
- ✅ Novel "Shadow PR" concept
- ✅ Unique blast radius visualization
- ✅ Innovative use of IBM Bob for repository intelligence
- ✅ Practical developer tool, not generic chatbot

---

## 🛠️ Development Commands

**Always use pnpm** (never npm or yarn):

```bash
# Frontend
pnpm install          # Install dependencies
pnpm dev              # Development server
pnpm build            # Production build
pnpm lint             # Run linting

# Backend
pip install -r requirements.txt  # Install dependencies
uvicorn app.main:app --reload    # Development server
pytest                           # Run tests
```

---

## 🚢 Deployment

### Frontend (Vercel)
```bash
cd frontend
pnpm build
# Deploy to Vercel
```

### Backend (Docker)
```bash
cd backend
docker build -t repotwin-backend .
docker run -p 8000:8000 repotwin-backend
```

### Full Stack (Docker Compose)
```bash
docker-compose up -d
```

---

## 📊 Project Status

- ✅ Core analysis engine
- ✅ Shadow PR generation
- ✅ Frontend dashboard
- ✅ Redis job orchestration
- ✅ watsonx.ai integration
- ✅ Demo data and scenarios
- ✅ Comprehensive documentation
- ✅ IBM Bob evidence collection

---

## 🤝 Team

Built by a distributed team using IBM Bob IDE for the IBM Bob Hackathon.

**Roles**:
- Backend & Redis: Analysis engine, job orchestration
- Frontend: Dashboard UI, user experience
- Product Intelligence: IBM Bob workflows, Shadow PR design
- QA & Documentation: Testing, docs, submission prep

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **IBM Bob IDE** - For revolutionizing AI-assisted development
- **IBM watsonx.ai** - For optional runtime LLM enhancement
- **lablab.ai** - For hosting the hackathon
- **Tree-sitter** - For robust code parsing
- **NetworkX** - For impact graph analysis

---

## 🔗 Links

- **GitHub Repository**: [RepoTwin](https://github.com/yourusername/repotwin)
- **Live Demo**: [repotwin.vercel.app](https://repotwin.vercel.app)
- **IBM Bob IDE**: [IBM Bob](https://www.ibm.com/bob)
- **Hackathon**: [lablab.ai IBM Bob Hackathon](https://lablab.ai)

---

**Built with ❤️ using IBM Bob IDE**

*Simulate the blast radius. Code with confidence.*