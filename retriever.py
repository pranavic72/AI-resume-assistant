import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
import PyPDF2
import io

# In-memory store
_documents = []  # {"text": str, "filename": str}
_vectorizer = None
_matrix = None

def _rebuild_index():
    global _vectorizer, _matrix
    if not _documents:
        _vectorizer = None
        _matrix = None
        return
    texts = [d["text"] for d in _documents]
    _vectorizer = TfidfVectorizer(stop_words="english")
    _matrix = _vectorizer.fit_transform(texts)

def extract_text_from_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_pdf(file_bytes):
    pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    return "\n".join([page.extract_text() or "" for page in pdf.pages])

def add_file_to_collection(filename, file_bytes):
    if filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    elif filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        return False

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    for chunk in chunks:
        _documents.append({"text": chunk, "filename": filename})
    _rebuild_index()
    return True

def remove_file_from_collection(filename):
    global _documents
    _documents = [d for d in _documents if d["filename"] != filename]
    _rebuild_index()

def get_relevant_context(query, filenames=None):
    if not _documents or _vectorizer is None:
        return "No documents uploaded yet."

    # Filter by filenames if needed
    docs = _documents
    if filenames:
        docs = [d for d in _documents if d["filename"] in filenames]
    if not docs:
        return "No documents uploaded yet."

    texts = [d["text"] for d in docs]
    matrix = _vectorizer.transform(texts)
    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix)[0]
    top_indices = np.argsort(scores)[::-1][:5]

    context = ""
    for i in top_indices:
        context += f"\n[From: {docs[i]['filename']}]\n{docs[i]['text']}\n"
    return context