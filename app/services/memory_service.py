import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings

class MemoryService:
    def __init__(self):
        try:
            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
            self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GEMINI_API_KEY)
            
            # Collection names
            self.collections = ["user_memory", "rag_documents", "conversation_history"]
            self._ensure_collections()
            self.connected = True
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant. Memory features disabled. Error: {e}")
            self.connected = False
            self.client = None

    def _ensure_collections(self):
        """Ensure all required collections exist in Qdrant."""
        if not self.connected: return

        for collection_name in self.collections:
            if not self.client.collection_exists(collection_name):
                print(f"Creating Qdrant collection: {collection_name}")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )

    def store_memory(self, user_id: str, text: str, memory_type: str = "user_memory"):
        """Store a new memory point."""
        if not self.connected:
            print("Qdrant disconnected. Cannot store memory.")
            return None
        vector = self.embeddings.embed_query(text)
        point_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=memory_type,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"user_id": user_id, "text": text, "type": memory_type}
                )
            ]
        )
        return point_id

    def retrieve_relevant_memory(self, user_id: str, query: str, memory_type: str = "user_memory", top_k: int = 3):
        """Retrieve most relevant memories for the user query."""
        if not self.connected:
            print("Qdrant disconnected. Returning empty memory.")
            return []
            
        query_vector = self.embeddings.embed_query(query)
        
        search_result = self.client.search(
            collection_name=memory_type,
            query_vector=query_vector,
            query_filter=None,  # Ideally filter by user_id
            limit=top_k
        )
        
        return [hit.payload["text"] for hit in search_result]

memory_service = MemoryService()
