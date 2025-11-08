# CRUSH.md - Repository Agent Guide

## Project Overview
This is a **金融售前方案辅助系统** (Financial Presales Proposal Assistant System) - a full-stack web application for generating and managing financial presales proposals. The system uses FastAPI backend with React frontend, integrated with AI services for proposal generation.

## Architecture & Stack
- **Backend**: FastAPI (Python 3.9+) with SQLAlchemy ORM
- **Frontend**: React 18 + TypeScript + Vite + Ant Design
- **Database**: PostgreSQL (primary) + SQLite (testing)
- **Cache**: Redis
- **Vector Storage**: ChromaDB for embeddings
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker Compose

## Development Commands

### Backend Development
```bash
cd backend
make install           # Install dependencies
make dev              # Format + lint + type + test
make run              # Start development server
make test             # Run tests
make cov              # Run tests with coverage
make ci               # Full CI pipeline locally
make security         # Security scan (bandit + safety)
make alembic-upgrade  # Apply database migrations
```

### Frontend Development  
```bash
cd frontend
npm install           # Install dependencies
npm run dev          # Start development server
npm run build        # Production build
npm run lint         # ESLint check
npm run test         # Run unit tests
npm run test:coverage # Run tests with coverage
```

### Full Stack Development
```bash
docker-compose up -d    # Start all services (Postgres, Redis, Backend, Frontend)
docker-compose down      # Stop all services
```

## Project Structure

### Backend (`/backend`)
- `app/main.py` - FastAPI application entry point
- `app/api/` - API route handlers (auth, documents, proposals, etc.)
- `app/core/` - Configuration, database, metrics
- `app/models/` - SQLAlchemy model definitions
- `app/services/` - Business logic (AI service, document processor, etc.)
- `app/utils/` - Utility functions
- `app/middleware/` - Custom middleware
- `alembic/` - Database migration files
- `tests/` - Test suites (unit, integration, e2e)
- `storage/` - File uploads and exports

### Frontend (`/frontend`)
- `src/App.tsx` - Main React application
- `src/components/` - Reusable UI components
- `src/pages/` - Page components (Dashboard, Documents, etc.)
- `src/services/` - API service layer
- `src/store/` - Zustand state management
- `src/utils/` - Utility functions

## Code Standards & Patterns

### Backend Patterns
- **FastAPI dependency injection** for database sessions, authentication
- **Pydantic schemas** for request/response models
- **SQLAlchemy models** in PascalCase with table definitions
- **Service layer** pattern in `app/services/`
- **Async/await** throughout for I/O operations
- **Loguru** for structured logging

### Frontend Patterns
- **TypeScript strict mode** enabled
- **Functional components** with hooks
- **Zustand** for state management
- **Ant Design** component library
- **Axios** for API calls
- **React Router** for navigation

### Code Style
- **Python**: Black formatter (88 char line), isort imports, flake8 linting, mypy type checking
- **TypeScript**: ESLint + Prettier, 2-space indentation
- **File naming**: PascalCase for components, camelCase for utilities

## Testing Strategy

### Backend Testing
```bash
# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests
pytest tests/e2e/ -v                     # End-to-end tests
pytest tests/ -k "vector" -v             # Vector-related tests

# Coverage requirements: ≥80% line coverage
pytest tests/ --cov=app --cov-report=html --cov-fail-under=55
```

### Frontend Testing
```bash
# Vitest unit tests
npm run test

# Coverage reporting  
npm run test:coverage
```

### Test Environment
- **Database**: SQLite for unit tests, PostgreSQL for integration
- **AI Services**: Mocked in tests (test keys provided)
- **Fixtures**: Located in `tests/conftest.py`

## Database & Migrations

### Alembic Workflow
```bash
# Create new migration after model changes
alembic revision --autogenerate -m "descriptive message"

# Apply migrations
alembic upgrade head

# Check model signature consistency
python scripts/check_model_signature.py
```

### Model Changes
When modifying SQLAlchemy models:
1. Update model files in `app/models/`
2. Generate migration: `alembic revision --autogenerate`
3. Update `alembic/model_signature.json`
4. Test migration on copy of production data

## AI Integration

### Supported Providers
- **智谱AI (Zhipu)** - Primary provider
- **通义千问 (Tongyi)** - Secondary provider  
- **文心一言 (Wenxin)** - Fallback provider
- **OpenAI** - Optional provider

