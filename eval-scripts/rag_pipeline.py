# Creating RAG pipleline to embed source into model vs using a system prompt like context stuffing - will compare results

import pathlib
import pickle
import faiss

import numpy as np
from functools import cache
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000  # number of characters per chunk, adjust based on your needs and model context window
CHUNK_OVERLAP = 200  # number of characters to overlap between chunks, helps maintain context across chunks
TOP_K = 5  # number of similar chunks to retrieve for a given query
INDEX_DIR = pathlib.Path("data/faiss_index")


# Caching the embedder and index/chunks to avoid reloading on every retrieval (cheaper to keep in memory than reloading from disk)
@cache
def _get_embedder() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@cache
def _get_index_chunks() -> tuple:
    index = faiss.read_index(str(INDEX_DIR / "index.faiss"))
    with open(INDEX_DIR / "chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    return index, chunks


# Splitting the document into chunks that are small enough for the model to process, while trying to maintain context.
def chunk_doc(text: str) -> list[str]:
    # Split markdown into sections based on headers
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "H1"),
            ("##", "H2"),
            ("###", "H3"),
            ("####", "H4"),
            ("#####", "H5"),
            ("######", "H6"),
        ],
        strip_headers=False,  # keep headers in the chunks to preserve context
    )
    header_docs = header_splitter.split_text(text)

    # Further split sections into smaller chunks with overlap
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    finished_docs = char_splitter.split_documents(header_docs)

    return [doc.page_content for doc in finished_docs]


# Building FAISS index for retrieval-augmented generation (RAG) pipeline. This will embed the document chunks and save the index and chunks to disk for later retrieval.
def build_faiss_index():
    print("Loading doc...")
    text = pathlib.Path("data/D&D_5e_OGL_1.md").read_text(encoding="utf-8")

    print("Chunking doc...")
    chunks = chunk_doc(text)
    print(f"Number of chunks: {len(chunks)}")

    print("Embedding chunks...")
    embedder = _get_embedder()
    embeddings = embedder.encode(chunks, show_progress_bar=True, batch_size=64)
    embeddings = np.array(embeddings, dtype="float32")

    faiss.normalize_L2(embeddings)  # normalize embeddings for cosine similarity search

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))
    with open(INDEX_DIR / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    print(f"FAISS index built and saved to {INDEX_DIR}.")


# Retrieving relevant chunks from the FAISS index based on a query.
def retrieve(query: str, top_k: int = TOP_K) -> list[str]:
    embedder = _get_embedder()
    index, chunks = _get_index_chunks()

    query_vector = np.array(embedder.encode([query]), dtype="float32")
    faiss.normalize_L2(query_vector)

    _, indices = index.search(query_vector, top_k)

    return [chunks[i] for i in indices[0] if i != -1]  # filter out any invalid indices


# Tests to verify that the retrieval runs as expected from this file.
if __name__ == "__main__":
    build_faiss_index()
    results = retrieve("What are the rules for spellcasting?")
    for i, chunk in enumerate(results, 1):
        print(f"\n--- Chunk {i} ---\n{chunk}")
