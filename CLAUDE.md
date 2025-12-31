# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Communication Preferences

**IMPORTANT: Keep all responses concise and narrowly scoped.**

- Answer ONLY what was asked - no additional examples, reference cards, or "helpful extras"
- Provide minimal code snippets - only what's needed
- Skip verbose explanations unless specifically requested
- No emoji headers, tables, or formatting unless asked

## Project Overview

This is the **ELEC 498A capstone project** implementing a **Graph-based Retrieval-Augmented Generation (GraphRAG) system for clinical health guidelines**, developed in partnership with **ICI Medical**. The system ingests medical documents, builds a knowledge graph, and returns cited, context-aware answers through a secure REST API.

**Supervisor:** Heidi Miller
**Group 08 Members:**

- Omar Afify (20oamz - 20287159)
- Nicolas Poirier (20ndp3 - 20288795)
- Sebastien Terrade (20sct7 - 20278526)
- Ian Fairfield (20idf - 20283931)

### Design Problem

Traditional vector-based RAG systems struggle with clinical documents because medical terminology causes tight clustering in semantic space, reducing retrieval precision. GraphRAG addresses this by constructing a knowledge graph that captures entities, relationships, and hierarchical communities, providing both local and global understanding of clinical guidelines.

## Project Status & Progress

This section tracks completed work against the project blueprint objectives. For detailed CI/CD implementation information, see `elec_498a_graph_rag/CICD_IMPLEMENTATION.md`.

### ✅ Phase 1: CI/CD Pipeline (COMPLETED)

**Completion Date:** Sprint 1
**Status:** Fully operational

#### What Was Implemented

1. **Project Structure**
   - Created modular repository structure with `src/`, `tests/`, `test_data/`, `.github/workflows/`
   - Configured Python 3.11 & 3.12 support with `pyproject.toml`
   - Set up dependency management with `requirements.txt`
   - Created `.gitignore` for Python, AWS, and GraphRAG artifacts

2. **FastAPI Application** (`src/main.py`)
   - **Health Check Endpoint** (`GET /`): Returns API version and status
   - **Query Endpoint** (`POST /query`): GraphRAG query interface with method selection (local/global/drift/basic)
   - **Index Endpoint** (`POST /index`): Trigger document indexing pipeline
   - **Build Endpoint** (`POST /build`): Build knowledge graph
   - Full Pydantic validation with request/response models
   - OpenAPI documentation auto-generated
   - Integrated with `GraphRAGService` for synchronous operations

3. **Test Suite** (`tests/`)
   - **20+ comprehensive tests** covering all endpoints and GraphRAG integration
   - Parametrized tests for all GraphRAG query methods
   - Validation tests for request/response schemas
   - Error handling tests (404, 400, 422 status codes)
   - GraphRAG integration tests with service layer
   - Test fixtures and client setup with pytest
   - Current coverage: **100%**

4. **GitHub Actions CI/CD Workflows**

   **CI Workflow** (`ci.yml`) - Runs on all branches
   - ✅ Ruff linting (code quality checks)
   - ✅ pytest with coverage reporting
   - ✅ Security checks with Safety
   - ✅ Codecov integration
   - ℹ️ No minimum coverage threshold (informational only)

   **Staging Workflow** (`staging.yml`) - Runs on main branch
   - ✅ Full test suite execution
   - ✅ Strict linting (no auto-fixes)
   - ✅ **70% coverage threshold enforced** (build fails if below)
   - 🔄 Docker build placeholder (ready for Phase 2)
   - ✅ Coverage report artifacts uploaded

   **Production Workflow** (`production.yml`) - Runs on version tags (v*.*.*)
   - ✅ Semantic version validation
   - ✅ Comprehensive test suite with strict markers
   - ✅ **80% coverage threshold enforced** (build fails if below)
   - ✅ Security scanning (Safety + Bandit)
   - ✅ High-severity vulnerability blocking
   - 🔄 Docker build placeholder (ready for Phase 3)
   - ✅ Deployment readiness summary

5. **Documentation**
   - Created `CICD_IMPLEMENTATION.md` (500+ lines) with complete reference
   - Workflow usage guides for development, staging, production
   - Troubleshooting section for common issues
   - Local testing commands
   - Branch protection recommendations

#### Current State

