import os
import glob
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

class KnowledgeBase:
    def __init__(self, persist_directory="./.chroma", docs_dir="./documents"):
        self.persist_directory = persist_directory
        self.docs_dir = docs_dir
        # Use Google GenAI embeddings for zero local memory footprint (fixes Render OOM)
        self.embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        self.vector_store = Chroma(
            collection_name="knowledge_base",
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def ingest_documents(self):
        """Scans the documents directory and ingests new files into the knowledge base."""
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)

        # Get existing sources to avoid duplicate ingestion
        try:
            existing_data = self.vector_store.get(include=["metadatas"])
            existing_sources = set()
            for meta in existing_data.get("metadatas", []):
                if meta and "source" in meta:
                    existing_sources.add(meta["source"])
        except Exception as e:
            print(f"Error fetching existing documents: {e}")
            existing_sources = set()

        files = glob.glob(os.path.join(self.docs_dir, "*"))
        new_docs = []

        for file_path in files:
            if file_path in existing_sources:
                continue

            print(f"Ingesting new document: {file_path}")
            try:
                if file_path.lower().endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                elif file_path.lower().endswith('.txt') or file_path.lower().endswith('.md'):
                    loader = TextLoader(file_path)
                    docs = loader.load()
                else:
                    print(f"Unsupported file type: {file_path}")
                    continue

                # Add source metadata explicitly just in case
                for doc in docs:
                    doc.metadata["source"] = file_path

                new_docs.extend(docs)
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")

        if new_docs:
            chunks = self.text_splitter.split_documents(new_docs)
            print(f"Adding {len(chunks)} chunks to the knowledge base...")
            self.vector_store.add_documents(chunks)
            print("Ingestion complete.")
        else:
            print("No new documents to ingest.")

    def search(self, query: str, k: int = 4) -> str:
        """Search the knowledge base for relevant chunks."""
        results = self.vector_store.similarity_search(query, k=k)
        if not results:
            return "No relevant information found in the knowledge base."
        
        snippets = []
        for doc in results:
            source = os.path.basename(doc.metadata.get('source', 'Unknown'))
            page = doc.metadata.get('page', '')
            page_info = f" (Page {page})" if page else ""
            snippets.append(f"--- From {source}{page_info} ---\n{doc.page_content}")
            
        return "\n\n".join(snippets)

# Singleton instance
knowledge_base = KnowledgeBase()
