# vector_store.py
# Handles turning text chunks into embeddings and storing/searching them in ChromaDB.

import chromadb
from sentence_transformers import SentenceTransformer

# Load the embedding model once when this file is imported.
# "all-MiniLM-L6-v2" is small, fast, and good enough for a student project.
# (This downloads the model the first time you run it — a few hundred MB.)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create a persistent ChromaDB client — "persistent" means data survives
# even after we restart the server (stored in the chroma_db/ folder).
chroma_client = chromadb.PersistentClient(path="chroma_db")

# Get (or create, if it doesn't exist yet) a "collection" — think of this
# like a table in a normal database, specifically for our medical document chunks.
collection = chroma_client.get_or_create_collection(name="medical_documents")


def embed_and_store_chunks(chunks: list[str], filename: str) -> int:
    """
    Takes a list of text chunks from one PDF, generates embeddings for
    each one, and stores them in ChromaDB along with metadata.
    Returns how many chunks were stored.
    """
    if not chunks:
        return 0

    # Generate embeddings for all chunks at once (more efficient than one-by-one)
    embeddings = embedding_model.encode(chunks).tolist()

    # ChromaDB needs a unique string ID for every chunk we store
    ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]

    # Metadata lets us remember which document and page a chunk came from
    metadatas = [
        {"source_document": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]

    # Store everything in the collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,      # the original text, so we can display it later
        metadatas=metadatas,
    )

    return len(chunks)


def get_collection_count() -> int:
    """Returns how many chunks are currently stored — useful for debugging."""
    return collection.count()