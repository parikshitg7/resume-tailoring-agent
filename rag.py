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

def store_chunks_in_db(chunks: list[str], source_filename: str) -> int:
    """
    Converts text chunks into embeddings and stores them locally in ChromaDB.
    """
    # Create metadata so the AI knows where the data came from
    metadatas = [{"source": source_filename, "chunk_index": i} for i in range(len(chunks))]
    
    # Generate unique IDs for the database records
    ids = [f"{source_filename}_{uuid.uuid4()}" for _ in chunks]
    
    # Save everything to the database
    vector_store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
    
    return len(chunks)