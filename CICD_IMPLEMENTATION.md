# CI/CD Pipeline Implementation - Complete Reference

**Date Implemented**: November 13, 2024
**Phase**: Minimal MVP (Phase 1)
**Status**: ✅ Complete

---

## Overview

This document provides a complete reference for the CI/CD pipeline implementation for the GraphRAG Clinical Guidelines project. The pipeline uses GitHub Actions and follows the development methodology outlined in the project blueprint.

## What Was Implemented

### 📁 Project Structure Created

```
elec_498a_graph_rag/
├── .gitignore                    # Python, AWS, IDE, Docker ignores
├── pyproject.toml                # Project config, dependencies, tool settings
├── requirements.txt              # Pip dependencies list
├── src/
│   ├── __init__.py              # Package initialization with version
│   └── main.py                  # FastAPI application with REST endpoints
├── tests/
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Pytest fixtures and test configuration
│   └── test_main.py             # Comprehensive test suite (10+ tests)
└── .github/workflows/
    ├── ci.yml                   # Main CI workflow (all branches/PRs)
    ├── staging.yml              # Staging workflow (main branch)
    ├── production.yml           # Production workflow (release tags)
    └── README.md                # Complete workflow documentation
```

---

## Workflows Implemented

### 1. CI Workflow (`ci.yml`)

**Purpose**: Continuous integration for all feature branches and pull requests

**Triggers**:
- Push to any branch
- Pull requests to any branch

**Jobs**:

1. **Lint** - Code quality checks
   - Ruff linter check
   - Ruff formatter check
   - Fast feedback (runs in parallel with tests)

2. **Test** - Run test suite
   - pytest with coverage
   - Matrix testing (Python 3.11, expandable)
   - Coverage report generation (XML, HTML, terminal)
   - Codecov upload (if configured)

3. **Security Check** - Dependency scanning
   - Safety check for known vulnerabilities
   - Continues on error (informational)

4. **Status Check** - Aggregate status
   - Verifies all jobs passed
   - Required for PR merge

**Coverage Requirements**: None (informational only)

**When to use**:
- Feature development
- Bug fixes
- Experimental work
- All pull requests

---

### 2. Staging Workflow (`staging.yml`)

**Purpose**: Pre-production validation for code merged to main

**Triggers**:
- Push to `main` branch

**Jobs**:

1. **Full Test Suite** - Comprehensive testing
   - All tests with strict markers
   - Coverage threshold enforcement
   - HTML coverage report generation
   - Artifact upload for review

2. **Strict Linting** - No auto-fixes
   - Ruff check with --no-fix
   - Ruff format check
   - Fails on any violations

3. **Docker Build Placeholder** - Ready for Phase 2
   - Validates tests/linting pass first
   - Logs readiness for Docker implementation
   - Sets staging metadata

4. **Staging Ready** - Deployment checklist
   - Confirms all checks passed
   - Provides manual deployment steps
   - Lists future automation plans

**Coverage Requirements**: ≥70% (enforced, build fails below)

**When to use**:
- After PR merge to main
- Integration testing
- Pre-production validation
- Before deploying to staging environment

**Future Enhancements**:
- Automatic Docker build
- Push to GitHub Container Registry or ECR
- Deploy to staging ECS cluster
- Run integration tests against staging

---

### 3. Production Workflow (`production.yml`)

**Purpose**: Production-grade validation and deployment preparation

**Triggers**:
- Push tags matching `v[0-9]+.[0-9]+.[0-9]+`
- Examples: `v1.0.0`, `v2.1.3`, `v0.1.0`

**Jobs**:

1. **Validate Version** - Semantic versioning check
   - Extracts version from tag
   - Validates format (MAJOR.MINOR.PATCH)
   - Outputs version for other jobs

2. **Comprehensive Tests** - Full test suite
   - All tests with --strict-markers
   - Enhanced coverage reporting
   - 80% coverage threshold (strict)

3. **Strict Linting** - Production standards
   - Ruff check (no auto-fix)
   - Ruff format check
   - Zero tolerance for violations

4. **Security Scan** - Multi-tool analysis
   - Safety check (fails on vulnerabilities)
   - Bandit security scan
   - Blocks on high-severity issues

