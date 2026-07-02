import fitz
import io


def extract_text_from_pdf(file_bytes):

    document = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text