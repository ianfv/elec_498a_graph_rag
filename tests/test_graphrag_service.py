"""
Unit tests for GraphRAGService class.

Tests cover:
- Class initialization and directory path handling
- Configuration loading and caching
- Indexing method resolution
- Internal stats and file listing methods
- Document indexing and updating operations
- Query and export functionality
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from graphrag.config.enums import IndexingMethod

from src.graphrag_service import GraphRAGService

# =============================================================================
# TestGraphRAGServiceInitialization
# =============================================================================


class TestGraphRAGServiceInitialization:
    """Tests for GraphRAGService initialization and class variables."""

    def test_init_default_paths(self, temp_graphrag_root, mock_settings_yaml):
        """Test service initializes with correct default directory structure."""
        service = GraphRAGService(root_dir=temp_graphrag_root)

        assert service.root_dir == temp_graphrag_root
        assert service.input_dir == temp_graphrag_root / "input"
        assert service.output_dir == temp_graphrag_root / "output"
        assert service.update_output_dir == temp_graphrag_root / "update_output"
        assert service.cache_dir == temp_graphrag_root / "cache"

    def test_init_custom_root_dir_string(self, tmp_path):
        """Test service accepts string root_dir."""
        root_str = str(tmp_path / "custom_root")
        service = GraphRAGService(root_dir=root_str)

        assert service.root_dir == Path(root_str)
        assert isinstance(service.root_dir, Path)

    def test_init_custom_root_dir_path(self, tmp_path):
        """Test service accepts Path root_dir."""
        root_path = tmp_path / "custom_root"
        service = GraphRAGService(root_dir=root_path)

        assert service.root_dir == root_path
        assert isinstance(service.root_dir, Path)

    @pytest.mark.parametrize(
        "root_dir_suffix,expected_input_suffix,expected_output_suffix",
        [
            ("test_data", "test_data/input", "test_data/output"),
            ("graphrag_workspace", "graphrag_workspace/input", "graphrag_workspace/output"),
            ("my/nested/path", "my/nested/path/input", "my/nested/path/output"),
        ],
    )
    def test_init_directory_paths_parametrized(
        self, tmp_path, root_dir_suffix, expected_input_suffix, expected_output_suffix
    ):
        """Test directory paths are correctly derived from root_dir."""
        root = tmp_path / root_dir_suffix
        service = GraphRAGService(root_dir=root)

        assert str(service.input_dir).endswith(expected_input_suffix)
        assert str(service.output_dir).endswith(expected_output_suffix)

    def test_class_variables_set_correctly(self, temp_graphrag_root, mock_settings_yaml):
        """Test all class variables are properly initialized."""
        service = GraphRAGService(root_dir=temp_graphrag_root)

        # Check all expected attributes exist
        assert hasattr(service, "root_dir")
        assert hasattr(service, "input_dir")
        assert hasattr(service, "output_dir")
        assert hasattr(service, "update_output_dir")
        assert hasattr(service, "cache_dir")
        assert hasattr(service, "_config")

        # Config should be None initially (lazy loaded)
        assert service._config is None


# =============================================================================
# TestGraphRAGServiceConfig
# =============================================================================


class TestGraphRAGServiceConfig:
    """Tests for configuration loading and caching."""

    def test_load_config_from_settings_yaml(self, graphrag_service, mock_load_config):
        """Test _load_config loads from settings.yaml."""
        mock_func, mock_config = mock_load_config

        config = graphrag_service._load_config()

        mock_func.assert_called_once()
        assert config == mock_config

    def test_load_config_caching(self, graphrag_service, mock_load_config):
        """Test _load_config caches result and doesn't reload."""
        mock_func, mock_config = mock_load_config

        # First call
        config1 = graphrag_service._load_config()
        # Second call
        config2 = graphrag_service._load_config()

        # Should only be called once due to caching
        mock_func.assert_called_once()
        assert config1 is config2

    def test_load_config_missing_file(self, temp_graphrag_root):
        """Test _load_config raises FileNotFoundError when settings missing."""
        # Create service without settings.yaml
        (temp_graphrag_root / "settings.yaml").unlink(missing_ok=True)
        service = GraphRAGService(root_dir=temp_graphrag_root)

        with pytest.raises(FileNotFoundError, match="Settings file not found"):
            service._load_config()

    def test_config_interaction_with_graphrag_config(self, temp_graphrag_root, mock_settings_yaml):
        """Test that config is properly passed to load_config function."""
        service = GraphRAGService(root_dir=temp_graphrag_root)

        with patch("src.graphrag_service.load_config") as mock_load:
            mock_load.return_value = MagicMock()
            service._load_config()

            # Verify load_config was called with correct paths
            mock_load.assert_called_once()
            call_kwargs = mock_load.call_args[1]
            assert call_kwargs["root_dir"] == temp_graphrag_root
            assert call_kwargs["config_filepath"] == temp_graphrag_root / "settings.yaml"