### Configuration
Set environment variables:
- `AI_PROVIDER` - Provider choice
- `ZHIPU_API_KEY`, `TONGYI_API_KEY`, `WENXIN_API_KEY`, `OPENAI_API_KEY`

### AI Services
- `app/services/ai_service.py` - Main AI integration
- `app/services/vector_service.py` - Embedding and vector storage
- `app/services/proposal_generator.py` - Proposal generation logic

## Security Guidelines

### Authentication
- JWT token-based authentication
- Role-based access control (RBAC)
- CSRF protection enabled

### Security Scanning
```bash
make security         # Run bandit + safety
bandit -r app/ -ll    # High/medium severity issues only
safety check         # Check vulnerable dependencies
```

### Configuration Security
- Copy `.env.example` to `.env` for local development
- Never commit actual API keys or secrets
- Use environment variables for all sensitive data

## Performance & Monitoring

### Metrics Collection
- **Prometheus**: Metrics endpoint at `/metrics`
- **Custom middleware**: Request tracking in `app/middleware/`
- **Grafana dashboards**: Available in `grafana/dashboards/`

### Performance Testing
```bash
# Run performance benchmarks
pytest tests/test_performance_benchmarks.py -v

# Load testing with k6
k6 run backend/performance_test_k6.js
```

## CI/CD Pipeline

### GitHub Actions Workflow
- **Triggers**: Push to main/develop, Pull Requests
- **Matrix**: Python 3.9, 3.10
- **Stages**: Lint → Type Check → Security → Test → Integration → Performance → E2E
- **Coverage**: Generates badge and reports
- **Deployment**: Automatic badge updates on main branch

### PR Requirements
- All tests must pass (≥55% coverage)
- Code formatting with black
- Type checking with mypy
- Security scan passes
- Alembic migration generated if models change

## Common Gotchas

### Database Connection
- Use `DATABASE_URL` environment variable format
- Test environment defaults to SQLite
- Integration tests require PostgreSQL

### Vector Storage
- ChromaDB persistence directory: `./storage/chroma`
- Embeddings generated on document upload
- Vector similarity search for knowledge retrieval

### Frontend Build
- Vite dev server uses HMR (Hot Module Replacement)
- Production build requires Node.js 18+
- Ant Design theme customization via CSS variables

### File Uploads
- Document storage: `./storage/documents/`
- Export storage: `./storage/exports/`
- File validation in `services/document_processor.py`

## Environment Setup

### Quick Start
```bash
# Clone and setup
git clone <repo>
cd Fin_Pre_Assist

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
make install

# Frontend setup  
cd ../frontend
npm install

# Start services
cd ..
docker-compose up -d
```

### Environment Files
- `backend/.env.example` - Backend environment template
- `frontend/.env.example` - Frontend environment template
- `.env.prod.example` - Production environment template

## Debugging Tips

### Backend Debugging
- Use `logger.info()` for structured logging
- Check logs in `backend/logs/` directory
- Database queries logged in debug mode
- API documentation at `http://localhost:8000/api/docs`

### Frontend Debugging
- React DevTools browser extension
- Network tab in browser dev tools for API calls
- Vite dev server provides source maps

### Common Issues
- **Port conflicts**: Check if ports 5433, 6379, 8000, 3000 are available
- **Database connection**: Verify `DATABASE_URL` format
- **AI service failures**: Check API keys and provider status
- **Vector search issues**: Verify ChromaDB persistence directory permissions

## Key Files to Understand

### Core Application Files
- `backend/app/main.py` - FastAPI app setup and middleware
- `backend/app/core/config.py` - Configuration management
- `backend/app/core/database.py` - Database connection handling
- `frontend/src/App.tsx` - React app structure and routing

### API Endpoints
- `backend/app/api/auth.py` - Authentication routes
- `backend/app/api/proposals.py` - Proposal CRUD operations
- `backend/app/api/documents.py` - Document management
- `backend/app/services/ai_service.py` - AI integration logic

### Configuration Files
- `docker-compose.yml` - Service orchestration
- `backend/alembic.ini` - Database migration config
- `frontend/vite.config.ts` - Frontend build configuration
- `backend/pytest.ini` - Test configuration