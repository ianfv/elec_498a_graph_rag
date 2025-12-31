# GraphRAG Clinical Guidelines System

![CI](https://github.com/ianfv/elec_498a_graph_rag/workflows/CI/badge.svg)
![Staging](https://github.com/ianfv/elec_498a_graph_rag/workflows/Staging/badge.svg)
![Production](https://github.com/ianfv/elec_498a_graph_rag/workflows/Production/badge.svg)

**ELEC 498A Capstone Project - Group 08**

A Graph-based Retrieval-Augmented Generation (GraphRAG) system for clinical health guidelines, developed in partnership with ICI Medical. This system ingests medical documents, builds a knowledge graph, and returns cited, context-aware answers through a secure REST API.

---

## Table of Contents

- [Overview](#overview)
- [CI/CD Pipeline](#cicd-pipeline)
- [Tests Performed](#tests-performed)
- [Code Push Requirements](#code-push-requirements)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Development Workflow](#development-workflow)
- [Team](#team)

---

## Overview

Traditional vector-based RAG systems struggle with clinical documents because medical terminology causes tight clustering in semantic space, reducing retrieval precision. GraphRAG addresses this by constructing a knowledge graph that captures entities, relationships, and hierarchical communities, providing both local and global understanding of clinical guidelines.

### Key Features

- **FastAPI REST API** with OpenAPI documentation
- **Knowledge Graph Construction** using Microsoft GraphRAG
- **Multiple Query Methods**: Local, Global, Drift, and Basic search
- **Citation Support**: Context-aware answers with embedded citations
- **AWS Deployment** (planned): ECS Fargate, API Gateway, Cognito
- **Comprehensive Testing**: 10+ tests with coverage enforcement

### Technology Stack

- **Python 3.11** with FastAPI
- **Microsoft GraphRAG** for knowledge graph ingestion
- **Neo4j/Neptune** for graph database (planned)
- **AWS Services**: ECS, S3, DynamoDB, Bedrock/SageMaker (planned)
- **Testing**: pytest, pytest-cov
- **Linting**: Ruff
- **CI/CD**: GitHub Actions

---

## CI/CD Pipeline

Our CI/CD pipeline consists of **three automated workflows** that ensure code quality, test coverage, and security at every stage of development.

### Workflow Overview

| Workflow | Trigger | Purpose | Coverage Required |
|----------|---------|---------|-------------------|
| **CI** | All branches/PRs | Code quality validation | None (informational) |
| **Staging** | Push to `main` | Pre-production validation | ≥70% (enforced) |
| **Production** | Version tags (`v*.*.*`) | Production deployment | ≥80% (enforced) |

### 1. CI Workflow (All Branches)

**Purpose**: Fast feedback for feature development

**Jobs Performed**:

- **Lint Code**: Ruff linter and formatter checks
- **Run Tests**: Full test suite with coverage reporting
- **Security Check**: Dependency vulnerability scanning with Safety
- **Status Check**: Aggregate status for PR merge gates

**When It Runs**: Every push and pull request on any branch

### 2. Staging Workflow (Main Branch)

**Purpose**: Validate code merged to main branch

**Jobs Performed**:

- **Full Test Suite**: All tests with strict markers
- **Coverage Enforcement**: Build fails if coverage < 70%
- **Strict Linting**: No auto-fixes, zero tolerance
- **Docker Build Placeholder**: Ready for Phase 2 implementation
- **Staging Ready**: Deployment checklist and status

**When It Runs**: Every push to `main` branch

**Build Blocker**: Coverage below 70% will fail the build

### 3. Production Workflow (Release Tags)

**Purpose**: Production-grade validation for releases

**Jobs Performed**:

- **Version Validation**: Semantic versioning check (vX.Y.Z)
- **Comprehensive Tests**: Full suite with enhanced reporting
- **Coverage Enforcement**: Build fails if coverage < 80%
- **Strict Linting**: Production standards, zero tolerance
- **Security Scan**: Safety + Bandit with high-severity blocking
- **Docker Build Placeholder**: Ready for Phase 3 implementation
- **Production Ready**: Complete deployment summary

**When It Runs**: When pushing tags matching `v[0-9]+.[0-9]+.[0-9]+`

**Build Blockers**:

- Coverage below 80%
- Known security vulnerabilities
- High-severity Bandit issues
- Invalid version format

---

## Tests Performed

### Test Suite Coverage

**Location**: `tests/test_main.py`

**Total Tests**: 13 test cases (10 unique + 3 parametrized)

#### API Endpoint Tests

1. ✅ **Root Endpoint** (`test_root_endpoint`)
   - Validates health check at `/`
   - Verifies API version and status

2. ✅ **Health Check Endpoint** (`test_health_check_endpoint`)
   - Validates `/health` endpoint
   - Used by load balancers and monitoring

3. ✅ **Query Endpoint - Default Method** (`test_query_endpoint_with_default_method`)
   - Tests `/query` with default "local" search method
   - Validates request/response structure

4. ✅ **Query Endpoint - Global Method** (`test_query_endpoint_with_global_method`)
   - Tests `/query` with "global" search method
   - Ensures method routing works correctly

5. ✅ **Query Validation** (`test_query_endpoint_requires_question`)
   - Verifies Pydantic validation works
   - Ensures required fields are enforced

6. ✅ **Index Endpoint** (`test_index_documents_endpoint`)
   - Tests document indexing trigger
   - Validates `/index` POST endpoint

7. ✅ **Build Endpoint** (`test_build_graph_endpoint`)
   - Tests graph construction trigger
   - Validates `/build` POST endpoint

8. ✅ **OpenAPI Documentation** (`test_openapi_docs_available`)
   - Verifies Swagger UI is accessible at `/docs`
   - Ensures interactive API documentation works

9. ✅ **ReDoc Documentation** (`test_redoc_available`)
   - Verifies ReDoc is accessible at `/redoc`
   - Alternative API documentation interface

10. ✅ **Parametrized Query Methods** (`test_query_with_different_methods`)
    - Tests all 4 query methods: `local`, `global`, `drift`, `basic`
    - Ensures routing works for each method
    - **Runs 4 test cases** (one per method)

### Code Quality Checks

#### Linting (Ruff)

- **Code Style**: PEP 8 compliance
- **Import Sorting**: isort configuration
- **Code Quality**: Pyflakes, pycodestyle rules
- **Formatting**: Consistent code formatting
- **Rules**: E, W, F, I, B, C4, UP rule sets

#### Security Scanning

- **Safety**: Checks for known vulnerabilities in dependencies
- **Bandit**: Static code analysis for security issues
  - Blocks on high-severity issues in production
  - Scans for SQL injection, hardcoded passwords, etc.

### Coverage Reporting

Coverage is measured using `pytest-cov` and enforced at different thresholds:

- **Development**: No minimum (informational only)
- **Staging**: ≥70% required (build fails below)
- **Production**: ≥80% required (build fails below)

**Coverage includes**:

- Line coverage
- Branch coverage
- Source files in `src/` directory

### Test Fixtures

Located in `tests/conftest.py`:

- `client`: FastAPI TestClient for API testing
- `sample_query`: Sample query request data
- `sample_guideline_text`: Sample clinical guideline content

---

## Code Push Requirements

### For All Branches (CI Workflow)

Before pushing code to any branch, ensure:

1. **Code passes linting**:

   ```bash
   ruff check src/ tests/
   ruff format --check src/ tests/
   ```

2. **All tests pass**:

   ```bash
   pytest tests/ -v
   ```

3. **No security vulnerabilities**:

   ```bash
   safety check
   ```

**What Happens**: CI runs automatically and reports status. PR merges are **not blocked** by coverage.

### For Main Branch (Staging Workflow)

When merging to `main`, you must meet **stricter requirements**:

1. **All CI checks pass** (linting, tests, security)

2. **Test coverage ≥70%**:

   ```bash
   pytest tests/ --cov=src --cov-fail-under=70
   ```

3. **Pull request approved** by at least one team member

4. **No linting violations**:

   ```bash
   ruff check src/ tests/ --no-fix
   ```

**What Happens**: Build **will fail** if coverage < 70%. You must add tests before merging.

### For Production Releases (Production Workflow)

When creating a release tag, you must meet **production standards**:

1. **All staging checks pass** (linting, tests, security)

2. **Test coverage ≥80%**:

   ```bash
   pytest tests/ --cov=src --cov-fail-under=80
   ```

3. **No security vulnerabilities**:

   ```bash
   safety check
   bandit -r src/ -ll
   ```

4. **Valid semantic version tag** (e.g., `v1.0.0`, `v2.1.3`)

5. **Clean security scan** (no high-severity Bandit issues)

**What Happens**: Build **will fail** if any check fails. Production requires the highest quality bar.

### Branch Protection Rules

The `main` branch is protected with these rules:

- Require pull request before merging
- Require at least 1 approval
- Dismiss stale approvals when new commits are pushed
- Require status checks to pass:
  - `Lint Code`
  - `Run Tests`
  - `CI Status Check`
- Require conversation resolution before merging

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip or uv for package management
- Git

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/ianfv/elec_498a_graph_rag.git
   cd elec_498a_graph_rag
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Start the FastAPI server**:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the API**:

- Interactive docs: <http://localhost:8000/docs>
- Alternative docs: <http://localhost:8000/redoc>
- Health check: <http://localhost:8000/>

### Running Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Specific test file
pytest tests/test_main.py -v

# Check coverage threshold
pytest tests/ --cov=src --cov-fail-under=70
```

### Running Linter

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

---

## Project Structure

```
elec_498a_graph_rag/
├── .github/workflows/          # GitHub Actions CI/CD workflows
│   ├── ci.yml                 # CI workflow (all branches)
│   ├── staging.yml            # Staging workflow (main branch)
│   ├── production.yml         # Production workflow (version tags)
│   └── README.md              # Workflow documentation
├── src/                       # Source code
│   ├── __init__.py           # Package initialization
│   └── main.py               # FastAPI application
├── tests/                     # Test suite
│   ├── __init__.py           # Test package initialization
│   ├── conftest.py           # Pytest fixtures
│   └── test_main.py          # Comprehensive tests (10+)
├── .gitignore                # Git ignore patterns
├── pyproject.toml            # Project configuration
├── requirements.txt          # Python dependencies
├── CICD_IMPLEMENTATION.md    # Complete CI/CD reference (500+ lines)
└── README.md                 # This file
```

---

## API Endpoints

### Health & Status

#### `GET /`

Health check endpoint

**Response**:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "message": "GraphRAG Clinical Guidelines API"
}
```

#### `GET /health`

Detailed health status

**Response**:

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Core Operations

#### `POST /query`

Query the knowledge graph

**Request**:

```json
{
  "question": "What are the diabetes treatment guidelines?",
  "method": "local"  // Options: local, global, drift, basic
}
```

**Response**:

```json
{
  "answer": "Based on the clinical guidelines...",
  "citations": ["source1", "source2"],
  "method": "local"
}
```

#### `POST /index`

Trigger document indexing

**Request**:

```json
{
  "documents": ["doc1.pdf", "doc2.pdf"]
}
```

**Response**:

```json
{
  "status": "indexing_started",
  "documents_count": 2
}
```

#### `POST /build`

Build knowledge graph

**Request**:

```json
{
  "force_rebuild": false
}
```

**Response**:

```json
{
  "status": "build_started",
  "message": "Graph building initiated"
}
```

### Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/openapi.json>

---

## Development Workflow

### Creating a Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Make changes, add tests
# ...

# Run linting
ruff check src/ tests/ --fix
ruff format src/ tests/

# Run tests
pytest tests/ -v --cov=src

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to GitHub (triggers CI)
git push origin feature/your-feature-name
```

### Creating a Pull Request

```bash
# Using GitHub CLI
gh pr create --title "Add your feature" --body "Description of changes"

# Or create PR through GitHub web interface
```

**PR Checklist**:

- [ ] All CI checks pass (linting, tests, security)
- [ ] Code follows project style (Ruff compliant)
- [ ] Tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow convention

### Merging to Main

After PR approval and CI passes:

```bash
# Merge through GitHub interface or:
gh pr merge --squash
```

**Post-merge**: Staging workflow runs automatically on main branch

### Creating a Release

```bash
# Ensure main branch is stable
git checkout main
git pull origin main

# Create version tag
git tag -a v1.0.0 -m "Release version 1.0.0: Initial production release"

# Push tag (triggers production workflow)
git push origin v1.0.0
```

**Production workflow** validates the release and prepares for deployment

---

## Team

**Group 08 - ELEC 498A Capstone Project**

| Member | Student ID | Role |
|--------|------------|------|
| Omar Afify | 20oamz - 20287159 | Cloud Infrastructure & CI/CD |
| Nicolas Poirier | 20ndp3 - 20288795 | API Development & CRUD Operations |
| Sebastien Terrade | 20sct7 - 20278526 | Data Ingestion & Graph Building |
| Ian Fairfield | 20idf - 20283931 | Knowledge Graph & Evaluation |

**Supervisor**: Heidi Miller
**Partner**: ICI Medical

---

## Documentation

### Project Documentation

- [CLAUDE.md](../CLAUDE.md) - Complete project guide
- [CICD_IMPLEMENTATION.md](CICD_IMPLEMENTATION.md) - Complete CI/CD reference (500+ lines)
- [.github/workflows/README.md](.github/workflows/README.md) - Workflow details

### External Resources

- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
- [GraphRAG Paper](https://arxiv.org/abs/2404.16130)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)

---

## Project Status

**Current Version**: 0.1.0
**Phase**: 1 - CI/CD Pipeline (✅ Complete)

### Completed Milestones

- ✅ Project structure setup
- ✅ FastAPI REST API implementation
- ✅ Comprehensive test suite (10+ tests)
- ✅ GitHub Actions CI/CD workflows (3 environments)
- ✅ Linting and code quality checks
- ✅ Security scanning integration
- ✅ Coverage enforcement (70% staging, 80% production)

### Next Steps

- 🔄 Local GraphRAG validation with test documents
- 🔄 Docker integration (Phase 2)
- ⏳ AWS infrastructure deployment (Phase 3)
- ⏳ Knowledge graph implementation
- ⏳ Production deployment

---

## License

This project is developed as part of the ELEC 498A capstone course at Queen's University.

---

## Contributing

This is a capstone project with a fixed team. For questions or issues:

- **Team Discord**: Internal communication
- **Notion**: Sprint planning and issue tracking
- **GitHub Issues**: Bug reports and feature requests

---

**Last Updated**: November 13, 2024
**CI/CD Status**: ✅ Operational
