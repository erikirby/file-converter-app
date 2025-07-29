import streamlit as st
import os
import json
import csv
import pptx
from docx import Document
import pdfplumber

def extract_text_from_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext == ".txt":
        return file.read().decode("utf-8", errors="ignore")
    elif ext == ".docx":
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".csv":
        return file.read().decode("utf-8", errors="ignore")
    elif ext == ".pdf":
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    elif ext == ".pptx":
        presentation = pptx.Presentation(file)
        text = ""
        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    else:
        return f"[Unsupported file type: {file.name}]"

def main():
    st.title("🗃️ File to Text Converter")
    st.caption("Convert multiple files into a single file for AI training")

    uploaded_files = st.file_uploader(
        "Select files to convert",
        accept_multiple_files=True,
        type=["docx", "txt", "csv", "pdf", "pptx"]
    )

    export_format = st.radio("Choose export format", ["Plain Text (.txt)", "Structured JSONL (.jsonl)"])

    if st.button("Convert Files 🚀"):
        if uploaded_files:
            all_texts = []
            for file in uploaded_files:
                text = extract_text_from_file(file)
                cleaned = text.strip()
                if export_format == "Structured JSONL (.jsonl)":
                    all_texts.append(json.dumps({"source": file.name, "content": cleaned}, ensure_ascii=False))
                else:
                    all_texts.append(f"--- {file.name} ---\n{cleaned}\n")

            if export_format == "Structured JSONL (.jsonl)":
                full_content = "\n".join(all_texts)
                st.download_button(
                    label="Download .jsonl",
                    data=full_content,
                    file_name="all_content.jsonl",
                    mime="application/json"
                )
            else:
                full_content = "\n".join(all_texts)
                st.download_button(
                    label="Download .txt",
                    data=full_content,
                    file_name="all_content.txt",
                    mime="text/plain"
                )

            st.text_area("Preview (first 1000 characters)", full_content[:1000], height=300)
        else:
            st.warning("Please upload some files first!")

if __name__ == "__main__":
    main()