import tiktoken
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Global cache to prevent reloading the tokenizer model (heavy operation)
# on every instantiation of TextChunker.
_ENCODING_CACHE = {}

def get_encoding_cached(encoding_name: str):
    if encoding_name not in _ENCODING_CACHE:
        _ENCODING_CACHE[encoding_name] = tiktoken.get_encoding(encoding_name)
    return _ENCODING_CACHE[encoding_name]

@dataclass
class Chunk:
    text: str
    doc_id: str
    chunk_id: int
    start_idx: int # Start token index relative to original doc
    end_idx: int   # End token index relative to original doc
    token_count: int
    # Use field(default_factory...) to avoid dangerous mutable default arguments
    metadata: Dict = field(default_factory=dict)

class TextChunker:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 100, encoding_name: str = "cl100k_base"):
        # Validation: Infinite loop prevention
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = get_encoding_cached(encoding_name)

    def chunk_by_sentences(self, text: str, doc_id: str) -> List[Chunk]:
        """
        Recommended for GraphRAG: Respects sentence boundaries.
        Accumulates sentences until the chunk limit is reached.
        """
        # 1. Split by sentence delimiters (keep delimiter with the sentence)
        # This regex looks for punctuation (.!?) followed by whitespace
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        chunk_id = 0

        # Buffers for the current chunk
        current_tokens = []
        current_text_parts = []

        # Track position in original token stream
        # Note: This is an approximation since we are re-joining sentences
        current_start_idx = 0

        for sentence in sentences:
            if not sentence.strip():
                continue

            sent_tokens = self.encoding.encode(sentence)
            sent_len = len(sent_tokens)

            # 2. Check if adding this sentence would exceed the chunk size
            if len(current_tokens) + sent_len > self.chunk_size:
                # A. Emit the current chunk
                if current_tokens:
                    chunk_text = "".join(current_text_parts) # Join sentences accurately

                    chunks.append(Chunk(
                        text=chunk_text.strip(),
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        start_idx=current_start_idx,
                        end_idx=current_start_idx + len(current_tokens),
                        token_count=len(current_tokens),
                        metadata={"strategy": "sentence_aware"}
                    ))
                    chunk_id += 1

                # B. Handle Overlap
                # We need to keep the last N tokens for the next chunk.
                # Since we operate on whole sentences, we can't just slice tokens arbitrarily
                # without breaking the "sentence aware" promise.
                # Strategy: Keep as many full sentences as fit in the overlap window.

                overlap_buffer_tokens = []
                overlap_buffer_text = []

                # Walk backwards through current parts to find overlap candidates
                current_overlap_size = 0
                for i in range(len(current_text_parts) - 1, -1, -1):
                    part_tokens = self.encoding.encode(current_text_parts[i])
                    if current_overlap_size + len(part_tokens) > self.chunk_overlap:
                        break
                    overlap_buffer_tokens.insert(0, part_tokens) # Prepend
                    overlap_buffer_text.insert(0, current_text_parts[i]) # Prepend
                    current_overlap_size += len(part_tokens)

                # Reset buffers with overlap content
                current_tokens = [t for sent in overlap_buffer_tokens for t in sent] # Flatten
                current_text_parts = overlap_buffer_text

                # Update start index for the next chunk (approximate based on what we kept)
                # New start = Old end - overlap
                current_start_idx += (len(chunks[-1].text) if chunks else 0) # Logic simplified for stream
                # A robust implementation for exact indices often requires re-tokenizing the whole doc maps
                # or strict tracking. For RAG, relative flow is usually sufficient.

            # 3. Add current sentence to buffer
            current_tokens.extend(sent_tokens)
            current_text_parts.append(sentence + " ") # Add space back for joining

        # 4. Final chunk
        if current_tokens:
            chunk_text = "".join(current_text_parts)
            chunks.append(Chunk(
                text=chunk_text.strip(),
                doc_id=doc_id,
                chunk_id=chunk_id,
                start_idx=current_start_idx,
                end_idx=current_start_idx + len(current_tokens),
                token_count=len(current_tokens),
                metadata={"strategy": "sentence_aware"}
            ))

        return chunks


    def chunk_group_strings(self, text_parts: List[str], doc_id: str, metadata: Dict) -> List[Chunk]:
        """
        Groups a list of distinct strings (like CSV rows or JSON objects) into chunks.
        Tries not to split individual strings unless they exceed chunk_size.
        """
        chunks = []
        chunk_id = 0
        current_tokens = []
        current_text_parts = []
        current_start_idx = 0 # Approx tracker

        for part in text_parts:
            part_str = str(part)
            if not part_str.strip():
                continue

            part_tokens = self.encoding.encode(part_str)
            part_len = len(part_tokens)

            # If a single row is massive, we MUST split it (fallback to token chunking for just this row)
            if part_len > self.chunk_size:
                # 1. Flush current buffer if any
                if current_tokens:
                    chunks.append(Chunk(
                        text="\n".join(current_text_parts),
                        doc_id=doc_id,
                        chunk_id=chunk_id,
                        start_idx=current_start_idx,
                        end_idx=current_start_idx + len(current_tokens),
                        token_count=len(current_tokens),
                        metadata=metadata.copy()
                    ))
                    chunk_id += 1
                    current_tokens = []
                    current_text_parts = []

                # 2. Chunk this huge row using standard token slicing
                sub_chunks = self.chunk_by_tokens(part_str, doc_id)
                for sub in sub_chunks:
                    sub.chunk_id = chunk_id # Re-assign ID
                    sub.metadata = metadata.copy()
                    chunks.append(sub)
                    chunk_id += 1
                continue

            # Check fit
            if len(current_tokens) + part_len > self.chunk_size:
                chunks.append(Chunk(
                    text="\n".join(current_text_parts),
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    start_idx=current_start_idx,
                    end_idx=current_start_idx + len(current_tokens),
                    token_count=len(current_tokens),
                    metadata=metadata.copy()
                ))
                chunk_id += 1
                current_tokens = []
                current_text_parts = []

            current_tokens.extend(part_tokens)
            current_text_parts.append(part_str)

        # Final flush
        if current_tokens:
            chunks.append(Chunk(
                text="\n".join(current_text_parts),
                doc_id=doc_id,
                chunk_id=chunk_id,
                start_idx=current_start_idx,
                end_idx=current_start_idx + len(current_tokens),
                token_count=len(current_tokens),
                metadata=metadata.copy()
            ))

        return chunks


    def chunk_by_tokens(self, text: str, doc_id: str) -> List[Chunk]:
        """
        Fast / Strict sliding window.
        Fixed to remove Unicode replacement characters from mid-token splits.
        """
        tokens = self.encoding.encode(text)
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))

            # Decode the slice
            chunk_text = self.encoding.decode(tokens[start:end])

            # FIX: Strip replacement characters () caused by splitting multi-byte tokens
            # This is critical for non-English text or emojis
            chunk_text = chunk_text.strip("")

            if chunk_text.strip():
                chunks.append(Chunk(
                    text=chunk_text,
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    start_idx=start,
                    end_idx=end,
                    token_count=end - start,
                    metadata={"strategy": "token_window"}
                ))
                chunk_id += 1

            start += self.chunk_size - self.chunk_overlap

        return chunks
