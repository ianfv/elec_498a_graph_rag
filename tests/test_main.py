"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from src import __version__


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns correct health status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == __version__
    assert "GraphRAG" in data["message"]


def test_health_check_endpoint(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == __version__


def test_query_endpoint_with_default_method(client: TestClient, sample_local_query: dict):
    """Test query endpoint with default search method."""
    response = client.post("/query", json=sample_local_query)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert data["method"] == "local"
    assert isinstance(data["citations"], list)


def test_query_endpoint_with_global_method(client: TestClient, sample_global_query: dict):
    """Test query endpoint with global search method."""
    response = client.post("/query", json=sample_global_query)
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "global"


def test_query_endpoint_requires_question(client: TestClient):
    """Test query endpoint validation - question is required."""
    response = client.post("/query", json={"method": "local"})
    assert response.status_code == 422  # Validation error


def test_index_documents_endpoint(client: TestClient):
    """Test document indexing endpoint."""
    response = client.post("/index")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data


def test_build_graph_endpoint(client: TestClient):
    """Test graph building endpoint."""
    response = client.post("/build")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data


def test_openapi_docs_available(client: TestClient):
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available(client: TestClient):
    """Test that ReDoc documentation is available."""
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "method",
    ["local", "global", "drift", "basic"],
)
def test_query_with_different_methods(client: TestClient, method: str):
    """Test query endpoint with different search methods."""
    query = {
        "question": "Test question",
        "method": method,
    }
    response = client.post("/query", json=query)
    assert response.status_code == 200
    assert response.json()["method"] == method
