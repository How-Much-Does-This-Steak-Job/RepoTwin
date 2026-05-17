# RepoTwin Frontend

Next.js 16 frontend for the RepoTwin Shadow PR analysis platform.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui
- **Icons**: lucide-react
- **Package Manager**: pnpm (required)

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (install with `npm install -g pnpm`)

### Installation

```bash
pnpm install
```

### Development

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
pnpm build
pnpm start
```

### Linting

```bash
pnpm lint
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Landing page
│   ├── layout.tsx         # Root layout
│   ├── globals.css        # Global styles
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
├── types/
│   └── api.ts             # TypeScript contracts
├── data/
│   └── sample-shadow-pr.json  # Demo data
└── public/
    └── data/              # Public assets
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Features

- **Landing Page**: Product introduction and demo CTA
- **Demo Input**: Natural language change request input
- **Analysis Progress**: Real-time progress tracking with WebSocket
- **Results Dashboard**: Comprehensive Shadow PR visualization
  - Blast Radius Map
  - Risk Assessment
  - Affected Files
  - Implementation Plan
  - Test Recommendations
  - PR Brief

## API Integration

The frontend communicates with the FastAPI backend via a typed API client (`lib/api.ts`).

### Demo Mode
Uses local sample data from `data/sample-shadow-pr.json` for offline demos.

### Live Mode
Connects to backend API for real-time analysis.

## Development Notes

- Always use `pnpm` (never npm or yarn)
- Follow TypeScript strict mode
- Use shadcn/ui components for consistency
- Maintain responsive design
- Keep IBM Bob attribution visible

## Built with IBM Bob IDE

This frontend was developed using IBM Bob IDE for:
- Component generation
- TypeScript type safety
- API client implementation
- UI/UX design decisions
- Documentation

---

**Part of RepoTwin by Bob - IBM Bob Hackathon Project**
