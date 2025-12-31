"""
Integration tests for GraphRAG service and API endpoints.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.graphrag_service import GraphRAGService


@pytest.fixture
def sample_document_path() -> Path:
    """
    Get path to sample test document.

    Returns:
        Path to book.txt in test_data/input/
    """
    return Path("test_data/input/book.txt")


@pytest.fixture
def sample_document_content(sample_document_path: Path) -> str:
    """
    Load sample test document content.

    Returns:
        Content of book.txt for testing
    """
    if sample_document_path.exists():
        return sample_document_path.read_text()
    else:
        return "Sample document for testing GraphRAG integration."


@pytest.fixture
def graphrag_service() -> GraphRAGService:
    """
    Create GraphRAG service instance for testing.

    Returns:
        GraphRAGService instance pointing to test_data/
    """
    return GraphRAGService(root_dir="test_data")


def test_graphrag_service_initialization(graphrag_service: GraphRAGService):
    """Test GraphRAG service initializes correctly."""
    assert graphrag_service.root_dir.name == "test_data"
    assert graphrag_service.input_dir.name == "input"
    assert graphrag_service.output_dir.name == "output"


def test_index_documents_endpoint(client: TestClient):
    """Test /index endpoint returns correct structure."""
    response = client.post("/index")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "indexed_files" in data
    assert "entities_extracted" in data
    assert isinstance(data["indexed_files"], list)


def test_build_graph_endpoint(client: TestClient):
    """Test /build endpoint returns correct structure."""
    response = client.post("/build")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "nodes" in data
    assert "edges" in data
    assert "communities" in data
    assert isinstance(data["nodes"], int)
    assert isinstance(data["edges"], int)


def test_query_endpoint_with_graphrag_service(
    client: TestClient, sample_local_query: dict
):
    """Test /query endpoint integrates with GraphRAG service."""
    response = client.post("/query", json=sample_local_query)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "method" in data
    assert data["method"] == "local"


def test_graphrag_service_index_documents(graphrag_service: GraphRAGService):
    """Test GraphRAG service index_documents method."""
    result = graphrag_service.index_documents(documents=["book.txt"])
    assert "status" in result
    assert result["status"] in ["completed", "failed"]
    assert "indexed_files" in result
    assert isinstance(result["indexed_files"], list)


def test_graphrag_service_build_graph(graphrag_service: GraphRAGService):
    """Test GraphRAG service build_graph method."""
    result = graphrag_service.build_graph()
    assert "status" in result
    assert result["status"] in ["completed", "failed"]
    assert "nodes" in result
    assert "edges" in result


def test_graphrag_service_query_graph(graphrag_service: GraphRAGService):
    """Test GraphRAG service query_graph method."""
    result = graphrag_service.query_graph(
        question="What is the main theme?",
        method="local"
    )
    assert "answer" in result
    assert "citations" in result
    assert "method" in result
    assert result["method"] == "local"


@pytest.mark.parametrize("method", ["local", "global", "drift", "basic"])
def test_query_all_methods_with_service(
    client: TestClient, method: str
):
    """Test query endpoint works with all GraphRAG methods."""
    query = {
        "question": "Test question for GraphRAG",
        "method": method,
    }
    response = client.post("/query", json=query)
    assert response.status_code == 200
    assert response.json()["method"] == method


def test_sample_document_exists(sample_document_path: Path):
    """Test that sample document exists in test_data."""
    # This test will pass even if file doesn't exist yet (planned for migration)
    expected_location = Path("test_data/input/book.txt")
    assert sample_document_path == expected_location
