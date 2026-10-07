import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Extract text from every page of a PDF.

    Returns:
        list: List of dictionaries containing
            page number and page text.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text
            })

    document.close()

    return pages