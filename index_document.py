from backend.pdf_processor import extract_text_from_pdf
from backend.chunker import chunk_pages
from backend.embeddings import EmbeddingModel
from backend.vector_store import VectorStore


PDF_PATH = "data/uploads/sample.pdf"


# --------------------------------
# 1. Extract PDF
# --------------------------------

print("\n[1] Extracting PDF...")

pages = extract_text_from_pdf(PDF_PATH)

print(f"Extracted {len(pages)} pages.")


# --------------------------------
# 2. Create chunks
# --------------------------------

print("\n[2] Creating chunks...")

chunks = chunk_pages(
    pages,
    source="sample.pdf"
)

print(f"Created {len(chunks)} chunks.")


# --------------------------------
# 3. Generate embeddings
# --------------------------------

print("\n[3] Generating embeddings...")

embedding_model = EmbeddingModel()

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_model.generate_embeddings(
    texts
)

print(
    "Embedding shape:",
    embeddings.shape
)


# --------------------------------
# 4. Store in ChromaDB
# --------------------------------

print("\n[4] Storing in ChromaDB...")

vector_store = VectorStore()

vector_store.add_documents(
    chunks,
    embeddings
)

print("\nDocument indexing completed successfully! ✅")