# EclipseInsight

A modern, full-stack URL shortener with AI-powered content analysis and advanced analytics, built with FastAPI and Next.js.

## Features

### Core Features
- **URL Shortening**: Generate short, memorable links with optional custom aliases
- **QR Code Generation**: Generate downloadable QR code PNGs for any short URL
- **Click Analytics**: Track clicks with detailed breakdowns by device, browser, OS, country, and referrer
- **Date Range Filtering**: Filter analytics by custom date ranges for campaign analysis
- **CSV Analytics Export**: Download click analytics as CSV for external analysis
- **Real-time Statistics**: Live click counting and analytics via Redis
- **Bulk URL Management**: Delete multiple URLs at once with partial-success reporting
- **User Authentication**: Secure JWT-based authentication with role-based access
- **User URL Quotas**: Configurable per-user URL limits to prevent abuse (admins bypass)
- **Rate Limiting**: Protect against abuse with configurable rate limits
- **Admin Dashboard**: Platform-wide statistics and URL management

### AI-Powered Features
- **Smart Tag Generation**: Automatically generate relevant tags for URLs using Claude AI
- **Content Summarization**: AI-generated summaries of linked content
- **Toxicity Detection**: Automatic detection of potentially harmful content
- **Suggested Aliases**: AI-powered memorable alias suggestions

### URL Preview System
- **Open Graph Extraction**: Automatic extraction of page titles, descriptions, and images
- **Screenshot Generation**: Automated preview screenshots using Puppeteer
- **Preview Storage**: Screenshots stored in MongoDB GridFS

### User Experience
- **Dark/Light Mode**: Tesla-inspired theming with smooth transitions
- **Responsive Design**: Mobile-first UI with Framer Motion animations
- **Interactive Charts**: Analytics visualization with Recharts

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database with Beanie ODM
- **Redis** - Caching and real-time analytics
- **Anthropic Claude** - AI-powered content analysis
- **JWT** - Secure authentication
- **SlowAPI** - Rate limiting
- **Pyppeteer** - Automated screenshot generation
- **BeautifulSoup** - HTML parsing for URL previews

