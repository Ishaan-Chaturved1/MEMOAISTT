# rag.py
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

DB_PATH = "vectorstore"

def create_vectorstore(data_path="data"):
    docs = []

    for file in os.listdir(data_path):
        loader = TextLoader(os.path.join(data_path, file))
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    split_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(DB_PATH)
    print("✅ Vector DB created")


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)


def retrieve_docs(query, k=3):
    db = load_vectorstore()
    docs = db.similarity_search(query, k=k)
    return "\n\n".join([d.page_content for d in docs])