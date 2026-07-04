import os
from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.documents import Document

class MemoryDatabase:
    def __init__(self, persist_directory="./.chroma"):
        self.persist_directory = persist_directory
        # Use sentence-transformers for local, fast embeddings
        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize Chroma vector store
        self.vector_store = Chroma(
            collection_name="user_memory",
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )

    def save_memory(self, text: str, user_id: str = "default_user"):
        """Save a new memory to the vector database."""
        doc = Document(page_content=text, metadata={"user_id": user_id})
        self.vector_store.add_documents([doc])

    def get_relevant_memories(self, query: str, user_id: str = "default_user", k: int = 3) -> str:
        """Retrieve relevant memories based on the user's query."""
        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter={"user_id": user_id}
        )
        
        if not results:
            return "No previous relevant memories found."
            
        memories = [doc.page_content for doc in results]
        return "\n".join(memories)

# Singleton instance
memory_db = MemoryDatabase()