- **Repository**: `elec_498a_graph_rag/` fully initialized with git
- **Main Branch**: Protected with CI checks
- **Feature Branches**: CI runs automatically on push
- **Pull Requests**: CI must pass before merge
- **Releases**: Production workflow ready for v1.0.0 tag

#### Migration Path Status

| Phase | Status | Components |
|-------|--------|-----------|
| **Phase 1: CI/CD MVP** | ✅ **COMPLETE** | Linting, Testing, Coverage, Security scanning, Workflows |
| **Phase 2: Docker** | ✅ **COMPLETE** | Dockerfile, docker-compose, GraphRAG service layer, Integration tests |
| **Phase 3: GraphRAG Implementation** | 🔄 In Progress | Entity extraction, Neo4j integration, LanceDB embeddings |
| **Phase 4: AWS Integration** | 🔄 Planned | ECR, ECS Fargate, AWS CDK, Infrastructure as Code |
| **Phase 5: Advanced** | 🔄 Planned | Blue-green deployment, Rollback, Load testing |

### ✅ Phase 2: Docker Integration (COMPLETED)

**Completion Date:** Current Sprint
**Status:** Fully operational

#### What Was Implemented

1. **GraphRAG Service Layer** (`src/graphrag_service.py`)
   - Synchronous document indexing
   - Knowledge graph building
   - Query execution with multiple methods
   - Designed for future async conversion

2. **Docker Infrastructure**
   - **Dockerfile**: Multi-stage build with Python 3.12
   - **docker-compose.yml**: Orchestrates FastAPI + Neo4j + Ollama
   - **.dockerignore**: Optimized build context
   - Health checks and volume mounts configured

3. **Test Data Integration**
   - Moved `gr_test_env/christmas/` → `test_data/`
   - Created `.env.example` for Ollama configuration
   - Sample documents integrated with pytest fixtures

4. **Updated Dependencies**
   - Added: `graphrag>=0.3.0`, `neo4j>=5.14.0`, `lancedb>=0.3.0`, `boto3>=1.34.0`
   - Support for Python 3.11 and 3.12

5. **CI/CD Enhancements**
   - Added Docker build step to CI workflow
   - Matrix testing for Python 3.11 & 3.12
   - Updated staging workflow to Python 3.12

### 🔄 Current Sprint Focus

**Milestone 1: System Foundation** (Target: S1 Week 8)

- ✅ CI/CD pipeline established
- ✅ Docker integration complete
- ✅ Local GraphRAG setup complete
- 🔄 Implement GraphRAG library integration
- 🔄 Cloud infrastructure deployment pending
- ⏳ Database & storage configuration pending
- ⏳ Authentication system pending

**Next Steps:**

1. Implement GraphRAG indexing logic in `graphrag_service.py`
2. Implement Neo4j graph building
3. Implement query execution with LanceDB
4. Begin AWS infrastructure setup with CDK
5. Set up Cognito authentication

### 📊 Milestone Progress Tracking

| Milestone | Target | Status | Completed Tasks |
|-----------|--------|--------|----------------|
| **M1: System Foundation** | S1 W8 | 🔄 In Progress | CI/CD complete, GraphRAG testing |
| **M2: Data Ingestion Pipeline** | S1 W12 | ⏳ Not Started | - |
| **M3: Knowledge Graph & Retrieval** | S2 W1 | ⏳ Not Started | - |
| **M4: Evaluation Framework** | S2 W4 | ⏳ Not Started | - |

### 🏗️ System Architecture Status

#### Implemented Components

- ✅ **FastAPI REST API**: Core framework operational with 5 endpoints
- ✅ **GraphRAG Service**: Synchronous service layer with placeholder implementation
- ✅ **Test Infrastructure**: pytest framework with 20+ tests (100% coverage)
- ✅ **CI/CD Pipeline**: GitHub Actions workflows for 3 environments + Docker build
- ✅ **Docker Infrastructure**: Multi-stage Dockerfile + docker-compose with Neo4j + Ollama
- ✅ **Code Quality**: Ruff linting and formatting configured
- ✅ **Security Scanning**: Safety and Bandit integrated
- ✅ **Python Support**: 3.11 and 3.12 matrix testing

#### In Development

- 🔄 **Document Ingestion**: GraphRAG indexing pipeline implementation
- 🔄 **GraphRAG Engine**: Entity extraction with Ollama local LLM
- 🔄 **Neo4j Integration**: Graph construction and storage
- 🔄 **LanceDB Integration**: Vector embeddings for retrieval

