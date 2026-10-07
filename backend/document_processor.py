import os

from backend.pdf_processor import extract_text_from_pdf
from backend.chunker import chunk_pages


class DocumentProcessor:

    def __init__(
        self,
        embedding_model,
        vector_store
    ):

        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def process_document(self, pdf_path):

        print("\n[1] Extracting PDF...")

        pages = extract_text_from_pdf(pdf_path)

        if not pages:
            raise ValueError(
                "No text could be extracted from the PDF."
            )

        print(
            f"Extracted {len(pages)} pages."
        )

        print("\n[2] Creating chunks...")

        source = os.path.basename(pdf_path)

        chunks = chunk_pages(
            pages,
            source=source
        )

        print(
            f"Created {len(chunks)} chunks."
        )

        print("\n[3] Generating embeddings...")

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_model
            .generate_embeddings(texts)
        )

        print(
            f"Embedding shape: {embeddings.shape}"
        )

        print("\n[4] Updating ChromaDB...")

        self.vector_store.clear()

        self.vector_store.add_documents(
            chunks,
            embeddings
        )

        print(
            "\nDocument indexing completed successfully!"
        )

        return {
            "filename": source,
            "pages": len(pages),
            "chunks": len(chunks)
        }