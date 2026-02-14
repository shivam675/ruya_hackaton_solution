from pathlib import Path
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

PDF_DIR = Path("hr_pdfs")
DB_DIR = Path("chroma_db")
DB_DIR.mkdir(exist_ok=True)

client = chromadb.PersistentClient(path=str(DB_DIR))
collection_name = "hr_policies"
if collection_name in [c.name for c in client.list_collections()]:
    collection = client.get_collection(collection_name)
else:
    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    )

chunk_size = 1500

def read_pdf(file_path):
    reader = PdfReader(str(file_path))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

for pdf_file in PDF_DIR.glob("*.pdf"):
    text = read_pdf(pdf_file)
    for i, start in enumerate(range(0, len(text), chunk_size)):
        chunk = text[start:start+chunk_size]
        doc_id = f"{pdf_file.stem}_{i}"  # unique ID
        collection.add(
            ids=[doc_id],
            documents=[chunk],
            metadatas=[{"source": pdf_file.name}]
        )

print("PDF ingestion complete!")
