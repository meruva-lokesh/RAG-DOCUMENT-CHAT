# RAG Project - Complete Beginner's Guide

## Table of Contents
1. [What Problem Does This Project Solve?](#what-problem-does-this-project-solve)
2. [What is RAG?](#what-is-rag)
3. [Key Terminology Explained](#key-terminology-explained)
4. [Project Architecture](#project-architecture)
5. [How Each File Works](#how-each-file-works)
6. [Step-by-Step: What Happens When You Ask a Question](#step-by-step-what-happens-when-you-ask-a-question)
7. [Technologies Used](#technologies-used)
8. [Real-World Analogy](#real-world-analogy)

---

## What Problem Does This Project Solve?

Imagine you have 100 PDF documents about your company's policies. You want to ask questions like:
- "What is the leave policy?"
- "How do I apply for reimbursement?"

**Traditional approach**: Open each PDF, use Ctrl+F, search manually. Takes hours!

**This RAG project**: Upload all PDFs, ask questions in plain English, get instant answers with sources.

---

## What is RAG?

### RAG = Retrieval-Augmented Generation

Let's break this down:

| Word | Meaning |
|------|---------|
| **Retrieval** | Finding relevant information from your documents |
| **Augmented** | Enhanced or improved |
| **Generation** | Creating a human-readable answer |

### Simple Definition:
RAG is a technique where we:
1. **RETRIEVE** relevant pieces of text from your documents
2. **AUGMENT** (add) this text to a question
3. **GENERATE** an answer using AI

### Why RAG? Why not just use ChatGPT?

| ChatGPT Alone | RAG System |
|---------------|------------|
| Only knows training data (cut-off date) | Knows YOUR documents |
| Can't read your private files | Reads and understands your files |
| May "hallucinate" (make up facts) | Answers based on actual document content |
| Generic answers | Specific answers from your data |

---

## Key Terminology Explained

### 1. **Embedding**

**What it is**: Converting text into numbers (a list of numbers called a "vector").

**Why we need it**: Computers don't understand words like "cat" or "dog". They only understand numbers. Embeddings convert words/sentences into numbers while preserving meaning.

**Example**:
```
"I love dogs" → [0.2, 0.5, 0.1, 0.8, ...]  (384 numbers)
"I adore puppies" → [0.21, 0.49, 0.11, 0.79, ...]  (similar numbers because similar meaning!)
"I hate mathematics" → [0.9, 0.1, 0.7, 0.2, ...]  (different numbers because different meaning)
```

**Key insight**: Similar sentences have similar number patterns. This is how the computer "understands" meaning.

---

### 2. **Vector**

**What it is**: A list (array) of numbers.

**Example**:
```
[0.1, 0.5, 0.3, 0.8]  ← This is a vector with 4 dimensions
```

**In this project**: Each text chunk becomes a vector with **384 dimensions** (384 numbers).

---

### 3. **Vector Store / Vector Database**

**What it is**: A special database that stores vectors and can quickly find similar vectors.

**Analogy**: Think of a library where books are organized not by alphabet, but by topic similarity. Books about cooking are near each other, books about programming are near each other.

**In this project**: We use **FAISS** (Facebook AI Similarity Search) as our vector store.

---

### 4. **FAISS (Facebook AI Similarity Search)**

**What it is**: A library created by Facebook to efficiently search through millions of vectors.

**What it does**: Given a question vector, it finds the most similar document vectors in milliseconds.

**Simple code example**:
```python
# Store vectors
index.add(document_vectors)

# Search for similar vectors
similar_docs = index.search(question_vector, k=3)  # Find 3 most similar
```

---

### 5. **Chunking**

**What it is**: Breaking a large document into smaller pieces.

**Why we need it**:
- AI models have limited memory (can only read ~500 words at a time)
- Smaller pieces = more precise search results
- Better matching between question and relevant content

**Example**:
```
Original Document (5000 words):
"Chapter 1: Introduction... [long text]... Chapter 2: Methods... [long text]..."

After Chunking (10 chunks of 500 words each):
Chunk 1: "Chapter 1: Introduction..."
Chunk 2: "...continued introduction..."
Chunk 3: "Chapter 2: Methods..."
...
```

---

### 6. **Chunk Overlap**

**What it is**: When chunking, we include some text from the previous chunk.

**Why we need it**: To avoid cutting sentences in the middle and losing context.

**Example**:
```
Chunk 1: "The company was founded in 1990. It started with 5 employees."
Chunk 2: "It started with 5 employees. By 2000, it had grown to 500."
         ↑ This part is repeated (overlap)
```

**In this project**: 
- Chunk size: 500 characters
- Overlap: 50 characters (10%)

---

### 7. **LLM (Large Language Model)**

**What it is**: An AI model trained on massive amounts of text that can understand and generate human language.

**Examples**: ChatGPT (GPT-4), Claude, Llama, Flan-T5

**In this project**: We use **Flan-T5-base** - a smaller, free, open-source LLM.

---

### 8. **Transformer**

**What it is**: The AI architecture that powers modern language models.

**Key innovation**: "Attention mechanism" - the model can focus on relevant parts of text.

**Example**: In "The cat sat on the mat because it was tired", the model understands "it" refers to "cat" by paying attention to the context.

**In this project**: Both the embedding model and LLM use transformer architecture.

---

### 9. **Sentence Transformer**

**What it is**: A special type of transformer designed to create embeddings for sentences.

**In this project**: We use `all-MiniLM-L6-v2`:
- "MiniLM" = Mini Language Model (small and fast)
- "L6" = 6 layers deep
- "v2" = version 2

---

### 10. **Semantic Search**

**What it is**: Searching by meaning, not just keywords.

**Traditional Search (Keyword)**:
```
Query: "How to terminate employment?"
Result: Only finds documents containing exact words "terminate" and "employment"
```

**Semantic Search**:
```
Query: "How to terminate employment?"
Result: Also finds documents about "firing employees", "ending job contract", "resignation process"
        (because meanings are similar!)
```

---

### 11. **Top-K Retrieval**

**What it is**: Retrieving the K most similar/relevant results.

**In this project**: K=3 by default, meaning we retrieve the 3 most relevant chunks.

---

### 12. **Context Window**

**What it is**: The maximum amount of text an AI model can "see" at once.

**In this project**: Flan-T5-base has a context window of 512 tokens (~400 words).

**Why it matters**: We can only feed limited text to the model, so we must choose the most relevant chunks.

---

### 13. **Prompt / Prompt Engineering**

**What it is**: The text instruction we give to the AI model.

**Example prompt in this project**:
```
Context: [Retrieved chunks from your documents]
Question: [Your question]
Answer based on the context above:
```

**Prompt Engineering**: The art of writing prompts that make AI give better answers.

---

### 14. **Inference**

**What it is**: Using a trained AI model to make predictions/generate output.

**Training vs Inference**:
- Training: Teaching the model (done by researchers, takes weeks/months)
- Inference: Using the trained model (what we do, takes seconds)

---

### 15. **Tokenization / Tokens**

**What it is**: Breaking text into smaller units (tokens) that the AI can process.

**Example**:
```
"I love programming" → ["I", "love", "program", "ming"]  (4 tokens)
```

**Note**: 1 token ≈ 0.75 words (roughly)

---

### 16. **Cosine Similarity / L2 Distance**

**What it is**: Ways to measure how similar two vectors are.

**Cosine Similarity**: Measures the angle between vectors (0 to 1, higher = more similar)
**L2 Distance**: Measures the straight-line distance (lower = more similar)

**In this project**: We use L2 distance with FAISS.

---

### 17. **Streamlit**

**What it is**: A Python library to create web applications easily.

**Why we use it**: Build a chat interface without knowing HTML/CSS/JavaScript.

```python
import streamlit as st
st.title("My App")  # That's it! You have a web page with a title
```

---

### 18. **Session State**

**What it is**: Memory that persists across user interactions in Streamlit.

**Why we need it**: Without it, the app forgets everything when you click a button.

```python
# Store chat history
st.session_state.messages = []

# Messages persist even after clicking buttons
```

---

### 19. **Pipeline**

**What it is**: A series of steps that data flows through.

**RAG Pipeline in this project**:
```
Document → Chunking → Embedding → Storage → Retrieval → Generation → Answer
```

---

### 20. **Multimodal**

**What it is**: Working with multiple types of data (text + images + audio, etc.)

**In this project**: We support text documents AND images using CLIP model.

---

### 21. **CLIP (Contrastive Language-Image Pre-training)**

**What it is**: An AI model by OpenAI that understands both images and text.

**How it works**: 
- Converts images to vectors
- Converts text to vectors
- Images and text with similar meaning have similar vectors

**Example**: 
- Image of a dog → [0.2, 0.5, ...]
- Text "a cute puppy" → [0.21, 0.49, ...]  (similar vectors!)

---

## Project Architecture

### Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                      (Streamlit - app.py)                        │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ File Upload │  │ Chat Interface  │  │ Settings Sidebar    │  │
│  └─────────────┘  └─────────────────┘  └─────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOCUMENT PROCESSING                         │
│                                                                  │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────┐  │
│  │ File Loader │ ───▶ │   Chunker   │ ───▶ │ Embedding Model │  │
│  │ (PDF, DOCX, │      │ (Split text │      │ (Convert to     │  │
│  │  TXT, etc.) │      │  into parts)│      │  numbers)       │  │
│  └─────────────┘      └─────────────┘      └─────────────────┘  │
│                                                    │             │
└────────────────────────────────────────────────────┼─────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       VECTOR STORAGE                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                         FAISS                                ││
│  │                                                              ││
│  │   Chunk 1 Vector: [0.1, 0.2, 0.3, ...]                      ││
│  │   Chunk 2 Vector: [0.4, 0.5, 0.6, ...]                      ││
│  │   Chunk 3 Vector: [0.7, 0.8, 0.9, ...]                      ││
│  │   ...                                                        ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────┬────────────┘
                                                     │
                          WHEN USER ASKS A QUESTION  │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RETRIEVAL                                 │
│                                                                  │
│  User Question ──▶ Convert to Vector ──▶ Find Similar Chunks    │
│                                                                  │
│  "What is leave policy?" → [0.3, 0.4, ...] → Chunks 2, 5, 8    │
└────────────────────────────────────────────────────┬────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       GENERATION                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ PROMPT:                                                   │   │
│  │                                                           │   │
│  │ Context: [Text from Chunks 2, 5, 8]                      │   │
│  │ Question: What is leave policy?                          │   │
│  │ Answer:                                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   Flan-T5 LLM   │                          │
│                    │   (AI Model)    │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│                             ▼                                    │
│              "Employees are entitled to 20 days..."             │
└─────────────────────────────────────────────────────────────────┘
```

---

## How Each File Works

### 📁 Project Structure

```
RAG PROJECT/
│
├── app.py                    # Main application (what you run)
├── config.py                 # Settings and configuration
├── requirements.txt          # List of packages needed
│
├── modules/                  # Core functionality
│   ├── __init__.py          # Makes this a Python package
│   ├── file_loader.py       # Reads different file types
│   ├── text_processor.py    # Chunks the text
│   ├── vector_store.py      # Stores and searches vectors
│   ├── rag_pipeline.py      # Connects everything together
│   └── multimodal_rag.py    # Adds image support
│
├── data/                     # Storage
│   ├── uploaded_files/      # Your uploaded documents
│   ├── vector_store/        # Saved FAISS index
│   └── chat_history/        # Past conversations
│
└── examples/                 # Sample files for testing
```

---

### 1. `config.py` - The Settings File

**Purpose**: Store all configuration in one place.

**What's inside**:
```python
# Model Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Which embedding model to use
LLM_MODEL = "google/flan-t5-base"                          # Which AI model for answers

# Chunking Settings  
CHUNK_SIZE = 500        # How many characters per chunk
CHUNK_OVERLAP = 50      # How many characters overlap between chunks

# Retrieval Settings
TOP_K = 3               # How many chunks to retrieve

# File Paths
VECTOR_STORE_PATH = "data/vector_store"
UPLOAD_FOLDER = "data/uploaded_files"
```

**Why separate config?**: 
- Change settings without touching code
- Easy to experiment with different values
- Professional practice

---

### 2. `file_loader.py` - Reading Documents

**Purpose**: Read text from different file formats.

**How it works**:

```python
# Factory Pattern - Creates the right loader based on file type
class FileLoaderFactory:
    def get_loader(file_extension):
        if extension == ".pdf":
            return PDFLoader()
        elif extension == ".docx":
            return DOCXLoader()
        elif extension == ".txt":
            return TextLoader()
        # ... etc
```

**Supported formats**:
| Format | Library Used | Notes |
|--------|--------------|-------|
| PDF | PyMuPDF, pdfplumber | Extracts text from PDFs |
| DOCX | python-docx | Microsoft Word files |
| TXT | Built-in Python | Plain text |
| MD | markdown | Markdown files |
| CSV | pandas | Spreadsheet data |

**Example usage**:
```python
loader = FileLoaderFactory.get_loader(".pdf")
text = loader.load("company_policy.pdf")
# text = "Chapter 1: Introduction..."
```

---

### 3. `text_processor.py` - Chunking Text

**Purpose**: Break large text into smaller, manageable pieces.

**How it works**:

```python
class TextProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap  # Move back a bit for overlap
        return chunks
```

**Visual example**:
```
Original Text (1000 characters):
[===========================================]

After Chunking (chunk_size=500, overlap=50):
Chunk 1: [====================]
Chunk 2:                [====================]
                        ↑ overlap
```

---

### 4. `vector_store.py` - Storing and Searching Vectors

**Purpose**: Store document embeddings and find similar ones quickly.

**Key operations**:

```python
class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatL2(384)  # 384 = embedding dimensions
        self.documents = []  # Store original text
    
    def add_documents(self, texts, embeddings):
        """Store documents and their vectors"""
        self.index.add(embeddings)
        self.documents.extend(texts)
    
    def search(self, query_embedding, k=3):
        """Find k most similar documents"""
        distances, indices = self.index.search(query_embedding, k)
        return [self.documents[i] for i in indices[0]]
    
    def save(self, path):
        """Save to disk"""
        faiss.write_index(self.index, path)
    
    def load(self, path):
        """Load from disk"""
        self.index = faiss.read_index(path)
```

**How FAISS search works**:
```
Query Vector:     [0.3, 0.4, 0.5, ...]

Stored Vectors:
  Doc 1: [0.1, 0.2, 0.3, ...]  → Distance: 0.8 (far)
  Doc 2: [0.31, 0.39, 0.51, ...] → Distance: 0.02 (very close!) ✓
  Doc 3: [0.9, 0.8, 0.7, ...]  → Distance: 1.2 (far)

Result: Doc 2 is most similar
```

---

### 5. `rag_pipeline.py` - The Main Engine

**Purpose**: Connect all components and orchestrate the RAG process.

**How it works**:

```python
class RAGPipeline:
    def __init__(self):
        # Initialize all components
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.llm = T5ForConditionalGeneration.from_pretrained('google/flan-t5-base')
        self.vector_store = VectorStore()
        self.text_processor = TextProcessor()
    
    def add_document(self, file_path):
        """Process and store a document"""
        # Step 1: Load document
        text = FileLoader.load(file_path)
        
        # Step 2: Chunk text
        chunks = self.text_processor.process(text)
        
        # Step 3: Create embeddings
        embeddings = self.embedding_model.encode(chunks)
        
        # Step 4: Store in vector database
        self.vector_store.add_documents(chunks, embeddings)
    
    def query(self, question):
        """Answer a question"""
        # Step 1: Convert question to vector
        question_embedding = self.embedding_model.encode(question)
        
        # Step 2: Find relevant chunks
        relevant_chunks = self.vector_store.search(question_embedding, k=3)
        
        # Step 3: Create prompt
        context = "\n".join(relevant_chunks)
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        
        # Step 4: Generate answer
        answer = self.llm.generate(prompt)
        
        return answer
```

---

### 6. `multimodal_rag.py` - Adding Image Support

**Purpose**: Extend RAG to handle images alongside text.

**How it works**:

```python
class MultiModalRAG(RAGPipeline):
    def __init__(self):
        super().__init__()
        # Add CLIP model for images
        self.clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
        self.image_index = faiss.IndexFlatL2(512)  # CLIP uses 512 dimensions
    
    def add_image(self, image_path):
        """Process and store an image"""
        image = load_image(image_path)
        embedding = self.clip_model.encode_image(image)
        self.image_index.add(embedding)
    
    def search_images(self, text_query):
        """Find images matching a text description"""
        text_embedding = self.clip_model.encode_text(text_query)
        similar_images = self.image_index.search(text_embedding, k=3)
        return similar_images
```

---

### 7. `app.py` - The User Interface

**Purpose**: Create the web application users interact with.

**Structure**:

```python
import streamlit as st
from modules.rag_pipeline import RAGPipeline

# Page configuration
st.set_page_config(page_title="Document Chat", layout="wide")

# Initialize session state (memory)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()

# Sidebar - Settings and file upload
with st.sidebar:
    st.title("Settings")
    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])
    
    if uploaded_file:
        # Process uploaded file
        st.session_state.rag_pipeline.add_document(uploaded_file)
        st.success("Document processed!")

# Main area - Chat interface
st.title("Chat with your Documents")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_question = st.chat_input("Ask a question about your documents")

if user_question:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Get answer from RAG
    answer = st.session_state.rag_pipeline.query(user_question)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": answer})
    
    # Display answer
    with st.chat_message("assistant"):
        st.write(answer)
```

---

## Step-by-Step: What Happens When You Ask a Question

### Example Scenario

**You uploaded**: `company_policy.pdf` (50 pages)
**You ask**: "How many vacation days do employees get?"

### Step 1: Document Processing (happens when you upload)

```
┌─────────────────────────────────────────────────────────┐
│                    company_policy.pdf                    │
│                      (50 pages)                         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ PDF      │
                    │ Loader   │
                    └────┬─────┘
                         │
              Extracted Text (50,000 characters)
                         │
                         ▼
                    ┌──────────┐
                    │ Chunker  │
                    │ (500 ch) │
                    └────┬─────┘
                         │
              100 Chunks (500 characters each)
                         │
                         ▼
                    ┌──────────┐
                    │ Embedding│
                    │ Model    │
                    └────┬─────┘
                         │
              100 Vectors (384 numbers each)
                         │
                         ▼
                    ┌──────────┐
                    │ FAISS    │
                    │ Index    │
                    └──────────┘
                    (Stored!)
```

### Step 2: Question Processing (happens when you ask)

```
┌─────────────────────────────────────────────────────────┐
│    "How many vacation days do employees get?"           │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ Embedding│
                    │ Model    │
                    └────┬─────┘
                         │
              Question Vector: [0.23, 0.45, 0.67, ...]
                         │
                         ▼
                    ┌──────────┐
                    │ FAISS    │
                    │ Search   │
                    └────┬─────┘
                         │
              Compare with 100 stored vectors
                         │
                         ▼
              Found 3 most similar chunks:
              
              Chunk 47: "Annual leave policy: Full-time 
                        employees are entitled to 20 days 
                        of paid vacation per year..."
                        
              Chunk 48: "...vacation days can be carried 
                        over to the next year, up to a 
                        maximum of 5 days..."
                        
              Chunk 52: "Part-time employees receive 
                        vacation days proportional to 
                        their working hours..."
```

### Step 3: Answer Generation

```
┌─────────────────────────────────────────────────────────┐
│                      PROMPT                              │
│                                                          │
│ Context:                                                 │
│ Annual leave policy: Full-time employees are entitled   │
│ to 20 days of paid vacation per year...                 │
│ ...vacation days can be carried over to the next year,  │
│ up to a maximum of 5 days...                            │
│ Part-time employees receive vacation days proportional  │
│ to their working hours...                               │
│                                                          │
│ Question: How many vacation days do employees get?       │
│                                                          │
│ Answer:                                                  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ Flan-T5  │
                    │ LLM      │
                    └────┬─────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ "Full-time employees are entitled to 20 days of paid   │
│  vacation per year. Up to 5 unused days can be carried │
│  over to the next year. Part-time employees receive    │
│  vacation days proportional to their working hours."   │
└─────────────────────────────────────────────────────────┘
```

---

## Technologies Used

### Python Libraries

| Library | Purpose | Why We Use It |
|---------|---------|---------------|
| `streamlit` | Web interface | Build UI with minimal code |
| `torch` | Deep learning | Powers AI models |
| `transformers` | AI models | Access to pre-trained models |
| `sentence-transformers` | Embeddings | Convert text to vectors |
| `faiss-cpu` | Vector search | Fast similarity search |
| `pypdf` / `pymupdf` | PDF reading | Extract text from PDFs |
| `python-docx` | Word reading | Extract text from DOCX |
| `pandas` | Data handling | Process CSV files |
| `Pillow` | Image processing | Handle images for multimodal |

### AI Models

| Model | Purpose | Size | Speed |
|-------|---------|------|-------|
| `all-MiniLM-L6-v2` | Text embeddings | 80 MB | Very fast |
| `flan-t5-base` | Answer generation | 250 MB | Fast |
| `clip-vit-base-patch32` | Image understanding | 350 MB | Fast |

---

## Real-World Analogy

### Think of RAG as a Smart Librarian

**Traditional Search (Google-style)**:
- You: "Books about cooking"
- Librarian: Here are all books with "cooking" in the title
- Problem: Misses books titled "Culinary Arts" or "Chef's Guide"

**RAG System (Smart Librarian)**:
- You: "Books about cooking"
- Librarian: 
  1. Understands you want food preparation content
  2. Searches by meaning, not just keywords
  3. Finds "Culinary Arts", "Chef's Guide", "Kitchen Mastery"
  4. Reads relevant sections
  5. Summarizes: "Based on these 3 books, here's what you need to know about cooking..."

### The Complete Analogy

| RAG Component | Library Analogy |
|---------------|-----------------|
| Documents | Books in the library |
| Chunking | Breaking books into chapters/sections |
| Embeddings | Cataloging books by topic/meaning |
| Vector Store | The card catalog system |
| Retrieval | Finding relevant books |
| LLM | The librarian who reads and summarizes |
| User Interface | The front desk where you ask questions |

---

## Summary: The 5-Minute Explanation

1. **Upload documents** → System reads and breaks them into small chunks
2. **Create embeddings** → Each chunk is converted to numbers (vectors)
3. **Store vectors** → All vectors are saved in FAISS database
4. **Ask question** → Your question is also converted to a vector
5. **Find similar** → FAISS finds chunks most similar to your question
6. **Generate answer** → AI reads those chunks and writes an answer

**That's RAG in a nutshell!** 🎉

---

## Next Steps for Learning

1. **Run the project** and experiment with different documents
2. **Change config values** (chunk size, top_k) and see the difference
3. **Read the code** line by line with this guide
4. **Try different models** (swap Flan-T5 for a larger model)
5. **Add new file formats** (practice the Factory pattern)

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│                 RAG QUICK REFERENCE                     │
├────────────────────────────────────────────────────────┤
│                                                         │
│  EMBEDDING MODEL: all-MiniLM-L6-v2 (384 dimensions)    │
│  LLM: google/flan-t5-base (250M parameters)            │
│  VECTOR STORE: FAISS IndexFlatL2                       │
│  CHUNK SIZE: 500 characters                            │
│  CHUNK OVERLAP: 50 characters                          │
│  TOP-K RETRIEVAL: 3 chunks                             │
│                                                         │
│  FLOW: Document → Chunk → Embed → Store → Retrieve →   │
│        Generate → Answer                                │
│                                                         │
│  RUN: streamlit run app.py                             │
│  URL: http://localhost:8501                            │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

*This guide was created to help beginners understand every aspect of this RAG project. Happy learning! 🚀*