5. **Docker Build Placeholder** - Phase 3 ready
   - Validates all checks pass first
   - Logs version and build plan
   - Ready for production Docker implementation

6. **Production Ready** - Deployment summary
   - Comprehensive readiness check
   - Creates GitHub summary with status table
   - Lists manual deployment steps
   - Documents future automation

**Coverage Requirements**: ≥80% (enforced, build fails below)

**Security Requirements**:
- No known vulnerabilities
- No high-severity Bandit issues
- All dependencies up to date

**When to use**:
- Official releases
- Production deployments
- Version milestones (v1.0.0, v2.0.0, etc.)

**Future Enhancements**:
- Automated Docker build and ECR push
- Blue-green deployment to ECS
- Automated rollback on failure
- Post-deployment health checks
- Canary deployments

---

## FastAPI Application

### Endpoints Implemented

**Location**: `src/main.py`

#### `GET /` - Root endpoint
- Health check
- Returns status, version, message
- Always available

#### `GET /health` - Health check endpoint
- Detailed health status
- Used by load balancers/monitoring
- Returns operational status

#### `POST /query` - Query knowledge graph
- **Request**: `{"question": "string", "method": "local|global|drift|basic"}`
- **Response**: `{"answer": "string", "citations": ["string"], "method": "string"}`
- Currently placeholder implementation
- TODO: Integrate actual GraphRAG logic

#### `POST /index` - Trigger document indexing
- Starts document ingestion pipeline
- Currently placeholder implementation
- TODO: Implement document processing

#### `POST /build` - Build knowledge graph
- Triggers graph construction
- Currently placeholder implementation
- TODO: Implement graph building logic

### API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Test Suite

### Location: `tests/`

### Test Coverage

**`test_main.py`** - 10+ comprehensive tests:

1. ✅ `test_root_endpoint` - Root endpoint health check
2. ✅ `test_health_check_endpoint` - Health endpoint validation
3. ✅ `test_query_endpoint_with_default_method` - Query with default method
4. ✅ `test_query_endpoint_with_global_method` - Query with global method
5. ✅ `test_query_endpoint_requires_question` - Request validation
6. ✅ `test_index_documents_endpoint` - Index endpoint
7. ✅ `test_build_graph_endpoint` - Build endpoint
8. ✅ `test_openapi_docs_available` - Swagger UI available
9. ✅ `test_redoc_available` - ReDoc available
10. ✅ `test_query_with_different_methods` - Parametrized test (4 methods)

**Total test cases**: 13 (10 unique + 3 parametrized)

### Fixtures (`conftest.py`)

- `client` - FastAPI TestClient for API testing
- `sample_query` - Sample query request data
- `sample_guideline_text` - Sample clinical guideline content

### Running Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Specific test file
pytest tests/test_main.py -v

# With HTML coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html

# Check coverage threshold
pytest tests/ --cov=src --cov-fail-under=70
```

---

## Configuration Files

### `pyproject.toml`

**Project Metadata**:
- Name: elec-498a-graph-rag
- Version: 0.1.0
- Python: ≥3.11
- Authors: All 4 team members

**Dependencies**:
- fastapi ≥0.104.0
- uvicorn[standard] ≥0.24.0
- pydantic ≥2.5.0
- python-multipart ≥0.0.6

**Dev Dependencies**:
- pytest ≥7.4.0
- pytest-cov ≥4.1.0
- pytest-asyncio ≥0.21.0
- httpx ≥0.25.0
- ruff ≥0.1.0

**Tool Configuration**:

- **pytest**: Coverage settings, test paths, addopts
- **coverage**: Source paths, branch coverage, exclusions
- **ruff**: Linting rules (E, W, F, I, B, C4, UP), isort config
- **ruff.format**: Code formatting preferences

### `.gitignore`

Comprehensive ignore patterns:
- Python artifacts (`__pycache__`, `*.pyc`, etc.)
- Virtual environments (`venv/`, `.venv/`)
- Testing artifacts (`.pytest_cache/`, `coverage.xml`)
- IDE configs (`.idea/`, `.vscode/`)
- Environment variables (`.env`)
- AWS credentials (`.aws/`, `*.pem`)
- GraphRAG outputs (`output/`, `cache/`, `*.parquet`)
- OS files (`.DS_Store`, `Thumbs.db`)

---

## Usage Guide

### Local Development Workflow

1. **Setup environment**:
```bash
cd elec_498a_graph_rag
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. **Run linting**:
```bash
# Check code
ruff check src/ tests/

# Auto-fix issues
ruff check src/ tests/ --fix

# Check formatting
ruff format --check src/ tests/

# Auto-format
ruff format src/ tests/
```

