import uuid
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Initialize the local HuggingFace embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize ChromaDB to save data to a local folder named "chroma_db"
vector_store = Chroma(
    collection_name="master_resume_data",
    embedding_function=embeddings,
    persist_directory="./chroma_db" 
)

# UPDATED: This function now clears old data before storing new data
def store_chunks_in_db(chunks: list[str], source_filename: str) -> int:
    """
    Automatically clears out any existing records in ChromaDB,
    then generates new embeddings and stores the fresh chunks.
    """
    # 1. Fetch and delete all existing entries in the database
    existing_data = vector_store.get()
    old_ids = existing_data.get("ids", [])
    
    if old_ids:
        print(f"--- AUTO-CLEANUP: Removing {len(old_ids)} old chunks from ChromaDB ---")
        vector_store.delete(ids=old_ids)
    
    # 2. Setup metadata and unique IDs for the new chunks
    metadatas = [{"source": source_filename, "chunk_index": i} for i in range(len(chunks))]
    ids = [f"{source_filename}_{uuid.uuid4()}" for _ in chunks]
    
    # 3. Store the new chunks
    vector_store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
    
    return len(chunks)