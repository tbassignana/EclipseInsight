# PROMPT.MD

You are Claude, an AI coding expert. Refactor the existing "EclipseURL" project into "EclipseInsight", adding AI-powered content analysis and tagging. Build off the baseline EclipseURL (FastAPI backend, Next.js frontend, MongoDB, etc.). Use a "ralph-loop" process: Complete ONE item from TODO.md at a time, write unit/integration tests, debug if tests fail, mark as complete only when tests pass, update GitHub (commit/push changes), then update TODO.md by marking the item [DONE], commit the changes to GitHub, then compress the entire session history into a summary, and loop back. Respond ONLY with: 1) Code changes/files created, 2) Tests written/ran/results, 3) Debug logs if needed, 4) Updated TODO.md, 5) GitHub update confirmation, 6) Compressed session summary.

First response: Create TODO.md with the granular list below, then start the loop with item 1.

Project specs:
- Backend: Use FastAPI (latest v0.124+) with Python 3.12 for API. Integrate Anthropic API (SDK v0.74.0) for AI (NLP to scrape/analyze URL content, generate tags/summaries/suggested aliases using Claude models). Prompt user for ANTHROPIC_API_KEY when first needed (e.g., in env setup); store in .env (gitignore'd, never expose in code). Include user auth (JWT with OAuth2), rate limiting (SlowAPI), analytics (track clicks with Redis), URL expiration. Store data in MongoDB (via Motor or PyMongo) for URLs/users, Redis for caching/analytics.
- Frontend: Use Next.js 15.4+ with React 18, TypeScript, Tailwind CSS v4.0+ for dark theme (dark red #8B0000 bg, grey #4B5563 accents, gradients like linear-gradient(to right, #8B0000, #4B0000)), shadcn/ui for components, Framer Motion v12.25.0+ for animations (e.g., fade-ins, hover scales), next-intl v4.7.0+ for i18n (en, es support).
- Features: Retain core (shorten, redirect 302, stats); Add AI: On shorten, use Anthropic to analyze content (summary, tags, suggest alias), auto-reject toxic/harmful. URL preview generation (e.g., via ScreenshotLayer or Puppeteer). Admin dashboard, CI/CD with GitHub Actions, performance opts (lazy load, code split).
- Security: Input validation, HTTPS, CORS. Env vars in .gitignore.
- Deployment-ready: Dockerfiles, docker-compose with mongo, redis, nginx.
- Flashy UI: Dark theme, animated loaders (shadcn spinners with gradients), gradient buttons, responsive (mobile-first).
- Image placeholders: Use <Image src="/placeholder-[name].png" alt="[desc]" width={w} height={h} /> from next/image. Specify: PNG, dimensions, desc (e.g., futuristic AI tag icon in neon red).

Initial granular to-do list for TODO.md (Claude: Create TODO.md with this, then proceed):

1. Scan repo which is a clone of EclipseURL. Check .gitignore with .env, node_modules, etc. Install/update deps: backend (fastapi==0.124.*, anthropic==0.74.0, motor, redis, slowapi, etc.); frontend (next@15.4, tailwindcss@4.0, framer-motion@12.25.0, shadcn-ui init, next-intl@4.7.0). Create .env.example with ANTHROPIC_API_KEY placeholder.

2. Update backend config: Switch DB to MongoDB with Motor async driver. Migrate models: User, ShortURL (add fields: tags[list], summary[str], suggested_alias[str]), ClickLog. Set up Anthropic client in a service file (load key from os.environ, prompt user if missing during dev).

3. Refactor user auth: Ensure JWT/OAuth2 works, add endpoint tweaks for AI features.

4. Implement AI analysis logic: Create service to fetch URL content (via requests/BeautifulSoup), call Anthropic API (Claude-3.5-Sonnet) for analysis (prompt: "Analyze this content: [text]. Generate 5 tags, 1-sentence summary, suggested alias. Detect toxicity."). Handle key prompt if not set.

5. Update shorten endpoint: POST integrates AI analysis, saves tags/summary/suggested_alias, offers custom alias or AI-suggested. Reject if toxic.

6. Implement URL preview: Add service using Puppeteer (headless) to generate PNG preview, store in Mongo GridFS. Add /preview/{short_code} endpoint.

7. Update redirect: Ensure 302 redirect, log clicks.

8. Add rate limiting and analytics: SlowAPI for endpoints, Redis for real-time clicks.

9. Update frontend base: Apply dark red/grey theme in tailwind.config (extend colors), init shadcn/ui components (button, input, etc.), set up next-intl for en/es.

10. Refactor auth pages: /register, /login with shadcn forms, animations (Framer Motion fade-in), i18n.

11. Update shorten page: Form with AI suggestions (display tags/summary post-analysis, animate reveal), placeholder: AI icon src="/placeholder-ai-icon.png" w=48 h=48, desc: Glowing red brain analyzing links.

12. Add dashboard: List URLs with AI tags/summaries, previews (lazy load), stats graphs (Recharts with gradients), animations (stagger children).

13. Add admin dashboard: Top URLs, delete, with shadcn tables, i18n.

14. Implement performance opts: Code splitting in Next.js, lazy loading components/images, SWR for data fetching.

15. Set up CI/CD: GitHub Actions workflow for tests/build/deploy (e.g., to Vercel/Docker).

16. Add tests: Pytest for backend (AI mocks, endpoints), Jest/RTL for frontend.

17. Dockerize: Update Dockerfiles/compose for new deps (include Puppeteer).

18. Final polish: Error pages (animated 404 with red gradients), SEO, a11y. Update README.md with new features, setup instructions (including AI key).