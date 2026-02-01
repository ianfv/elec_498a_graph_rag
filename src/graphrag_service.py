"""
GraphRAG service module for document indexing, updating, and querying.

This module provides synchronous wrappers around the GraphRAG library for:
- Document indexing (full pipeline including graph building)
- Incremental document updates
- Query execution with multiple search methods
"""

import asyncio

import nest_asyncio

# Allow nested event loops (needed when called from FastAPI/uvicorn)
nest_asyncio.apply()
from pathlib import Path
from typing import Any

import pandas as pd
from graphrag.api.index import build_index
from graphrag.api.query import global_search, local_search
from graphrag.config.enums import IndexingMethod
from graphrag.config.load_config import load_config
from graphrag.config.models.graph_rag_config import GraphRagConfig


class GraphRAGService:
    """Service for managing GraphRAG operations."""

    def __init__(self, root_dir: str | Path = "./test_data"):
        """
        Initialize GraphRAG service.

        Args:
            root_dir: Root directory for GraphRAG workspace
        """
        self.root_dir = Path(root_dir)
        self.input_dir = self.root_dir / "input"
        self.output_dir = self.root_dir / "output"
        self.update_output_dir = self.root_dir / "update_output"
        self.cache_dir = self.root_dir / "cache"
        self._config: GraphRagConfig | None = None

    def _load_config(self) -> GraphRagConfig:
        """
        Load GraphRAG configuration from settings.yaml.

        Returns:
            GraphRagConfig instance

        Raises:
            FileNotFoundError: If settings.yaml does not exist
        """
        if self._config is None:
            settings_path = self.root_dir / "settings.yaml"
            if not settings_path.exists():
                raise FileNotFoundError(f"Settings file not found: {settings_path}")
            self._config = load_config(root_dir=self.root_dir, config_filepath=settings_path)
        return self._config

    def _get_indexing_method(self, method: str, is_update: bool = False) -> IndexingMethod:
        """
        Convert method string to IndexingMethod enum.

        Args:
            method: Method name ('standard' or 'fast')
            is_update: Whether this is an update operation

        Returns:
            Appropriate IndexingMethod enum value
        """
        if is_update:
            return (
                IndexingMethod.StandardUpdate if method == "standard" else IndexingMethod.FastUpdate
            )
        return IndexingMethod.Standard if method == "standard" else IndexingMethod.Fast

    def _get_index_stats(self, update: bool = False) -> dict[str, int]:
        """
        Parse parquet output files to get indexing statistics.

        Args:
            update: Whether to read from update_output directory

        Returns:
            Dictionary with entity, node, edge, and community counts
        """
        output_dir = self.update_output_dir if update else self.output_dir
        stats = {"entities": 0, "nodes": 0, "edges": 0, "communities": 0}

        entities_file = output_dir / "create_final_entities.parquet"
        if entities_file.exists():
            df = pd.read_parquet(entities_file)
            stats["entities"] = len(df)
            stats["nodes"] = len(df)

        relationships_file = output_dir / "create_final_relationships.parquet"
        if relationships_file.exists():
            df = pd.read_parquet(relationships_file)
            stats["edges"] = len(df)

        communities_file = output_dir / "create_final_communities.parquet"
        if communities_file.exists():
            df = pd.read_parquet(communities_file)
            stats["communities"] = len(df)

        return stats

    def _get_indexed_files(self) -> list[str]:
        """
        Get list of indexed document files.

        Returns:
            List of filenames in the input directory
        """
        if not self.input_dir.exists():
            return []
        return [f.name for f in self.input_dir.iterdir() if f.is_file()]

    def _get_updated_files(self) -> list[str]:
        """
        Get list of files processed in the last update.

        Returns:
            List of updated filenames (reads from update output if available)
        """
        documents_file = self.update_output_dir / "create_final_documents.parquet"
        if documents_file.exists():
            df = pd.read_parquet(documents_file)
            if "title" in df.columns:
                return df["title"].tolist()
        return self._get_indexed_files()

    def index_documents(self, method: str = "standard") -> dict[str, Any]:
        """
        Index documents through GraphRAG pipeline.

        Runs the complete indexing pipeline including:
        - Document chunking into text units
        - Entity and relationship extraction
        - Community detection
        - Embedding generation

        Args:
            method: Indexing method ('standard' or 'fast')

        Returns:
            Dictionary with indexing results:
            {
                "status": "completed" | "failed",
                "indexed_files": [list of indexed filenames],
                "entities_extracted": int,
                "nodes": int,
                "edges": int,
                "communities": int,
                "error": str (if failed)
            }
        """
        try:
            config = self._load_config()
            indexing_method = self._get_indexing_method(method, is_update=False)

            # Run async build_index in sync context
            asyncio.run(
                build_index(
                    config=config,
                    method=indexing_method,
                    is_update_run=False,
                    verbose=True,
                )
            )

            # Parse results from parquet files
            stats = self._get_index_stats(update=False)
            indexed_files = self._get_indexed_files()

            return {
                "status": "completed",
                "indexed_files": indexed_files,
                "entities_extracted": stats["entities"],
                "nodes": stats["nodes"],
                "edges": stats["edges"],
                "communities": stats["communities"],
            }

        except FileNotFoundError as e:
            return {
                "status": "failed",
                "indexed_files": [],
                "entities_extracted": 0,
                "nodes": 0,
                "edges": 0,
                "communities": 0,
                "error": str(e),
            }
        except Exception as e:
            return {
                "status": "failed",
                "indexed_files": [],
                "entities_extracted": 0,
                "nodes": 0,
                "edges": 0,
                "communities": 0,
                "error": f"Indexing failed: {e!s}",
            }

    def update_documents(self, method: str = "standard") -> dict[str, Any]:
        """
        Update documents through GraphRAG incremental pipeline.

        Processes only new or changed documents, leveraging cached results
        for unchanged content. Communities are recomputed to include new entities.

        Args:
            method: Indexing method ('standard' or 'fast')

        Returns:
            Dictionary with update results:
            {
                "status": "completed" | "failed",
                "updated_files": [list of updated filenames],
                "entities_extracted": int,
                "nodes": int,
                "edges": int,
                "communities": int,
                "error": str (if failed)
            }
        """
        try:
            config = self._load_config()
            indexing_method = self._get_indexing_method(method, is_update=True)

            # Run async build_index in sync context with update mode
            asyncio.run(
                build_index(
                    config=config,
                    method=indexing_method,
                    is_update_run=True,
                    verbose=True,
                )
            )

            # Parse results from update output directory
            stats = self._get_index_stats(update=True)
            updated_files = self._get_updated_files()

            return {
                "status": "completed",
                "updated_files": updated_files,
                "entities_extracted": stats["entities"],
                "nodes": stats["nodes"],
                "edges": stats["edges"],
                "communities": stats["communities"],
            }

        except FileNotFoundError as e:
            return {
                "status": "failed",
                "updated_files": [],
                "entities_extracted": 0,
                "nodes": 0,
                "edges": 0,
                "communities": 0,
                "error": str(e),
            }
        except Exception as e:
            return {
                "status": "failed",
                "updated_files": [],
                "entities_extracted": 0,
                "nodes": 0,
                "edges": 0,
                "communities": 0,
                "error": f"Update failed: {e!s}",
            }

    def query_graph(self, question: str, method: str = "local") -> dict[str, Any]:
        """
        Query the knowledge graph.

        Executes synchronous query against the knowledge graph using local or global search.

        Args:
            question: User question to answer
            method: Search method ('local' or 'global')
                - local: Entity-focused search for specific questions
                - global: Community-based search for thematic/holistic questions

        Returns:
            Dictionary with query results:
            {
                "answer": str,
                "citations": [list of source citations],
                "method": str,
                "context_data": dict (optional)
            }
        """
        try:
            config = self._load_config()

            if method == "local":
                result = asyncio.run(self._query_local(question, config))
            elif method == "global":
                result = asyncio.run(self._query_global(question, config))
            else:
                return {
                    "answer": f"Unknown search method: {method}. Use 'local' or 'global'.",
                    "citations": [],
                    "method": method,
                }

            return result

        except FileNotFoundError as e:
            return {
                "answer": f"Configuration error: {e}",
                "citations": [],
                "method": method,
            }
        except Exception as e:
            return {
                "answer": f"Query failed: {e!s}",
                "citations": [],
                "method": method,
            }

    async def _query_local(self, question: str, config: GraphRagConfig) -> dict[str, Any]:
        """
        Execute local search query.

        Local search combines knowledge graph data with text chunks for
        entity-focused questions.

        Args:
            question: User question
            config: GraphRAG configuration

        Returns:
            Query result dictionary
        """
        # Load indexed data from parquet files
        output_dir = self.root_dir / "output"
        
        entities = pd.read_parquet(output_dir / "entities.parquet")
        communities = pd.read_parquet(output_dir / "communities.parquet")
        community_reports = pd.read_parquet(output_dir / "community_reports.parquet")
        text_units = pd.read_parquet(output_dir / "text_units.parquet")
        relationships = pd.read_parquet(output_dir / "relationships.parquet")
        
        # Covariates may not exist
        covariates_path = output_dir / "covariates.parquet"
        covariates = pd.read_parquet(covariates_path) if covariates_path.exists() else None

        result = await local_search(
            config=config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            text_units=text_units,
            relationships=relationships,
            covariates=covariates,
            community_level=2,
            response_type="multiple paragraphs",
            query=question,
        )

        # Result is a tuple (response, context_data)
        response, context_data = result

        return {
            "answer": response if isinstance(response, str) else str(response),
            "citations": [],  # TODO: Implement citation extraction
            "method": "local",
            "context_data": context_data,
        }

    async def _query_global(self, question: str, config: GraphRagConfig) -> dict[str, Any]:
        """
        Execute global search query.

        Global search uses community reports for holistic/thematic questions
        across the entire dataset.

        Args:
            question: User question
            config: GraphRAG configuration

        Returns:
            Query result dictionary
        """
        # Load indexed data from parquet files
        output_dir = self.root_dir / "output"
        
        entities = pd.read_parquet(output_dir / "entities.parquet")
        communities = pd.read_parquet(output_dir / "communities.parquet")
        community_reports = pd.read_parquet(output_dir / "community_reports.parquet")

        result = await global_search(
            config=config,
            entities=entities,
            communities=communities,
            community_reports=community_reports,
            community_level=2,
            response_type="multiple paragraphs",
            query=question,
        )

        # Result is a tuple (response, context_data)
        response, context_data = result

        return {
            "answer": response if isinstance(response, str) else str(response),
            "citations": [],  # TODO: Implement citation extraction
            "method": "global",
            "context_data": context_data,
        }

    # TODO: Implement _extract_citations method when ready

    def export_graph(self, output_path: str | Path) -> dict[str, Any]:
        """
        Export knowledge graph to parquet format.

        Args:
            output_path: Path to save parquet file

        Returns:
            Dictionary with export results
        """
        # TODO: Implement graph export
        # 1. Query output directory for all parquet files
        # 2. Bundle into single archive or copy to output_path
        # 3. Return structured response

        return {
            "status": "not_implemented",
            "output_path": str(output_path),
        }
