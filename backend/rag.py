import chromadb
from sentence_transformers import SentenceTransformer

# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# ==========================================
# INITIALIZE CHROMADB
# ==========================================

print("Connecting to ChromaDB...")

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="bible_verses"
)

print("ChromaDB connected successfully.")

# ==========================================
# RETRIEVE SCRIPTURE
# ==========================================

def retrieve_scripture(
    query: str,
    top_k: int = 5
):
    """
    Retrieve relevant Bible verses
    using semantic similarity search.
    """

    try:

        # Generate embedding
        query_embedding = embedding_model.encode(
            query
        ).tolist()

        # Search ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        retrieved_verses = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        # Format response
        for doc, metadata in zip(
            documents,
            metadatas
        ):

            retrieved_verses.append({

                "reference": metadata.get(
                    "reference",
                    "Unknown"
                ),

                "book": metadata.get(
                    "book",
                    ""
                ),

                "chapter": metadata.get(
                    "chapter",
                    ""
                ),

                "verse": metadata.get(
                    "verse",
                    ""
                ),

                "text": metadata.get(
                    "text",
                    doc
                )
            })

        return retrieved_verses

    except Exception as e:

        print(
            f"[RAG ERROR] {str(e)}"
        )

        return []

# ==========================================
# BUILD SCRIPTURE CONTEXT
# ==========================================

def build_scripture_context(verses):
    """
    Convert retrieved verses into
    formatted prompt context.
    """

    if not verses:
        return "No scripture found."

    context = ""

    for verse in verses:

        reference = verse["reference"]
        text = verse["text"]

        context += (
            f"{reference}: {text}\n\n"
        )

    return context.strip()

# ==========================================
# VALIDATE SCRIPTURE REFERENCE
# ==========================================

def validate_scripture_reference(
    reference: str
):
    """
    Check whether scripture reference exists.
    """

    try:

        results = collection.query(
            query_texts=[reference],
            n_results=1
        )

        if (
            results["documents"]
            and len(results["documents"][0]) > 0
        ):
            return True

        return False

    except Exception as e:

        print(
            f"[VALIDATION ERROR] {str(e)}"
        )

        return False

# ==========================================
# HYBRID RETRIEVAL
# ==========================================

def retrieve_by_topic(
    topic: str,
    denomination: str = None
):
    """
    Retrieve scripture based on topic.
    """

    query = f"""
    Bible verses about {topic}
    Christian teaching on {topic}
    """

    if denomination:

        query += (
            f" {denomination} interpretation"
        )

    return retrieve_scripture(query)

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    print("\n===== TESTING RAG =====\n")

    test_query = (
        "What does Bible say about forgiveness?"
    )

    verses = retrieve_scripture(
        test_query,
        top_k=3
    )

    print("Retrieved Verses:\n")

    for verse in verses:

        print(
            f"{verse['reference']}"
        )

        print(
            f"{verse['text']}\n"
        )

    print("\n===== CONTEXT =====\n")

    context = build_scripture_context(
        verses
    )

    print(context)

    print("\n===== VALIDATION =====\n")

    is_valid = validate_scripture_reference(
        "John 3:16"
    )

    print(
        f"John 3:16 Exists: {is_valid}"
    )