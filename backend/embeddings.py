from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self):
        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

    def generate_embeddings(self, texts):
        """
        Generate vector embeddings for a list of texts.
        """

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True
        )

        return embeddings