3. **Run tests**:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Specific test
pytest tests/test_main.py::test_root_endpoint -v

# Watch mode (requires pytest-watch)
ptw tests/
```

4. **Start development server**:
```bash
# Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m uvicorn src.main:app --reload

# Visit http://localhost:8000/docs for API documentation
```

5. **Commit changes**:
```bash
# Stage changes
git add .

# Commit with conventional commit format
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "test: add tests for feature"

# Push (triggers CI)
git push origin feature/your-branch
```

### Branch Workflow

#### Feature Development

```bash
# Create feature branch
git checkout -b feature/add-graph-query

# Make changes, commit, push
git add .
git commit -m "feat: implement graph query logic"
git push origin feature/add-graph-query

# CI runs automatically on push
# Check Actions tab on GitHub

# Create PR when ready
gh pr create --title "Add graph query functionality" --body "Description..."

# After PR approval and CI passes, merge to main
```

#### Staging Deployment

```bash
# After PR merged to main, staging workflow runs automatically
# Check Actions tab → Staging workflow

# Verify staging checks:
# - Full test suite passed
# - Coverage ≥70%
# - Strict linting passed
# - Ready for staging deployment

# Manual deployment to staging (until Phase 2 automation)
# Follow steps in staging workflow output
```

#### Production Release

```bash
# Ensure main branch is stable and tested
git checkout main
git pull origin main

# Create release tag (triggers production workflow)
git tag -a v1.0.0 -m "Release version 1.0.0: Initial production release"
git push origin v1.0.0

# Production workflow runs automatically
# Check Actions tab → Production workflow

# Verify production checks:
# - Version validated
# - All tests passed
# - Coverage ≥80%
# - Security scan passed
# - Ready for production deployment

# Manual deployment to production (until Phase 3 automation)
# Follow steps in production workflow output
```

---

## Coverage Requirements by Environment

| Environment | Minimum Coverage | Enforced | Build Fails Below |
|-------------|------------------|----------|-------------------|
| Development (CI) | None | No | No |
| Staging (main) | 70% | Yes | Yes |
| Production (tags) | 80% | Yes | Yes |

### Checking Coverage Locally

```bash
# Check if you meet staging requirements (70%)
pytest tests/ --cov=src --cov-fail-under=70

# Check if you meet production requirements (80%)
pytest tests/ --cov=src --cov-fail-under=80

# Generate HTML report to see coverage details
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # or start htmlcov/index.html on Windows
```

---

## Troubleshooting

### CI Fails: Linting Errors

**Problem**: Ruff reports style violations

**Solution**:
```bash
# Auto-fix most issues
ruff check src/ tests/ --fix
ruff format src/ tests/

# Commit fixes
git add .
git commit -m "style: fix linting issues"
git push
```

### CI Fails: Test Failures

**Problem**: Tests are failing

**Solution**:
```bash
# Run tests locally with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_main.py::test_name -v -s

# Check for import errors
python -c "import src.main"

# Ensure dependencies installed
pip install -r requirements.txt
```

### Staging Fails: Coverage Below 70%

**Problem**: Coverage is 65%, need 70% for staging

**Solution**:
```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Open report in browser
open htmlcov/index.html

# Identify files with low coverage
# Add tests for uncovered lines

# Common areas needing coverage:
# - Error handling (try/except blocks)
# - Edge cases (empty inputs, invalid data)
# - Different method branches (if/elif/else)

# Re-run coverage check
pytest tests/ --cov=src --cov-fail-under=70
```

### Production Fails: Coverage Below 80%

**Problem**: Coverage is 75%, need 80% for production

**Solution**:
- Add integration tests
- Test error conditions
- Add parametrized tests for multiple scenarios
- Consider E2E tests for critical paths

### Production Fails: Security Vulnerabilities

**Problem**: Safety or Bandit reports vulnerabilities

**Safety issues**:
```bash
# Check vulnerabilities locally
safety check

