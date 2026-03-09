import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load OpenAI key from .env
load_dotenv()

# ==========================================
# 1. Load Real Data from the Directory
# ==========================================
print("📂 Loading documents from ./knowledge_base...")

# This will load all .txt files from the knowledge_base folder
loader = DirectoryLoader('./knowledge_base', glob="**/*.pdf", loader_cls=PyPDFLoader)
documents = loader.load()

print(f"Loaded {len(documents)} document(s).")

# ==========================================
# 2. Split the Documents into Chunks
# ==========================================
print("✂️ Splitting documents into manageable chunks...")

# This splitter breaks text at paragraphs, then sentences, then words
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # Max characters per chunk
    chunk_overlap=200,     # Overlap chunks by 200 chars so we don't cut a sentence in half
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.split_documents(documents)

print(f"Split into {len(chunks)} chunks.")

# ==========================================
# 3. Embed and Store in ChromaDB
# ==========================================
print("🧠 Embedding chunks and updating Vector Database...")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create or update the local database
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db" 
)

print("✅ Knowledge base successfully updated with real data!")