"""
Vector store for PMC chatbot using ChromaDB
"""
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
from utils import setup_logging, get_config, load_data

logger = setup_logging()

class PMCVectorStore:
    def __init__(self):
        self.config = get_config()
        self.persist_directory = self.config['chroma_persist_directory']
        self.embedding_model_name = self.config['embedding_model_name']
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="pmc_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Vector store initialized at {self.persist_directory}")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return []
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store"""
        try:
            all_texts = []
            all_metadatas = []
            all_ids = []
            
            for i, doc in enumerate(documents):
                # Add each chunk as a separate document
                for j, chunk in enumerate(doc.get('chunks', [])):
                    if chunk.strip():
                        all_texts.append(chunk)
                        all_metadatas.append({
                            'url': doc.get('url', ''),
                            'title': doc.get('title', ''),
                            'chunk_index': j,
                            'total_chunks': len(doc.get('chunks', [])),
                            **doc.get('metadata', {})
                        })
                        all_ids.append(f"doc_{i}_chunk_{j}")
            
            if not all_texts:
                logger.warning("No valid texts to add to vector store")
                return False
            
            # Create embeddings
            embeddings = self.create_embeddings(all_texts)
            
            if not embeddings:
                logger.error("Failed to create embeddings")
                return False
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=all_texts,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            logger.info(f"Added {len(all_texts)} document chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance,  # Convert distance to similarity
                        'rank': i + 1
                    })
            
            logger.info(f"Found {len(formatted_results)} relevant documents for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'embedding_model': self.embedding_model_name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection("pmc_documents")
            self.collection = self.client.create_collection(
                name="pmc_documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
    
    def load_and_index_data(self, data_file: str = "data/pmc_scraped_data.json") -> bool:
        """Load data from file and index it in the vector store"""
        try:
            # Check if data already exists in vector store
            if self.collection.count() > 0:
                logger.info("Vector store already contains data. Skipping indexing.")
                return True
            
            # Load data from file
            documents = load_data(data_file)
            if not documents:
                logger.warning(f"No data found in {data_file}")
                return False
            
            # Add documents to vector store
            success = self.add_documents(documents)
            if success:
                logger.info(f"Successfully indexed {len(documents)} documents")
            else:
                logger.error("Failed to index documents")
            
            return success
            
        except Exception as e:
            logger.error(f"Error loading and indexing data: {e}")
            return False
    
    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant context for a query, respecting token limits"""
        try:
            # Search for relevant documents
            results = self.search(query, n_results=10)
            
            if not results:
                return ""
            
            # Build context string
            context_parts = []
            current_tokens = 0
            
            for result in results:
                content = result['content']
                # Rough token estimation (1 token ≈ 4 characters)
                estimated_tokens = len(content) // 4
                
                if current_tokens + estimated_tokens > max_tokens:
                    break
                
                context_parts.append(f"Source: {result['metadata'].get('title', 'Unknown')}\n{content}")
                current_tokens += estimated_tokens
            
            context = "\n\n".join(context_parts)
            logger.info(f"Generated context with ~{current_tokens} tokens")
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""

def main():
    """Test the vector store"""
    try:
        vector_store = PMCVectorStore()
        
        # Load and index data
        success = vector_store.load_and_index_data()
        
        if success:
            # Test search
            query = "What is the Prime Minister's Office?"
            results = vector_store.search(query, n_results=3)
            
            print(f"\nSearch results for: {query}")
            for i, result in enumerate(results):
                print(f"\n{i+1}. Similarity: {result['similarity_score']:.3f}")
                print(f"   Title: {result['metadata'].get('title', 'Unknown')}")
                print(f"   Content: {result['content'][:200]}...")
        
        # Print stats
        stats = vector_store.get_collection_stats()
        print(f"\nCollection stats: {stats}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main() 
