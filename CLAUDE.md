# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

DrugInsightAI is a monorepo containing a pharmaceutical data analysis platform with the following structure:

- **apps/**: Frontend applications
  - `web/`: Next.js web application with TypeScript
  - `mobile/`: React Native mobile application
- **services/**: Backend microservices (Python/Poetry)
  - `api/`: FastAPI REST API with SQLAlchemy, Alembic, Redis, Celery
  - `data-harvesters/`: Data collection from pharmaceutical sources using requests, BeautifulSoup, pandas
  - `data-processors/`: ML/analytics pipeline with pandas, scikit-learn, scipy
- **packages/**: Shared libraries (Python/Poetry)
  - `common/`: Shared utilities
  - `auth/`: Authentication components
  - `database/`: Database models and utilities
  - `logging/`: Logging utilities
- **infra/**: Infrastructure as Code for AWS deployment
  - `database/`: Docker Compose for local PostgreSQL + Redis
  - `terraform/`: Infrastructure definitions
  - `kubernetes/`: K8s manifests

## Development Commands

### Python Services & Packages
Each Python service/package uses Poetry for dependency management:
```bash
cd services/{service-name} # or packages/{package-name}
poetry install              # Install dependencies
poetry run pytest          # Run tests
poetry run black .         # Format code
poetry run isort .          # Sort imports
poetry run flake8          # Lint code
poetry run mypy .           # Type checking
```

### Web Application
```bash
cd apps/web
npm ci                      # Install dependencies
npm run dev                 # Start development server
npm run build               # Build for production
npm run start               # Start production server
npm run lint                # Lint code
npm test                    # Run tests
npm run test:watch          # Run tests in watch mode
```

### Mobile Application
```bash
cd apps/mobile
npm install                 # Install dependencies
npm run android             # Run on Android
npm run ios                 # Run on iOS
npm start                   # Start Metro bundler
npm run lint                # Lint code
npm test                    # Run tests
```

### Infrastructure
```bash
# Local database setup
cd infra/database
docker-compose up -d        # Start PostgreSQL + Redis

# Database credentials (local):
# - Database: druginsightai
# - User: druginsightai
# - Password: changeme (configurable via DB_PASSWORD env var)
```

### Build All Components
```bash
./scripts/build/build-all.sh   # Builds all services, packages, and web app
```

## Code Standards

### Python (All services & packages)
- Python 3.11+
- Black formatter (line length: 88)
- isort for import sorting (Black profile)
- Type hints with mypy
- pytest for testing

### TypeScript (Web app)
- Strict TypeScript configuration
- Path aliases: `@/*` maps to `./src/*`
- Next.js framework conventions

### React Native (Mobile app)
- TypeScript enabled
- React Navigation for routing
- Babel preset for React Native

## Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Alembic, Redis, Celery
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Mobile**: React Native, React Navigation
- **Data**: pandas, scikit-learn, scipy, BeautifulSoup
- **Database**: PostgreSQL (production), Redis (caching/queues)
- **Infrastructure**: AWS, Docker, Kubernetes, Terraform
- **Testing**: pytest (Python), Jest (JavaScript/TypeScript)
