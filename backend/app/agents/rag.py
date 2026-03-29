import io
import numpy as np
import faiss
import PyPDF2
import google.generativeai as genai
from typing import Optional

EMBED_MODEL = "models/text-embedding-004"
CHUNK_SIZE  = 700
OVERLAP     = 100


def extract_pdf_text(pdf_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text.strip()


def chunk_text(text: str) -> list:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE].strip())
        start += CHUNK_SIZE - OVERLAP
    return [c for c in chunks if len(c) > 50]


def embed_texts(texts: list) -> np.ndarray:
    embeddings = []
    for text in texts:
        result = genai.embed_content(
            model=EMBED_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        embeddings.append(result["embedding"])
    return np.array(embeddings, dtype="float32")


class FAISSVectorStore:
    def __init__(self):
        self.index  = None
        self.chunks = []

    def build(self, chunks: list):
        embeddings   = embed_texts(chunks)
        dim          = embeddings.shape[1]
        self.index   = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.chunks  = chunks

    def search(self, query: str, top_k: int = 4) -> list:
        if self.index is None or not self.chunks:
            return []
        q_emb = embed_texts([query])
        _, indices = self.index.search(q_emb, top_k)
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]


def build_vector_store(pdf_bytes: Optional[bytes]):
    """Returns (store, rag_available). store=None if no PDF provided."""
    if not pdf_bytes:
        return None, False
    try:
        text   = extract_pdf_text(pdf_bytes)
        chunks = chunk_text(text)
        store  = FAISSVectorStore()
        store.build(chunks)
        return store, True
    except Exception:
        return None, False
