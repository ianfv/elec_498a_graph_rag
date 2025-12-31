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
    result = graphrag_service.query_graph(
        question=request.question,
        method=request.method
    )

    return QueryResponse(
        answer=result["answer"],
        citations=result.get("citations", []),
        method=result["method"],
    )


@app.post("/index")
async def index_documents() -> dict[str, str | int]:
    """
    Trigger document indexing.

    Processes documents through GraphRAG pipeline synchronously.
    Extracts entities and prepares for graph construction.

    Returns:
        Status message with indexing results
    """
    result = graphrag_service.index_documents()

    return {
        "status": result["status"],
        "message": result.get("message", "Documents indexed successfully"),
        "indexed_files": result.get("indexed_files", []),
        "entities_extracted": result.get("entities_extracted", 0),
    }


@app.post("/build")
async def build_graph() -> dict[str, str | int]:
    """
    Build or rebuild the knowledge graph.

    Constructs Neo4j graph from indexed documents synchronously.
    Creates entities, relationships, communities, and LanceDB embeddings.

    Returns:
        Status message with graph statistics
    """
    result = graphrag_service.build_graph()

    return {
        "status": result["status"],
        "message": result.get("message", "Graph built successfully"),
        "nodes": result.get("nodes", 0),
        "edges": result.get("edges", 0),
        "communities": result.get("communities", 0),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