# Update vulnerable packages
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt
```

**Bandit issues**:
```bash
# Run Bandit locally
bandit -r src/

# Review high-severity issues
# Fix code issues (don't just disable warnings)

# If false positive, add # nosec comment with justification
variable = eval(user_input)  # nosec - validated upstream
```

### Production Fails: Invalid Version Tag

**Problem**: Tag doesn't match expected format

**Solution**:
```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0

# Create tag with correct format (vX.Y.Z)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag
git push origin v1.0.0
```

---

## GitHub Actions Badges

Add these to your main `README.md`:

```markdown
# GraphRAG Clinical Guidelines System

![CI](https://github.com/ianfv/elec_498a_graph_rag/workflows/CI/badge.svg)
![Staging](https://github.com/ianfv/elec_498a_graph_rag/workflows/Staging/badge.svg)
![Production](https://github.com/ianfv/elec_498a_graph_rag/workflows/Production/badge.svg)
[![codecov](https://codecov.io/gh/ianfv/elec_498a_graph_rag/branch/main/graph/badge.svg)](https://codecov.io/gh/ianfv/elec_498a_graph_rag)
```

---

## Migration Path

### ✅ Phase 1: Minimal MVP (COMPLETE)

**Status**: Implemented

**Components**:
- [x] Project structure (src/, tests/)
- [x] FastAPI application with REST endpoints
- [x] Comprehensive test suite (10+ tests)
- [x] Linting with Ruff
- [x] Coverage reporting
- [x] GitHub Actions workflows (CI, Staging, Production)
- [x] Environment-aware pipelines
- [x] Security scanning (Safety)
- [x] Complete documentation

**Outcome**: Production-ready CI/CD for code quality and testing

---

### 🔄 Phase 2: Docker Integration (NEXT)

**Status**: Not started (placeholders in place)

**Tasks**:
- [ ] Create `Dockerfile` for FastAPI app
- [ ] Create multi-stage Docker build
- [ ] Add `.dockerignore`
- [ ] Update CI workflow to build Docker images
- [ ] Push to GitHub Container Registry
- [ ] Add container security scanning (Trivy)
- [ ] Update staging workflow for Docker builds
- [ ] Add docker-compose for local development

**Expected Timeline**: Milestone 2 (S1 Week 12)

**Outcome**: Containerized application ready for cloud deployment

---

### 🚀 Phase 3: AWS Integration (FUTURE)

**Status**: Not started

**Prerequisites**: Phase 2 complete, AWS credentials configured

**Tasks**:
- [ ] Configure AWS credentials in GitHub Secrets
- [ ] Create AWS CDK infrastructure code
- [ ] Set up ECR repositories (staging, production)
- [ ] Set up ECS clusters (staging, production)
- [ ] Update staging workflow:
  - [ ] Build Docker image
  - [ ] Push to ECR
  - [ ] Deploy to ECS staging cluster
- [ ] Update production workflow:
  - [ ] Build production Docker image
  - [ ] Push to ECR with version tags
  - [ ] Deploy to ECS production cluster
- [ ] Add post-deployment health checks
- [ ] Integrate with AWS CodeBuild

**Expected Timeline**: Milestone 3 (S2 Week 1)

**Outcome**: Fully automated cloud deployment pipeline

---

### 🎯 Phase 4: Advanced Features (OPTIONAL)

**Status**: Not started

**Prerequisites**: Phase 3 complete

**Tasks**:
- [ ] Integration tests against staging environment
- [ ] E2E tests with real data
- [ ] Load testing with Locust or k6
- [ ] Blue-green deployment strategy
- [ ] Automated rollback on failure
- [ ] Canary deployments
- [ ] Performance monitoring integration
- [ ] Slack/Discord notifications
- [ ] Automated dependency updates (Dependabot)

**Expected Timeline**: Milestone 4 (S2 Week 4)

**Outcome**: Enterprise-grade CI/CD with advanced features

---

## Environment Variables & Secrets

### Current Requirements

**None** - The minimal MVP doesn't require secrets for basic operation.

### Future Requirements (Phase 3+)

When implementing AWS integration, add these secrets:

**GitHub Repository Secrets**:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | `wJalrXUtnFEMI/K7MDENG/...` |
| `AWS_REGION` | AWS region | `ca-central-1` |
| `ECR_REPOSITORY_STAGING` | ECR repo for staging | `graphrag-staging` |
| `ECR_REPOSITORY_PRODUCTION` | ECR repo for production | `graphrag-production` |
| `ECS_CLUSTER_STAGING` | ECS cluster name | `graphrag-staging-cluster` |
| `ECS_SERVICE_STAGING` | ECS service name | `graphrag-staging-service` |
| `ECS_CLUSTER_PRODUCTION` | ECS cluster name | `graphrag-production-cluster` |
| `ECS_SERVICE_PRODUCTION` | ECS service name | `graphrag-production-service` |

**Environment Variables** (in workflow):
- `PYTHONPATH`: Set to repository root
- `ENVIRONMENT`: `staging` or `production`
- `VERSION`: Extracted from git tag

---

## Best Practices

### Commit Message Format

Follow Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `test`: Adding tests
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `chore`: Build process, dependencies
- `ci`: CI/CD changes

**Examples**:
```bash
feat(api): add query endpoint with citation support
fix(tests): resolve flaky test in test_query_endpoint
test(api): add integration tests for graph building
docs(readme): update installation instructions
ci(workflows): add Docker build to staging workflow
```

### Code Review Checklist

Before approving PR:
- [ ] All CI checks pass (lint, test, security)
- [ ] Coverage doesn't decrease
- [ ] Code follows project style (Ruff compliant)
- [ ] Tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] No security vulnerabilities introduced
- [ ] Commit messages follow convention

### Testing Checklist

For new features:
- [ ] Unit tests for all new functions
- [ ] Integration tests for API endpoints
- [ ] Test error conditions
- [ ] Test edge cases
- [ ] Parametrize tests where appropriate
- [ ] Use fixtures to reduce duplication
- [ ] Tests are isolated (no shared state)
- [ ] Tests are deterministic (no randomness)

---

## Additional Resources

### Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Project Documentation

- [CLAUDE.md](../CLAUDE.md) - Complete project guide
- [.github/workflows/README.md](.github/workflows/README.md) - Workflow details
- [README.md](../README.md) - Project overview

### GraphRAG Resources

- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
- [GraphRAG Paper](https://arxiv.org/abs/2404.16130)
- Blueprint: `documents/ELEC498A_group08_draft_blueprint.pdf`

---

## Changelog

### Version 0.1.0 (November 13, 2024)

**Added**:
- Initial project structure (src/, tests/)
- FastAPI application with REST API
- Comprehensive test suite (10+ tests)
- GitHub Actions CI workflow
- GitHub Actions Staging workflow
- GitHub Actions Production workflow
- Linting with Ruff
- Coverage reporting with pytest-cov
- Security scanning with Safety
- Complete documentation (CICD_IMPLEMENTATION.md)
- Workflow documentation (.github/workflows/README.md)

**Configuration**:
- pyproject.toml with all tool configurations
- requirements.txt with dependencies
- .gitignore for Python/AWS/Docker

**Testing**:
- pytest configuration
- Test fixtures (client, sample_query, sample_guideline_text)
- Coverage thresholds (70% staging, 80% production)

**Workflows**:
- CI: Lint + Test + Security for all branches
- Staging: Full suite with 70% coverage for main
- Production: Strict validation with 80% coverage for tags

---

## Next Steps Checklist

After reviewing this document:

- [ ] Read complete implementation guide
- [ ] Set up local development environment
- [ ] Run linting locally: `ruff check src/ tests/`
- [ ] Run tests locally: `pytest tests/ -v`
- [ ] Start FastAPI server: `uvicorn src.main:app --reload`
- [ ] Visit API docs: http://localhost:8000/docs
- [ ] Commit and push changes to trigger CI
- [ ] Verify CI runs successfully on GitHub
- [ ] Set up branch protection rules for main
- [ ] Add CI badges to README.md
- [ ] Review Phase 2 tasks (Docker integration)
- [ ] Plan Phase 3 tasks (AWS integration)
- [ ] Share this document with team

---

**Document Version**: 1.0
**Last Updated**: November 13, 2024
**Author**: Ian Fairfield
