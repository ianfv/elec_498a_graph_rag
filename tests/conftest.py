"""
Pytest configuration and fixtures for GraphRAG tests.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.graphrag_service import GraphRAGService
from src.main import app

# =============================================================================
# Endpoint Testing Fixtures
# =============================================================================


@pytest.fixture
def client() -> TestClient:
    """
    Create a FastAPI test client.

    Returns:
        TestClient instance for testing API endpoints
    """
    return TestClient(app)


@pytest.fixture
def sample_local_query() -> dict[str, str]:
    """
    Sample query request for testing.

    Returns:
        Dictionary with sample query data
    """
    return {
        "question": "What should I monitor when treating diabetes and how often?",
        "method": "local",
    }


@pytest.fixture
def sample_global_query() -> dict[str, str]:
    """
    Sample global request for testing.

    Returns:
        Dictionary with sample query data
    """
    return {
        "question": "What are the most important steps in treating diabetes",
        "method": "global",
    }


@pytest.fixture
def sample_guideline_text() -> str:
    """
    Sample clinical guideline text for testing.

    Returns:
        String containing sample guideline content
    """
    return """
    Diabetes Treatment Guidelines:
    1. Monitor blood glucose levels regularly
    2. Maintain HbA1c below 7% for most adults
    3. Consider lifestyle modifications first
    4. Prescribe metformin as first-line therapy
    5. Adjust medications based on individual response
    """


# =============================================================================
# Service Layer Testing Fixtures
# =============================================================================


@pytest.fixture
def temp_graphrag_root(tmp_path) -> Path:
    """
    Create temporary GraphRAG directory structure.

    Returns:
        Path to temporary root directory with input/output/update_output/cache subdirs
    """
    root = tmp_path / "graphrag_test"
    (root / "input").mkdir(parents=True)
    (root / "output").mkdir()
    (root / "update_output").mkdir()
    (root / "cache").mkdir()
    return root


@pytest.fixture
def mock_settings_yaml(temp_graphrag_root) -> Path:
    """
    Create minimal settings.yaml for testing.

    Returns:
        Path to created settings.yaml file
    """
    settings_content = """
models:
  default_chat_model:
    type: ollama
    model: llama3
  default_embedding_model:
    type: ollama
    model: nomic-embed-text
input:
  type: file
  base_dir: input
output:
  type: file
  base_dir: output
cache:
  type: file
  base_dir: cache
"""
    settings_path = temp_graphrag_root / "settings.yaml"
    settings_path.write_text(settings_content)
    return settings_path


@pytest.fixture
def graphrag_service(temp_graphrag_root, mock_settings_yaml) -> GraphRAGService:
    """
    Create GraphRAGService instance with isolated temp directory.

    Returns:
        GraphRAGService instance pointing to temporary directory
    """
    return GraphRAGService(root_dir=temp_graphrag_root)


@pytest.fixture
def mock_parquet_output(temp_graphrag_root) -> Path:
    """
    Create mock parquet files in output directory for stats testing.

    Returns:
        Path to output directory containing mock parquet files
    """
    output_dir = temp_graphrag_root / "output"

    # Mock entities parquet
    entities_df = pd.DataFrame({"id": range(10), "name": [f"entity_{i}" for i in range(10)]})
    entities_df.to_parquet(output_dir / "create_final_entities.parquet")

    # Mock relationships parquet
    relationships_df = pd.DataFrame({"source": range(15), "target": range(15)})
    relationships_df.to_parquet(output_dir / "create_final_relationships.parquet")

    # Mock communities parquet
    communities_df = pd.DataFrame({"id": range(3), "title": ["comm_1", "comm_2", "comm_3"]})
    communities_df.to_parquet(output_dir / "create_final_communities.parquet")

    return output_dir


@pytest.fixture
def mock_update_parquet_output(temp_graphrag_root) -> Path:
    """
    Create mock parquet files in update_output for update stats testing.

    Returns:
        Path to update_output directory containing mock parquet files
    """
    update_dir = temp_graphrag_root / "update_output"

    # Mock documents parquet with title column
    docs_df = pd.DataFrame({"title": ["doc1.txt", "doc2.txt"]})
    docs_df.to_parquet(update_dir / "create_final_documents.parquet")

    # Mock entities parquet
    entities_df = pd.DataFrame({"id": range(5), "name": [f"entity_{i}" for i in range(5)]})
    entities_df.to_parquet(update_dir / "create_final_entities.parquet")

    # Mock relationships parquet
    relationships_df = pd.DataFrame({"source": range(8), "target": range(8)})
    relationships_df.to_parquet(update_dir / "create_final_relationships.parquet")

    # Mock communities parquet
    communities_df = pd.DataFrame({"id": range(2), "title": ["comm_1", "comm_2"]})
    communities_df.to_parquet(update_dir / "create_final_communities.parquet")

    return update_dir


@pytest.fixture
def sample_input_files(temp_graphrag_root) -> list[Path]:
    """
    Create sample input files for testing.

    Returns:
        List of paths to created sample input files
    """
    input_dir = temp_graphrag_root / "input"
    files = []
    for name in ["doc1.txt", "doc2.txt", "doc3.txt"]:
        f = input_dir / name
        f.write_text(f"Content of {name}")
        files.append(f)
    return files


@pytest.fixture
def sample_document_path() -> Path:
    """
    Get path to sample test document (for integration tests).

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
    return "Sample document for testing GraphRAG integration."


# =============================================================================
# Mocking Fixtures
# =============================================================================


@pytest.fixture
def mock_build_index():
    """
    Mock graphrag.api.index.build_index to avoid actual indexing.

    Yields:
        Mocked build_index function
    """
    with patch("src.graphrag_service.build_index", new_callable=AsyncMock) as mock:
        mock.return_value = None  # build_index returns None on success
        yield mock


@pytest.fixture
def mock_load_config():
    """
    Mock graphrag config loading.

    Yields:
        Tuple of (mock function, mock config object)
    """
    with patch("src.graphrag_service.load_config") as mock:
        mock_config = MagicMock()
        mock.return_value = mock_config
        yield mock, mock_config
