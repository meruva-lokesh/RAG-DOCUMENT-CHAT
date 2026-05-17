"""
Configuration file for Universal Document Chat RAG application.
Contains all model settings, paths, and hyperparameters.
"""

import os

# ============================================================================
# MODEL SETTINGS
# ============================================================================

# Embedding model for creating document and query embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimension of all-MiniLM-L6-v2 embeddings

# Language model for answer generation
LLM_MODEL = "google/flan-t5-base"  # Can upgrade to flan-t5-large for better quality
LLM_MAX_LENGTH = 300  # Maximum length of generated answers (in tokens)
LLM_TEMPERATURE = 0.7  # Creativity vs determinism (0.0 = deterministic, 1.0 = creative)

# ============================================================================
# TEXT PROCESSING SETTINGS
# ============================================================================

# Chunking parameters
# Larger chunks = more context per chunk (better for detailed answers)
CHUNK_SIZE = 800  # Characters per chunk (increased for more context)
CHUNK_OVERLAP = 150  # Overlapping characters between chunks (better continuity)

# ============================================================================
# RETRIEVAL SETTINGS
# ============================================================================

# Number of top chunks to retrieve for each query
# Higher = more context but may include less relevant info
TOP_K_RETRIEVAL = 8  # Increased for more comprehensive answers

# Minimum similarity score threshold (0.0 to 1.0)
# Chunks below this threshold will not be used
# Lower = more results, Higher = stricter matching
SIMILARITY_THRESHOLD = 0.20  # Lowered to catch more relevant chunks

# ============================================================================
# CHAT SETTINGS
# ============================================================================

# Number of previous chat messages to include as context
CHAT_HISTORY_LIMIT = 5

# ============================================================================
# STORAGE PATHS
# ============================================================================

# Base data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Vector store persistence path
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")

# Uploaded files cache directory
UPLOADED_FILES_DIR = os.path.join(DATA_DIR, "uploaded_files")

# ============================================================================
# SUPPORTED FILE TYPES
# ============================================================================

SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".docx", ".csv"]

# ============================================================================
# UI SETTINGS
# ============================================================================

APP_TITLE = "Universal Document Chat"
APP_SUBTITLE = "Talk to Your Files with AI"
APP_ICON = "💬"

# Processing status messages
STATUS_EXTRACTING = "📄 Extracting text from documents..."
STATUS_CHUNKING = "✂️ Splitting text into chunks..."
STATUS_EMBEDDING = "🧠 Creating embeddings..."
STATUS_INDEXING = "🗂️ Indexing documents..."
STATUS_READY = "✅ Ready to chat!"
STATUS_ERROR = "❌ Error processing documents"
