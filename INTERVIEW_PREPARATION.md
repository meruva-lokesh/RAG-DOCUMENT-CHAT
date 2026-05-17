# 🎯 Interview Preparation Guide: Universal Document Chat (RAG Project)

A comprehensive guide covering everything an interviewer may ask about this RAG-based Document Q&A system.

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Core RAG Concepts](#2-core-rag-concepts)
3. [Embeddings & Vector Search](#3-embeddings--vector-search)
4. [Chunking Strategy](#4-chunking-strategy)
5. [LLM & Generation](#5-llm--generation)
6. [Multimodal Support](#6-multimodal-support)
7. [System Design](#7-system-design)
8. [Code Architecture & Design Patterns](#8-code-architecture--design-patterns)
9. [Evaluation & Metrics](#9-evaluation--metrics)
10. [Advanced & Challenging Questions](#10-advanced--challenging-questions)
11. [Quick Reference Card](#11-quick-reference-card)
12. [Code Snippets to Explain](#12-code-snippets-to-explain)
13. [Questions to Ask the Interviewer](#13-questions-to-ask-the-interviewer)

---

## 1. Project Overview

### 📌 One-Line Description
> A Python-based Generative AI application that enables users to upload documents and interact with them through natural language chat using RAG (Retrieval-Augmented Generation).

### 📌 Key Features
- **Multi-Format Support**: PDF, TXT, MD, DOCX, CSV files
- **Intelligent Retrieval**: FAISS vector database for fast similarity search
- **AI-Powered Answers**: HuggingFace open-source models (Flan-T5)
- **Citation Tracking**: Every answer includes source references (file name, page numbers)
- **Multimodal**: Supports text + image retrieval from PDFs
- **Persistent Storage**: Documents, embeddings, and chat history saved to disk
- **Modern UI**: Streamlit-based web interface

### 📌 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` |
| LLM | `google/flan-t5-base` |
| Image Model | `CLIP-ViT-B-32` |
| Vector Database | FAISS |
| Web Framework | Streamlit |
| PDF Processing | PyMuPDF, pdfplumber |
| Document Processing | python-docx, pandas |

### 📌 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INDEXING PIPELINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📄 Document    →    📝 Text         →    ✂️ Chunking    →    🧠 Embedding   │
│  Upload              Extraction           (500 chars)         (384 dim)     │
│                                                                    ↓        │
│                                                              🗄️ FAISS      │
│                                                              Vector Index   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            QUERY PIPELINE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❓ User        →    🧠 Query        →    🔍 Similarity   →    📚 Top-K     │
│  Question            Embedding            Search              Chunks        │
│                                                                    ↓        │
│                      💬 Answer       ←    🤖 LLM          ←    📋 Context   │
│                      + Sources            Generation           Building     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core RAG Concepts

### ❓ Q: What is RAG and why did you use it?

**Answer:**
RAG (Retrieval-Augmented Generation) is a technique that combines retrieval-based and generative approaches for question answering. Instead of relying solely on an LLM's training data, we:

1. **Retrieve** relevant context from a document corpus
2. **Augment** the LLM prompt with this context
3. **Generate** an answer grounded in the retrieved information

**Why RAG?**
- ✅ **Reduces hallucination**: Answers are grounded in actual documents
- ✅ **Works with private data**: Can answer questions about documents the LLM was never trained on
- ✅ **No fine-tuning needed**: Cheaper and faster than training custom models
- ✅ **Up-to-date information**: Documents can be updated without retraining
- ✅ **Traceable**: Can cite sources for every answer

### ❓ Q: Explain the complete RAG pipeline flow

**Answer:**

**Phase 1: Indexing (Offline)**
```
1. Document Upload → User uploads PDF/TXT/DOCX/CSV
2. Text Extraction → Extract raw text using format-specific loaders
3. Chunking → Split into 500-character overlapping chunks
4. Embedding → Convert chunks to 384-dimensional vectors using sentence-transformers
5. Storage → Store embeddings in FAISS index + metadata in parallel arrays
```

**Phase 2: Querying (Online)**
```
1. Question Input → User types natural language question
2. Query Embedding → Convert question to same 384-dim vector space
3. Similarity Search → FAISS finds top-5 most similar chunks (L2 distance)
4. Filtering → Remove chunks below similarity threshold (0.3)
5. Context Building → Concatenate retrieved chunks with source info
6. LLM Generation → Flan-T5 generates answer based on context + question
7. Response → Return answer with source citations
```

### ❓ Q: What's the difference between RAG and Fine-tuning?

| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| **Data Privacy** | Documents stay local | Data used in training |
| **Cost** | Low (no training) | High (GPU compute) |
| **Updates** | Instant (re-index docs) | Requires retraining |
| **Accuracy** | Depends on retrieval quality | Depends on training data |
| **Hallucination** | Lower (grounded) | Can still hallucinate |
| **Best For** | Document Q&A, knowledge bases | Style transfer, specific tasks |

---

## 3. Embeddings & Vector Search

### ❓ Q: What is an embedding and why do we need it?

**Answer:**
An embedding is a **dense vector representation** of text that captures semantic meaning. Words/sentences with similar meanings have similar vectors.

**Why needed:**
- Computers can't understand text directly
- Embeddings enable **semantic search** (meaning-based, not keyword-based)
- Similar content clusters together in vector space

**Example:**
```
"dog" → [0.2, 0.5, 0.1, ...]
"puppy" → [0.21, 0.48, 0.12, ...]  # Similar vectors!
"car" → [0.8, 0.1, 0.9, ...]       # Different vector
```

### ❓ Q: Why did you choose `all-MiniLM-L6-v2`?

**Answer:**
- **Lightweight**: Only 22M parameters, fast inference
- **384 dimensions**: Good balance between quality and storage
- **Pre-trained for similarity**: Optimized for semantic textual similarity tasks
- **Open-source**: Free to use, no API costs
- **Benchmarks**: Top performer on sentence similarity benchmarks for its size

**Alternatives considered:**
- `all-mpnet-base-v2`: Better quality, but slower (768 dim)
- OpenAI `text-embedding-ada-002`: Best quality, but paid API
- `e5-large`: Excellent quality, but heavier

### ❓ Q: What is FAISS and why did you choose it?

**Answer:**
FAISS (Facebook AI Similarity Search) is a library for efficient similarity search of dense vectors.

**Why FAISS:**
- ✅ **Speed**: Handles millions of vectors in milliseconds
- ✅ **Open-source**: Free, well-maintained by Meta
- ✅ **Flexible**: Supports various index types (Flat, IVF, HNSW)
- ✅ **Local**: Runs entirely on your machine, no data leaves

**Alternatives:**
| Database | Type | Best For |
|----------|------|----------|
| Pinecone | Managed | Production, no DevOps |
| Chroma | Embedded | Simple projects |
| Weaviate | Self-hosted | Hybrid search |
| Milvus | Distributed | Large scale |
| Qdrant | Self-hosted | Filtering + search |

### ❓ Q: What is L2 distance vs Cosine similarity?

**Answer:**

**L2 (Euclidean) Distance:**
- Measures straight-line distance between two points
- Formula: `√Σ(a_i - b_i)²`
- Affected by vector magnitude
- Lower = more similar

**Cosine Similarity:**
- Measures angle between vectors
- Formula: `(A·B) / (||A|| × ||B||)`
- Normalized, ignores magnitude
- Higher = more similar

**In my project:** I use L2 distance (`IndexFlatL2`), but since sentence-transformers produces normalized embeddings, L2 and cosine produce equivalent rankings.

### ❓ Q: How does FAISS search work internally?

**Answer:**

For `IndexFlatL2` (what I use):
1. **Brute-force search**: Compares query against ALL vectors
2. **Optimized**: Uses SIMD instructions for fast distance computation
3. **Exact**: Guarantees finding the true nearest neighbors

For **larger datasets**, you'd use approximate methods:
- **IVF (Inverted File)**: Clusters vectors, only searches relevant clusters
- **HNSW (Hierarchical Navigable Small World)**: Graph-based, very fast
- **PQ (Product Quantization)**: Compresses vectors for memory efficiency

---

## 4. Chunking Strategy

### ❓ Q: Why do we need to chunk documents?

**Answer:**
1. **LLM context limits**: Models have token limits (Flan-T5: ~512 tokens)
2. **Precise retrieval**: Smaller chunks = more targeted results
3. **Reduced noise**: Large chunks include irrelevant information
4. **Cost efficiency**: Fewer tokens = cheaper API calls (for paid models)

### ❓ Q: Why 500 characters? How did you decide?

**Answer:**
**500 characters ≈ 100-125 tokens** (average ~4 chars/token)

**Considerations:**
- **Too small (<200)**: Loses context, fragments sentences
- **Too large (>1000)**: Includes irrelevant info, hurts precision
- **500-512**: Sweet spot for most Q&A tasks

**I would tune this based on:**
- Document type (technical docs need larger chunks)
- Query patterns (specific questions → smaller chunks)
- Evaluation metrics (test different sizes)

### ❓ Q: What is chunk overlap and why 50 characters?

**Answer:**
**Overlap** = Characters shared between consecutive chunks

**Why overlap:**
```
Without overlap:
Chunk 1: "...the meeting is scheduled for"
Chunk 2: "Tuesday at 3 PM in the conference room..."
→ Question about meeting time might miss context!

With overlap:
Chunk 1: "...the meeting is scheduled for Tuesday at 3"
Chunk 2: "for Tuesday at 3 PM in the conference room..."
→ Information preserved in at least one chunk!
```

**50 characters (10% of chunk size)**: Captures most sentence boundaries without excessive duplication.

### ❓ Q: How do you handle sentence boundaries?

**Answer:**
My `TextChunker` class implements smart boundary detection:

```python
# Look for natural break points near chunk end
sentence_endings = ['. ', '! ', '? ', '\n\n']

# Search backwards from target end position
for i in range(end, end - search_range, -1):
    for ending in sentence_endings:
        if text[i:i+len(ending)] == ending:
            best_break = i + len(ending)
            break
```

This ensures chunks end at sentence boundaries when possible, not mid-word.

---

## 5. LLM & Generation

### ❓ Q: Why Flan-T5 instead of GPT-4 or ChatGPT?

**Answer:**

| Aspect | Flan-T5 (My Choice) | GPT-4/ChatGPT |
|--------|---------------------|---------------|
| **Cost** | Free | $0.01-0.06/1K tokens |
| **Privacy** | Data stays local | Data sent to OpenAI |
| **Latency** | ~1s local | Network latency |
| **Quality** | Good for Q&A | Best-in-class |
| **Control** | Full control | API limits |
| **Offline** | Works offline | Needs internet |

**For production**, I'd consider:
- GPT-4 for highest quality
- Claude for long context
- Llama 2/3 for open-source + quality balance

### ❓ Q: What is a Seq2Seq model?

**Answer:**
**Sequence-to-Sequence** models have an encoder-decoder architecture:

```
Input: "What is the capital of France?"
       ↓
   [ENCODER] → Understands input, creates representation
       ↓
   [DECODER] → Generates output token by token
       ↓
Output: "Paris"
```

**Flan-T5** is a Seq2Seq model fine-tuned on instruction-following tasks.

### ❓ Q: What is temperature in LLM generation?

**Answer:**
Temperature controls **randomness** in token selection:

```
Temperature = 0.0: Always pick highest probability token (deterministic)
Temperature = 0.7: Balanced (my setting)
Temperature = 1.0: More random/creative
Temperature > 1.0: Very random, often incoherent
```

**For Q&A systems**: Lower temperature (0.3-0.7) is better for factual accuracy.

### ❓ Q: What other generation parameters exist?

**Answer:**

| Parameter | Description | My Setting |
|-----------|-------------|------------|
| `max_length` | Maximum tokens to generate | 300 |
| `temperature` | Randomness | 0.7 |
| `top_k` | Consider only top-k tokens | 50 (default) |
| `top_p` | Nucleus sampling threshold | 0.9 (default) |
| `repetition_penalty` | Penalize repeated tokens | 1.0 |
| `do_sample` | Enable sampling | True |

---

## 6. Multimodal Support

### ❓ Q: How do you handle images in documents?

**Answer:**
My `MultiModalRAG` class extends the standard pipeline:

1. **Extract images** from PDFs using PyMuPDF (`fitz`)
2. **Filter** small images (<2KB, likely icons)
3. **Embed images** using CLIP model
4. **Store** in separate image index
5. **Query** searches both text AND image embeddings
6. **Return** relevant images alongside text answers

### ❓ Q: What is CLIP and how does it work?

**Answer:**
**CLIP (Contrastive Language-Image Pre-training)** by OpenAI:

- Trained on 400M image-text pairs from the internet
- Creates **aligned embeddings** for both images AND text
- A text query can find relevant images (and vice versa)

**How it works:**
```
Text: "a dog playing in the park"  → [0.2, 0.5, 0.1, ...] 
Image: [photo of dog in park]       → [0.21, 0.48, 0.12, ...]
                                       ↑ Similar vectors!
```

### ❓ Q: Why did you use CLIP-ViT-B-32?

**Answer:**
- **ViT-B/32**: Vision Transformer with 32x32 patches
- **Balance**: Good quality vs speed trade-off
- **Compatible**: Works with sentence-transformers library
- **768-dim embeddings**: Same API as text models

---

## 7. System Design

### ❓ Q: How would you scale this for millions of documents?

**Answer:**

**1. Vector Database:**
- Switch from `IndexFlatL2` to `IndexIVFFlat` or `IndexHNSW`
- Or use managed solution (Pinecone, Weaviate)

**2. Processing:**
- Async document processing with Celery + Redis
- Batch embedding generation
- Distributed workers

**3. Storage:**
- Shard by document type or date
- Use cloud storage (S3) for documents
- Separate metadata in PostgreSQL

**4. Caching:**
- Cache frequent queries
- Cache embeddings for common terms

**5. Infrastructure:**
```
                    ┌─────────────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ API 1   │       │ API 2   │       │ API 3   │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        ┌─────▼─────┐            ┌─────▼─────┐
        │ FAISS     │            │ PostgreSQL│
        │ (Vectors) │            │ (Metadata)│
        └───────────┘            └───────────┘
```

### ❓ Q: How do you handle document updates?

**Answer:**

**Current approach (simple):**
- Re-index entire document on update
- Works for small document sets

**Better approach:**
```python
def update_document(doc_id, new_content):
    # 1. Delete old chunks
    old_chunk_ids = get_chunks_by_doc_id(doc_id)
    vector_store.delete(old_chunk_ids)
    
    # 2. Process new content
    new_chunks = chunk_document(new_content)
    new_embeddings = embed_chunks(new_chunks)
    
    # 3. Add new chunks
    vector_store.add(new_chunks, new_embeddings)
```

### ❓ Q: What's the latency breakdown?

**Answer:**

| Step | Time | Notes |
|------|------|-------|
| Query embedding | ~50ms | sentence-transformers |
| FAISS search | ~10ms | For 10K chunks |
| LLM generation | 500ms-2s | Depends on length |
| **Total** | **~1-3s** | Per query |

**Bottleneck**: LLM generation. Can optimize with:
- GPU acceleration
- Model quantization (INT8)
- Streaming responses

### ❓ Q: How do you handle concurrent users?

**Answer:**

**Streamlit limitation:** Single-threaded by default

**Solutions:**
1. **Streamlit caching**: `@st.cache_resource` for models
2. **Session isolation**: Each user gets their own session state
3. **Production**: Deploy with multiple workers (Gunicorn + FastAPI)

```python
# Current: Models loaded once, shared across sessions
@st.cache_resource
def load_models():
    return RAGPipeline()
```

---

## 8. Code Architecture & Design Patterns

### ❓ Q: Explain the design patterns you used

**Answer:**

**1. Factory Pattern** (`FileLoaderFactory`):
```python
class FileLoaderFactory:
    @staticmethod
    def load_file(file_path, file_name):
        ext = os.path.splitext(file_name)[1].lower()
        
        if ext == '.pdf':
            return PDFLoader().load(file_path, file_name)
        elif ext in ['.txt', '.md']:
            return TextLoader().load(file_path, file_name)
        # ... etc
```
**Why:** Single entry point to create appropriate loader based on file type.

**2. Strategy Pattern** (Different Loaders):
```python
class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path, file_name):
        pass

class PDFLoader(BaseLoader): ...
class TextLoader(BaseLoader): ...
class DocxLoader(BaseLoader): ...
```
**Why:** Interchangeable algorithms for loading different file types.

**3. Inheritance** (`MultiModalRAG` extends `RAGPipeline`):
```python
class MultiModalRAG(RAGPipeline):
    def __init__(self):
        super().__init__()  # Get all text RAG functionality
        self.clip_model = ...  # Add image capabilities
```
**Why:** Extend base functionality without modifying it.

**4. Singleton-like** (Session State):
```python
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()
```
**Why:** Single instance of expensive models shared across requests.

### ❓ Q: Why separate modules?

**Answer:**
**Separation of Concerns:**

```
modules/
├── file_loader.py    # Only handles file reading
├── text_processor.py # Only handles chunking
├── vector_store.py   # Only handles FAISS operations
├── rag_pipeline.py   # Orchestrates everything
└── multimodal_rag.py # Extends with image support
```

**Benefits:**
- ✅ Easier testing (mock individual components)
- ✅ Easier maintenance (change one without affecting others)
- ✅ Reusable (use vector_store in different projects)
- ✅ Clear responsibilities

### ❓ Q: Why use a config file?

**Answer:**
```python
# config.py
CHUNK_SIZE = 500
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K_RETRIEVAL = 5
```

**Benefits:**
- ✅ **Single source of truth** for all settings
- ✅ **Easy tuning** without code changes
- ✅ **Environment-specific** configs (dev/prod)
- ✅ **12-factor app** principle compliance

---

## 9. Evaluation & Metrics

### ❓ Q: How would you evaluate RAG quality?

**Answer:**

**Retrieval Metrics:**

| Metric | Formula | Measures |
|--------|---------|----------|
| **Recall@K** | Relevant in top-K / Total relevant | Coverage |
| **Precision@K** | Relevant in top-K / K | Accuracy |
| **MRR** | 1/rank of first relevant | Ranking quality |
| **NDCG** | Normalized DCG | Graded relevance |

**Generation Metrics:**

| Metric | Measures |
|--------|----------|
| **Faithfulness** | Is answer grounded in context? |
| **Answer Relevance** | Does it answer the question? |
| **Context Relevance** | Is retrieved context useful? |
| **ROUGE/BLEU** | Overlap with reference answers |

**Tools:**
- **RAGAS**: Open-source RAG evaluation framework
- **LangSmith**: LangChain's evaluation platform
- **TruLens**: Feedback-based evaluation

### ❓ Q: How do you handle "I don't know" cases?

**Answer:**

**My approach:**
```python
SIMILARITY_THRESHOLD = 0.3

results = []
for idx, similarity in zip(indices, similarities):
    if similarity >= SIMILARITY_THRESHOLD:  # Filter low confidence
        results.append(...)

if not results:
    return "I couldn't find relevant information in the documents."
```

**Better approach:**
- Add explicit "I don't know" training
- Use confidence scoring
- Return "Based on the documents, I cannot find..." with partial matches

### ❓ Q: What's your similarity threshold and why 0.3?

**Answer:**
```python
SIMILARITY_THRESHOLD = 0.3
```

- **0.0-0.2**: Likely irrelevant
- **0.3-0.5**: Somewhat relevant (my threshold)
- **0.5-0.7**: Relevant
- **0.7+**: Highly relevant

**0.3 chosen because:**
- Allows partial matches (useful for paraphrased queries)
- Filters obvious noise
- Should be tuned based on evaluation data

---

## 10. Advanced & Challenging Questions

### ❓ Q: What are the limitations of your system?

**Answer:**

1. **Context window limit**: Can only use top-K chunks, may miss info scattered across documents
2. **Semantic-only search**: Doesn't handle exact keyword matches well
3. **Single-hop reasoning**: Can't combine info from multiple documents effectively
4. **No query understanding**: Doesn't rephrase or expand ambiguous queries
5. **Cold start**: First query is slow (model loading)
6. **No incremental updates**: Deleting documents requires rebuilding index

### ❓ Q: How would you add hybrid search?

**Answer:**
Combine **semantic search** (vectors) with **keyword search** (BM25):

```python
from rank_bm25 import BM25Okapi

class HybridSearch:
    def search(self, query, k=5):
        # 1. Semantic search
        semantic_results = faiss_search(query_embedding, k*2)
        
        # 2. Keyword search
        bm25_results = bm25.get_top_n(query.split(), documents, n=k*2)
        
        # 3. Combine with Reciprocal Rank Fusion
        combined = reciprocal_rank_fusion(semantic_results, bm25_results)
        
        return combined[:k]

def reciprocal_rank_fusion(list1, list2, k=60):
    scores = {}
    for rank, doc in enumerate(list1):
        scores[doc] = scores.get(doc, 0) + 1/(k + rank)
    for rank, doc in enumerate(list2):
        scores[doc] = scores.get(doc, 0) + 1/(k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```

### ❓ Q: How do you handle hallucination?

**Answer:**

1. **Grounding**: Prompt instructs to only use provided context
```
"Answer the question based ONLY on the following context. 
If the answer is not in the context, say 'I don't know'."
```

2. **Citation**: Always show sources for verification

3. **Low temperature**: Reduce creativity (0.3-0.5 for factual Q&A)

4. **Retrieval quality**: Better retrieval = less hallucination

5. **Post-processing**: Verify entities in answer exist in context

### ❓ Q: How would you implement reranking?

**Answer:**
Reranking improves retrieval by using a more powerful model on top-K results:

```python
from sentence_transformers import CrossEncoder

class RerankedRAG:
    def __init__(self):
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    def search(self, query, k=5):
        # 1. Get more candidates than needed
        candidates = self.vector_store.search(query, k=20)
        
        # 2. Rerank with cross-encoder
        pairs = [[query, c['text']] for c in candidates]
        scores = self.reranker.predict(pairs)
        
        # 3. Sort by reranker scores
        reranked = sorted(zip(candidates, scores), 
                         key=lambda x: x[1], reverse=True)
        
        return [c for c, s in reranked[:k]]
```

### ❓ Q: How would you handle multi-document reasoning?

**Answer:**

**Problem:** "Compare the revenue in Q1 2023 report vs Q2 2023 report"

**Solutions:**

1. **Query decomposition:**
```python
sub_queries = decompose_query(query)
# ["What is revenue in Q1 2023?", "What is revenue in Q2 2023?"]
results = [rag.query(q) for q in sub_queries]
final_answer = synthesize(results)
```

2. **Document metadata filtering:**
```python
q1_chunks = search(query, filter={"document": "Q1_2023_report"})
q2_chunks = search(query, filter={"document": "Q2_2023_report"})
```

3. **Agentic RAG:** Use LLM to iteratively search and reason

### ❓ Q: How would you implement streaming responses?

**Answer:**

```python
# Using HuggingFace TextIteratorStreamer
from transformers import TextIteratorStreamer
from threading import Thread

def generate_streaming(prompt):
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)
    
    inputs = tokenizer(prompt, return_tensors="pt")
    
    generation_kwargs = dict(
        inputs, 
        streamer=streamer, 
        max_new_tokens=300
    )
    
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    
    for text in streamer:
        yield text  # Stream each token
```

---

## 11. Quick Reference Card

### 🔧 Technical Specifications

| Component | Value |
|-----------|-------|
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Embedding Dimension** | 384 |
| **LLM** | `google/flan-t5-base` |
| **LLM Parameters** | ~250M |
| **Image Model** | `CLIP-ViT-B-32` |
| **Vector Database** | FAISS (IndexFlatL2) |
| **Distance Metric** | L2 (Euclidean) |
| **Chunk Size** | 500 characters |
| **Chunk Overlap** | 50 characters |
| **Top-K Retrieval** | 5 chunks |
| **Similarity Threshold** | 0.3 |
| **Max Answer Length** | 300 tokens |
| **Temperature** | 0.7 |
| **Supported Formats** | PDF, TXT, MD, DOCX, CSV |

### 📊 Performance Characteristics

| Metric | Value |
|--------|-------|
| Query embedding time | ~50ms |
| FAISS search (10K chunks) | ~10ms |
| LLM generation | 500ms-2s |
| Total query latency | 1-3 seconds |
| Memory (models loaded) | ~2-4 GB |

---

## 12. Code Snippets to Explain

### 📌 Embedding Generation
```python
def create_embeddings(self, texts: List[str]) -> np.ndarray:
    """Convert texts to embeddings using sentence-transformers."""
    embeddings = self.embedding_model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        batch_size=32
    )
    return embeddings
```

### 📌 FAISS Search
```python
def search(self, query_embedding: np.ndarray, k: int = 5):
    query = query_embedding.astype('float32').reshape(1, -1)
    distances, indices = self.index.search(query, k)
    
    # Convert L2 distance to similarity score
    similarities = np.exp(-distances[0])
    
    results = []
    for idx, sim in zip(indices[0], similarities):
        if sim >= self.threshold:
            results.append({
                'text': self.chunks[idx],
                'metadata': self.metadata[idx],
                'score': float(sim)
            })
    return results
```

### 📌 Answer Generation
```python
def generate_answer(self, question: str, context: str) -> str:
    prompt = f"""Answer the question based on the context below.

Context: {context}

Question: {question}

Answer:"""
    
    inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
    
    outputs = self.llm.generate(
        **inputs,
        max_length=300,
        temperature=0.7,
        do_sample=True
    )
    
    return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

---

## 13. Questions to Ask the Interviewer

Show engagement by asking thoughtful questions:

1. **"What vector database does your team currently use for RAG systems?"**

2. **"How do you handle evaluation of RAG systems in production? Do you use RAGAS or similar frameworks?"**

3. **"Do you implement any reranking after the initial retrieval step?"**

4. **"What's your approach to handling document updates - full re-indexing or incremental?"**

5. **"Are you using any agentic RAG patterns for complex multi-step queries?"**

6. **"How do you handle multimodal content (tables, charts, images) in your RAG pipeline?"**

---

## 📝 Final Checklist Before Interview

- [ ] Can explain RAG pipeline end-to-end
- [ ] Know why each technology was chosen
- [ ] Understand embeddings, FAISS, chunking
- [ ] Can discuss trade-offs and alternatives
- [ ] Know how to scale the system
- [ ] Understand evaluation metrics
- [ ] Can explain code architecture
- [ ] Prepared questions for interviewer

---

**Good luck with your interview! 🚀**