#### Planned Components

- ⏳ **AWS Deployment**: ECS Fargate, API Gateway, Cognito
- ⏳ **Graph Database**: Neptune/Neo4j setup
- ⏳ **Vector Store**: LanceDB integration
- ⏳ **LLM Integration**: Bedrock/SageMaker deployment
- ⏳ **Storage**: S3 for documents, DynamoDB for caching

### 📈 Testing Coverage Status

| Environment | Coverage Requirement | Current Status | Notes |
|-------------|---------------------|----------------|-------|
| **Development** | None (informational) | ✅ Baseline established | All branches pass CI |
| **Staging** | ≥70% enforced | ✅ Infrastructure ready | Enforced on main branch |
| **Production** | ≥80% enforced | ✅ Infrastructure ready | Enforced on version tags |

### 🔐 Security & Compliance Progress

- ✅ Dependency vulnerability scanning (Safety)
- ✅ Static code analysis (Bandit)
- ✅ High-severity issue blocking in production
- ⏳ AWS KMS encryption (pending infrastructure)
- ⏳ Cognito authentication (pending setup)
- ⏳ IAM least-privilege policies (pending deployment)
- ⏳ CloudTrail audit logging (pending AWS setup)
- ⏳ Canadian data residency validation (pending deployment)

### 📝 Documentation Status

- ✅ **CLAUDE.md**: Comprehensive project guide (this file)
- ✅ **CICD_IMPLEMENTATION.md**: Complete CI/CD reference
- ✅ **Workflow README**: GitHub Actions usage guide
- ⏳ **API Documentation**: OpenAPI specs (auto-generated, needs expansion)
- ⏳ **Deployment Guide**: AWS setup instructions (pending)
- ⏳ **Developer Onboarding**: Team guide (pending)

### 🎯 Performance Metrics - Baseline Targets

These targets are from the project blueprint. Current status shows progress toward meeting them:

| Metric | Target | Current Status |
|--------|--------|----------------|
| Local query latency | ≤12±3s | ⏳ Not measured (pipeline not deployed) |
| Global query latency | ≤30±8s | ⏳ Not measured (pipeline not deployed) |
| Graph capacity | 30k nodes, 100k edges | ⏳ Not measured (graph not built) |
| System uptime | ≥90% | ⏳ Not deployed |
| Data residency | 100% Canadian | ⏳ Pending AWS deployment |
| Test coverage | ≥70% staging, ≥80% prod | ✅ Enforcement infrastructure ready |

## System Architecture

### Microservices Design

The system follows a **modular microservices architecture** with independently deployable components communicating through REST APIs. This enables parallel development, isolated unit testing, and scalable cloud deployment.

### High-Level Data Flow

1. **Document Ingestion** → Documents (.pdf, .docx, JSON) processed via Document Loader (OCR, parsing)
2. **Text Processing** → Text + Metadata flows into Microsoft GraphRAG pipeline
3. **Entity Extraction** → LLM identifies medical entities (organizations, people, geo, events)
4. **Graph Generation** → Graph Generation Engine creates knowledge graph with community detection
5. **Storage** → Knowledge Graph stored in Neptune/Neo4j with LanceDB vector store
6. **Query Interface** → REST API provides Index, Build, Fetch, and Query operations
7. **Response Generation** → Returns answers with citations from graph traversal

### Architecture Diagram

See `Picture1.svg` in root directory and Figure 3 in `documents/ELEC498A_group08_draft_blueprint.pdf`

## System Requirements

### Functional Requirements

1. **CRUD Operations**: Full Create, Read, Update, Delete support on knowledge graph
2. **Document Ingestion Pipeline**: Process 1-2 clinical guidelines (100k-300k tokens each)
3. **Query with Citations**: Return context with embedded metadata citations

### Interface Requirements

1. **REST API**: Three primary endpoints - `query`, `index`, `build`
2. **Cloud Deployment**: AWS hosting with IAM and Cognito authentication
3. **Developer Documentation**: Full API and pipeline documentation in Markdown

### Performance Requirements

| Metric | Target Value |
|--------|--------------|
| Local query latency | ≤ 12 ± 3 seconds |
| Global query latency | ≤ 30 ± 8 seconds |
| Graph capacity | 30k nodes, 100k edges (±10k/±30k) |
| System uptime | ≥90% during testing |
| Data residency | 100% Canadian servers (PHIPA/PIPEDA) |