# =============================================================================
# TestIndexingMethodResolution
# =============================================================================


class TestIndexingMethodResolution:
    """Tests for _get_indexing_method method."""

    @pytest.mark.parametrize(
        "method,is_update,expected",
        [
            ("standard", False, IndexingMethod.Standard),
            ("fast", False, IndexingMethod.Fast),
            ("standard", True, IndexingMethod.StandardUpdate),
            ("fast", True, IndexingMethod.FastUpdate),
        ],
    )
    def test_get_indexing_method(self, graphrag_service, method, is_update, expected):
        """Test indexing method resolution for all combinations."""
        result = graphrag_service._get_indexing_method(method, is_update=is_update)
        assert result == expected

    def test_get_indexing_method_standard(self, graphrag_service):
        """Test standard indexing method."""
        result = graphrag_service._get_indexing_method("standard")
        assert result == IndexingMethod.Standard

    def test_get_indexing_method_fast(self, graphrag_service):
        """Test fast indexing method."""
        result = graphrag_service._get_indexing_method("fast")
        assert result == IndexingMethod.Fast

    def test_get_indexing_method_standard_update(self, graphrag_service):
        """Test standard update indexing method."""
        result = graphrag_service._get_indexing_method("standard", is_update=True)
        assert result == IndexingMethod.StandardUpdate

    def test_get_indexing_method_fast_update(self, graphrag_service):
        """Test fast update indexing method."""
        result = graphrag_service._get_indexing_method("fast", is_update=True)
        assert result == IndexingMethod.FastUpdate

    def test_get_indexing_method_default_not_update(self, graphrag_service):
        """Test is_update defaults to False."""
        result = graphrag_service._get_indexing_method("standard")
        assert result == IndexingMethod.Standard


# =============================================================================
# TestInternalStatsMethods
# =============================================================================


class TestInternalStatsMethods:
    """Tests for internal stats and file listing methods."""

    def test_get_index_stats_from_output(self, graphrag_service, mock_parquet_output):
        """Test _get_index_stats reads from output directory."""
        stats = graphrag_service._get_index_stats(update=False)

        assert stats["entities"] == 10
        assert stats["nodes"] == 10
        assert stats["edges"] == 15
        assert stats["communities"] == 3

    def test_get_index_stats_from_update_output(self, graphrag_service, mock_update_parquet_output):
        """Test _get_index_stats reads from update_output directory."""
        stats = graphrag_service._get_index_stats(update=True)

        assert stats["entities"] == 5
        assert stats["nodes"] == 5
        assert stats["edges"] == 8
        assert stats["communities"] == 2

    def test_get_index_stats_missing_parquets(self, graphrag_service):
        """Test _get_index_stats returns zeros when parquet files missing."""
        stats = graphrag_service._get_index_stats(update=False)

        assert stats["entities"] == 0
        assert stats["nodes"] == 0
        assert stats["edges"] == 0
        assert stats["communities"] == 0

    def test_get_indexed_files(self, graphrag_service, sample_input_files):
        """Test _get_indexed_files returns list of input files."""
        files = graphrag_service._get_indexed_files()

        assert isinstance(files, list)
        assert len(files) == 3
        assert "doc1.txt" in files
        assert "doc2.txt" in files
        assert "doc3.txt" in files

    def test_get_indexed_files_empty_dir(self, graphrag_service):
        """Test _get_indexed_files returns empty list for empty input dir."""
        files = graphrag_service._get_indexed_files()

        assert isinstance(files, list)
        assert len(files) == 0

    def test_get_indexed_files_missing_dir(self, temp_graphrag_root, mock_settings_yaml):
        """Test _get_indexed_files handles missing input directory."""
        # Remove input directory
        import shutil

        shutil.rmtree(temp_graphrag_root / "input")

        service = GraphRAGService(root_dir=temp_graphrag_root)
        files = service._get_indexed_files()

        assert isinstance(files, list)
        assert len(files) == 0

    def test_get_updated_files_from_parquet(self, graphrag_service, mock_update_parquet_output):
        """Test _get_updated_files reads from documents parquet."""
        files = graphrag_service._get_updated_files()

        assert isinstance(files, list)
        assert len(files) == 2
        assert "doc1.txt" in files
        assert "doc2.txt" in files

    def test_get_updated_files_fallback(self, graphrag_service, sample_input_files):
        """Test _get_updated_files falls back to _get_indexed_files."""
        # No update parquet exists, should fall back to indexed files
        files = graphrag_service._get_updated_files()

        assert isinstance(files, list)
        assert len(files) == 3
        assert "doc1.txt" in files


