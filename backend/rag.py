from backend.embeddings import EmbeddingModel
from backend.vector_store import VectorStore
from backend.llm import LLM


class RAGPipeline:

    def __init__(self):

        print("Loading RAG components...")

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.llm = LLM()

        print("RAG components loaded.")

    def answer_question(self, question, top_k=3):

        # ------------------------------------------
        # 1. Generate query embedding
        # ------------------------------------------

        query_embedding = (
            self.embedding_model
            .generate_embeddings([question])[0]
        )

        # ------------------------------------------
        # 2. Search vector database
        # ------------------------------------------

        results = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        # ------------------------------------------
        # 3. Build context for LLM
        # ------------------------------------------

        context_parts = []

        sources = []

        for i in range(len(documents)):

            source = metadatas[i]["source"]
            page = metadatas[i]["page"]
            distance = distances[i]
            document = documents[i]

            context_parts.append(
                f"""
Source: {source}
Page: {page}

Content:
{document}
"""
            )

            sources.append({
                "source": source,
                "page": page,
                "distance": distance,
                "content": document
            })

        context = "\n\n".join(context_parts)

        # ------------------------------------------
        # 4. Generate grounded answer
        # ------------------------------------------

        answer = self.llm.generate_answer(
            question,
            context
        )

        return answer, sources