# 📖 Complete Code Explanation - Line by Line

This document explains **EVERY FILE** and **EVERY LINE OF CODE** in the Universal Document Chat project.

---

## 📋 Table of Contents

### Core Application Files
1. [config.py - Configuration Settings](#1-configpy---configuration-settings)
2. [modules/__init__.py - Package Initializer](#2-modules__init__py---package-initializer)
3. [modules/file_loader.py - Document Loading](#3-modulesfile_loaderpy---document-loading)
4. [modules/text_processor.py - Text Chunking](#4-modulestext_processorpy---text-chunking)
5. [modules/vector_store.py - FAISS Vector Database](#5-modulesvector_storepy---faiss-vector-database)
6. [modules/rag_pipeline.py - Main RAG Pipeline](#6-modulesrag_pipelinepy---main-rag-pipeline)
7. [modules/multimodal_rag.py - Image + Text Support](#7-modulesmultimodal_ragpy---image--text-support)
8. [app.py - Streamlit Web Application](#8-apppy---streamlit-web-application)
9. [requirements.txt - Dependencies](#9-requirementstxt---dependencies)

### Utility Scripts
10. [fix_cache.py - Cache Clearing Utility](#10-fix_cachepy---cache-clearing-utility)
11. [install_deps.py - Quick Install Script](#11-install_depspy---quick-install-script)
12. [generate_samples.py - Sample Document Generator](#12-generate_samplespy---sample-document-generator)

### Data Files & Folders
13. [examples/ - Sample Documents](#13-examples---sample-documents)
14. [data/ - Application Data Storage](#14-data---application-data-storage)

### Project Structure Overview
15. [Complete Project Structure](#15-complete-project-structure)

---

## 1. config.py - Configuration Settings

This file contains all the settings and hyperparameters for the application.

```python
"""
Configuration file for Universal Document Chat RAG application.
Contains all model settings, paths, and hyperparameters.
"""
# ↑ Docstring: Explains what this file does
```

```python
import os
# ↑ Import the 'os' module to work with file paths and directories
```

### Model Settings Section

```python
# Embedding model for creating document and query embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```
- **What it is**: The model that converts text into numerical vectors (embeddings)
- **all-MiniLM-L6-v2**: A lightweight model from HuggingFace
- **Why this model**: Fast, 384 dimensions, good quality for semantic search

```python
EMBEDDING_DIMENSION = 384  # Dimension of all-MiniLM-L6-v2 embeddings
```
- **What it is**: The size of each embedding vector
- **384**: This specific model produces 384-dimensional vectors
- **Why it matters**: FAISS needs to know this to create the index

```python
LLM_MODEL = "google/flan-t5-base"  # Can upgrade to flan-t5-large for better quality
```
- **What it is**: The language model that generates answers
- **Flan-T5**: Google's instruction-tuned T5 model
- **"base"**: 250 million parameters (medium size)

```python
LLM_MAX_LENGTH = 300  # Maximum length of generated answers (in tokens)
```
- **What it is**: Limits how long the LLM's answer can be
- **300 tokens**: Approximately 225 words
- **Why limit**: Prevents very long, rambling answers

```python
LLM_TEMPERATURE = 0.7  # Creativity vs determinism (0.0 = deterministic, 1.0 = creative)
```
- **What it is**: Controls randomness in text generation
- **0.7**: Balanced between factual and creative
- **Lower (0.3)**: More deterministic, factual answers
- **Higher (0.9)**: More creative, varied answers

### Text Processing Settings

```python
CHUNK_SIZE = 500  # Characters per chunk
```
- **What it is**: How many characters in each text chunk
- **500 chars**: About 100-125 words
- **Why 500**: Good balance between context and precision

```python
CHUNK_OVERLAP = 50  # Overlapping characters between chunks
```
- **What it is**: Characters shared between consecutive chunks
- **Why overlap**: Prevents losing information at chunk boundaries
- **Example**: 
  ```
  Chunk 1: "...the meeting is scheduled for Tuesday at 3"
  Chunk 2: "for Tuesday at 3 PM in the conference room..."
  ↑ "for Tuesday at 3" overlaps in both chunks
  ```

### Retrieval Settings

```python
TOP_K_RETRIEVAL = 5
```
- **What it is**: Number of similar chunks to retrieve per query
- **5 chunks**: Gets the 5 most relevant pieces of text
- **Why 5**: Enough context without overwhelming the LLM

```python
SIMILARITY_THRESHOLD = 0.3
```
- **What it is**: Minimum relevance score to include a chunk
- **0.3**: Allows somewhat relevant matches
- **0.0-0.3**: Probably irrelevant
- **0.3-0.5**: Somewhat relevant
- **0.5+**: Highly relevant

### Chat Settings

```python
CHAT_HISTORY_LIMIT = 5
```
- **What it is**: How many previous messages to include as context
- **5 messages**: Keeps last 5 Q&A pairs for follow-up questions

### Storage Paths

```python
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
```
- **What it does**: Creates path to "data" folder next to config.py
- **`__file__`**: Path to the current file (config.py)
- **`os.path.dirname(__file__)`**: Gets the directory containing config.py
- **`os.path.join(..., "data")`**: Adds "data" to that path

```python
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")
```
- **What it does**: Path to store FAISS index and metadata
- **Result**: `data/vector_store/`

```python
UPLOADED_FILES_DIR = os.path.join(DATA_DIR, "uploaded_files")
```
- **What it does**: Path to cache uploaded documents
- **Result**: `data/uploaded_files/`

### Supported File Types

```python
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".docx", ".csv"]
```
- **What it is**: List of file extensions the app can process

### UI Settings

```python
APP_TITLE = "Universal Document Chat"
APP_SUBTITLE = "Talk to Your Files with AI"
APP_ICON = "💬"
```
- **What they are**: Display text for the web interface

```python
STATUS_EXTRACTING = "📄 Extracting text from documents..."
STATUS_CHUNKING = "✂️ Splitting text into chunks..."
# ... etc
```
- **What they are**: Status messages shown during processing

---

## 2. modules/__init__.py - Package Initializer

```python
"""
Universal Document Chat - Core Modules
"""
# ↑ Docstring describing the package

__version__ = "1.0.0"
# ↑ Package version number
```

**Purpose**: Makes the `modules` folder a Python package so you can import from it:
```python
from modules.rag_pipeline import RAGPipeline
```

---

## 3. modules/file_loader.py - Document Loading

This module extracts text from different file formats.

### Imports

```python
import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import pdfplumber
from docx import Document
import csv
```

| Import | Purpose |
|--------|---------|
| `os` | File path operations |
| `typing` | Type hints for better code documentation |
| `abc` | Abstract Base Class - for creating interfaces |
| `pdfplumber` | Extract text from PDFs |
| `docx.Document` | Read Word documents |
| `csv` | Parse CSV files |

### BaseLoader (Abstract Base Class)

```python
class BaseLoader(ABC):
    """Abstract base class for document loaders."""
```
- **ABC**: Abstract Base Class - cannot be instantiated directly
- **Purpose**: Defines the interface all loaders must follow

```python
    @abstractmethod
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
```
- **@abstractmethod**: Forces subclasses to implement this method
- **Parameters**:
  - `file_path: str` - Full path to file on disk
  - `file_name: str` - Original filename for metadata
- **Returns**: Dictionary with `'text'` and `'metadata'` keys

### PDFLoader

```python
class PDFLoader(BaseLoader):
    """Loader for PDF files using pdfplumber."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Extract text from PDF with page number tracking."""
        all_text = []  # Store text from each page
        metadata = {
            'file_name': file_name,
            'file_type': 'pdf',
            'pages': []  # Will store info about each page
        }
```

```python
        try:
            with pdfplumber.open(file_path) as pdf:  # Open PDF file
                for page_num, page in enumerate(pdf.pages, start=1):  # Loop through pages
                    text = page.extract_text()  # Get text from page
                    if text:  # If page has text
                        all_text.append(text)  # Add to our list
                        metadata['pages'].append({
                            'page_number': page_num,
                            'text_length': len(text)
                        })
                
                metadata['total_pages'] = len(pdf.pages)  # Count total pages
```

- **`with ... as pdf`**: Context manager - automatically closes file when done
- **`enumerate(..., start=1)`**: Gives us index starting from 1 (not 0)
- **`page.extract_text()`**: pdfplumber method to get text

```python
            return {
                'text': '\n\n'.join(all_text),  # Combine all pages with double newlines
                'metadata': metadata
            }
        except Exception as e:
            raise Exception(f"Error loading PDF {file_name}: {str(e)}")
```

### TextLoader

```python
class TextLoader(BaseLoader):
    """Loader for plain text and markdown files."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:  # Open file with UTF-8 encoding
                text = f.read()  # Read entire file content
            
            lines = text.split('\n')  # Split by newlines to count lines
            metadata = {
                'file_name': file_name,
                'file_type': 'txt' if file_name.endswith('.txt') else 'md',  # Detect type
                'total_lines': len(lines),
                'text_length': len(text)
            }
            
            return {
                'text': text,
                'metadata': metadata
            }
```

### DocxLoader

```python
class DocxLoader(BaseLoader):
    """Loader for Microsoft Word documents."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        try:
            doc = Document(file_path)  # python-docx loads the file
            # Get all non-empty paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = '\n\n'.join(paragraphs)  # Join with double newlines
```

- **`doc.paragraphs`**: List of all paragraphs in the Word doc
- **`para.text.strip()`**: Get text and remove whitespace

### CSVLoader

```python
class CSVLoader(BaseLoader):
    """Loader for CSV files, converting tabular data to contextual text."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # Reads CSV with headers as keys
                headers = reader.fieldnames  # Get column names
                
                text_rows = []
                row_count = 0
                for row in reader:  # Each row is a dictionary
                    # Convert: {"Name": "John", "Age": "25"} → "Name: John, Age: 25"
                    row_text = ', '.join([f"{col}: {val}" for col, val in row.items() if val])
                    text_rows.append(row_text)
                    row_count += 1
                
                text = '\n'.join(text_rows)  # One row per line
```

**Example CSV conversion:**
```
Name,Age,City
John,25,NYC
Jane,30,LA
```
Becomes:
```
Name: John, Age: 25, City: NYC
Name: Jane, Age: 30, City: LA
```

### FileLoaderFactory (Factory Pattern)

```python
class FileLoaderFactory:
    """Factory class to route files to appropriate loaders."""
    
    # Mapping of file extensions to loader classes
    LOADERS = {
        '.pdf': PDFLoader,
        '.txt': TextLoader,
        '.md': TextLoader,    # Markdown uses same loader as txt
        '.docx': DocxLoader,
        '.csv': CSVLoader
    }
```

**Factory Pattern**: Creates objects without specifying the exact class.

```python
    @classmethod
    def get_loader(cls, file_name: str) -> BaseLoader:
        """Get the appropriate loader for a file based on its extension."""
        ext = os.path.splitext(file_name)[1].lower()  # Get extension, lowercase
        # os.path.splitext("document.PDF") → ("document", ".PDF")
        # [1] gets ".PDF", .lower() makes it ".pdf"
        
        if ext not in cls.LOADERS:
            raise ValueError(f"Unsupported file type: {ext}")
        
        loader_class = cls.LOADERS[ext]  # Get the class (not instance)
        return loader_class()  # Create and return instance
```

```python
    @classmethod
    def load_file(cls, file_path: str, file_name: str) -> Dict[str, Any]:
        """Convenience method to load a file using the appropriate loader."""
        loader = cls.get_loader(file_name)  # Get correct loader
        return loader.load(file_path, file_name)  # Use it to load file
```

**Usage:**
```python
# No need to know which loader to use!
document = FileLoaderFactory.load_file("report.pdf", "report.pdf")
# Automatically uses PDFLoader
```

---

## 4. modules/text_processor.py - Text Chunking

This module splits documents into smaller pieces for better retrieval.

### TextChunker Class

```python
class TextChunker:
    """Splits text into overlapping chunks for better retrieval."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the text chunker.
        """
        # Use provided values or fall back to config defaults
        self.chunk_size = chunk_size or config.CHUNK_SIZE      # 500
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP  # 50
```

### Main Chunking Method

```python
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks while preserving metadata."""
        
        if not text or not text.strip():  # Handle empty text
            return []
        
        chunks = []           # Will hold all our chunks
        text_length = len(text)  # Total characters
        start = 0             # Current position in text
        chunk_id = 0          # Unique ID for each chunk
```

```python
        while start < text_length:  # Keep going until we've processed all text
            # Calculate end position
            end = start + self.chunk_size  # 500 characters later
```

### Smart Boundary Detection

```python
            # If not the last chunk, try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence endings
                sentence_endings = ['. ', '! ', '? ', '\n\n']
                best_break = end
                
                # Search backwards from end position for a good break point
                search_range = min(100, self.chunk_size // 4)  # Search last 25%
                
                for i in range(end, max(start, end - search_range), -1):
                    # Loop backwards from end
                    for ending in sentence_endings:
                        if text[i:i+len(ending)] == ending:
                            # Found a sentence ending!
                            best_break = i + len(ending)  # End after the punctuation
                            break
                    if best_break != end:
                        break  # Stop searching if we found a break
                
                end = best_break
```

**Example:**
```
Original text: "The quick brown fox jumps over the lazy dog. The cat sleeps peacefully."
                                                   ↑
                                      If chunk_size ends here, we search backwards
                                      and find ". " at position 44
                                      New end = 45 (after the period + space)
```

### Create Chunk with Metadata

```python
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                # Create chunk metadata - copy original and add chunk-specific info
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = chunk_id
                chunk_metadata['chunk_start'] = start
                chunk_metadata['chunk_end'] = end
                chunk_metadata['chunk_size'] = len(chunk_text)
                
                # For PDFs, estimate which page this chunk is on
                if metadata.get('file_type') == 'pdf' and 'pages' in metadata:
                    chunk_metadata['estimated_page'] = self._estimate_page(
                        start, end, text_length, metadata['total_pages']
                    )
                
                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata
                })
                
                chunk_id += 1
```

### Move to Next Chunk (with Overlap)

```python
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            # Example: end=500, overlap=50 → new start=450
            # So next chunk starts at 450, overlapping 50 chars with previous
            
            # Prevent infinite loop (if no progress made)
            if start <= end - self.chunk_size:
                start = end
        
        return chunks
```

### Page Estimation

```python
    def _estimate_page(self, start: int, end: int, total_length: int, total_pages: int) -> int:
        """Estimate which page a chunk belongs to based on character position."""
        # Use midpoint of chunk for estimation
        midpoint = (start + end) / 2
        # If we're 60% through the text and have 10 pages, we're around page 6
        estimated_page = int((midpoint / total_length) * total_pages) + 1
        return min(estimated_page, total_pages)  # Don't exceed total pages
```

**Example:**
- Document has 10,000 characters and 10 pages
- Chunk starts at 5,000, ends at 5,500
- Midpoint = 5,250
- Position ratio = 5250 / 10000 = 0.525 (52.5% through)
- Estimated page = 0.525 * 10 + 1 = 6.25 → page 6

---

## 5. modules/vector_store.py - FAISS Vector Database

This module handles storing and searching embeddings.

### Initialization

```python
class VectorStore:
    """FAISS-based vector database for document chunks."""
    
    def __init__(self, dimension: int = None):
        self.dimension = dimension or config.EMBEDDING_DIMENSION  # 384
        
        # Create FAISS index with L2 (Euclidean) distance
        self.index = faiss.IndexFlatL2(self.dimension)
        # IndexFlatL2: Flat (brute-force) index using L2 distance
        # 384: The dimension of our embedding vectors
        
        self.chunks = []       # Parallel list to store chunk texts
        self.metadata = []     # Parallel list to store chunk metadata
        self.document_files = set()  # Track unique document files (no duplicates)
```

**Parallel Arrays Concept:**
```
index position:     0           1           2
self.index:      [vec0]      [vec1]      [vec2]    ← FAISS stores vectors
self.chunks:     ["text0"]   ["text1"]   ["text2"] ← We store texts
self.metadata:   [{meta0}]   [{meta1}]   [{meta2}] ← We store metadata

When FAISS returns index 1, we use it to get chunks[1] and metadata[1]
```

### Adding Documents

```python
    def add_documents(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """Add document chunks and their embeddings to the vector store."""
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match embeddings")
        
        # FAISS requires float32 data type
        embeddings = embeddings.astype('float32')
        
        # Add vectors to FAISS index
        self.index.add(embeddings)
        
        # Store texts and metadata (parallel to FAISS index)
        for chunk in chunks:
            self.chunks.append(chunk['text'])
            self.metadata.append(chunk['metadata'])
            self.document_files.add(chunk['metadata']['file_name'])  # Track unique files
```

### Similarity Search

```python
    def search(self, query_embedding: np.ndarray, k: int = None) -> List[Dict[str, Any]]:
        """Search for top-k most similar chunks to the query embedding."""
        
        k = k or config.TOP_K_RETRIEVAL  # Default: 5
        
        if self.index.ntotal == 0:  # No documents indexed
            return []
        
        # Reshape to 2D array (1 query, 384 dimensions) and ensure float32
        query_embedding = query_embedding.astype('float32').reshape(1, -1)
        # reshape(1, -1): Makes shape (384,) become (1, 384)
        
        # FAISS search returns distances and indices
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        # distances: [[0.5, 0.8, 1.2, ...]] - L2 distances (lower = more similar)
        # indices: [[42, 17, 5, ...]] - Position in our arrays
```

### Converting Distance to Similarity Score

```python
        # Convert distances to similarity scores
        # L2 distance: lower = more similar, but we want higher = more similar
        # Using negative exponential: similarity = e^(-distance)
        similarities = np.exp(-distances[0])
        # If distance = 0 → similarity = e^0 = 1.0 (perfect match)
        # If distance = 1 → similarity = e^-1 = 0.37
        # If distance = 2 → similarity = e^-2 = 0.14
```

### Building Results

```python
        results = []
        for idx, similarity in zip(indices[0], similarities):
            # Only include results above threshold
            if similarity >= config.SIMILARITY_THRESHOLD:  # 0.3
                results.append({
                    'text': self.chunks[idx],     # Get text using FAISS index
                    'metadata': self.metadata[idx],  # Get metadata
                    'score': float(similarity)       # Include relevance score
                })
        
        return results
```

### Persistence (Save/Load)

```python
    def save_to_disk(self, path: str = None):
        """Save the vector store to disk."""
        path = path or config.VECTOR_STORE_DIR
        os.makedirs(path, exist_ok=True)  # Create directory if needed
        
        # Save FAISS index (binary format)
        index_path = os.path.join(path, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        
        # Save our parallel arrays using pickle
        data_path = os.path.join(path, "chunks_metadata.pkl")
        with open(data_path, 'wb') as f:  # 'wb' = write binary
            pickle.dump({
                'chunks': self.chunks,
                'metadata': self.metadata,
                'document_files': self.document_files,
                'dimension': self.dimension
            }, f)
```

```python
    def load_from_disk(self, path: str = None) -> bool:
        """Load the vector store from disk."""
        path = path or config.VECTOR_STORE_DIR
        
        index_path = os.path.join(path, "faiss_index.bin")
        data_path = os.path.join(path, "chunks_metadata.pkl")
        
        # Check if both files exist
        if not os.path.exists(index_path) or not os.path.exists(data_path):
            return False  # Nothing to load
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load our data
            with open(data_path, 'rb') as f:  # 'rb' = read binary
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.metadata = data['metadata']
                self.document_files = data['document_files']
                self.dimension = data['dimension']
            
            return True  # Success
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
```

### Utility Methods

```python
    def clear(self):
        """Clear all data from the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)  # Create fresh index
        self.chunks = []
        self.metadata = []
        self.document_files = set()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_chunks': self.index.ntotal,  # Number of vectors in FAISS
            'total_documents': len(self.document_files),
            'document_files': sorted(list(self.document_files)),
            'dimension': self.dimension
        }
    
    def is_empty(self) -> bool:
        """Check if the vector store is empty."""
        return self.index.ntotal == 0
```

---

## 6. modules/rag_pipeline.py - Main RAG Pipeline

This is the **brain** of the application - orchestrates everything.

### Initialization

```python
class RAGPipeline:
    """Complete RAG pipeline for document Q&A."""
    
    def __init__(self):
        """Initialize the RAG pipeline with models and vector store."""
        
        # Check if GPU is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Initializing RAG Pipeline on {self.device.upper()}...")
```

### Loading the Embedding Model

```python
        # Load embedding model (sentence-transformers)
        print(f"📥 Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_model.to(self.device)  # Move to GPU if available
```

- **SentenceTransformer**: Library for text embeddings
- **`.to(self.device)`**: Moves model to GPU (faster) or keeps on CPU

### Loading the LLM

```python
        # Load LLM for generation (Flan-T5)
        print(f"📥 Loading LLM: {config.LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL)
        self.llm = AutoModelForSeq2SeqLM.from_pretrained(config.LLM_MODEL)
        self.llm.to(self.device)
```

- **Tokenizer**: Converts text → numbers (tokens) that the model understands
- **AutoModelForSeq2SeqLM**: Automatically loads the right model type
- **Seq2Seq**: Sequence-to-sequence (encoder-decoder architecture)

### Initialize Components

```python
        # Initialize our custom components
        self.text_chunker = TextChunker()
        self.vector_store = VectorStore()
        
        # Try to load existing vector store from disk
        if self.vector_store.load_from_disk():
            print(f"✅ Loaded existing vector store with {self.vector_store.get_stats()['total_chunks']} chunks")
        else:
            print("📝 Starting with empty vector store")
```

### Processing Uploaded Files

```python
    def process_uploaded_files(self, uploaded_files: List[Any]) -> Dict[str, Any]:
        """Process uploaded files and add them to the vector store."""
        
        results = {
            'success': True,
            'files_processed': 0,
            'total_chunks': 0,
            'errors': [],
            'file_details': []
        }
        
        # Get list of already indexed files to avoid duplicates
        existing_files = self.vector_store.get_stats()['document_files']
        
        all_chunks = []  # Collect all chunks from all files
```

### Process Each File

```python
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            # Skip if already indexed
            if file_name in existing_files:
                results['errors'].append(f"{file_name} is already indexed")
                continue
            
            try:
                # Save file to disk temporarily
                temp_path = os.path.join(config.UPLOADED_FILES_DIR, file_name)
                os.makedirs(config.UPLOADED_FILES_DIR, exist_ok=True)
                
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())  # Streamlit file → bytes → disk
                
                # Load and extract text using our factory
                document = FileLoaderFactory.load_file(temp_path, file_name)
                
                # Chunk the document
                chunks = self.text_chunker.chunk_text(document['text'], document['metadata'])
                
                all_chunks.extend(chunks)  # Add to our collection
                
                results['file_details'].append({
                    'file_name': file_name,
                    'chunks': len(chunks),
                    'type': document['metadata']['file_type']
                })
                results['files_processed'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error processing {file_name}: {str(e)}")
                results['success'] = False
```

### Generate Embeddings and Store

```python
        if all_chunks:
            # Extract just the text from chunks
            chunk_texts = [chunk['text'] for chunk in all_chunks]
            
            # Generate embeddings for all chunks at once (batched for efficiency)
            embeddings = self.embedding_model.encode(
                chunk_texts,
                show_progress_bar=True,     # Show progress
                convert_to_numpy=True       # Return numpy array
            )
            # embeddings shape: (num_chunks, 384)
            
            # Add to vector store
            self.vector_store.add_documents(all_chunks, embeddings)
            results['total_chunks'] = len(all_chunks)
            
            # Save to disk for persistence
            self.vector_store.save_to_disk()
```

### Answer Generation

```python
    def generate_answer(
        self, 
        question: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate an answer to a question using RAG."""
        
        # Check if we have documents
        if self.vector_store.is_empty():
            return {
                'answer': "⚠️ No documents have been uploaded yet!",
                'sources': [],
                'context_used': False
            }
```

### Step 1: Embed the Question

```python
        # Convert question to embedding (same model as documents)
        question_embedding = self.embedding_model.encode(
            question,
            convert_to_numpy=True
        )
        # Shape: (384,)
```

### Step 2: Retrieve Relevant Chunks

```python
        # Search for similar chunks
        retrieved_chunks = self.vector_store.search(question_embedding)
        # Returns top-5 most similar chunks with scores
        
        if not retrieved_chunks:
            return {
                'answer': "I couldn't find any relevant information...",
                'sources': [],
                'context_used': False
            }
```

### Step 3: Build Context

```python
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            
            # Create source label: "[Source 1: report.pdf, page 3]"
            source_info = f"[Source {i}: {metadata['file_name']}"
            if metadata.get('file_type') == 'pdf' and 'estimated_page' in metadata:
                source_info += f", page {metadata['estimated_page']}"
            source_info += "]"
            
            # Combine label with chunk text
            context_parts.append(f"{source_info}\n{chunk['text']}")
        
        return "\n\n".join(context_parts)
```

**Example context:**
```
[Source 1: report.pdf, page 3]
The company reported a 15% increase in revenue...

[Source 2: report.pdf, page 5]
Operating expenses were reduced by 10%...
```

### Step 4: Build Prompt

```python
    def _build_prompt(self, question: str, context: str, chat_history=None) -> str:
        """Build the prompt for the LLM (T5-optimized format)."""
        
        prompt_parts = []
        
        # Add context first (T5 works better with context before question)
        prompt_parts.append("Context:")
        prompt_parts.append(context)
        prompt_parts.append("")  # Empty line
        
        # Add question
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("")
        
        # Instruction for the model
        prompt_parts.append("Provide a comprehensive and complete answer based on the context above:")
        
        return "\n".join(prompt_parts)
```

### Step 5: Generate with LLM

```python
    def _generate_with_llm(self, prompt: str) -> str:
        """Generate answer using the LLM."""
        
        # Tokenize the prompt
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",   # Return PyTorch tensors
            max_length=1024,       # Truncate if too long
            truncation=True,
            padding=True
        ).to(self.device)  # Move to GPU if available
```

```python
        # Generate answer
        outputs = self.llm.generate(
            inputs["input_ids"],          # The tokenized input
            attention_mask=inputs["attention_mask"],  # Which tokens to attend to
            max_length=600,               # Max output length
            min_length=60,                # Force at least this many tokens
            num_beams=5,                  # Beam search (explores 5 paths)
            length_penalty=2.0,           # Favor longer answers
            no_repeat_ngram_size=3,       # Don't repeat 3-grams
            early_stopping=True           # Stop when all beams finish
        )
```

**Generation Parameters Explained:**
- **num_beams=5**: Explores 5 different generation paths, picks best
- **length_penalty=2.0**: Score = log_prob / length^2.0 (rewards longer)
- **no_repeat_ngram_size=3**: Prevents "the the the" repetitions

```python
        # Decode tokens back to text
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # outputs[0] is the generated token IDs
        # skip_special_tokens removes things like <pad>, </s>
        
        # Ensure answer ends with punctuation
        if answer and not answer.endswith(('.', '!', '?')):
            last_period = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
            if last_period > len(answer) // 2:
                answer = answer[:last_period + 1]  # Cut to last sentence
        
        return answer.strip()
```

### Source Extraction

```python
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from retrieved chunks."""
        sources = []
        seen_sources = set()  # Avoid duplicate sources
        
        for chunk in chunks:
            metadata = chunk['metadata']
            file_name = metadata['file_name']
            file_type = metadata.get('file_type', 'unknown')
            
            # Build unique identifier
            source_id = file_name
            if file_type == 'pdf' and 'estimated_page' in metadata:
                page = metadata['estimated_page']
                source_id += f"_page_{page}"
                source_detail = f"Page {page}"
            elif file_type in ['txt', 'md']:
                source_detail = f"Line ~{metadata.get('chunk_start', 0)}"
            else:
                source_detail = "Document section"
            
            # Only add if not seen before
            if source_id not in seen_sources:
                sources.append({
                    'file_name': file_name,
                    'file_type': file_type,
                    'detail': source_detail,
                    'score': chunk['score']
                })
                seen_sources.add(source_id)
        
        return sources
```

---

## 7. modules/multimodal_rag.py - Image + Text Support

Extends RAGPipeline to handle images.

### Class Definition (Inheritance)

```python
class MultiModalRAG(RAGPipeline):
    """
    Multi-modal RAG pipeline that handles both text and images.
    Inherits from standard RAGPipeline to keep existing functionality.
    """
    
    def __init__(self):
        # Initialize parent class (all text RAG functionality)
        super().__init__()
        # super().__init__() calls RAGPipeline.__init__()
```

### Load CLIP Model

```python
        print("🖼️ Initializing Multi-modal components...")
        
        # Load CLIP model for image-text matching
        self.clip_model_name = "clip-ViT-B-32"
        print(f"📥 Loading CLIP model: {self.clip_model_name}")
        self.clip_model = SentenceTransformer(self.clip_model_name)
        self.clip_model.to(self.device)
        
        # Store for image embeddings
        self.image_store = []
        # Structure: [{'embedding': tensor, 'image': PIL.Image, 'metadata': dict}]
        
        print("✅ Multi-modal RAG ready!")
```

**CLIP (Contrastive Language-Image Pre-training):**
- Creates embeddings for BOTH images AND text
- Text query can find relevant images (same embedding space)

### Processing Files (Override)

```python
    def process_uploaded_files(self, uploaded_files: List[Any]) -> Dict[str, Any]:
        """Process files for BOTH text (via super) and images."""
        
        # 1. Run standard text processing first (inherited method)
        print("📝 Processing text content...")
        results = super().process_uploaded_files(uploaded_files)
        
        # 2. Process images from PDFs
        print("🖼️ Extracting images from documents...")
        images_found = 0
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_path = os.path.join(config.UPLOADED_FILES_DIR, file_name)
            
            # Only PDFs contain embedded images
            if file_name.lower().endswith('.pdf'):
                extracted_images = self._extract_images_from_pdf(file_path, file_name)
                
                # Generate CLIP embeddings for each image
                for img_data in extracted_images:
                    embedding = self.clip_model.encode(img_data['image'], convert_to_tensor=True)
                    
                    self.image_store.append({
                        'embedding': embedding,
                        'image': img_data['image'],  # PIL Image object
                        'metadata': img_data['metadata']
                    })
                
                images_found += len(extracted_images)
        
        results['images_processed'] = images_found
        return results
```

### Extracting Images from PDF

```python
    def _extract_images_from_pdf(self, pdf_path: str, file_name: str) -> List[Dict]:
        """Extract images from PDF pages using PyMuPDF."""
        images = []
        
        try:
            doc = fitz.open(pdf_path)  # PyMuPDF opens PDF
            
            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)  # Get all images on page
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]  # Reference ID for the image
                    base_image = doc.extract_image(xref)  # Extract image data
                    image_bytes = base_image["image"]  # Raw bytes
                    
                    # Filter small images (likely icons/logos)
                    if len(image_bytes) < 2000:  # < 2KB
                        continue
                    
                    try:
                        # Convert bytes to PIL Image
                        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                        
                        # Skip very small dimensions
                        if pil_image.width < 100 or pil_image.height < 100:
                            continue
                        
                        images.append({
                            'image': pil_image,
                            'metadata': {
                                'source': file_name,
                                'page': page_num + 1,
                                'type': 'image'
                            }
                        })
                    except Exception as e:
                        print(f"⚠️ Failed to process image on page {page_num}: {e}")
                        
        except Exception as e:
            print(f"❌ Error extracting images from {file_name}: {e}")
        
        return images
```

### Image Retrieval

```python
    def _retrieve_images(self, query: str, top_k: int = 2) -> List[Dict]:
        """Find images matching the text query using CLIP."""
        
        if not self.image_store:
            return []
        
        # Embed query text using CLIP (same space as images!)
        query_embedding = self.clip_model.encode(query, convert_to_tensor=True)
        
        # Stack all image embeddings into a matrix
        image_embeddings = torch.stack([item['embedding'] for item in self.image_store])
        
        # Calculate cosine similarity between query and all images
        cos_scores = util.cos_sim(query_embedding, image_embeddings)[0]
        # cos_sim returns a matrix, [0] gets the first (only) row
        
        # Get top k results
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.image_store)))
        # Returns (values, indices) of top k elements
        
        retrieved_images = []
        for score, idx in zip(top_results[0], top_results[1]):
            if score > 0.25:  # Similarity threshold for images
                item = self.image_store[idx]
                retrieved_images.append({
                    'image': item['image'],
                    'metadata': item['metadata'],
                    'score': float(score)
                })
        
        return retrieved_images
```

---

## 8. app.py - Streamlit Web Application

The user interface.

### Imports and Setup

```python
import streamlit as st  # Web framework
import os
import json
from datetime import datetime
from typing import List
import config

# Try to import MultiModalRAG, fallback to regular RAG if not available
try:
    from modules.multimodal_rag import MultiModalRAG
    USE_MULTIMODAL = True
except:
    from modules.rag_pipeline import RAGPipeline
    USE_MULTIMODAL = False
```

### Page Configuration

```python
st.set_page_config(
    page_title=config.APP_TITLE,      # Browser tab title
    page_icon=config.APP_ICON,         # 💬 in browser tab
    layout="wide",                     # Use full width
    initial_sidebar_state="expanded"   # Sidebar open by default
)
```

### Custom CSS

```python
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
        }
        /* ... more styles ... */
    </style>
""", unsafe_allow_html=True)
# unsafe_allow_html=True allows raw HTML/CSS
```

### Session State Initialization

```python
def initialize_session_state():
    """Initialize Streamlit session state variables."""
    
    # Session state persists across reruns
    if 'rag_pipeline' not in st.session_state:
        with st.spinner("🚀 Initializing AI models..."):
            if USE_MULTIMODAL:
                st.session_state.rag_pipeline = MultiModalRAG()
            else:
                st.session_state.rag_pipeline = RAGPipeline()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'uploaded_file_names' not in st.session_state:
        st.session_state.uploaded_file_names = set()
    
    if 'document_summaries' not in st.session_state:
        st.session_state.document_summaries = {}
```

**Streamlit Session State:**
- Streamlit reruns the entire script on every interaction
- `st.session_state` persists data between reruns
- Without it, models would reload on every click!

### Sidebar Controls

```python
def sidebar_controls():
    """Render sidebar with file upload and controls."""
    
    with st.sidebar:  # Everything inside goes to sidebar
        st.header("📁 Document Management")
        
        # File uploader widget
        uploaded_files = st.file_uploader(
            "Upload your documents",
            type=['pdf', 'txt', 'md', 'docx', 'csv'],  # Allowed types
            accept_multiple_files=True,  # Can upload many at once
            help="Supported formats: PDF, TXT, MD, DOCX, CSV"
        )
```

### Processing Uploads

```python
        if uploaded_files:
            # Find newly uploaded files (not already processed)
            new_files = [f for f in uploaded_files 
                        if f.name not in st.session_state.uploaded_file_names]
            
            if new_files:
                with st.spinner("Processing documents..."):
                    status_placeholder = st.empty()  # Placeholder for status updates
                    status_placeholder.info(config.STATUS_EXTRACTING)
                    
                    # Process files through RAG pipeline
                    results = st.session_state.rag_pipeline.process_uploaded_files(new_files)
                    
                    if results['success'] or results['files_processed'] > 0:
                        status_placeholder.success(config.STATUS_READY)
                        
                        # Track uploaded files
                        for f in new_files:
                            st.session_state.uploaded_file_names.add(f.name)
                        
                        # Show success message
                        st.success(f"✅ Processed {results['files_processed']} file(s)")
```

### Chat Display

```python
def display_chat():
    """Display the chat interface."""
    
    # Display all previous messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):  # "user" or "assistant"
            st.markdown(message["content"])
            
            # Show images if available (multimodal)
            if message["role"] == "assistant" and "images" in message:
                st.markdown("### 🖼️ Relevant Images:")
                cols = st.columns(min(len(message["images"]), 3))  # Max 3 columns
                for idx, img_data in enumerate(message["images"][:3]):
                    with cols[idx]:
                        st.image(img_data['image'])
                        st.caption(f"Page {img_data['metadata']['page']}")
            
            # Show sources
            if message["role"] == "assistant" and "sources" in message:
                display_sources(message["sources"])
```

### Chat Input and Response

```python
    # Chat input at bottom of page
    if prompt := st.chat_input("Ask a question about your documents..."):
        # := is walrus operator: assigns AND checks if truthy
        
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            answer_placeholder = st.empty()  # For streaming effect
            
            full_answer = ""
            sources = []
            
            # Stream the answer token by token
            for chunk in st.session_state.rag_pipeline.generate_answer_stream(
                question=prompt,
                chat_history=st.session_state.chat_history[:-1]  # Exclude current question
            ):
                if chunk.get('type') == 'token':
                    full_answer += chunk['content']
                    answer_placeholder.markdown(full_answer + "▌")  # Cursor effect
                elif chunk.get('type') == 'done':
                    answer_placeholder.markdown(full_answer)
                    sources = chunk.get("sources", [])
            
            # Show sources
            if sources:
                display_sources(sources)
            
            # Save to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_answer,
                "sources": sources
            })
```

### Main Function

```python
def main():
    """Main application function."""
    
    # Initialize session state (models, history, etc.)
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Sidebar with upload and controls
    sidebar_controls()
    
    # Main area
    st.markdown("---")  # Horizontal line
    
    # Check if documents are loaded
    stats = st.session_state.rag_pipeline.get_stats()
    
    if stats['total_chunks'] == 0:
        st.info("👈 Please upload some documents using the sidebar!")
    else:
        display_chat()


if __name__ == "__main__":
    main()
```

---

## 9. requirements.txt - Dependencies

This file tells pip which packages to install.

```text
# ============================================================================
# Universal Document Chat - Complete Requirements
# Includes: Base RAG + Multi-modal (Image) Support
# ============================================================================
```
**Comments** starting with `#` are ignored by pip but help humans understand the file.

### Core ML/AI Libraries

```text
torch>=2.0.0
```
- **What it is**: PyTorch - the deep learning framework
- **>=2.0.0**: Version 2.0.0 or higher
- **Why needed**: Powers the neural networks (embedding model, LLM)
- **Size**: ~2GB (this is the largest dependency)

```text
transformers>=4.30.0
```
- **What it is**: HuggingFace Transformers library
- **Why needed**: Loads pre-trained models (Flan-T5)
- **Provides**: `AutoTokenizer`, `AutoModelForSeq2SeqLM`

```text
sentence-transformers>=2.2.2
```
- **What it is**: Library for text embeddings
- **Why needed**: Creates 384-dimensional vectors from text
- **Provides**: `SentenceTransformer` class

```text
accelerate>=0.26.0
```
- **What it is**: HuggingFace Accelerate library
- **Why needed**: Speeds up model loading and inference
- **Benefit**: Optimizes memory usage, enables GPU acceleration

### Vector Store & Embeddings

```text
numpy>=1.24.0
```
- **What it is**: Numerical Python library
- **Why needed**: Array operations for embeddings
- **Used for**: Reshaping, type conversion, math operations

```text
faiss-cpu>=1.7.4
```
- **What it is**: Facebook AI Similarity Search (CPU version)
- **Why needed**: Fast vector similarity search
- **Note**: Use `faiss-gpu` if you have NVIDIA GPU

### Document Processing

```text
pypdf>=3.0.0
```
- **What it is**: PDF reading library (alternative to pdfplumber)
- **Why included**: Backup PDF support
- **Note**: Project mainly uses pdfplumber

```text
python-docx>=0.8.11
```
- **What it is**: Microsoft Word document reader
- **Why needed**: Extract text from .docx files
- **Provides**: `Document` class

```text
python-markdown>=3.4.0
```
- **What it is**: Markdown parser
- **Why included**: For markdown file processing
- **Note**: Actually just read as plain text in this project

### Multi-modal Support (Images)

```text
pymupdf>=1.23.0
```
- **What it is**: PyMuPDF library (imported as `fitz`)
- **Why needed**: Extract images from PDF files
- **Provides**: PDF parsing, image extraction

```text
Pillow>=10.0.0
```
- **What it is**: Python Imaging Library fork
- **Why needed**: Image processing and manipulation
- **Used for**: Converting image bytes to PIL Image objects

### Web Application

```text
streamlit>=1.28.0
```
- **What it is**: Web app framework for data science
- **Why needed**: Creates the entire user interface
- **Provides**: Widgets, chat UI, file upload, session state

### Data Processing

```text
pandas>=2.0.0
```
- **What it is**: Data manipulation library
- **Why needed**: CSV file handling
- **Note**: Could use built-in csv module instead (lighter)

### Utilities

```text
tqdm>=4.65.0
```
- **What it is**: Progress bar library
- **Why needed**: Shows progress during embedding generation
- **Used by**: sentence-transformers internally

### How to Use This File

```bash
# Install all dependencies at once
pip install -r requirements.txt

# Install a specific package
pip install torch>=2.0.0

# Upgrade all packages
pip install --upgrade -r requirements.txt
```

---

## 10. fix_cache.py - Cache Clearing Utility

This script clears caches and verifies features are working.

### Full Code with Explanation

```python
# URGENT FIX - Run this to clear cache and restart properly
```
Comment explaining the script's purpose.

```python
import os
import shutil
import subprocess
import sys
```

| Import | Purpose |
|--------|---------|
| `os` | File path operations |
| `shutil` | Delete directories (`rmtree`) |
| `subprocess` | Run shell commands |
| `sys` | System-level operations |

```python
print("🔧 Universal Document Chat - Cache Clear & Restart")
print("=" * 60)
```
Header message. `"=" * 60` creates 60 equal signs for a line.

### Step 1: Clear Streamlit Cache

```python
cache_dir = os.path.expanduser("~/.streamlit")
```
- **`os.path.expanduser("~")`**: Expands `~` to user's home directory
- **Windows**: `C:\Users\YourName\.streamlit`
- **Linux/Mac**: `/home/yourname/.streamlit`

```python
if os.path.exists(cache_dir):
    try:
        shutil.rmtree(cache_dir)  # Delete directory and all contents
        print("✅ Cleared Streamlit cache")
    except:
        print("⚠️  Could not clear cache (may not exist)")
else:
    print("ℹ️  No cache to clear")
```
- **`shutil.rmtree()`**: Recursively deletes a directory
- **try/except**: Handle errors gracefully

### Step 2: Clear Python Cache

```python
pycache_dirs = []
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        pycache_dirs.append(os.path.join(root, "__pycache__"))
```
- **`os.walk(".")`**: Walks through all subdirectories starting from current (`.`)
- **Yields**: (root_path, directory_names, file_names)
- **Finds**: All `__pycache__` folders (Python bytecode cache)

```python
for cache in pycache_dirs:
    try:
        shutil.rmtree(cache)
        print(f"✅ Cleared {cache}")
    except:
        pass  # Ignore errors, continue with next
```

### Step 3: Verify Features

```python
print("\n🔍 Verifying features in code...")

with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()
```
Reads the entire app.py file into a string.

```python
features_check = {
    "Streaming": "generate_answer_stream" in app_content,
    "Export": "Download Chat History" in app_content,
    "Summaries": "Document Summaries" in app_content,
    "Auto-save": "save_chat_history()" in app_content
}
```
- **Dictionary comprehension**: Maps feature names to True/False
- **`"text" in string`**: Checks if substring exists in string

```python
all_good = True
for feature, exists in features_check.items():
    status = "✅" if exists else "❌"
    print(f"{status} {feature}: {'Found' if exists else 'MISSING'}")
    if not exists:
        all_good = False
```
- **`dict.items()`**: Returns (key, value) pairs
- **Ternary operator**: `a if condition else b`

### Final Output

```python
if all_good:
    print("✅ ALL FEATURES VERIFIED IN CODE!")
    print("\n📋 Next steps:")
    print("1. Close your browser completely")
    print("2. Stop Streamlit (Ctrl+C in terminal)")
    print("3. Run: streamlit run app.py --server.runOnSave=false")
    print("4. Open fresh browser window")
else:
    print("❌ SOME FEATURES MISSING - Code may be corrupted")
```

### How to Run

```bash
python fix_cache.py
```

---

## 11. install_deps.py - Quick Install Script

A simple script to install dependencies one by one.

### Full Code with Explanation

```python
# Quick Install Script - Run this with: .\venv\Scripts\python.exe install_deps.py
```
Comment showing how to run this script.

```python
import subprocess
import sys
```

| Import | Purpose |
|--------|---------|
| `subprocess` | Run external commands |
| `sys` | Access to Python executable path |

### Install Function

```python
def install(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
```

**Breakdown:**
- **`sys.executable`**: Path to current Python interpreter (e.g., `.\venv\Scripts\python.exe`)
- **`"-m", "pip"`**: Run pip as a module
- **`"install", package`**: The pip install command
- **`subprocess.check_call()`**: Runs command and raises error if it fails

**Why use `sys.executable` instead of `"python"`?**
- Ensures we use the SAME Python that ran this script
- Works correctly inside virtual environments
- Avoids PATH issues

### Package List

```python
packages = [
    "numpy",
    "torch --index-url https://download.pytorch.org/whl/cpu",  # CPU version
    "streamlit",
    "transformers",
    "sentence-transformers",
    "faiss-cpu",
    "pdfplumber",
]
```

**Special note about torch:**
```python
"torch --index-url https://download.pytorch.org/whl/cpu"
```
- **`--index-url`**: Specifies where to download from
- **`whl/cpu`**: CPU-only version (smaller, ~700MB instead of 2GB)
- **GPU users**: Would use `whl/cu118` or similar for CUDA support

### Installation Loop

```python
for pkg in packages:
    try:
        print(f"\n✅ Installing {pkg.split()[0]}...")
        install(pkg)
    except Exception as e:
        print(f"❌ Failed to install {pkg}: {e}")
        print("Continuing with next package...")
```

- **`pkg.split()[0]`**: Gets first word (e.g., "torch" from "torch --index-url...")
- **try/except**: Continues even if one package fails

### How to Run

```bash
# From project directory with venv activated:
python install_deps.py

# Or without activating venv:
.\venv\Scripts\python.exe install_deps.py
```

---

## 12. generate_samples.py - Sample Document Generator

Creates sample PDF and DOCX files for testing the application.

### Imports

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
```
- **`Document`**: Creates Word documents
- **`Inches, Pt`**: Unit conversions (inches, points)
- **`WD_ALIGN_PARAGRAPH`**: Text alignment enum

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
```
- **ReportLab**: PDF generation library
- **`platypus`**: Page Layout and Typography Using Scripts

### create_sample_docx Function

```python
def create_sample_docx():
    """Create a sample DOCX file."""
    doc = Document()  # Create new empty Word document
```

```python
    # Title
    title = doc.add_heading('Python Programming Guide', 0)
    # 0 = Title style, 1-9 = Heading levels
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER  # Center align
```

```python
    # Introduction paragraph
    doc.add_heading('Introduction', level=1)  # Heading 1
    intro = doc.add_paragraph(
        'Python is a high-level, interpreted programming language...'
    )
```

```python
    # Bullet list
    doc.add_paragraph('Easy to Learn', style='List Bullet')
    doc.add_paragraph('Versatile and Powerful', style='List Bullet')
```
- **`style='List Bullet'`**: Creates a bulleted list item

```python
    # Save the document
    output_path = os.path.join('examples', 'sample.docx')
    doc.save(output_path)
    print(f"✅ Created {output_path}")
```

### create_sample_pdf Function

```python
def create_sample_pdf():
    """Create a sample PDF file."""
    output_path = os.path.join('examples', 'sample.pdf')
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    # SimpleDocTemplate: Handles page layout automatically
    # letter: Standard US letter size (8.5" x 11")
```

```python
    story = []  # Container for all content
    # "Story" = sequence of flowable elements (paragraphs, spacers, etc.)
```

```python
    styles = getSampleStyleSheet()  # Get default styles
    
    # Create custom style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],  # Inherit from Heading1
        fontSize=24,
        textColor='#1f77b4',  # Blue color
        spaceAfter=30,  # Space after paragraph
        alignment=TA_CENTER  # Center aligned
    )
```

```python
    # Add content to story
    story.append(Paragraph("Artificial Intelligence Overview", title_style))
    story.append(Spacer(1, 0.2*inch))  # Vertical space
```
- **`Spacer(width, height)`**: Creates empty space
- **`0.2*inch`**: 0.2 inches of vertical space

```python
    story.append(PageBreak())  # Force new page
```

```python
    # Build the PDF
    doc.build(story)
    print(f"✅ Created {output_path}")
```
- **`build()`**: Renders all content and saves to file

### Main Execution

```python
if __name__ == "__main__":
    # Ensure examples directory exists
    os.makedirs('examples', exist_ok=True)
    
    print("📄 Generating sample documents...")
    
    try:
        create_sample_pdf()
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
    
    try:
        create_sample_docx()
    except Exception as e:
        print(f"❌ Error creating DOCX: {e}")
    
    print("✅ Done!")
```

- **`if __name__ == "__main__"`**: Only runs when script is executed directly
- **`os.makedirs(..., exist_ok=True)`**: Create directory, don't error if exists

### How to Run

```bash
pip install reportlab python-docx  # Install dependencies
python generate_samples.py
```

---

## 13. examples/ - Sample Documents

This folder contains sample documents for testing.

### sample.txt - Meeting Notes

```text
Meeting Notes - Q4 2024 Planning Session
Date: November 20, 2024
Attendees: Sarah Chen, Michael Rodriguez, Lisa Thompson, James Park

AGENDA
1. Review Q3 Performance
2. Q4 Goals and Objectives
...
```

**Purpose**: Test plain text file loading
**Format**: Simple meeting notes with sections

**When loaded, the app can answer:**
- "What was discussed in the Q4 planning session?"
- "What were the Q3 challenges?"
- "What is the Q4 budget?"

### sample.md - Machine Learning Guide

```markdown
# Introduction to Machine Learning

Machine learning (ML) is a subset of artificial intelligence...

## Types of Machine Learning

### 1. Supervised Learning
...
```

**Purpose**: Test Markdown file loading
**Format**: Structured document with headings

**When loaded, the app can answer:**
- "What is supervised learning?"
- "What are the applications of machine learning?"
- "Explain overfitting"

### sample.csv - Product Data

```csv
Product,Category,Price,Stock,Rating,Sales_Last_Month
Wireless Mouse,Electronics,29.99,150,4.5,342
Mechanical Keyboard,Electronics,89.99,85,4.8,156
...
```

**Purpose**: Test CSV file loading
**Converted to text as:**
```
Product: Wireless Mouse, Category: Electronics, Price: 29.99, Stock: 150, Rating: 4.5, Sales_Last_Month: 342
Product: Mechanical Keyboard, Category: Electronics, Price: 89.99, Stock: 85, Rating: 4.8, Sales_Last_Month: 156
```

**When loaded, the app can answer:**
- "What is the price of the Ergonomic Chair?"
- "Which product has the highest rating?"
- "What are the Electronics products?"

### sample.pdf - AI Overview

A multi-page PDF about Artificial Intelligence containing:
- What is AI
- Brief History
- Types of AI (Narrow, General, Super)
- Applications (Healthcare, Finance, Transportation, Education)
- Challenges and Ethics
- Future of AI

**Purpose**: Test PDF loading with page tracking

### sample.docx - Python Guide

A Word document about Python programming containing:
- Introduction
- Key Features
- Basic Syntax
- Data Types
- Applications
- Getting Started

**Purpose**: Test DOCX file loading

---

## 14. data/ - Application Data Storage

This folder stores persistent data created by the application.

### Structure

```
data/
├── chat_history/           # Saved conversations
│   ├── chat_20251122_220325.json
│   ├── chat_20251122_221206.json
│   └── ...
├── uploaded_files/         # Cached uploaded documents
│   ├── sample.csv
│   ├── sample.md
│   ├── sample.txt
│   └── DEPLOYMENT_GUIDE.md
└── vector_store/           # FAISS index and metadata
    ├── faiss_index.bin
    └── chunks_metadata.pkl
```

### chat_history/ - Saved Conversations

Each chat session is saved as a JSON file:

```json
{
  "timestamp": "20251122_220325",
  "messages": [
    {
      "role": "user",
      "content": "What is machine learning?"
    },
    {
      "role": "assistant",
      "content": "Machine learning is a subset of AI...",
      "sources": [
        {
          "file_name": "sample.md",
          "file_type": "md",
          "detail": "Line ~0",
          "score": 0.85
        }
      ]
    }
  ]
}
```

**Naming convention**: `chat_YYYYMMDD_HHMMSS.json`

### uploaded_files/ - Document Cache

Stores copies of uploaded files for:
1. **Persistence**: Don't lose files when app restarts
2. **Processing**: Loaders need file paths, not memory
3. **Reference**: Can re-process if needed

### vector_store/ - Embeddings Database

Two files store the entire searchable index:

**faiss_index.bin** (Binary)
- FAISS index containing all embedding vectors
- Format: Binary, not human-readable
- Size: ~1.5KB per 1000 chunks (with 384-dim embeddings)

**chunks_metadata.pkl** (Pickle)
- Python pickle file containing:
  ```python
  {
      'chunks': ["text of chunk 1", "text of chunk 2", ...],
      'metadata': [{'file_name': '...', 'chunk_id': 0, ...}, ...],
      'document_files': {'sample.txt', 'sample.md', ...},
      'dimension': 384
  }
  ```

**Why two files?**
- FAISS stores only vectors (fast search)
- We store texts/metadata separately (need to return them)
- Parallel arrays: `index[i]` corresponds to `chunks[i]` and `metadata[i]`

---

## 15. Complete Project Structure

```
E:\RAG PROJECT\
│
├── 📄 Core Application
│   ├── app.py                 # Main Streamlit application (476 lines)
│   ├── config.py              # Configuration settings (75 lines)
│   └── requirements.txt       # Python dependencies (32 lines)
│
├── 📁 modules/                # Core RAG components
│   ├── __init__.py           # Package initializer (6 lines)
│   ├── file_loader.py        # Document loaders (203 lines)
│   ├── text_processor.py     # Text chunking (133 lines)
│   ├── vector_store.py       # FAISS operations (174 lines)
│   ├── rag_pipeline.py       # Main RAG logic (446 lines)
│   └── multimodal_rag.py     # Image support (167 lines)
│
├── 📁 data/                   # Application data (created at runtime)
│   ├── chat_history/         # Saved conversations (JSON)
│   ├── uploaded_files/       # Cached documents
│   └── vector_store/         # FAISS index + metadata
│
├── 📁 examples/               # Sample test documents
│   ├── sample.txt            # Meeting notes (66 lines)
│   ├── sample.md             # ML guide (56 lines)
│   ├── sample.csv            # Product data (16 rows)
│   ├── sample.pdf            # AI overview (2 pages)
│   └── sample.docx           # Python guide
│
├── 🔧 Utility Scripts
│   ├── fix_cache.py          # Cache clearing utility
│   ├── install_deps.py       # Quick install script
│   └── generate_samples.py   # Sample document generator
│
├── 📚 Documentation
│   ├── README.md             # Project overview
│   ├── INSTALLATION_GUIDE.md # Setup instructions
│   ├── QUICKSTART.md         # Quick start guide
│   ├── START_APP.md          # How to run the app
│   ├── UI_GUIDE.md           # User interface guide
│   ├── TESTING_GUIDE.md      # Testing instructions
│   ├── SAMPLE_PDF_GUIDE.md   # PDF handling guide
│   ├── FEATURE_SUMMARY.md    # Feature overview
│   ├── ADVANCED_FEATURES.md  # Advanced features
│   ├── INTERVIEW_PREPARATION.md  # Interview Q&A
│   └── CODE_EXPLANATION.md   # This file!
│
└── 📁 venv/                   # Virtual environment (not tracked in git)
    ├── Scripts/              # Python executables (Windows)
    │   ├── python.exe
    │   ├── pip.exe
    │   └── streamlit.exe
    └── Lib/                  # Installed packages
        └── site-packages/
```

### File Statistics

| Category | Files | Total Lines |
|----------|-------|-------------|
| Core Python | 7 | ~1,700 |
| Utility Scripts | 3 | ~350 |
| Documentation | 12+ | ~3,000+ |
| Sample Data | 5 | ~200 |

### Code Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                              (app.py - Streamlit)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
        ┌───────────────────┐                 ┌───────────────────┐
        │   File Upload     │                 │   Ask Question    │
        └─────────┬─────────┘                 └─────────┬─────────┘
                  │                                     │
                  ▼                                     ▼
        ┌───────────────────┐                 ┌───────────────────┐
        │  FileLoaderFactory │                 │  Embed Question   │
        │  (file_loader.py)  │                 │  (rag_pipeline.py)│
        └─────────┬─────────┘                 └─────────┬─────────┘
                  │                                     │
                  ▼                                     ▼
        ┌───────────────────┐                 ┌───────────────────┐
        │   TextChunker     │                 │   FAISS Search    │
        │(text_processor.py)│                 │ (vector_store.py) │
        └─────────┬─────────┘                 └─────────┬─────────┘
                  │                                     │
                  ▼                                     ▼
        ┌───────────────────┐                 ┌───────────────────┐
        │  Embed Chunks     │                 │  Build Prompt     │
        │ (SentenceTransf.) │                 │  (Context + Q)    │
        └─────────┬─────────┘                 └─────────┬─────────┘
                  │                                     │
                  ▼                                     ▼
        ┌───────────────────┐                 ┌───────────────────┐
        │   Store in FAISS  │                 │  Generate Answer  │
        │ (vector_store.py) │                 │   (Flan-T5 LLM)   │
        └─────────┬─────────┘                 └─────────┬─────────┘
                  │                                     │
                  ▼                                     ▼
        ┌───────────────────┐                 ┌───────────────────┐
        │  Save to Disk     │                 │  Display + Sources│
        │ (faiss_index.bin) │                 │    (Streamlit)    │
        └───────────────────┘                 └───────────────────┘
```

---

## 🎓 Summary: Complete Data Flow

### INDEXING FLOW (When User Uploads a Document)

```
Step 1: USER UPLOADS FILE (e.g., report.pdf)
        ↓
        app.py: st.file_uploader() receives file
        ↓
Step 2: SAVE TO DISK
        ↓
        rag_pipeline.py: Saves to data/uploaded_files/report.pdf
        ↓
Step 3: EXTRACT TEXT
        ↓
        file_loader.py: PDFLoader uses pdfplumber
        Returns: {'text': "...", 'metadata': {'file_name': 'report.pdf', 'total_pages': 5, ...}}
        ↓
Step 4: CHUNK TEXT
        ↓
        text_processor.py: TextChunker splits into 500-char pieces
        Returns: [{'text': "chunk1...", 'metadata': {...}}, {'text': "chunk2...", 'metadata': {...}}, ...]
        ↓
Step 5: CREATE EMBEDDINGS
        ↓
        rag_pipeline.py: SentenceTransformer.encode(texts)
        Returns: numpy array shape (num_chunks, 384)
        ↓
Step 6: STORE IN FAISS
        ↓
        vector_store.py: index.add(embeddings)
        Also stores: chunks[], metadata[], document_files set
        ↓
Step 7: SAVE TO DISK
        ↓
        vector_store.py: Saves faiss_index.bin and chunks_metadata.pkl
        ↓
Step 8: SHOW SUCCESS
        ↓
        app.py: "✅ Processed 1 file(s), created 15 chunks"
```

### QUERY FLOW (When User Asks a Question)

```
Step 1: USER TYPES QUESTION
        "What were the Q3 revenue results?"
        ↓
        app.py: st.chat_input() receives question
        ↓
Step 2: EMBED QUESTION
        ↓
        rag_pipeline.py: SentenceTransformer.encode(question)
        Returns: numpy array shape (384,)
        ↓
Step 3: SEARCH FAISS
        ↓
        vector_store.py: index.search(query_embedding, k=5)
        Returns: distances and indices of top 5 similar chunks
        ↓
Step 4: CONVERT DISTANCES TO SCORES
        ↓
        vector_store.py: similarity = exp(-distance)
        Filter: Keep only chunks with score >= 0.3
        ↓
Step 5: BUILD CONTEXT
        ↓
        rag_pipeline.py: Concatenate chunk texts with source labels
        "[Source 1: report.pdf, page 3]\nRevenue increased by 23%..."
        ↓
Step 6: BUILD PROMPT
        ↓
        rag_pipeline.py: 
        "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        ↓
Step 7: TOKENIZE
        ↓
        rag_pipeline.py: tokenizer(prompt, return_tensors="pt")
        Converts text to token IDs: [101, 2023, 2003, 1037, ...]
        ↓
Step 8: GENERATE ANSWER
        ↓
        rag_pipeline.py: llm.generate(input_ids, max_length=600, num_beams=5, ...)
        Returns: token IDs of answer
        ↓
Step 9: DECODE TOKENS
        ↓
        rag_pipeline.py: tokenizer.decode(output_ids)
        Returns: "Revenue increased by 23% compared to Q2..."
        ↓
Step 10: EXTRACT SOURCES
         ↓
         rag_pipeline.py: Get file names, page numbers, scores from metadata
         ↓
Step 11: DISPLAY ANSWER
         ↓
         app.py: st.markdown(answer) + display_sources(sources)
         ↓
Step 12: SAVE TO HISTORY
         ↓
         app.py: Append to chat_history, save_chat_history()
```

### MULTIMODAL FLOW (Images)

```
Step 1: PDF UPLOAD (with images)
        ↓
Step 2: STANDARD TEXT PROCESSING (same as above)
        ↓
Step 3: IMAGE EXTRACTION
        ↓
        multimodal_rag.py: fitz.open(pdf) → page.get_images()
        Filter: Skip images < 2KB or < 100x100 pixels
        ↓
Step 4: IMAGE EMBEDDING
        ↓
        multimodal_rag.py: CLIP model encodes images
        Returns: tensor for each image
        ↓
Step 5: STORE IMAGES
        ↓
        multimodal_rag.py: image_store.append({embedding, image, metadata})
        ↓
Step 6: QUERY TIME
        ↓
        multimodal_rag.py: CLIP encodes text query
        Calculate cosine similarity with all image embeddings
        Return top 2 images with score > 0.25
        ↓
Step 7: DISPLAY
        ↓
        app.py: st.image(img_data['image'])
```

---

## 🔧 Key Python Concepts Used

### 1. Type Hints

```python
def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
```
- **`file_path: str`**: Parameter should be a string
- **`-> Dict[str, Any]`**: Returns a dictionary with string keys

### 2. Abstract Base Classes

```python
from abc import ABC, abstractmethod

class BaseLoader(ABC):
    @abstractmethod
    def load(self, ...):
        pass
```
- **ABC**: Can't instantiate directly
- **@abstractmethod**: Subclasses MUST implement this

### 3. Context Managers

```python
with open(file_path, 'r') as f:
    text = f.read()
```
- **`with`**: Automatically closes file when done
- **Works with**: files, database connections, locks

### 4. List Comprehensions

```python
paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
```
Equivalent to:
```python
paragraphs = []
for para in doc.paragraphs:
    if para.text.strip():
        paragraphs.append(para.text)
```

### 5. Dictionary Comprehension

```python
features_check = {
    "Streaming": "generate_answer_stream" in app_content,
    "Export": "Download Chat History" in app_content,
}
```

### 6. Class Methods

```python
class FileLoaderFactory:
    @classmethod
    def get_loader(cls, file_name: str):
        # cls refers to the class itself
```
- **`@classmethod`**: Method belongs to class, not instance
- **`cls`**: Reference to the class (like `self` for instances)

### 7. Inheritance

```python
class MultiModalRAG(RAGPipeline):
    def __init__(self):
        super().__init__()  # Call parent constructor
```
- **`(RAGPipeline)`**: Inherits from RAGPipeline
- **`super()`**: Access parent class methods

### 8. Session State (Streamlit)

```python
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()
```
- **Session state**: Persists between reruns
- **Without it**: Variables reset on every interaction

### 9. Walrus Operator

```python
if prompt := st.chat_input("Ask..."):
    # prompt is assigned AND checked
```
- **`:=`**: Assigns value AND returns it for condition check
- **Python 3.8+** feature

### 10. Ternary Operator

```python
status = "✅" if exists else "❌"
```
Equivalent to:
```python
if exists:
    status = "✅"
else:
    status = "❌"
```

---

## 🎯 Quick Reference - Important Variables

### config.py Constants

| Variable | Value | Purpose |
|----------|-------|---------|
| `EMBEDDING_MODEL` | "sentence-transformers/all-MiniLM-L6-v2" | Text → vectors |
| `EMBEDDING_DIMENSION` | 384 | Vector size |
| `LLM_MODEL` | "google/flan-t5-base" | Answer generation |
| `CHUNK_SIZE` | 500 | Characters per chunk |
| `CHUNK_OVERLAP` | 50 | Overlapping chars |
| `TOP_K_RETRIEVAL` | 5 | Chunks per query |
| `SIMILARITY_THRESHOLD` | 0.3 | Min relevance |

### app.py Session State

| Variable | Type | Purpose |
|----------|------|---------|
| `st.session_state.rag_pipeline` | RAGPipeline | Main pipeline object |
| `st.session_state.chat_history` | List[Dict] | Conversation messages |
| `st.session_state.uploaded_file_names` | Set[str] | Track uploaded files |
| `st.session_state.document_summaries` | Dict[str, str] | File summaries |

### rag_pipeline.py Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `self.device` | str | "cuda" or "cpu" |
| `self.embedding_model` | SentenceTransformer | Text embedder |
| `self.tokenizer` | AutoTokenizer | Text → tokens |
| `self.llm` | AutoModelForSeq2SeqLM | Answer generator |
| `self.text_chunker` | TextChunker | Splits text |
| `self.vector_store` | VectorStore | FAISS wrapper |

### vector_store.py Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `self.index` | faiss.IndexFlatL2 | FAISS index |
| `self.chunks` | List[str] | Chunk texts |
| `self.metadata` | List[Dict] | Chunk metadata |
| `self.document_files` | Set[str] | Unique file names |
| `self.dimension` | int | 384 |

---

## ✅ Checklist: Everything Explained

- [x] **config.py** - All settings and constants
- [x] **modules/__init__.py** - Package initializer
- [x] **modules/file_loader.py** - All 5 loader classes + factory
- [x] **modules/text_processor.py** - TextChunker class
- [x] **modules/vector_store.py** - VectorStore class
- [x] **modules/rag_pipeline.py** - Complete RAG logic
- [x] **modules/multimodal_rag.py** - CLIP + image extraction
- [x] **app.py** - Full Streamlit UI
- [x] **requirements.txt** - All dependencies explained
- [x] **fix_cache.py** - Cache clearing utility
- [x] **install_deps.py** - Installation script
- [x] **generate_samples.py** - Sample generator
- [x] **examples/** - All sample documents
- [x] **data/** - Storage structure
- [x] **Data flow diagrams** - Indexing + Query + Multimodal
- [x] **Python concepts** - 10 key concepts used
- [x] **Quick reference** - All important variables

---

**This document now covers EVERY file and EVERY line of code in the project!** 🎉
