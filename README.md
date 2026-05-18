# 🎯 Universal Document Chat - Multimodal RAG 💬

A complete Python-based **Generative AI application** that enables users to upload documents and interact with them through natural language chat using **Multimodal RAG (Retrieval-Augmented Generation)** with advanced AI capabilities.

**Now supports: Text + Images from documents! 🖼️**

## ⭐ Key Features

### Core RAG Capabilities
- **Multi-Format Support**: Upload PDF, TXT, MD, DOCX, and CSV files
- **Intelligent Retrieval**: FAISS vector database for ultra-fast similarity search
- **AI-Powered Answers**: Powered by HuggingFace open-source models
- **Citation Tracking**: Every answer includes source references (file name, page numbers)
- **Clean UI**: Modern Streamlit interface with real-time status updates

### 🆕 Advanced Features
- **Multimodal Support** 🖼️: Extract and retrieve images from PDF documents
  - Automatic image extraction from PDFs
  - CLIP-based image-to-text matching
  - Images returned alongside text answers
  
- **Persistent Chat History** 💾: Conversations auto-save and persist
  - Auto-saves after every message
  - Chat loads automatically on app restart
  - Export conversations as JSON
  - Never lose your discussions
  
- **Document Summarization** 📝: AI-powered automatic summaries
  - Auto-generates summaries when documents uploaded
  - View summaries in expandable sidebar sections
  - Quick document overview before asking questions
  
- **Streaming Responses** ⚡: Real-time answer generation
  - Answers stream word-by-word (like ChatGPT)
  - Cursor effect shows generation progress
  - More engaging and interactive experience
  
- **Chat Context**: Maintains conversation context for follow-up questions
- **Persistent Storage**: Documents, embeddings, and history saved to disk

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ User uploads documents (PDF, TXT, MD, DOCX, CSV)            │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   📝 TEXT PATH          🖼️ IMAGE PATH
        │                     │
   Text Extraction      Image Extraction
   + Chunking          (PyMuPDF)
        │                     │
        ▼                     ▼
   Embeddings          CLIP Embeddings
   (sentence-trans)    (ViT-B-32)
        │                     │
        └──────────┬──────────┘
                   ▼
         ┌─────────────────────┐
         │ Unified Vector Store│
         │ (FAISS Index)       │
         └────────┬────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
User Question         Context Building
      │                       │
      ├─→ Text Embeddings     │
      │   + Image Matching    │
      │                       │
      └─→ Hybrid Retrieval ───┘
                  │
                  ▼
          ┌──────────────────┐
          │ LLM Answer Gen   │
          │ (Flan-T5-Base)   │
          └────────┬─────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    📄 Text Answer      🖼️ Images + Citations
```

**Key Components**:
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Multimodal Model**: `clip-ViT-B-32` (for image-text matching)
- **LLM**: `google/flan-t5-base` (seq2seq model for answer generation)
- **Vector DB**: FAISS with L2 similarity search
- **Image Processing**: PyMuPDF + Pillow
- **UI Framework**: Streamlit

## 📋 Prerequisites

- Python 3.9 or higher
- 4GB+ RAM (8GB+ recommended for multimodal features)
- Optional: CUDA-enabled GPU for faster processing

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
cd "e:\RAG PROJECT"
```
Or on Linux/Mac:
```bash
cd ~/RAG_PROJECT
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First-time installation will download ~1-2GB of machine learning models:
- Embedding model (~600MB)
- CLIP model for images (~500MB)
- LLM model (~300MB)

This is normal and only happens once. Models are cached in `~/.cache/huggingface/`

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501` ✅

## 📖 How to Use

### Step 1: Upload Documents 📤
1. Click the **file uploader** in the left sidebar
2. Select one or more documents (PDF, TXT, MD, DOCX, CSV)
3. Wait for processing to complete
4. You'll see:
   - ✅ "Ready to chat!" message
   - 📝 **Auto-generated document summaries** in the sidebar
   - 🖼️ Image count if extracting from PDFs

### Step 2: View Document Summaries 📝
- Expandable summaries appear in the sidebar
- Quickly understand what's in each document
- Yellow summary boxes for easy visibility

### Step 3: Ask Questions 🤖
1. Type your question in the chat input at the bottom
2. Press Enter
3. Answer streams in real-time (word-by-word) ⚡
4. See relevant sources below the answer
5. View retrieved images if applicable 🖼️