### Optional Requirements

- **Fetch endpoint**: Direct node retrieval without querying
- **Web GUI**: Basic query interface for demonstrations
- **Graph import/export**: Archive/restore via parquet files

## Technology Stack

### Programming Languages & Frameworks

- **Python 3.11**: Primary language for all components
- **FastAPI**: High-performance async REST API framework with OpenAPI docs
- **Docker/Docker Compose**: Containerization for local development
- **AWS CDK (Python)**: Infrastructure as code

### Core Libraries

- **Microsoft GraphRAG Library**: Knowledge graph ingestion and traversal
- **Neo4j Drivers**: Graph database connectivity
- **LangChain**: LLM and graph retrieval integration
- **DeepEval**: LLM-as-a-judge evaluation framework
- **UV**: Python dependency management for reproducible builds
- **Pandas, NumPy, Matplotlib**: Data analysis and visualization
- **Pydantic**: Data validation for API schemas
- **pytest**: Unit and integration testing

### AWS Services

| Service | Purpose | Cost Allocation |
|---------|---------|-----------------|
| **ECS Fargate** | Host containerized FastAPI and ingestion jobs | $120 |
| **API Gateway** | Public REST endpoint exposure | (included) |
| **Cognito** | Authentication and user management | (included) |
| **Neptune / Neo4j (EC2)** | Graph database storage and Cypher queries | $100 |
| **S3** | Object storage for documents and summaries | $40 |
| **DynamoDB** | Cache for community summaries and logs | $50 |
| **Bedrock / SageMaker** | Managed LLM inference | $250 |
| **SQS** | Queue management for async jobs | (included) |
| **CloudWatch + CloudTrail** | System monitoring and audit logs | $40 |
| **KMS + Macie + WAF + IAM** | Encryption, DLP, and access control | (included) |
| **CodeBuild** | CI/CD deployment automation | (included) |

**Total Budget:** $600

### Development Tools

- **GitHub + GitHub Actions**: Version control and CI/CD
- **Notion**: Sprint planning and backlog management
- **Discord**: Daily team communication
- **Draw.io**: System architecture diagrams
- **Amazon Linux 2**: Container OS for AWS compatibility

## Development Methodology

### Agile Approach

- **Sprint Duration**: 2 weeks
- **Sprint Workflow**:
  1. Planning: Decompose milestones into atomic tasks
  2. Development: Parallel work with frequent commits and code reviews
  3. Integration Testing: Sprint-end validation and CI/CD push
  4. Review & Retrospective: Demo to supervisor, gather feedback

### Iterative Prototyping Versions

#### v0.1 - Proof of Concept (Milestones 1-2, S1 Week 8)

- Local GraphRAG engine, single test document, CLI query interface
- Validates document-to-graph conversion feasibility
- Manual testing with sample document

#### v0.5 - Alpha (Milestone 2-3, S1 Week 12)

- Cloud-deployed with 5 documents
- Basic REST API with index & query endpoints
- Unit tests + integration tests + simple CI/CD

#### v1.0 - MVP (Milestone 3, S2 Week 1)

- Complete ingestion pipeline, multi-document graph
- Full REST API (all endpoints operational)
- Comprehensive unit tests (100% coverage)
- AWS production deployment with full CI/CD

#### v2.0 - Production (Milestone 4, S2 Week 4)

- Evaluation framework integrated
- LLM-as-judge via DeepEval
- Load testing and security hardening
- Comparative analysis complete

## Milestones & Division of Labor

### Milestone 1: System Foundation (S1 Week 8)

- 1.1 Local GraphRAG Setup (Seb T, Ian F)
- 1.2 Cloud Infrastructure Deployment (Omar A)
- 1.3 Database & Storage Configuration (Ian F, Seb T)
- 1.4 Authentication System (Nick P, Omar A)
- 1.5 Deploy Compute Resources (Omar A)

### Milestone 2: Data Ingestion Pipeline (S1 Week 12)

- 2.1 Parse Documents & Validate Formats (Seb T)
- 2.2 Extract Metadata for Citations (Seb T, Ian F)
- 2.3 Implement Node/Edge/Community Scripts (Seb T)
- 2.4 Create Initial CRUD Operations (Nick P, Seb T)

### Milestone 3: Knowledge Graph & Retrieval (S2 Week 1)

