import fitz
import shutil


def save_uploaded_file(file, file_path):

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def extract_text_from_pdf(file_path):

    document = fitz.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text