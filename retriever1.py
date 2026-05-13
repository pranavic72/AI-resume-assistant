import chromadb
import os
from docx import Document
import PyPDF2
import io

# Single ChromaDB client for the whole session
client = chromadb.Client()
collection = client.get_or_create_collection(name="candidates")

def extract_text_from_docx(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_pdf(file_bytes):
    pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

def add_file_to_collection(filename, file_bytes):
    # Extract text based on file type
    if filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    elif filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        return False
    
    # Split into chunks
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    
    # Add to ChromaDB with filename as metadata
    collection.add(
        documents=chunks,
        ids=[f"{filename}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"filename": filename} for _ in chunks]
    )
    return True

def remove_file_from_collection(filename):
    # Get all IDs for this file and delete them
    results = collection.get(where={"filename": filename})
    if results["ids"]:
        collection.delete(ids=results["ids"])

def get_relevant_context(query, filenames=None):
    # Build filter if specific files selected
    if filenames and len(filenames) == 1:
        where = {"filename": filenames[0]}
    else:
        where = None
    
    results = collection.query(
        query_texts=[query],
        n_results=5,
        where=where
    )
    
    if not results["documents"][0]:
        return "No documents uploaded yet."
    
    # Include filename in context so Gemini knows which candidate said what
    context = ""
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context += f"\n[From: {meta['filename']}]\n{doc}\n"
    
    return context