- 3.1 Integrate Retrieval Model with Graph (Ian F, Omar A)
- 3.2 Implement Query Mappings via REST API (Nick P)
- 3.3 Log Performance Metrics (Ian F)

### Milestone 4: Evaluation Framework (S2 Week 4)

- 4.1 Implement LLM-as-judge Evaluation (Ian F, Omar A)
- 4.2 Collect Metrics (Ian F, Omar A)
- 4.3 Create Performance Report (Everyone)

## Common Commands

### Local Development

**Setup environment:**

```bash
# Create conda environment with Python 3.12
conda create -n elec498_py312 python=3.12
conda activate elec498_py312

# Install dependencies
python -m pip install -r requirements.txt
```

**Run FastAPI server:**

```bash
# Development mode with auto-reload
python -m uvicorn src.main:app --reload

# Access API docs at http://localhost:8000/docs
```

**Run tests:**

```bash
# All tests with coverage
python -m pytest tests/ -v --cov=src

# Single test
python -m pytest tests/test_main.py::test_root_endpoint -v

# Integration tests only
python -m pytest tests/test_graphrag_integration.py -v
```

**Test data location:**

```bash
# Sample documents
ls test_data/input/

# GraphRAG configuration
cat test_data/settings.yaml
cat test_data/.env.example
```

### Docker Commands

**Build and run all services:**

```bash
# Build containers
docker-compose build

# Start services (FastAPI + Neo4j + Ollama)
docker-compose up

# Run in background
docker-compose up -d
```

**Test Docker setup:**

```bash
# Check API health
curl http://localhost:8000/health

# View Neo4j browser
open http://localhost:7474

# Check logs
docker-compose logs -f fastapi-graphrag
```

**Stop services:**

```bash
docker-compose down

# Remove volumes
docker-compose down -v
```

### AWS Deployment

**Deploy infrastructure:**

```bash
cd infrastructure
cdk deploy
```

**Check CloudWatch metrics:**

```bash
aws cloudwatch get-metric-statistics \
  --namespace GraphRAG \
  --metric-name QueryLatency \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

## Configuration

### GraphRAG Settings

Located at `test_data/settings.yaml` and `test_data/.env.example`:

**Current Setup (Local Ollama):**

- Chat Model: llama3 (via Ollama)
- Embedding: Local embeddings
- Base URL: `http://localhost:11434` (or `http://ollama:11434` in Docker)
- No API key required

**Future Setup (HuggingFace):**

- Will use HuggingFace hosted models
- API Key: `${HUGGINGFACE_API_KEY}` from `.env`

**Legacy (Not Used):**

- OpenAI GPT-4o-mini
- API Key: `${GRAPHRAG_API_KEY}`

**Chunking:**

- Size: 1200 tokens
- Overlap: 100 tokens
- Group by: ID column

**Entity Extraction:**

- Entity types: `[organization, person, geo, event]`
- Max gleanings: 1
- Custom prompt: `prompts/extract_graph.txt`

**Graph Processing:**

- Max cluster size: 10
- Community reports: Enabled
- Graph embeddings (node2vec): Disabled
- UMAP: Disabled

### Search Methods

Four modes available in `prompts/`:

1. **local_search**: Context-focused, embedding-based retrieval (≤12s)
2. **global_search**: Map-reduce across entire graph (≤30s)
3. **drift_search**: Iterative query refinement
4. **basic_search**: Simple embedding search

### Custom Prompts

Modify prompts in `gr_test_env/christmas/prompts/`:

- `extract_graph.txt`: Entity and relationship extraction
- `local_search_system_prompt.txt`: Local search behavior
- `global_search_map_system_prompt.txt`: Global search mapping
- `global_search_reduce_system_prompt.txt`: Global search reduction
- `community_report_graph.txt`: Community summarization
- `summarize_descriptions.txt`: Entity descriptions

## Testing Strategy

### Test Environment

- **Local-dev**: Docker Compose for rapid iteration
- **Staging**: ECS Fargate + API Gateway for integration tests
- **Production**: Full AWS deployment

### Test Stages

1. **Unit Tests** (local, CI with pytest):
   - Ingestion: File parsing, text extraction, citation capture
   - Graph build: Schema conformance, de-duplication
   - Retrieval: Prompt assembly, local vs global routing
   - API: Request/response validation (Pydantic)

2. **Component Tests** (CI + staging):
   - Index pipeline: S3 → preprocessing → GraphRAG → Neptune
   - Query path: API Gateway → Cognito → FastAPI → retriever → LLM
   - SQS queues: Enqueue/dequeue, dead-letter routing

