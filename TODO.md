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

- [ ] **4. AI Analysis Logic**
  - Create service to fetch URL content (via requests/BeautifulSoup)
  - Call Anthropic API (Claude-3.5-Sonnet) for analysis
  - Prompt: "Analyze this content: [text]. Generate 5 tags, 1-sentence summary, suggested alias. Detect toxicity."
  - Handle key prompt if not set

- [ ] **5. Update Shorten Endpoint**
  - POST integrates AI analysis
  - Saves tags/summary/suggested_alias
  - Offers custom alias or AI-suggested
  - Reject if toxic

- [ ] **6. URL Preview**
  - Add service using Puppeteer (headless) to generate PNG preview
  - Store in Mongo GridFS
  - Add /preview/{short_code} endpoint

- [ ] **7. Update Redirect**
  - Ensure 302 redirect
  - Log clicks

- [ ] **8. Rate Limiting & Analytics**
  - SlowAPI for endpoints
  - Redis for real-time clicks

- [ ] **9. Frontend Base Updates**
  - Apply dark red/grey theme in tailwind.config (extend colors)
  - Dark red #8B0000 bg, grey #4B5563 accents
  - Gradients: linear-gradient(to right, #8B0000, #4B0000)
  - Init shadcn/ui components (button, input, etc.)
  - Set up next-intl for en/es

- [ ] **10. Auth Pages Refactor**
  - /register, /login with shadcn forms
  - Animations (Framer Motion fade-in)
  - i18n support

- [ ] **11. Shorten Page Update**
  - Form with AI suggestions
  - Display tags/summary post-analysis
  - Animate reveal
  - Placeholder: AI icon src="/placeholder-ai-icon.png" w=48 h=48, desc: Glowing red brain analyzing links

- [ ] **12. Dashboard**
  - List URLs with AI tags/summaries
  - Previews (lazy load)
  - Stats graphs (Recharts with gradients)
  - Animations (stagger children)

- [ ] **13. Admin Dashboard**
  - Top URLs
  - Delete functionality
  - shadcn tables
  - i18n support

- [ ] **14. Performance Optimizations**
  - Code splitting in Next.js
  - Lazy loading components/images
  - SWR for data fetching

- [ ] **15. CI/CD Setup**
  - GitHub Actions workflow for tests/build/deploy
  - E.g., to Vercel/Docker

- [ ] **16. Tests**
  - Pytest for backend (AI mocks, endpoints)
  - Jest/RTL for frontend

- [ ] **17. Dockerize**
  - Update Dockerfiles/compose for new deps
  - Include Puppeteer

- [ ] **18. Final Polish**
  - Error pages (animated 404 with red gradients)
  - SEO
  - a11y
  - Update README.md with new features, setup instructions (including AI key)

---

## Progress Log

| Task | Status | Date |
|------|--------|------|
| 1. Initial Setup & Dependencies | DONE | 2026-01-09 |
| 2. Backend Config & Models | DONE | 2026-01-09 |
| 3. User Authentication Refactor | DONE | 2026-01-09 |
