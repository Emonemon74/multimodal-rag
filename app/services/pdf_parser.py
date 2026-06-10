import re

from unstructured.partition.pdf import partition_pdf

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 250
MIN_CHUNK_LENGTH = 120


def _normalize_text(text):

    collapsed_text = re.sub(r"\s+", " ", text)

    return collapsed_text.strip()


def _split_text_with_overlap(text):

    if len(text) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        if end < len(text):
            split_at = text.rfind(" ", start, end)

            if split_at > start + (CHUNK_SIZE // 2):
                end = split_at

        chunk = text[start:end].strip()

        if len(chunk) >= MIN_CHUNK_LENGTH:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def parse_pdf(pdf_path):

    elements = partition_pdf(filename=pdf_path, strategy="auto")

    pages = {}

    for element in elements:
        raw_text = getattr(element, "text", "") or str(element)

        text = _normalize_text(raw_text)

        if not text:
            continue

        metadata = getattr(element, "metadata", None)

        page_number = getattr(metadata, "page_number", None) or 1

        pages.setdefault(page_number, []).append(text)

    documents = []

    for page_number in sorted(pages):
        page_text = _normalize_text(" ".join(pages[page_number]))

        if len(page_text) < MIN_CHUNK_LENGTH:
            continue

        page_chunks = _split_text_with_overlap(page_text)

        for chunk_index, chunk_text in enumerate(page_chunks):
            documents.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "page": page_number,
                        "chunk_index": chunk_index,
                        "source": pdf_path.split("/")[-1],
                    },
                }
            )

    print("PARSED PAGES:", len(pages))

    print("CHUNKS CREATED:", len(documents))

    return {"documents": documents, "tables": [], "pages": len(pages)}
