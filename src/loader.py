import json
import datetime
import pandas as pd
from pathlib import Path
from typing import list, dict

# Library imports for specific file types
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

from .chunker import TextChunker, Chunk

class DocumentLoader:
    def __init__(self, chunker: TextChunker = None):
        self.chunker = chunker or TextChunker()
        # Only advertise support for libraries that are actually installed
        self.supported_formats = {'.txt', '.csv', '.json'}
        if PdfReader: self.supported_formats.add('.pdf')
        if DocxDocument: self.supported_formats.add('.docx')

    def load_directory(self, directory: str) -> list[Chunk]:
        """Scans directory recursively and loads all supported files."""
        path = Path(directory)
        if not path.exists():
            print(f"Directory not found: {directory}")
            return []

        all_chunks = []
        for file_path in path.rglob('*'):
            if file_path.suffix.lower() in self.supported_formats:
                print(f"Loading: {file_path.name}")
                try:
                    file_chunks = self.load_file(str(file_path))
                    all_chunks.extend(file_chunks)
                except Exception as e:
                    print(f"Failed to load {file_path.name}: {e}")
        return all_chunks

    def load_file(self, file_path: str) -> list[Chunk]:
        """Dispatches loading based on file extension."""
        path = Path(file_path)
        doc_id = path.stem

        # Base metadata for every chunk from this file
        metadata = {
            "source": path.name,
            "file_path": str(path),
            "date_added": datetime.datetime.now().isoformat(),
            "file_type": path.suffix.lower()
        }

        ext = path.suffix.lower()

        if ext == '.txt':
            return self._load_txt(file_path, doc_id, metadata)
        elif ext == '.pdf':
            return self._load_pdf(file_path, doc_id, metadata)
        elif ext == '.docx':
            return self._load_docx(file_path, doc_id, metadata)
        elif ext == '.csv':
            return self._load_csv(file_path, doc_id, metadata)
        elif ext == '.json':
            return self._load_json(file_path, doc_id, metadata)
        else:
            print(f"Unsupported file type: {ext}")
            return []

    def _apply_metadata(self, chunks: list[Chunk], metadata: dict) -> list[Chunk]:
        """Merges file-level metadata with chunk-level metadata."""
        for chunk in chunks:
            combined = metadata.copy()
            combined.update(chunk.metadata) # Keep chunk-specific meta (like strategy)
            chunk.metadata = combined
        return chunks

    # --- Unstructured Text Handlers (Use Sentence Chunking) ---

    def _load_txt(self, file_path: str, doc_id: str, metadata: dict) -> list[Chunk]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        return self._apply_metadata(self.chunker.chunk_by_sentences(text, doc_id), metadata)

    def _load_pdf(self, file_path: str, doc_id: str, metadata: dict) -> list[Chunk]:
        if not PdfReader:
            raise ImportError("pypdf not installed. Run `pip install pypdf`")

        reader = PdfReader(file_path)
        text_parts = []

        # pypdf API is identical here:
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)

        full_text = "\n\n".join(text_parts)
        return self._apply_metadata(self.chunker.chunk_by_sentences(full_text, doc_id), metadata)

    def _load_docx(self, file_path: str, doc_id: str, metadata: dict) -> list[Chunk]:
        if not DocxDocument:
            raise ImportError("python-docx not installed. Run `pip install python-docx`")

        doc = DocxDocument(file_path)
        # Join paragraphs with double newline to preserve paragraph structure clearly
        full_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return self._apply_metadata(self.chunker.chunk_by_sentences(full_text, doc_id), metadata)

    # --- Structured Data Handlers (Use Group Chunking) ---

    def _load_csv(self, file_path: str, doc_id: str, metadata: dict) -> list[Chunk]:
        # Use pandas to load, then convert rows to readable strings
        df = pd.read_csv(file_path)

        # Convert row to string: "Column1: Value1, Column2: Value2"
        # This keeps the data semantically linked per row.
        row_strings = []
        for _, row in df.iterrows():
            # Filter out nulls to keep text clean
            row_items = [f"{col}: {val}" for col, val in row.items() if pd.notnull(val)]
            row_strings.append(", ".join(row_items))

        # Use the 'group_strings' method we added to Chunker
        return self.chunker.chunk_group_strings(row_strings, doc_id, metadata)

    def _load_json(self, file_path: str, doc_id: str, metadata: dict) -> list[Chunk]:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        # If it's a list of records, treat them as rows
        if isinstance(data, list):
            json_strings = [json.dumps(item, ensure_ascii=False) for item in data]
            return self.chunker.chunk_group_strings(json_strings, doc_id, metadata)

        # If it's a single dict, dump it and treat as text
        elif isinstance(data, dict):
            text = json.dumps(data, indent=2, ensure_ascii=False)
            return self._apply_metadata(self.chunker.chunk_by_sentences(text, doc_id), metadata)

        return []

    def save_chunks(self, chunks: list[Chunk], output_path: str):
        data = [{'text': c.text, 'doc_id': c.doc_id, 'metadata': c.metadata} for c in chunks]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
