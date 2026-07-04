import asyncio
from app.agents.rag import knowledge_base

def main():
    print("Starting Knowledge Base Ingestion...")
    knowledge_base.ingest_documents()
    print("Done!")

if __name__ == "__main__":
    main()
