{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import json\
import streamlit as st\
from PyPDF2 import PdfReader\
from docx import Document\
\
\
def read_pdf(file):\
    try:\
        reader = PdfReader(file)\
        return "\\n".join(page.extract_text() or "" for page in reader.pages)\
    except:\
        return "[Error reading PDF]"\
\
\
def read_docx(file):\
    try:\
        doc = Document(file)\
        return "\\n".join([para.text for para in doc.paragraphs])\
    except:\
        return "[Error reading DOCX]"\
\
\
def read_txt(file):\
    try:\
        return file.read().decode("utf-8")\
    except:\
        return "[Error reading TXT]"\
\
\
def convert_file(file):\
    name = file.name\
    suffix = name.split(".")[-1].lower()\
    if suffix == "pdf":\
        text = read_pdf(file)\
    elif suffix == "docx":\
        text = read_docx(file)\
    elif suffix == "txt":\
        text = read_txt(file)\
    else:\
        text = "[Unsupported file type]"\
    return name, text\
\
\
def main():\
    st.title("File to Text Converter")\
    st.caption("Convert your documents to a single file for AI training")\
\
    uploaded_files = st.file_uploader(\
        "Select files to convert",\
        type=["pdf", "docx", "txt"],\
        accept_multiple_files=True\
    )\
\
    export_format = st.radio("Choose export format", ["Plain Text (.txt)", "Structured JSONL (.jsonl)"])\
\
    if st.button("Convert Files }