### Step 4: Continue Chatting 💬
- Ask follow-up questions - AI remembers context
- View full conversation history
- Export chat history as JSON (💾 button in sidebar)
- Chat auto-saves between sessions!

### Controls
- **🗑️ Clear Chat**: Reset conversation history (keeps documents loaded)
- **🔄 Reset Docs**: Remove all documents and start fresh
- **📥 Download Chat History**: Export as JSON for backup/sharing

## 📁 Project Structure

```
e:/RAG PROJECT/
├── 🎯 Core Application Files
│   ├── app.py                      # Main Streamlit application
│   ├── config.py                   # Configuration & settings
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # This file
│
├── 📦 modules/                     # Core RAG logic
│   ├── __init__.py
│   ├── file_loader.py              # Document loaders (PDF, DOCX, TXT, MD, CSV)
│   ├── text_processor.py           # Text chunking with overlap
│   ├── rag_pipeline.py             # Standard RAG orchestration
│   ├── multimodal_rag.py           # 🆕 Multimodal RAG (text + images)
│   └── vector_store.py             # FAISS wrapper & similarity search
│
├── 📊 data/                        # Created at runtime
│   ├── vector_store/               # Persisted FAISS index files
│   ├── uploaded_files/             # Cached uploaded documents
│   └── chat_history/               # 🆕 Persistent chat conversations (JSON)
│
├── 📚 examples/                    # Sample test documents
│   ├── sample.pdf                  # AI overview document
│   ├── sample.docx                 # Python programming guide
│   ├── sample.md                   # Markdown sample
│   ├── sample.txt                  # Text file sample
│   └── sample.csv                  # Data in CSV format
│
└── 📖 Documentation Files
    ├── ADVANCED_FEATURES.md        # Advanced implementation guide
    ├── FEATURE_SUMMARY.md          # Feature overview
    ├── BEGINNER_GUIDE.md           # Getting started guide
    ├── CODE_EXPLANATION.md         # Detailed code walkthrough
    ├── INSTALLATION_GUIDE.md       # Setup instructions
    ├── TESTING_GUIDE.md            # Testing procedures
    └── QUICKSTART.md               # Quick reference
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "google/flan-t5-base"

# Text Processing
CHUNK_SIZE = 800                    # Characters per chunk
CHUNK_OVERLAP = 150                 # Overlap between chunks

# Retrieval
TOP_K_RETRIEVAL = 8                 # Number of results
SIMILARITY_THRESHOLD = 0.20         # Minimum similarity score

# Chat
CHAT_HISTORY_LIMIT = 5              # Previous messages for context
```

**Common Tweaks:**
- ↑ `CHUNK_SIZE` (800→1200) = More context per chunk
- ↓ `CHUNK_SIZE` (800→400) = Faster, less context
- ↑ `TOP_K_RETRIEVAL` (8→15) = More comprehensive answers
- 🔄 `LLM_MODEL` = "google/flan-t5-large" for better quality (needs more RAM)

## 🧪 Testing with Examples

Sample documents are provided in the `examples/` folder for quick testing:

### Quick Start Test
1. Open the app: `streamlit run app.py`
2. Click **"Upload your documents"** in sidebar
3. Select all files from `examples/` folder
4. Wait for processing (you'll see summaries appear)

### Test Questions to Try

**Basic Understanding:**
- "What is this document about?"
- "Summarize the key points"
- "Who is the author?"

**Multimodal (Images from PDFs):**
- "Are there any diagrams or images?"
- "Show me the images from the PDF"
- "What do the charts show?"

**Cross-Document:**
- "Compare information from different files"
- "What's the difference between these documents?"

**Data Analysis:**
- "What data is in the CSV file?"
- "Analyze the statistics"
- "What are the trends?"

### Sample File Contents
- **sample.pdf**: 2-page AI overview with diagrams
- **sample.docx**: Python programming guide with examples
- **sample.md**: Markdown formatted technical content
- **sample.txt**: Plain text information
- **sample.csv**: Structured data for analysis

## 🆕 Advanced Features Guide

### 1. Multimodal Image Support 🖼️
```
PDFs → PyMuPDF Extraction → CLIP Encoding → Vector Store
             ↓
      Retrieve images matching user queries
```
- Automatically extracts images from PDF files
- Indexes using CLIP (vision-language model)
- Returns relevant images alongside text answers
- Supports large PDFs with multiple images

### 2. Persistent Chat History 💾
```
Every message → Auto-save JSON → data/chat_history/
                      ↓
           Load on next session
```
- Conversations automatically saved to disk
- Previous chat loads on app restart
- Export button to download chat history
- JSON format for easy integration

### 3. Document Summarization 📝
```
Upload documents → LLM processes → AI generates summary
       ↓
   Display in sidebar with metadata
```
- Automatic summaries generated on upload
- Quick understanding of document content
- Expandable cards in sidebar
- Helps choose relevant documents

### 4. Streaming Responses ⚡
```
Question → LLM generates → Stream word-by-word → Display in real-time
              ↓
         Shows cursor effect while generating
```
- Real-time response streaming (like ChatGPT)
- Better UX with visible progress
- Same quality, better experience

## 🐛 Troubleshooting

### Models Not Downloading
- **Issue**: Network error during first run
- **Solution**: 
  - Ensure stable internet connection
  - First run may take 10-15 minutes to download all models
  - Models are cached in `~/.cache/huggingface/` - they download only once
  - If interrupted, delete cache and retry: `rm -rf ~/.cache/huggingface/`

### Out of Memory (OOM) Errors
- **Issue**: "CUDA out of memory" or system freezing
- **Solutions**:
  - Reduce `CHUNK_SIZE` in config.py: `CHUNK_SIZE = 400`
  - Use smaller LLM: `LLM_MODEL = "google/flan-t5-small"`
  - Reduce `TOP_K_RETRIEVAL`: `TOP_K_RETRIEVAL = 4`
  - Close other applications
  - Disable GPU and use CPU (slower but safer)

### Images Not Being Extracted
- **Issue**: "0 images processed" for PDFs with images
- **Solutions**:
  - Some PDFs have images as embedded objects - try a different PDF
  - Use high-quality PDFs with clear, standard image formats
  - Check image sizes in PDF (PyMuPDF filters <2KB images as potential noise)

### PDF Text Extraction Issues
- **Issue**: Empty or garbled text from PDF
- **Solutions**:
  - Use PDFs with selectable text (not scanned images)
  - Try online PDF converters or tools like OCR to make it text-extractable
  - Some PDFs may require special permissions to extract text

### Slow Response Times
- **CPU Mode**: First query ~10-30 seconds (normal - model loading)
- **Solutions**:
  - Subsequent queries should be 5-10 seconds
  - Reduce `TOP_K_RETRIEVAL` in config.py
  - Switch to GPU (see GPU Acceleration section)
  - Use smaller LLM: `flan-t5-small`

### Chat History Not Loading
- **Issue**: Chat doesn't persist between restarts
- **Solutions**:
  - Check `data/chat_history/` folder exists and has JSON files
  - Ensure write permissions to `data/` directory
  - Check browser cache is not blocking storage
  - Try "Clear Chat" and then refresh browser

### Multimodal Features Not Working
- **Issue**: Images not being retrieved, no image extraction
- **Solutions**:
  - Ensure `multimodal_rag.py` exists in `modules/` folder
  - Check `pip list | grep -i clip` - CLIP model must be installed
  - Verify PDF has extractable images (not graphics)
  - Check memory - multimodal uses more RAM

### Streamlit Session Errors
- **Issue**: "SessionState error" or app crashing
- **Solutions**:
  - Clear browser cache: Ctrl+Shift+Delete
  - Kill and restart Streamlit: Ctrl+C, then `streamlit run app.py`
  - Clear temp files: `rm -rf ~/.streamlit/`
  - Ensure latest Streamlit: `pip install --upgrade streamlit`

## 🚀 Advanced Usage

### Using GPU Acceleration ⚡

For 5-10x faster performance, use NVIDIA GPU:

**1. Install CUDA Toolkit** (https://developer.nvidia.com/cuda-toolkit)

**2. Update Dependencies:**
```bash
# Remove CPU version
pip uninstall faiss-cpu

# Install GPU versions
pip install faiss-gpu
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

**3. Verify GPU Detection:**
```bash
# In Python
import torch
print(torch.cuda.is_available())  # Should print: True
print(torch.cuda.get_device_name(0))  # Shows GPU name
```

**4. Run App:**
```bash
streamlit run app.py
# Watch for: "🚀 Initializing RAG Pipeline on GPU..."
```

### Switching to Different LLMs

For different quality/speed tradeoffs:

```python
# config.py

# Fast (3-5 seconds, lower quality)
LLM_MODEL = "google/flan-t5-small"

# Balanced (current default, 5-15 seconds)
LLM_MODEL = "google/flan-t5-base"

# High Quality (10-30 seconds, needs 8GB+ RAM)
LLM_MODEL = "google/flan-t5-large"

# Using Open-Source Models (alternative)
LLM_MODEL = "mistralai/Mistral-7B-v0.1"  # Better quality, needs GPU
```

### Using Different Embedding Models

```python
# config.py

# Fast & Small (256 dimensions)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Better Quality (768 dimensions, slower)
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Multilingual (100+ languages)
EMBEDDING_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v2"
```

### Clearing All Data

To reset everything and start fresh:

```bash
# Windows
rmdir /s /q data\vector_store
rmdir /s /q data\uploaded_files
rmdir /s /q data\chat_history

# Linux/Mac
rm -rf data/vector_store/*
rm -rf data/uploaded_files/*
rm -rf data/chat_history/*
```

Or use the app UI:
- **🔄 Reset Docs** button in sidebar (resets documents & chat)

### Running on Different Machines

**Server Mode (Headless):**
```bash
streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0
```

**Then access from another machine:**
```
http://<server-ip>:8501
```

### Monitoring Performance

Check processing speed:
```python
# In app.py, after processing documents
print(f"Embedded {results['total_chunks']} chunks in {results['time']:.2f} seconds")
print(f"Speed: {results['total_chunks']/results['time']:.0f} chunks/second")
```

## 📊 Performance Benchmarks

| Operation | CPU | GPU (CUDA) |
|-----------|-----|-----------|
| Model Loading | 30-60s | 30-60s |
| PDF Processing (10 pages) | 2-5s | 1-2s |
| Embedding 100 chunks | 10-15s | 2-3s |
| Answer Generation | 5-15s | 1-3s |
| Image Extraction (PDF) | 2-5s | 2-5s |
| **Total First Query** | 20-40s | 5-15s |
| **Subsequent Queries** | 5-15s | 1-3s |

**Note**: Times vary based on document size, chunk count, and system specs.

## 🔧 API Usage (For Developers)

### Direct Pipeline Usage

```python
from modules.multimodal_rag import MultiModalRAG

# Initialize
rag = MultiModalRAG()

# Process documents
results = rag.process_uploaded_files(file_list)
print(f"Processed {results['files_processed']} files")

# Generate answer
response = rag.generate_answer("Your question here")
print(response['answer'])
print(response['sources'])
print(response['relevant_images'])  # If multimodal
```

### Vector Store Direct Access

```python
from modules.vector_store import VectorStore

store = VectorStore()
store.load_from_disk()

# Search
results = store.search(query_embedding, k=5)
for result in results:
    print(f"{result['metadata']['file_name']}: {result['score']:.2f}")
```

## � Documentation

For detailed information:

| Document | Purpose |
|----------|---------|
| [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md) | Step-by-step setup for beginners |
| [QUICKSTART.md](QUICKSTART.md) | Quick reference guide |
| [CODE_EXPLANATION.md](CODE_EXPLANATION.md) | Deep dive into code architecture |
| [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) | Implementing additional features |
| [FEATURE_SUMMARY.md](FEATURE_SUMMARY.md) | Overview of all features |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | How to test the system |
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Detailed installation steps |

## 🛣️ Roadmap & Future Enhancements

### Currently Implemented ✅
- [x] Text + Image multimodal RAG
- [x] Persistent chat history
- [x] Document summarization
- [x] Streaming responses
- [x] Multi-format document support
- [x] FAISS vector store
- [x] Citation tracking
- [x] Streamlit UI

### Planned Features 🔄
- [ ] OCR support for scanned PDFs
- [ ] Web URL ingestion
- [ ] Multi-language support
- [ ] Advanced semantic search (re-ranking)
- [ ] Conversation branching (multiple paths)
- [ ] API endpoint server mode
- [ ] Batch document processing
- [ ] Integration with cloud LLMs (OpenAI, Claude, Gemini)
- [ ] Document source visualization
- [ ] Vector store analytics dashboard

### Under Consideration 💡
- Semantic clustering of documents
- Named entity extraction
- Table extraction from PDFs
- Audio/video document support
- Fact verification
- Source quality scoring
- Real-time collaborative chat

## 🤝 Contributing

Contributions welcome! Here's how:

1. **Report Issues**: Found a bug? [Open an issue](#)
2. **Suggest Features**: Have ideas? Create a discussion
3. **Submit Code**: 
   - Fork the repository
   - Create a feature branch: `git checkout -b feature/amazing-feature`
   - Make changes and test thoroughly
   - Commit: `git commit -m 'Add amazing feature'`
   - Push: `git push origin feature/amazing-feature`
   - Open a Pull Request

4. **Improve Docs**: Documentation improvements always welcome!

## 📝 License

This project is open-source and available under the **MIT License**.

You're free to:
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use in private projects
- ✅ Include in other software

Just include a license copy with your distribution.

## 📧 Support & Community

### Getting Help
1. **Check Troubleshooting Section** above - covers most issues
2. **Review Documentation** - BEGINNER_GUIDE.md has setup help
3. **Search Issues** - Your question might be answered already
4. **Ask Community** - Create a discussion/issue

### Useful Links
- [Streamlit Docs](https://docs.streamlit.io) - UI framework help
- [HuggingFace Models](https://huggingface.co/models) - Model options
- [FAISS Documentation](https://github.com/facebookresearch/faiss) - Vector store
- [PyMuPDF Docs](https://pymupdf.readthedocs.io/) - PDF processing
- [Sentence Transformers](https://www.sbert.net/) - Embeddings

### Reporting Bugs
When reporting bugs, please include:
- Your OS (Windows/Linux/Mac)
- Python version: `python --version`
- Specific error message (full traceback)
- Steps to reproduce
- Your config.py settings (model names, etc.)

## 💡 Tips for Best Results

### Document Preparation
- **Quality matters**: Use clear, well-formatted documents
- **Text-based PDFs**: Better than scanned/image PDFs
- **Reasonable size**: 1-500 pages per file works best
- **Multiple files**: 3-10 documents is sweet spot

### Question Asking
- **Be specific**: "What are the main benefits?" vs "What?"
- **Ask in context**: "In the PDF about X, what is..."
- **Follow-ups work**: AI remembers previous questions
- **Cite sources**: Ask for page numbers in answers

### Performance Tips
- **Upload in batches**: 5-10 files at a time
- **Specific chunk size**: Adjust for document types
  - Longer chunks (1200) = more context, slower
  - Shorter chunks (400) = less context, faster
- **Use GPU if available**: 5-10x faster
- **Monitor memory**: Close other apps for large batches

## 🎓 Learning Resources

### Understanding RAG
- [RAG Paper](https://arxiv.org/abs/2005.11401) - Original research
- [LLM Basics](https://huggingface.co/course) - HuggingFace course
- [Vector Databases](https://www.databricks.com/blog/2024/01/18/what-are-vector-databases.html) - Explained

### Relevant Technologies
- **Embeddings**: sentence-transformers, CLIP
- **Vector Stores**: FAISS, Pinecone, Weaviate
- **LLMs**: Flan-T5, Mistral, Llama
- **UI**: Streamlit
- **Document Processing**: PyMuPDF, python-docx, pdfplumber

## 🙏 Acknowledgments

Built with amazing open-source projects:
- [Streamlit](https://streamlit.io/) - UI framework
- [HuggingFace](https://huggingface.co/) - Models & transformers
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [CLIP](https://github.com/openai/CLIP) - Vision-language model

## 📊 Project Statistics

- **Total Lines of Code**: ~2000+
- **Supported File Formats**: 5 (PDF, TXT, MD, DOCX, CSV)
- **ML Models Integrated**: 3 (Embeddings, LLM, Vision-Language)
- **Advanced Features**: 4 (Multimodal, Chat History, Summarization, Streaming)
- **Documentation Pages**: 7+
- **Example Datasets**: 5 samples

---

## 🚀 Quick Command Reference

```bash
# Setup
cd e:\RAG_PROJECT
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run
streamlit run app.py

# Test with examples
# - Upload files from examples/ folder
# - Try sample questions

# Development
# - Edit config.py for settings
# - Check logs in terminal
# - Clear data: rm -rf data/*

# GPU Setup
pip install faiss-gpu
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

**Last Updated**: May 2026  
**Version**: 2.0 (Multimodal RAG)  
**Status**: Active Development ✅  

**⭐ If this project helps you, please give it a star!** ⭐

---

**Built with ❤️ for AI enthusiasts and developers**
