# EclipseInsight TODO

Refactoring EclipseURL into EclipseInsight with AI-powered content analysis and tagging.

## Tasks

- [x] **1. Initial Setup & Dependencies** [DONE]
  - Scan repo (clone of EclipseURL)
  - Check .gitignore includes .env, node_modules, etc.
  - Install/update backend deps: fastapi==0.124.*, anthropic==0.74.0, motor, redis, slowapi, etc.
  - Install/update frontend deps: next@15.4, tailwindcss@4.0, framer-motion@12.25.0, shadcn-ui init, next-intl@4.7.0
  - Create .env.example with ANTHROPIC_API_KEY placeholder

- [x] **2. Backend Config & Models** [DONE]
  - Switch DB to MongoDB with Motor async driver
  - Migrate models: User, ShortURL (add fields: tags[list], summary[str], suggested_alias[str]), ClickLog
  - Set up Anthropic client in a service file (load key from os.environ, prompt user if missing during dev)

- [x] **3. User Authentication Refactor** [DONE]
  - Ensure JWT/OAuth2 works
  - Add endpoint tweaks for AI features

- [x] **4. AI Analysis Logic** [DONE]
  - Create service to fetch URL content (via requests/BeautifulSoup)
  - Call Anthropic API (Claude-3.5-Sonnet) for analysis
  - Prompt: "Analyze this content: [text]. Generate 5 tags, 1-sentence summary, suggested alias. Detect toxicity."
  - Handle key prompt if not set

- [x] **5. Update Shorten Endpoint** [DONE]
  - POST integrates AI analysis
  - Saves tags/summary/suggested_alias
  - Offers custom alias or AI-suggested
  - Reject if toxic

- [x] **6. URL Preview** [DONE]
  - Add service using Puppeteer (headless) to generate PNG preview
  - Store in Mongo GridFS
  - Add /preview/{short_code} endpoint

- [x] **7. Update Redirect** [DONE]
  - Ensure 302 redirect
  - Log clicks

- [x] **8. Rate Limiting & Analytics** [DONE]
  - SlowAPI for endpoints
  - Redis for real-time clicks

- [x] **9. Frontend Base Updates** [DONE]
  - Apply dark red/grey theme in tailwind.config (extend colors)
  - Dark red #8B0000 bg, grey #4B5563 accents
  - Gradients: linear-gradient(to right, #8B0000, #4B0000)
  - Init shadcn/ui components (button, input, etc.)
  - Set up next-intl for en/es

- [x] **10. Auth Pages Refactor** [DONE]
  - /register, /login with shadcn forms
  - Animations (Framer Motion fade-in)
  - i18n support

- [x] **11. Shorten Page Update** [DONE]
  - Form with AI suggestions
  - Display tags/summary post-analysis
  - Animate reveal
  - AI analysis options (skip/use suggested alias)

- [x] **12. Dashboard** [DONE]
  - List URLs with AI tags/summaries
  - AI analyzed count stat card
  - Tag search functionality
  - Animations (stagger children)

- [x] **13. Admin Dashboard** [DONE]
  - Top URLs with search
  - Delete functionality with confirmation
  - Stats overview cards
  - Activity stats (today/week)

- [x] **14. Performance Optimizations** [DONE]
  - Code splitting in Next.js (automatic)
  - SWR hooks for data fetching
  - Standalone output for Docker

- [x] **15. CI/CD Setup** [DONE]
  - GitHub Actions workflow for tests/build/deploy
  - Backend tests, frontend tests, Docker build

- [x] **16. Tests** [DONE]
  - Pytest for backend (75 tests passing)
  - Jest/RTL for frontend (25 tests passing)

- [x] **17. Dockerize** [DONE]
  - Update Dockerfiles/compose for new deps
  - Include Chromium for Pyppeteer screenshots
  - Added Anthropic API key config

- [x] **18. Final Polish** [DONE]
  - Error pages (animated 404 with red gradients)
  - SWR hooks for data fetching
  - AI analysis display in dashboard and shorten page

---

## Progress Log

| Task | Status | Date |
|------|--------|------|
| 1. Initial Setup & Dependencies | DONE | 2026-01-09 |
| 2. Backend Config & Models | DONE | 2026-01-09 |
| 3. User Authentication Refactor | DONE | 2026-01-09 |
| 4. AI Analysis Logic | DONE | 2026-01-09 |
| 5. Update Shorten Endpoint | DONE | 2026-01-09 |
| 6. URL Preview | DONE | 2026-01-09 |
| 7. Update Redirect | DONE | 2026-01-09 |
| 8. Rate Limiting & Analytics | DONE | 2026-01-09 |
| 9. Frontend Base Updates | DONE | 2026-01-09 |
| 10. Auth Pages Refactor | DONE | 2026-01-09 |
| 11. Shorten Page Update | DONE | 2026-01-09 |
| 12. Dashboard | DONE | 2026-01-09 |
| 13. Admin Dashboard | DONE | 2026-01-09 |
| 14. Performance Optimizations | DONE | 2026-01-09 |
| 15. CI/CD Setup | DONE | 2026-01-09 |
| 16. Tests | DONE | 2026-01-09 |
| 17. Dockerize | DONE | 2026-01-09 |
| 18. Final Polish | DONE | 2026-01-09 |