### Frontend
- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component patterns
- **Framer Motion** - Smooth animations
- **Recharts** - Analytics data visualization
- **SWR** - Data fetching and caching
- **Lucide React** - Icon library

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| **Python** | 3.12+ | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org/) or use `nvm install 20` |
| **MongoDB** | 7+ | [mongodb.com/docs/manual/installation](https://www.mongodb.com/docs/manual/installation/) |
| **Redis** | 7+ | [redis.io/docs/install](https://redis.io/docs/install/) |
| **Docker** (optional) | Latest | [docker.com/get-started](https://www.docker.com/get-started/) |

### Verify Installations

```bash
# Check Python version
python --version  # Should show Python 3.12.x or higher

# Check Node.js version
node --version    # Should show v20.x.x or higher

# Check npm version
npm --version     # Should show 10.x.x or higher

# Check MongoDB (if installed locally)
mongod --version

# Check Redis (if installed locally)
redis-server --version

# Check Docker (optional)
docker --version
docker-compose --version
```

---

## Quick Start

### Option 1: Docker (Recommended)

The easiest way to get started is using Docker, which handles all dependencies automatically.

#### Development Mode (with hot reload)

```bash
# Clone the repository
git clone https://github.com/yourusername/eclipseurl.git
cd eclipseurl

# Copy environment example
cp .env.example .env

# Start all services with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

#### Production Mode

```bash
# Clone and set up environment
git clone https://github.com/yourusername/eclipseurl.git
cd eclipseurl
cp .env.example .env

# IMPORTANT: Edit .env with secure production values
# - Change SECRET_KEY to a strong random string
# - Set secure MongoDB credentials
# - Update BASE_URL and NEXT_PUBLIC_API_URL for your domain

# Build and run all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove all data (WARNING: destroys database)
docker-compose down -v
```

### Option 2: Local Development (Manual Setup)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/eclipseurl.git
cd eclipseurl
```

#### Step 2: Start MongoDB and Redis

**macOS (using Homebrew):**
```bash
brew services start mongodb-community
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo systemctl start mongod
sudo systemctl start redis-server
```

**Windows:**
```powershell
# Start MongoDB
net start MongoDB

# Start Redis (if installed via chocolatey)
redis-server
```

Or use Docker for just the databases:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

#### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
# Edit .env with your configuration (see Environment Variables section)

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

#### Step 4: Frontend Setup

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run the development server
npm run dev
```

The frontend will be available at: http://localhost:3000

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the project root (or `backend/` directory):

```bash
# Application
APP_NAME=EclipseInsight
DEBUG=true

# MongoDB Configuration
MONGO_ROOT_USER=eclipse
MONGO_ROOT_PASSWORD=your_secure_password_here
MONGO_DB=eclipse_insight

# For local development without auth:
# MONGODB_URL=mongodb://localhost:27017/eclipse_insight

# For authenticated MongoDB:
MONGODB_URL=mongodb://eclipse:your_secure_password_here@localhost:27017/eclipse_insight?authSource=admin

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Security - CHANGE THIS IN PRODUCTION!
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# URLs
BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# CORS Origins (JSON array)
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_SHORTEN=10/minute
RATE_LIMIT_REGISTER=5/minute

# Short Code Configuration
SHORT_CODE_LENGTH=6

# URL Quotas (0 = unlimited, admins always bypass)
MAX_URLS_PER_USER=500

# AI Features (Optional - enables smart tagging and content analysis)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=EclipseInsight
```

### Generating a Secure SECRET_KEY

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

---

## Docker Deployment

### Docker Compose Services

| Service | Description | Port |
|---------|-------------|------|
| `mongodb` | MongoDB database | 27017 |
| `redis` | Redis cache | 6379 |
| `backend` | FastAPI application | 8000 |
| `frontend` | Next.js application | 3000 |

### Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Compose File | `docker-compose.dev.yml` | `docker-compose.yml` |
| Hot Reload | Yes | No |
| Volume Mounts | Source code mounted | Built images only |
| Environment | Development | Production |
| Health Checks | Minimal | Full |

### Useful Docker Commands

```bash
# Build without cache (useful after dependency changes)
docker-compose build --no-cache

# Scale a service
docker-compose up -d --scale backend=3

# View resource usage
docker stats

# Enter a container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# View MongoDB data
docker-compose exec mongodb mongosh -u eclipse -p your_password

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## GitHub Actions CI/CD

The project includes a comprehensive CI/CD pipeline in `.github/workflows/ci.yml`.

### Pipeline Jobs

| Job | Description | Triggers |
|-----|-------------|----------|
| `backend-lint` | Runs Ruff, Black, and isort checks | Push/PR to main, develop |
| `backend-test` | Runs pytest with coverage | Push/PR to main, develop |
| `frontend-lint` | Runs ESLint and TypeScript checks | Push/PR to main, develop |
| `frontend-test` | Runs Jest tests with coverage | Push/PR to main, develop |
| `frontend-build` | Verifies production build | Push/PR to main, develop |
| `docker-build` | Builds Docker images | Push to main only |

### Running CI Locally

You can run the same checks locally before pushing:

```bash
# Backend checks
cd backend
pip install ruff black isort
ruff check app/
black --check app/
isort --check-only app/

# Backend tests
pytest -v --cov=app

# Frontend checks
cd frontend
npm run lint
npx tsc --noEmit

# Frontend tests
npm run test:coverage

# Frontend build
npm run build
```

### GitHub Actions Secrets

For the CI to work properly, configure these secrets in your GitHub repository:

| Secret | Description |
|--------|-------------|
| `CODECOV_TOKEN` | (Optional) For coverage reporting |

---

## Project Structure

```
eclipseinsight/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── admin.py      # Admin endpoints
│   │   │   ├── analytics.py  # Click analytics & breakdown stats
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── redirect.py   # URL redirect handler
│   │   │   └── urls.py       # URL management endpoints
│   │   ├── core/             # Config, security, database
│   │   │   ├── config.py     # Application settings
│   │   │   ├── database.py   # MongoDB/Redis connections
│   │   │   └── security.py   # JWT, password hashing
│   │   ├── models/           # Beanie document models
│   │   │   ├── click.py      # Click tracking model
│   │   │   ├── url.py        # URL model with AI fields
│   │   │   └── user.py       # User model
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic
│   │   │   ├── ai.py         # AI content analysis (Anthropic)
│   │   │   ├── analytics.py  # Statistics aggregation & CSV export
│   │   │   ├── auth.py       # Authentication service
│   │   │   ├── click.py      # Click tracking service
│   │   │   ├── preview.py    # URL preview & screenshots
│   │   │   ├── qrcode.py     # QR code image generation
│   │   │   └── url.py        # URL CRUD, quotas, short code gen
│   │   └── main.py           # FastAPI app initialization
│   ├── tests/                # Pytest tests (146 tests)
│   ├── Dockerfile            # Production Dockerfile
│   ├── Dockerfile.dev        # Development Dockerfile
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (App Router)
│   │   │   ├── dashboard/    # User dashboard
│   │   │   ├── admin/        # Admin dashboard
│   │   │   ├── shorten/      # URL creation page
│   │   │   └── [shortCode]/  # Dynamic redirect route
│   │   ├── components/       # React components
│   │   │   ├── layout/       # Layout components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   └── providers/    # Context providers
│   │   ├── context/          # React context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Utilities and API client
│   │   ├── types/            # TypeScript type definitions
│   │   └── __tests__/        # Jest tests
│   ├── public/               # Static assets
│   ├── Dockerfile            # Production Dockerfile
│   ├── Dockerfile.dev        # Development Dockerfile
│   └── package.json          # Node.js dependencies
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD
├── docker-compose.yml        # Production deployment
├── docker-compose.dev.yml    # Development with hot reload
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| GET | `/api/v1/auth/me` | Get current user info |
| POST | `/api/v1/auth/forgot-password` | Request password reset token |
| POST | `/api/v1/auth/reset-password` | Reset password with token |

### URLs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/urls/shorten` | Create short URL (with optional AI analysis) |
| GET | `/api/v1/urls` | List user's URLs |
| GET | `/api/v1/urls/preview` | Fetch URL preview metadata (Open Graph) |
| GET | `/api/v1/urls/{short_code}` | Get URL details |
| GET | `/api/v1/urls/{short_code}/stats` | Get URL analytics |
| GET | `/api/v1/urls/{short_code}/qr` | Generate QR code PNG (no auth required) |
| PATCH | `/api/v1/urls/{short_code}` | Update URL destination, alias, or expiration |
| DELETE | `/api/v1/urls/{short_code}` | Delete URL (soft delete) |
| POST | `/api/v1/urls/bulk-delete` | Delete multiple URLs at once (max 100) |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stats/{short_code}` | Comprehensive stats (supports `date_from`/`date_to` filtering) |
| GET | `/api/v1/stats/{short_code}/realtime` | Real-time click count (via Redis) |
| GET | `/api/v1/stats/{short_code}/browsers` | Browser breakdown |
| GET | `/api/v1/stats/{short_code}/os` | OS breakdown |
| GET | `/api/v1/stats/{short_code}/export` | Download click analytics as CSV |

### Redirect

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{short_code}` | Redirect to original URL (302) with click logging |

### Admin (requires admin role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/stats/summary` | Platform statistics |
| GET | `/api/v1/admin/top-urls` | Top performing URLs |
| DELETE | `/api/v1/admin/urls/{short_code}` | Delete any URL |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/api/v1/health` | API health check |

---

## Testing

### Backend Tests

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_register_user
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- src/__tests__/components/button.test.tsx
```

---

## Troubleshooting

### Common Issues

**MongoDB connection refused:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod  # Linux
brew services list           # macOS

# Start MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

**Redis connection refused:**
```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis   # macOS
```

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>
```

**Docker containers not starting:**
```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` and `npm test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework
- [Next.js](https://nextjs.org/) - React framework
- [Anthropic Claude](https://www.anthropic.com/) - AI-powered content analysis
- [shadcn/ui](https://ui.shadcn.com/) - UI component patterns
- [Framer Motion](https://www.framer.com/motion/) - Animation library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Recharts](https://recharts.org/) - Analytics visualization
- [Beanie](https://beanie-odm.dev/) - MongoDB ODM
