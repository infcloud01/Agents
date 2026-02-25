from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_oci import OCIGenAIEmbeddings, ChatOCIGenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURATION ---
# Replace with your specific OCI Compartment OCID and Region Endpoint
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaa5iuuooli253n4vn7dkwuothobenpa5rbxlxsuykc2kgke6kd67ca"
ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com" 

# --- 2. INITIALIZE OCI MODELS (COHERE) ---
embeddings = OCIGenAIEmbeddings(
    model_id="cohere.embed-english-v3.0",
    service_endpoint=ENDPOINT,
    compartment_id=COMPARTMENT_ID
)

llm = ChatOCIGenAI(
    model_id="cohere.command-r-08-2024",
    service_endpoint=ENDPOINT,
    compartment_id=COMPARTMENT_ID,
    model_kwargs={"temperature": 0} # Set to 0 to keep the model factual and grounded
)

# --- 3. LOAD & CHUNK THE PDF DOCUMENTS ---
# Point the loader to your folder. It will process all PDFs inside.
loader = PyPDFDirectoryLoader("./knowledge_base/")
docs = loader.load()

# Break the documents into smaller, readable pieces
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(docs)

# --- 4. CREATE THE VECTOR STORE ---
# This creates a local, in-memory Chroma database
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Retrieve the top 3 most relevant chunks

# --- 5. BUILD THE RAG CHAIN ---
template = """Use the following pieces of retrieved context to answer the question. 
If the answer is not in the context, just say that you don't know. 
Keep the answer concise and factual.

Context: {context}

Question: {question}

Answer:"""
prompt = PromptTemplate.from_template(template)

# Helper function to format the retrieved documents into a single string
def format_docs(retrieved_docs):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)

# The simple LangChain pipeline
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- 6. RUN THE AGENT ---
# --- 6. RUN THE INTERACTIVE AGENT ---
print("\n" + "="*40)
print("🤖 Your RAG Agent is ready!")
print("Type 'quit' or 'exit' to stop.")
print("="*40 + "\n")

while True:
    # 1. Prompt the user for a question
    query = input("Ask a question: ")
    
    # 2. Check if the user wants to quit
    if query.lower() in ['quit', 'exit']:
        print("Shutting down the agent. Goodbye!")
        break
        
    # Ignore empty inputs
    if not query.strip():
        continue
        
    # 3. Process the query and print the answer
    print("-" * 20)
    print("Thinking...")
    
    answer = rag_chain.invoke(query)
    
    print("\nAnswer:", answer)
    print("-" * 20 + "\n")
"""
query = "What is the main takeaway from the documents?"
print(f"Question: {query}")
print("-" * 20)
print(rag_chain.invoke(query))
"""