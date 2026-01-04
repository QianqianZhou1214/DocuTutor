import os
import hashlib
from pathlib import Path
from typing import List, Optional
from pdfplumber import open as pdf_open
from pptx import Presentation
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from sqlalchemy.orm import Session
from ..models import File

# Settings
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
SEPARATOR = "=================================================="


# file parsing
def parse_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    text = ""

    if ext == ".pdf":
        with pdf_open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
    elif ext in [".ppt", ".pptx"]:
        prs = Presentation(file_path)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
    elif ext in [".txt"]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return text


# generating hash for files
def file_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# text splitter
def split_text(text: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[SEPARATOR]
    )
    return splitter.create_documents([text])


# initializing Chroma
def init_chroma_collection(collection_name: str):
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_function
    )


