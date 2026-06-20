"""
retriever.py
Embeds document chunks and stores them in ChromaDB. Provides a query()
function for semantic retrieval.

Spec (from planning.md):
- Embedding model: all-MiniLM-L6-v2 via sentence-transformers (local, no API key)
- Vector store: ChromaDB
- top-k: 5
"""

print("Starting retriever.py...")
import chromadb

print("chromadb imported.")
from chromadb.utils import embedding_functions

print("embedding_functions imported.")

from ingest import run_pipeline

print("ingest imported.")

COLLECTION_NAME = "unofficial_columbia_guide"
TOP_K = 5
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB's built-in embedding function wraps sentence-transformers for us --
# same model as before (all-MiniLM-L6-v2), but ChromaDB calls it internally
# whenever we add() or query(), so we don't have to call .encode() ourselves.
print(f"Loading embedding model {EMBEDDING_MODEL} (may download on first run)...")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
print("Embedding model loaded.")

# Persistent ChromaDB client -- writes to ./chroma_db on disk so we don't
# have to re-embed every time we run the app.
client = chromadb.PersistentClient(path="./chroma_db")


def get_or_create_collection():
    """Return the ChromaDB collection, creating it if it doesn't exist."""
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )


def embed_and_store():
    """
    Run the ingestion pipeline to get chunks and store them in ChromaDB.
    ChromaDB embeds each chunk internally using the embedding_function
    we attached to the collection (all-MiniLM-L6-v2).
    """
    chunks = run_pipeline()  # list of {"text": ..., "source": ...}

    collection = get_or_create_collection()

    # If the collection already has data, skip re-embedding (mirrors the
    # "Vector store already populated" pattern from Lab 1's RulesBot).
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Vector store already populated ({existing_count} chunks). Skipping embedding.")
        print("To re-embed, delete the ./chroma_db folder and restart.")
        return existing_count

    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]

    # ChromaDB needs a unique string ID per item, plus metadata dict per item.
    ids = [f"{src}_{i}" for i, src in enumerate(sources)]
    metadatas = []
    source_position = {}  # tracks position-within-document per source
    for src in sources:
        source_position[src] = source_position.get(src, 0) + 1
        metadatas.append({"source": src, "position": source_position[src]})

    print(f"Embedding {len(texts)} chunks with {EMBEDDING_MODEL}...")
    collection.add(
        ids=ids,
        documents=texts,   # ChromaDB embeds these automatically via embedding_fn
        metadatas=metadatas,
    )

    print(f"Stored {len(texts)} chunks in ChromaDB.")
    return len(texts)


def query(question: str, top_k: int = TOP_K):
    """
    Retrieve the top_k most similar chunks from ChromaDB for a given
    question. ChromaDB embeds the question internally using the same
    embedding_function, then compares it against stored chunk vectors.

    Returns a list of dicts: {"text": ..., "source": ..., "distance": ...}
    """
    collection = get_or_create_collection()

    results = collection.query(
        query_texts=[question],  # ChromaDB embeds this automatically
        n_results=top_k,
    )

    retrieved = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        retrieved.append({
            "text": doc,
            "source": meta["source"],
            "distance": dist,
        })

    return retrieved


def print_retrieval_results(question: str, results: list):
    """Pretty-print retrieval results for manual inspection."""
    print(f"\nQuery: {question}")
    print("-" * 60)
    for i, r in enumerate(results, 1):
        print(f"\n  Result {i} (source: {r['source']}, distance: {r['distance']:.3f}):")
        print(f"  {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}")
    print()


if __name__ == "__main__":
    embed_and_store()

    # Test with 3 of your evaluation plan queries (from planning.md)
    test_queries = [
        "How does the Columbia housing lottery actually work?",
        "What is the best dining hall at Columbia?",
        "How do I register for disability accommodations at Columbia?",
    ]

    for q in test_queries:
        results = query(q)
        print_retrieval_results(q, results)