3. **End-to-End Tests** (staging):
   - Full flow: Document upload → build → query → cited response
   - Snapshot tests for regression detection

4. **Non-Functional Tests** (staging):
   - Latency: P95 via CloudWatch
   - Capacity: 30k nodes / 100k edges
   - Reliability: ≥90% uptime, chaos testing
   - Security: Cognito auth, IAM least-privilege, KMS encryption
   - Cost controls: Budget alarms, per-request estimates

5. **LLM-as-Judge Evaluation** (DeepEval):
   - Faithfulness, Relevance, Citation accuracy
   - Comprehensiveness target: ≥72%
   - Pairwise comparison vs baseline vector RAG (>60% win rate)

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v --cov

# E2E tests
pytest tests/e2e/ -v --capture=no

# DeepEval evaluation
python scripts/evaluate.py --dataset clinical_guidelines
```

## CI/CD Pipeline

### GitHub Actions Workflow

On every pull request:

1. Checkout code
2. Lint with ruff/black
3. Run unit + component tests with pytest
4. Build Docker image
5. Push to AWS ECR on merge to main

### AWS CodeBuild Integration

On merge to main:

1. GitHub Actions triggers AWS CodeBuild
2. CodeBuild runs integration tests
3. Builds production container image
4. Pushes to ECR with versioned tags
5. Updates ECS service with new image
6. CloudWatch monitors deployment health

See `documents/ELEC498A_group08_draft_blueprint.pdf` Figure 2 for architecture diagram.

## Data Sources

### Clinical Guidelines

- **Diabetes Canada**: <https://guidelines.diabetes.ca/cpg>
- **WHO Guidelines**: World Health Organization clinical protocols
- **NCCN**: National Comprehensive Cancer Network guidelines

### Research Datasets

- **Microsoft GraphRAG**: Reference implementation and benchmarks
- **IEEE Xplore, arXiv**: Technical resources for methodology

### Test Data

- Current test: "A Christmas Carol" (gr_test_env/christmas/input/book.txt)
- Purpose: Validate pipeline before processing sensitive medical documents

## Security & Compliance

### Data Privacy

- **No PHI/PII**: Only public clinical guidelines, no patient data
- **PHIPA/PIPEDA**: 100% Canadian data residency requirement
- **Encryption**: KMS encryption at rest, TLS in transit
- **Access Control**: IAM least-privilege, Cognito authentication

### Security Measures

- **AWS Macie**: Scans S3 for accidental sensitive data exposure
- **WAF**: Protects API from common web exploits
- **CloudTrail**: Audit logs for all API calls
- **Secrets Management**: API keys in AWS Secrets Manager, never in code

## Known Issues & Mitigation

### Problem 1: Cloud Service Integration

**Mitigation:** Strict modularity, clear API interfaces, comprehensive logging
**Recovery:** Fall back to local containerized deployment during AWS debugging

### Problem 2: Slow Graph Building

**Mitigation:** Lightweight load testing, caching repeated queries
**Recovery:** Temporarily reduce graph scope while optimizing

### Problem 3: LLM Extraction Errors

**Mitigation:** Tight prompt control, validation scripts on each batch
**Recovery:** Mix LLM with rule-based extraction for critical sections

### Problem 4: Budget Overruns

**Mitigation:** AWS budget alarms, smaller models in dev, auto-shutdown
**Recovery:** Switch to Neo4j (local) and open-source LLMs

### Problem 5: Deployment Delays

**Mitigation:** Cross-trained backup developers, 1-2 day sprint buffers
**Recovery:** Reduce scope of non-critical features (GUI, fetch endpoint)

### Problem 6: Breaking Changes

**Mitigation:** CI/CD with automated integration tests
**Recovery:** Rollback to previous stable container image

## Project Structure

```
/Users/ianfairfield/queens/elec_498A/
├── documents/                              # Project documentation
│   ├── ELEC498A_group08_draft_blueprint.pdf  # Detailed system design
│   ├── graphrag_paper.pdf                  # Microsoft GraphRAG research
│   └── proposallecture.pdf                 # Course materials
├── elec_498a_graph_rag/                    # Main git repository
│   ├── src/                                # Source code
│   │   ├── __init__.py                     # Package initialization
│   │   ├── main.py                         # FastAPI application
│   │   └── graphrag_service.py             # GraphRAG service layer
│   ├── tests/                              # Test suites
│   │   ├── conftest.py                     # pytest fixtures
│   │   ├── test_main.py                    # API endpoint tests
│   │   └── test_graphrag_integration.py    # GraphRAG integration tests
│   ├── test_data/                          # Test environment (moved from gr_test_env)
│   │   ├── settings.yaml                   # GraphRAG configuration
│   │   ├── .env.example                    # Environment template
│   │   ├── input/                          # Input documents
│   │   │   └── book.txt                    # "A Christmas Carol" sample
│   │   ├── output/                         # Generated graph artifacts
│   │   ├── cache/                          # Pipeline cache
│   │   ├── logs/                           # Processing logs
│   │   └── prompts/                        # Custom LLM prompts
│   ├── .github/workflows/                  # CI/CD workflows
│   │   ├── ci.yml                          # CI with Docker build
│   │   ├── staging.yml                     # Staging deployment
│   │   └── production.yml                  # Production deployment
│   ├── Dockerfile                          # Multi-stage Docker build
│   ├── .dockerignore                       # Docker build exclusions
│   ├── docker-compose.yml                  # Local dev orchestration
│   ├── requirements.txt                    # Python dependencies
│   ├── pyproject.toml                      # Project configuration
│   └── CICD_IMPLEMENTATION.md              # CI/CD documentation
└── Picture1.svg                            # Architecture diagram
```

## Development Workflow

### Adding New Features

1. Create feature branch from `main`
2. Implement feature with unit tests
3. Run local tests: `pytest tests/ -v`
4. Submit PR with description
5. Code review by at least one team member
6. CI passes (linting + tests)
7. Merge to main triggers deployment

### Modifying Prompts

1. Edit prompt file in `gr_test_env/christmas/prompts/`
2. Test locally: `graphrag index --root gr_test_env/christmas`
3. Evaluate with DeepEval: `python scripts/evaluate.py`
4. Commit changes if metrics improve

### Adjusting Graph Parameters

1. Edit `test_data/settings.yaml`
2. Test in Docker: `docker-compose restart fastapi-graphrag`
3. Or rebuild locally: Access via API endpoints
4. Update documentation if changing defaults

### Deploying to AWS

1. Update AWS CDK stacks in `infrastructure/`
2. Run `cdk diff` to preview changes
3. Deploy: `cdk deploy --all`
4. Monitor CloudWatch for errors
5. Rollback if needed: `cdk deploy --rollback`

## Performance Optimization Tips

- **Caching**: Use DynamoDB for repeated community summaries
- **Batch Processing**: Process multiple documents in single indexing run
- **Smaller Models**: Use GPT-3.5-turbo in development to reduce costs
- **Chunking**: Adjust size/overlap in `settings.yaml` for balance of context vs speed
- **Graph Pruning**: Remove low-weight edges to reduce traversal time

## Important Notes

### API Keys and Secrets

- `.env` files contain sensitive keys - NEVER commit to Git
- Use AWS Secrets Manager for production credentials
- Rotate keys regularly per security policy

### Medical Domain Considerations

- Entity types optimized for clinical guidelines (organization, person, geo, event)
- Citations embedded in graph nodes via metadata
- Consider HIPAA implications for any future patient data

### GraphRAG Rate Limiting

- 25 concurrent LLM requests
- Auto rate limiting based on model
- Native retry strategy with max 10 retries

### Cost Management

- CloudWatch alarms set at 80% of budget
- Auto-shutdown non-production resources
- Use smaller models and reduced datasets in dev/test

## Resources & References

- **Microsoft GraphRAG**: <https://microsoft.github.io/graphrag/>
- **GraphRAG Paper**: [arXiv:2404.16130](https://arxiv.org/abs/2404.16130)
- **AWS Well-Architected**: <https://docs.aws.amazon.com/wellarchitected/>
- **DeepEval Docs**: <https://deepeval.com/docs/getting-started>
- **FastAPI Docs**: <https://fastapi.tiangolo.com/>
- **Neo4j Cypher**: <https://neo4j.com/docs/cypher-manual/>

## Contact & Support

- **Supervisor**: Heidi Miller
- **GitHub**: <https://github.com/ianfv/elec_498a_graph_rag>
- **Team Discord**: Internal communication channel
- **Notion**: Project tracking and sprint planning
