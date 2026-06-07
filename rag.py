import uuid
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Initialize the local HuggingFace embedding model (Free and fast)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize ChromaDB to save data to a local folder named "chroma_db"
vector_store = Chroma(
    collection_name="master_resume_data",
    embedding_function=embeddings,
    persist_directory="./chroma_db" 
)

def store_and_retrieve_master_data(master_chunks: list[str], jd_query: str, k: int = 4) -> str:
    """
    Clears old data, embeds the new Master Data, and performs a similarity 
    search using the Job Description to find the top 'k' most relevant chunks.
    """
    # 1. Fetch and delete all existing entries in the database to keep it clean
    existing_data = vector_store.get()
    old_ids = existing_data.get("ids", [])
    if old_ids:
        print(f"--- RAG: Removing {len(old_ids)} old chunks ---")
        vector_store.delete(ids=old_ids)
    
    # 2. Store the new chunks with unique IDs
    ids = [str(uuid.uuid4()) for _ in master_chunks]
    vector_store.add_texts(texts=master_chunks, ids=ids)
    print(f"--- RAG: Embedded {len(master_chunks)} new chunks ---")
    
    # 3. Retrieve the Top K chunks that semantically match the Job Description
    print("--- RAG: Searching for Master Data matching the JD ---")
    results = vector_store.similarity_search(jd_query, k=k)
    
    # 4. Combine the retrieved chunks into a single string for the LLM
    retrieved_context = "\n\n...[RETRIEVED MASTER DATA]...\n\n".join([doc.page_content for doc in results])
    return retrieved_context