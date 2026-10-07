import chromadb


class VectorStore:

    def __init__(self, persist_directory="data/chroma_db"):

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name="autosar_hld"
        )

    def clear(self):
        """
        Remove all existing documents from the collection.
        """

        existing = self.collection.get()

        if existing["ids"]:
            self.collection.delete(
                ids=existing["ids"]
            )

        print("Vector store cleared.")

    def add_documents(self, chunks, embeddings):

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in chunks
        ]

        ids = [
            f"chunk_{i}"
            for i in range(len(chunks))
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        print(
            f"Stored {len(documents)} chunks in ChromaDB."
        )

    def search(self, query_embedding, top_k=3):

        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=top_k
        )

        return results