"""
FastAPI application entry point for GraphRAG system.

This module provides the REST API for the GraphRAG clinical guidelines system.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from src import __version__
from src.graphrag_service import GraphRAGService

# Create FastAPI app
app = FastAPI(
    title="GraphRAG Clinical Guidelines API",
    description="Graph-based RAG system for clinical health guidelines",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize GraphRAG service
graphrag_service = GraphRAGService(root_dir="./test_data")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    message: str


class QueryRequest(BaseModel):
    """Query request model."""

    question: str
    method: str = "local"  # local, global, drift, basic


class QueryResponse(BaseModel):
    """Query response model."""

    answer: str
    citations: list[str] = []
    method: str


class IndexRequest(BaseModel):
    """Index/Update request model."""

    method: str = "standard"  # standard or fast


class IndexResponse(BaseModel):
    """Index response model."""

    status: str
    message: str
    indexed_files: list[str] = []
    entities_extracted: int = 0
    nodes: int = 0
    edges: int = 0
    communities: int = 0


class UpdateResponse(BaseModel):
    """Update response model."""

    status: str
    message: str
    updated_files: list[str] = []
    entities_extracted: int = 0
    nodes: int = 0
    edges: int = 0
    communities: int = 0


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        message="GraphRAG Clinical Guidelines API is running",
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        message="All systems operational",
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Query the knowledge graph.

    Executes synchronous query against Neo4j + LanceDB using specified method.

    Args:
        request: Query request containing question and search method

    Returns:
        QueryResponse with answer and citations
    """
    result = graphrag_service.query_graph(question=request.question, method=request.method)

    return QueryResponse(
        answer=result["answer"],
        citations=result.get("citations", []),
        method=result["method"],
    )


@app.post("/index", response_model=IndexResponse)
async def index_documents(request: IndexRequest = IndexRequest()) -> IndexResponse:
    """
    Trigger document indexing.

    Processes documents through the complete GraphRAG pipeline:
    - Document chunking into text units
    - Entity and relationship extraction
    - Community detection and summarization
    - Embedding generation

    Args:
        request: Index request containing method selection (standard/fast)

    Returns:
        IndexResponse with indexing results and graph statistics
    """
    result = graphrag_service.index_documents(method=request.method)

    message = "Indexing completed successfully"
    if result["status"] == "failed":
        message = result.get("error", "Indexing failed")

    return IndexResponse(
        status=result["status"],
        message=message,
        indexed_files=result.get("indexed_files", []),
        entities_extracted=result["entities_extracted"],
        nodes=result["nodes"],
        edges=result["edges"],
        communities=result["communities"],
    )


@app.post("/update", response_model=UpdateResponse)
async def update_documents(request: IndexRequest = IndexRequest()) -> UpdateResponse:
    """
    Trigger incremental document update.

    Processes only new or changed documents, leveraging cached results
    for unchanged content. Communities are recomputed to include new entities.

    Args:
        request: Index request containing method selection (standard/fast)

    Returns:
        UpdateResponse with update results and graph statistics
    """
    result = graphrag_service.update_documents(method=request.method)

    message = "Update completed successfully"
    if result["status"] == "failed":
        message = result.get("error", "Update failed")

    return UpdateResponse(
        status=result["status"],
        message=message,
        updated_files=result.get("updated_files", []),
        entities_extracted=result["entities_extracted"],
        nodes=result["nodes"],
        edges=result["edges"],
        communities=result["communities"],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
