import re


def clean_text(text):
    """
    Clean extracted PDF text while preserving meaningful structure.
    """

    # Replace multiple spaces/tabs with one space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def chunk_pages(pages, source="sample.pdf", max_chars=800):
    """
    Create structure-aware chunks from PDF pages.

    Each chunk keeps:
    - source document
    - page number
    - chunk text
    """

    chunks = []

    for page in pages:

        page_number = page["page"]

        text = clean_text(page["text"])

        # Split by paragraphs
        paragraphs = re.split(r"\n\s*\n", text)

        current_chunk = ""

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            # If adding the paragraph stays within the limit
            if len(current_chunk) + len(paragraph) <= max_chars:

                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += paragraph

            else:

                # Save current chunk
                if current_chunk:

                    chunks.append({
                        "text": current_chunk,
                        "metadata": {
                            "source": source,
                            "page": page_number
                        }
                    })

                # Start new chunk
                current_chunk = paragraph

        # Save remaining chunk
        if current_chunk:

            chunks.append({
                "text": current_chunk,
                "metadata": {
                    "source": source,
                    "page": page_number
                }
            })

    return chunks