# EclipseURL

A modern, full-stack URL shortener with advanced analytics, built with FastAPI and Next.js.

## Features

- **URL Shortening**: Generate short, memorable links with optional custom aliases
- **Click Analytics**: Track clicks with detailed breakdowns by device, browser, country, and referrer
- **User Authentication**: Secure JWT-based authentication with role-based access
- **Rate Limiting**: Protect against abuse with configurable rate limits
- **Admin Dashboard**: Platform-wide statistics and URL management
- **Dark/Light Mode**: Tesla-inspired theming with smooth transitions
- **Responsive Design**: Mobile-first UI with Framer Motion animations

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database with Beanie ODM
- **Redis** - Caching and real-time analytics
- **JWT** - Secure authentication
- **SlowAPI** - Rate limiting

### Frontend
- **Next.js 14+** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component patterns
- **Framer Motion** - Smooth animations

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
# MongoDB Configuration
MONGO_ROOT_USER=eclipse
MONGO_ROOT_PASSWORD=your_secure_password_here
MONGO_DB=eclipse_url

# For local development without auth:
# MONGODB_URL=mongodb://localhost:27017/eclipse_url

# For authenticated MongoDB:
MONGODB_URL=mongodb://eclipse:your_secure_password_here@localhost:27017/eclipse_url?authSource=admin

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Security - CHANGE THIS IN PRODUCTION!
SECRET_KEY=your-super-secret-key-minimum-32-characters-long

# URLs
BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# CORS Origins (JSON array)
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
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
eclipseurl/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── admin.py      # Admin endpoints
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── redirect.py   # URL redirect handler
│   │   │   └── urls.py       # URL management endpoints
│   │   ├── core/             # Config, security, database
│   │   │   ├── config.py     # Application settings
│   │   │   ├── database.py   # MongoDB/Redis connections
│   │   │   └── security.py   # JWT, password hashing
│   │   ├── models/           # Beanie document models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # Business logic
│   ├── tests/                # Pytest tests
│   ├── Dockerfile            # Production Dockerfile
│   ├── Dockerfile.dev        # Development Dockerfile
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (App Router)
│   │   ├── components/       # React components
│   │   ├── context/          # React context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Utilities and API client
│   │   └── types/            # TypeScript type definitions
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

### URLs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/urls/shorten` | Create short URL |
| GET | `/api/v1/urls` | List user's URLs |
| GET | `/api/v1/urls/{short_code}/stats` | Get URL analytics |
| DELETE | `/api/v1/urls/{short_code}` | Delete URL |

### Redirect

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{short_code}` | Redirect to original URL (302) |

### Admin (requires admin role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/stats/summary` | Platform statistics |
| GET | `/api/v1/admin/top-urls` | Top performing URLs |
| DELETE | `/api/v1/admin/urls/{short_code}` | Delete any URL |

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
- [shadcn/ui](https://ui.shadcn.com/) - UI component patterns
- [Framer Motion](https://www.framer.com/motion/) - Animation library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
