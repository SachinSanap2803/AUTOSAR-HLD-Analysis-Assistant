from backend.embeddings import EmbeddingModel
from backend.vector_store import VectorStore


# --------------------------------
# Load models
# --------------------------------

embedding_model = EmbeddingModel()

vector_store = VectorStore()


# --------------------------------
# User query
# --------------------------------

query = input("\nEnter your question: ")

print("\nSearching HLD document...\n")


# --------------------------------
# Create query embedding
# --------------------------------

query_embedding = embedding_model.generate_embeddings(
    [query]
)[0]


# --------------------------------
# Search ChromaDB
# --------------------------------

results = vector_store.search(
    query_embedding,
    top_k=3
)


# --------------------------------
# Display results
# --------------------------------

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]


for i in range(len(documents)):

    print("=" * 60)

    print(f"Result {i + 1}")

    print(
        f"Source: {metadatas[i]['source']}"
    )

    print(
        f"Page: {metadatas[i]['page']}"
    )

    print(
        f"Distance: {distances[i]:.4f}"
    )

    print("\nContent:")
    print(documents[i])

    print()