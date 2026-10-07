from backend.pdf_processor import extract_text_from_pdf
from backend.chunker import chunk_pages


pdf_path = "data/uploads/sample.pdf"

# Extract PDF
pages = extract_text_from_pdf(pdf_path)

print("Total pages:", len(pages))


# Create chunks
chunks = chunk_pages(
    pages,
    source="sample.pdf"
)

print("Total chunks:", len(chunks))


# Display chunks
for i, chunk in enumerate(chunks, start=1):

    print("\n==============================")
    print("Chunk:", i)
    print("Page:", chunk["metadata"]["page"])
    print("Source:", chunk["metadata"]["source"])
    print("==============================")

    print(chunk["text"])