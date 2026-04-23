import os
from tempfile import NamedTemporaryFile
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Store retrievers per session. Format: {"session_id": retriever}
retrievers = {}

try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
except Exception as e:
    pass

async def process_document(session_id: str, file: UploadFile):
    suffix = ".pdf" if file.filename.endswith(".pdf") else ".txt"
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(temp_path)
        else:
            loader = TextLoader(temp_path, encoding="utf-8")
        
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)
        texts = [doc.page_content for doc in chunks]

        # Use HuggingFace embeddings
        global embeddings
        if 'embeddings' not in globals():
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        vectorstore = FAISS.from_texts(texts, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        retrievers[session_id] = retriever
        return len(texts)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def get_retriever(session_id: str):
    return retrievers.get(session_id)
