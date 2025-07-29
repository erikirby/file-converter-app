import os
import json
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document


def read_pdf(file):
    try:
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except:
        return "[Error reading PDF]"


def read_docx(file):
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return "[Error reading DOCX]"


def read_txt(file):
    try:
        return file.read().decode("utf-8")
    except:
        return "[Error reading TXT]"


def convert_file(file):
    name = file.name
    suffix = name.split(".")[-1].lower()
    if suffix == "pdf":
        text = read_pdf(file)
    elif suffix == "docx":
        text = read_docx(file)
    elif suffix == "txt":
        text = read_txt(file)
    else:
        text = "[Unsupported file type]"
    return name, text


def main():
    st.title("File to Text Converter")
    st.caption("Convert your documents to a single file for AI training")

    uploaded_files = st.file_uploader(
        "Select files to convert",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    export_format = st.radio("Choose export format", ["Plain Text (.txt)", "Structured JSONL (.jsonl)"])

    if st.button("Convert Files 