"""
Vector store module using FAISS for efficient similarity search.
Handles embedding storage, retrieval, and persistence to disk.
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
import config


class VectorStore:
    """FAISS-based vector database for document chunks."""
    
    def __init__(self, dimension: int = None):
        """
        Initialize the vector store.
        
        Args:
            dimension: Dimension of embeddings (default from config)
        """
        self.dimension = dimension or config.EMBEDDING_DIMENSION
        self.index = faiss.IndexFlatL2(self.dimension)  # L2 distance for similarity
        self.chunks = []  # Parallel list to store chunk texts
        self.metadata = []  # Parallel list to store chunk metadata
        self.document_files = set()  # Track unique document files
    
    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Add document chunks and their embeddings to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            embeddings: Numpy array of embeddings (shape: [n_chunks, dimension])
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")
        
        # Ensure embeddings are float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store chunks and metadata
        for chunk in chunks:
            self.chunks.append(chunk['text'])
            self.metadata.append(chunk['metadata'])
            self.document_files.add(chunk['metadata']['file_name'])
    
    def search(self, query_embedding: np.ndarray, k: int = None) -> List[Dict[str, Any]]:
        """
        Search for top-k most similar chunks to the query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of top results to return (default from config)
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'score'
        """
        k = k or config.TOP_K_RETRIEVAL
        
        if self.index.ntotal == 0:
            return []
        
        # Ensure query is the right shape and type
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        
        # Perform search
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Convert distances to similarity scores (lower distance = higher similarity)
        # Using negative exponential: similarity = e^(-distance)
        similarities = np.exp(-distances[0])
        
        # Build results
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if similarity >= config.SIMILARITY_THRESHOLD:
                results.append({
                    'text': self.chunks[idx],
                    'metadata': self.metadata[idx],
                    'score': float(similarity)
                })
        
        return results
    
    def save_to_disk(self, path: str = None):
        """
        Save the vector store to disk.
        
        Args:
            path: Directory to save to (default from config)
        """
        path = path or config.VECTOR_STORE_DIR
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(path, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        
        # Save chunks and metadata with pickle
        data_path = os.path.join(path, "chunks_metadata.pkl")
        with open(data_path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata,
                'document_files': self.document_files,
                'dimension': self.dimension
            }, f)
    
    def load_from_disk(self, path: str = None) -> bool:
        """
        Load the vector store from disk.
        
        Args:
            path: Directory to load from (default from config)
            
        Returns:
            True if successfully loaded, False otherwise
        """
        path = path or config.VECTOR_STORE_DIR
        
        index_path = os.path.join(path, "faiss_index.bin")
        data_path = os.path.join(path, "chunks_metadata.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(data_path):
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load chunks and metadata
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
                self.document_files = data['document_files']
                self.dimension = data['dimension']
            
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def clear(self):
        """Clear all data from the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        self.metadata = []
        self.document_files = set()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with stats like number of chunks, documents, etc.
        """
        return {
            'total_chunks': self.index.ntotal,
            'total_documents': len(self.document_files),
            'document_files': sorted(list(self.document_files)),
            'dimension': self.dimension
        }
    
    def is_empty(self) -> bool:
        """Check if the vector store is empty."""
        return self.index.ntotal == 0
