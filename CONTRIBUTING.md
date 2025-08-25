# Contributing to DrugInsightAI

Thank you for your interest in contributing to DrugInsightAI! We welcome contributions from the community and are excited to collaborate with you.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots and animated GIFs if helpful
- Include relevant environment details (OS, Python version, Node.js version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful

### Pull Requests

1. Ensure an issue exists for the change, bug, or new feature you wish to add. If none exist create one.
2. Fork the repository
2. Follow the instructions in the README.md file to set up your development environment.
2. Create a new feature branch from `develop` for your feature or fix
3. Make your changes following our development guidelines
4. Add tests for your changes
5. Ensure all tests pass and precommit hooks pass.
6. Update documentation if needed
7. Create a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis
- Podman or Docker (for local database setup)

### Local Development

1. Clone the repository:

```bash
git clone https://github.com/john-agentic-ai-tools/DrugInsightAI.git
cd DrugInsightAI
```

2. Set up local databases:

```bash
cd infra/database
docker-compose up -d
```

3. Set up Python services:

```bash
# For each service/package
cd services/{service-name}  # or packages/{package-name}
poetry install
poetry run pytest
```

4. Set up web application:

```bash
cd apps/web
npm ci
npm run dev
```

5. Set up mobile application:

```bash
cd apps/mobile
npm install
npm start
```

## Development Guidelines

### Python Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Use Black formatter with default settings (88 character line length)
- Sort imports with isort using Black profile
- Run linting with flake8
- Use pytest for testing with good test coverage

### Python Development Workflow

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8

# Type checking
poetry run mypy .

# Run tests
poetry run pytest
```

### TypeScript/JavaScript Code Standards

- Use TypeScript for all new code
- Follow the existing code style and conventions
- Use meaningful variable and function names
- Write JSDoc comments for complex functions
- Ensure all tests pass

### TypeScript Development Workflow

```bash
# Lint code
npm run lint

# Run tests
npm test

# Type checking (handled by TypeScript compiler)
npm run build
```

### Commit Message Guidelines

We follow conventional commit format:

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

Example: `feat(api): add endpoint for drug interaction analysis`

### Testing

- Write tests for all new functionality
- Ensure existing tests continue to pass
- Aim for good test coverage
- Use appropriate test frameworks:
  - Python: pytest
  - JavaScript/TypeScript: Jest
  - Integration tests where appropriate

### Documentation

- Update relevant documentation for your changes
- Add docstrings/comments for complex code
- Update API documentation if you modify endpoints
- Consider adding examples for new features

## Project Structure

The project follows a monorepo structure:

- `apps/`: Frontend applications (Next.js web, React Native mobile)
- `services/`: Backend microservices (Python/FastAPI)
- `packages/`: Shared libraries (Python)
- `infra/`: Infrastructure and deployment configurations

## Getting Help

- Check existing issues and documentation first
- Create an issue for bugs or feature requests
- Join our community discussions
- Reach out to maintainers if needed

## Recognition

Contributors will be recognized in our README and release notes. We appreciate all contributions, no matter how small!

## License

By contributing to DrugInsightAI, you agree that your contributions will be licensed under the Apache License 2.0.
