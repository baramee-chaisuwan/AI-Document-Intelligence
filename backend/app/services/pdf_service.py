import fitz

def extract_text_from_pdf(file_bytes):

    try:

        document = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

    except Exception:

        raise Exception(
            "Invalid PDF file"
        )


    texts = []

    try:

        for page in document:

            texts.append(
                page.get_text()
            )

    finally:

        document.close()

    return "\n".join(
        texts
    ).strip()