# =============================================================================
# TestIndexDocuments
# =============================================================================


class TestIndexDocuments:
    """Tests for index_documents method."""

    def test_index_documents_standard(
        self,
        graphrag_service,
        mock_build_index,
        mock_load_config,
        mock_parquet_output,
        sample_input_files,
    ):
        """Test index_documents with standard method."""
        result = graphrag_service.index_documents(method="standard")

        assert result["status"] == "completed"
        assert "indexed_files" in result
        assert result["nodes"] == 10
        assert result["edges"] == 15
        assert result["communities"] == 3

    def test_index_documents_fast(
        self,
        graphrag_service,
        mock_build_index,
        mock_load_config,
        mock_parquet_output,
        sample_input_files,
    ):
        """Test index_documents with fast method."""
        result = graphrag_service.index_documents(method="fast")

        assert result["status"] == "completed"
        mock_build_index.assert_called_once()

    def test_index_documents_error_handling(
        self, graphrag_service, mock_build_index, mock_load_config
    ):
        """Test index_documents handles errors gracefully."""
        mock_build_index.side_effect = Exception("Test indexing error")

        result = graphrag_service.index_documents(method="standard")

        assert result["status"] == "failed"
        assert "error" in result
        assert "Indexing failed" in result["error"]
        assert result["nodes"] == 0
        assert result["edges"] == 0

    def test_index_documents_missing_settings(self, temp_graphrag_root):
        """Test index_documents handles missing settings.yaml."""
        # Remove settings.yaml
        (temp_graphrag_root / "settings.yaml").unlink(missing_ok=True)
        service = GraphRAGService(root_dir=temp_graphrag_root)

        result = service.index_documents(method="standard")

        assert result["status"] == "failed"
        assert "Settings file not found" in result["error"]

    @pytest.mark.parametrize("method", ["standard", "fast"])
    def test_index_all_methods(
        self,
        graphrag_service,
        mock_build_index,
        mock_load_config,
        mock_parquet_output,
        sample_input_files,
        method,
    ):
        """Test index_documents works with all indexing methods."""
        result = graphrag_service.index_documents(method=method)

        assert result["status"] == "completed"
        assert mock_build_index.called


# =============================================================================
# TestUpdateDocuments
# =============================================================================


