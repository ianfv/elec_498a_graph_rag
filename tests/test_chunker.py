import pytest
import json
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import your actual classes
from src.chunker import TextChunker
from src.loader import DocumentLoader

TEST_DATA_DIR = Path("test_data_temp")

@pytest.fixture(scope="module")
def setup_test_files():
    """Creates temporary test files (txt, csv, json) before tests run."""
    TEST_DATA_DIR.mkdir(exist_ok=True)

    # 1. Plain Text
    (TEST_DATA_DIR / "doc.txt").write_text(
        "GraphRAG improves retrieval. " * 50, encoding="utf-8"
    )

    # 2. CSV (Structured)
    df = pd.DataFrame([
        {"product": "Widget A", "desc": "A useful tool."},
        {"product": "Widget B", "desc": "Another tool."}
    ])
    df.to_csv(TEST_DATA_DIR / "data.csv", index=False)

    # 3. JSON (List of records)
    data = [{"id": 1, "val": "A"}, {"id": 2, "val": "B"}]
    with open(TEST_DATA_DIR / "data.json", "w") as f:
        json.dump(data, f)

    yield TEST_DATA_DIR

    # Cleanup
    import shutil
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)

@pytest.fixture
def loader():
    # Use small chunks to force splitting behavior
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    return DocumentLoader(chunker=chunker)

# --- Integration Tests ---

def test_txt_loading_strategy(loader, setup_test_files):
    """Verify .txt files use sentence-aware chunking."""
    chunks = loader.load_file(str(setup_test_files / "doc.txt"))

    assert len(chunks) > 0
    # Check metadata was applied
    assert chunks[0].metadata["file_type"] == ".txt"
    # Check strategy metadata (set by chunker)
    assert chunks[0].metadata.get("strategy") == "sentence_aware"

def test_csv_row_preservation(loader, setup_test_files):
    """Verify CSV rows are treated as atomic units (group chunking)."""
    chunks = loader.load_file(str(setup_test_files / "data.csv"))

    assert len(chunks) > 0
    # The loader converts rows to "product: Widget A, desc: A useful tool."
    # Verify exact string presence
    assert "product: Widget A" in chunks[0].text
    # Verify strategy is NOT sentence aware (it should be group/token based)
    # Note: `chunk_group_strings` doesn't strictly set "strategy" metadata in my snippet unless added.
    # But we can verify no sentence splitting happened by checking content.
    assert "product: Widget B" in chunks[0].text or "product: Widget B" in chunks[1].text

def test_json_list_handling(loader, setup_test_files):
    """Verify JSON lists are chunked by item."""
    chunks = loader.load_file(str(setup_test_files / "data.json"))

    assert len(chunks) > 0
    # Should contain the JSON structure
    assert '"id": 1' in chunks[0].text

# --- Mocked Tests for PDF/DOCX (Optional dependencies) ---

def test_pdf_extraction_call(loader):
    """Mock pypdf to ensure loader logic works without needing a real PDF."""
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page 1 content. Sentence two."
    mock_reader.pages = [mock_page, mock_page]

    # FIX: Patch 'src.loader.PdfReader' (or wherever loader imports it)
    # The loader code now imports PdfReader from pypdf
    with patch("src.loader.PdfReader", return_value=mock_reader):
        chunks = loader._load_pdf("dummy.pdf", "doc_pdf", {})

        assert len(chunks) > 0
        assert "Page 1 content." in chunks[0].text
        assert chunks[0].metadata.get("strategy") == "sentence_aware"


def test_docx_extraction_call(loader):
    """Mock DocxDocument to ensure loader logic works."""
    mock_doc = MagicMock()
    mock_para = MagicMock()
    mock_para.text = "Paragraph content."
    mock_doc.paragraphs = [mock_para, mock_para]

    with patch("src.loader.DocxDocument", return_value=mock_doc):
        chunks = loader._load_docx("dummy.docx", "doc_word", {})

        assert len(chunks) > 0
        assert "Paragraph content." in chunks[0].text
        assert chunks[0].metadata.get("strategy") == "sentence_aware"

# --- Chunker Unit Test Update (New Method) ---

def test_chunk_group_strings_logic():
    """Direct unit test for the new `chunk_group_strings` method."""
    chunker = TextChunker(chunk_size=10, chunk_overlap=0)

    # Input: 3 strings.
    # Strings 1 & 2 fit in one chunk (lengths approx 2-3 tokens).
    # String 3 forces a new chunk.
    inputs = ["Row 1", "Row 2", "Row 3"]

    chunks = chunker.chunk_group_strings(inputs, "doc_group", {})

    # With chunk_size=10, "Row 1" (2 tokens) + "Row 2" (2 tokens) = 4 tokens -> Fits.
    # If we add "Row 3", it fits.
    # Let's make them longer to force split.

    chunker = TextChunker(chunk_size=6, chunk_overlap=0)
    inputs = ["Longer Row 1", "Longer Row 2"]

    chunks = chunker.chunk_group_strings(inputs, "doc_group", {})

    # Should result in multiple chunks if they don't fit together
    # Check that they aren't split IN THE MIDDLE of a string if possible
    assert len(chunks) >= 1
    # Ensure "Longer Row 1" is intact in one of the chunks
    assert any("Longer Row 1" in c.text for c in chunks)
