"""
Text processing module for chunking documents into smaller pieces.
Preserves metadata for citation tracking.
"""

from typing import List, Dict, Any
import config


class TextChunker:
    """Splits text into overlapping chunks for better retrieval."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Number of characters per chunk (default from config)
            chunk_overlap: Number of overlapping characters (default from config)
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks while preserving metadata.
        
        Args:
            text: The full text to chunk
            metadata: Metadata from the file loader
            
        Returns:
            List of dictionaries, each containing 'text' and 'metadata'
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        text_length = len(text)
        start = 0
        chunk_id = 0
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If not the last chunk, try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence endings
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                best_break = end
                
                # Search backwards from end position for a good break point
                search_range = min(100, self.chunk_size // 4)  # Search in last 25% of chunk
                for i in range(end, max(start, end - search_range), -1):
                    for ending in sentence_endings:
                        if text[i:i+len(ending)] == ending:
                            best_break = i + len(ending)
                            break
                    if best_break != end:
                        break
                
                end = best_break
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                # Create chunk metadata
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = chunk_id
                chunk_metadata['chunk_start'] = start
                chunk_metadata['chunk_end'] = end
                chunk_metadata['chunk_size'] = len(chunk_text)
                
                # For PDFs, try to estimate which page this chunk belongs to
                if metadata.get('file_type') == 'pdf' and 'pages' in metadata:
                    chunk_metadata['estimated_page'] = self._estimate_page(
                        start, end, text_length, metadata['total_pages']
                    )
                
                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata
                })
                
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start <= end - self.chunk_size:
                start = end
        
        return chunks
    
    def _estimate_page(self, start: int, end: int, total_length: int, total_pages: int) -> int:
        """
        Estimate which page a chunk belongs to based on character position.
        
        Args:
            start: Start position of chunk
            end: End position of chunk
            total_length: Total length of document text
            total_pages: Total number of pages
            
        Returns:
            Estimated page number (1-indexed)
        """
        # Use midpoint of chunk for estimation
        midpoint = (start + end) / 2
        estimated_page = int((midpoint / total_length) * total_pages) + 1
        return min(estimated_page, total_pages)
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents at once.
        
        Args:
            documents: List of documents from file loaders
            
        Returns:
            Flattened list of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_text(doc['text'], doc['metadata'])
            all_chunks.extend(chunks)
        
        return all_chunks