class TestUpdateDocuments:
    """Tests for update_documents method."""

    def test_update_documents_standard(
        self,
        graphrag_service,
        mock_build_index,
        mock_load_config,
        mock_update_parquet_output,
        sample_input_files,
    ):
        """Test update_documents with standard method."""
        result = graphrag_service.update_documents(method="standard")

        assert result["status"] == "completed"
        assert "updated_files" in result
        assert result["nodes"] == 5
        assert result["edges"] == 8
        assert result["communities"] == 2

    def test_update_documents_fast(
        self,
        graphrag_service,
        mock_build_index,
        mock_load_config,
        mock_update_parquet_output,
        sample_input_files,
    ):
        """Test update_documents with fast method."""
        result = graphrag_service.update_documents(method="fast")

        assert result["status"] == "completed"
        mock_build_index.assert_called_once()

    def test_update_documents_error_handling(
        self, graphrag_service, mock_build_index, mock_load_config
    ):
        """Test update_documents handles errors gracefully."""
        mock_build_index.side_effect = Exception("Test update error")

        result = graphrag_service.update_documents(method="standard")

        assert result["status"] == "failed"
        assert "error" in result
        assert "Update failed" in result["error"]
        assert result["nodes"] == 0
        assert result["edges"] == 0

    def test_update_documents_missing_settings(self, temp_graphrag_root):
        """Test update_documents handles missing settings.yaml."""
        # Remove settings.yaml
        (temp_graphrag_root / "settings.yaml").unlink(missing_ok=True)
        service = GraphRAGService(root_dir=temp_graphrag_root)

        result = service.update_documents(method="standard")

        assert result["status"] == "failed"
        assert "Settings file not found" in result["error"]

    @pytest.mark.parametrize("method", ["standard", "fast"])
    def test_update_all_methods(
        self,
        graphrag_service,
        mock_build_index,
        mock_load_config,
        mock_update_parquet_output,
        sample_input_files,
        method,
    ):
        """Test update_documents works with all indexing methods."""
        result = graphrag_service.update_documents(method=method)

        assert result["status"] == "completed"
        assert mock_build_index.called

    def test_update_documents_calls_build_index_with_update_flag(
        self, graphrag_service, mock_build_index, mock_load_config, mock_update_parquet_output
    ):
        """Test update_documents passes is_update_run=True to build_index."""
        graphrag_service.update_documents(method="standard")

        mock_build_index.assert_called_once()
        call_kwargs = mock_build_index.call_args[1]
        assert call_kwargs["is_update_run"] is True


# =============================================================================
# TestQueryGraph
# =============================================================================


class TestQueryGraph:
    """Tests for query_graph method."""

    def test_query_graph_local(self, graphrag_service):
        """Test query_graph with local method."""
        result = graphrag_service.query_graph(question="What is the main theme?", method="local")

        assert "answer" in result
        assert "citations" in result
        assert result["method"] == "local"

    def test_query_graph_global(self, graphrag_service):
        """Test query_graph with global method."""
        result = graphrag_service.query_graph(question="What is the main theme?", method="global")

        assert "answer" in result
        assert "citations" in result
        assert result["method"] == "global"

    def test_query_graph_drift(self, graphrag_service):
        """Test query_graph with drift method."""
        result = graphrag_service.query_graph(question="What is the main theme?", method="drift")

        assert "answer" in result
        assert "citations" in result
        assert result["method"] == "drift"

    def test_query_graph_basic(self, graphrag_service):
        """Test query_graph with basic method."""
        result = graphrag_service.query_graph(question="What is the main theme?", method="basic")

        assert "answer" in result
        assert "citations" in result
        assert result["method"] == "basic"

    @pytest.mark.parametrize("method", ["local", "global", "drift", "basic"])
    def test_query_all_methods(self, graphrag_service, method):
        """Test query_graph works with all query methods."""
        result = graphrag_service.query_graph(question="Test question for GraphRAG", method=method)

        assert "answer" in result
        assert "citations" in result
        assert result["method"] == method

    def test_query_graph_returns_citations_list(self, graphrag_service):
        """Test query_graph returns citations as a list."""
        result = graphrag_service.query_graph(question="What is the main theme?", method="local")

        assert isinstance(result["citations"], list)


# =============================================================================
# TestExportGraph
# =============================================================================


class TestExportGraph:
    """Tests for export_graph method."""

    def test_export_graph_placeholder(self, graphrag_service, tmp_path):
        """Test export_graph returns not_implemented status."""
        output_path = tmp_path / "export.parquet"
        result = graphrag_service.export_graph(output_path=output_path)

        assert result["status"] == "not_implemented"
        assert result["output_path"] == str(output_path)

    def test_export_graph_accepts_string_path(self, graphrag_service, tmp_path):
        """Test export_graph accepts string path."""
        output_path = str(tmp_path / "export.parquet")
        result = graphrag_service.export_graph(output_path=output_path)

        assert result["output_path"] == output_path

    def test_export_graph_accepts_path_object(self, graphrag_service, tmp_path):
        """Test export_graph accepts Path object."""
        output_path = tmp_path / "export.parquet"
        result = graphrag_service.export_graph(output_path=output_path)

        assert result["output_path"] == str(output_path)
