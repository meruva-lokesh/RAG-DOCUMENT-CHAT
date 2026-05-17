"""
RAG Pipeline module - orchestrates the complete Retrieval-Augmented Generation workflow.
Handles embeddings, retrieval, and LLM-based answer generation.
"""

import os
from typing import List, Dict, Any, Optional
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import config
from modules.file_loader import FileLoaderFactory
from modules.text_processor import TextChunker
from modules.vector_store import VectorStore


class RAGPipeline:
    """Complete RAG pipeline for document Q&A."""
    
    def __init__(self):
        """Initialize the RAG pipeline with models and vector store."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Initializing RAG Pipeline on {self.device.upper()}...")
        
        # Load embedding model
        print(f"📥 Loading embedding model: {config.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embedding_model.to(self.device)
        
        # Load LLM for generation
        print(f"📥 Loading LLM: {config.LLM_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL)
        self.llm = AutoModelForSeq2SeqLM.from_pretrained(config.LLM_MODEL)
        self.llm.to(self.device)
        
        # Initialize components
        self.text_chunker = TextChunker()
        self.vector_store = VectorStore()
        
        # Try to load existing vector store
        if self.vector_store.load_from_disk():
            print(f"✅ Loaded existing vector store with {self.vector_store.get_stats()['total_chunks']} chunks")
        else:
            print("📝 Starting with empty vector store")
    
    def process_uploaded_files(self, uploaded_files: List[Any]) -> Dict[str, Any]:
        """
        Process uploaded files and add them to the vector store.
        
        Args:
            uploaded_files: List of Streamlit UploadedFile objects
            
        Returns:
            Dictionary with processing results and statistics
        """
        results = {
            'success': True,
            'files_processed': 0,
            'total_chunks': 0,
            'errors': [],
            'file_details': []
        }
        
        # Track already indexed files to avoid duplicates
        existing_files = self.vector_store.get_stats()['document_files']
        
        all_chunks = []
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            # Skip if already indexed
            if file_name in existing_files:
                results['errors'].append(f"{file_name} is already indexed")
                continue
            
            try:
                # Save file temporarily
                temp_path = os.path.join(config.UPLOADED_FILES_DIR, file_name)
                os.makedirs(config.UPLOADED_FILES_DIR, exist_ok=True)
                
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Load and extract text
                document = FileLoaderFactory.load_file(temp_path, file_name)
                
                # Chunk the document
                chunks = self.text_chunker.chunk_text(document['text'], document['metadata'])
                
                all_chunks.extend(chunks)
                
                results['file_details'].append({
                    'file_name': file_name,
                    'chunks': len(chunks),
                    'type': document['metadata']['file_type']
                })
                results['files_processed'] += 1
                
            except Exception as e:
                results['errors'].append(f"Error processing {file_name}: {str(e)}")
                results['success'] = False
        
        # Generate embeddings and add to vector store
        if all_chunks:
            chunk_texts = [chunk['text'] for chunk in all_chunks]
            embeddings = self.embedding_model.encode(
                chunk_texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            self.vector_store.add_documents(all_chunks, embeddings)
            results['total_chunks'] = len(all_chunks)
            
            # Persist to disk
            self.vector_store.save_to_disk()
            
            # === FEATURE 2: Generate document summaries ===
            summaries = {}
            for file_detail in results['file_details']:
                # Get all chunks for this file
                file_chunks = [chunk for chunk in all_chunks 
                              if chunk['metadata']['file_name'] == file_detail['file_name']]
                if file_chunks:
                    # Use first few chunks to generate summary
                    summary = self.generate_document_summary(file_chunks[:5], file_detail['file_name'])
                    summaries[file_detail['file_name']] = summary
            
            results['summaries'] = summaries
        
        return results
    
    def generate_answer(
        self, 
        question: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate an answer to a question using RAG.
        
        Args:
            question: User's question
            chat_history: Optional list of previous messages [{'role': 'user'/'assistant', 'content': '...'}]
            
        Returns:
            Dictionary with 'answer', 'sources', and metadata
        """
        # Validate input
        if not question or not question.strip():
            return {
                'answer': "Please enter a valid question.",
                'sources': [],
                'context_used': False
            }
        
        question = question.strip()
        
        if self.vector_store.is_empty():
            return {
                'answer': "⚠️ No documents have been uploaded yet. Please upload some documents first to start asking questions!",
                'sources': [],
                'context_used': False
            }
        
        try:
            # Embed the question
            question_embedding = self.embedding_model.encode(
                question,
                convert_to_numpy=True
            )
            
            # Retrieve relevant chunks
            retrieved_chunks = self.vector_store.search(question_embedding)
            
            # Re-rank chunks for better relevance
            retrieved_chunks = self._rerank_chunks(question, retrieved_chunks)
            
            if not retrieved_chunks:
                return {
                    'answer': "I couldn't find any relevant information in your documents to answer this question. Try:\n• Rephrasing your question\n• Using keywords from your documents\n• Asking about specific topics in your uploaded files",
                    'sources': [],
                    'context_used': False
                }
            
            # Build context from retrieved chunks
            context = self._build_context(retrieved_chunks)
            
            # Build prompt
            prompt = self._build_prompt(question, context, chat_history)
            
            # Generate answer
            answer = self._generate_with_llm(prompt)
            
            # Post-process answer for quality
            answer = self._post_process_answer(answer, question)
            
            # Extract sources
            sources = self._extract_sources(retrieved_chunks)
            
            return {
                'answer': answer,
                'sources': sources,
                'context_used': True,
                'num_sources': len(sources)
            }
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                'answer': f"I encountered an error while processing your question. Please try again or rephrase your question.",
                'sources': [],
                'context_used': False,
                'error': str(e)
            }
    
    def _post_process_answer(self, answer: str, question: str) -> str:
        """Clean up and improve the generated answer."""
        if not answer:
            return "I couldn't generate an answer based on the available documents."
        
        answer = answer.strip()
        
        # Remove any leftover prompt artifacts
        artifacts = ["Answer:", "Response:", "A:"]
        for artifact in artifacts:
            if answer.startswith(artifact):
                answer = answer[len(artifact):].strip()
        
        # Ensure answer ends with proper punctuation
        if answer and not answer.endswith(('.', '!', '?', ':')):
            # Find last complete sentence
            last_period = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
            if last_period > len(answer) * 0.5:  # Keep at least half the answer
                answer = answer[:last_period + 1]
            else:
                answer += "."
        
        # If answer is too short, indicate limited information
        if len(answer) < 20:
            answer = f"Based on the documents: {answer}"
        
        return answer
    
    def _rerank_chunks(self, question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-rank retrieved chunks based on keyword overlap and semantic relevance.
        This improves accuracy by prioritizing chunks that directly match question terms.
        """
        if not chunks:
            return chunks
        
        # Extract question keywords (simple tokenization)
        question_lower = question.lower()
        question_words = set(question_lower.split())
        # Remove common stop words
        stop_words = {'what', 'is', 'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'how', 'why', 'when', 'where', 'which', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must', 'for', 'with', 'about', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'on', 'off', 'over', 'under', 'again', 'then', 'once', 'here', 'there', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also'}
        question_keywords = question_words - stop_words
        
        # Score each chunk based on keyword overlap
        for chunk in chunks:
            chunk_text_lower = chunk['text'].lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for kw in question_keywords if kw in chunk_text_lower)
            
            # Bonus for exact phrase match
            exact_match_bonus = 0.2 if question_lower[:20] in chunk_text_lower else 0
            
            # Calculate combined score (original similarity + keyword boost)
            original_score = chunk.get('score', 0.5)
            keyword_boost = min(keyword_matches * 0.05, 0.3)  # Max 30% boost
            
            chunk['rerank_score'] = original_score + keyword_boost + exact_match_bonus
        
        # Sort by reranked score (descending)
        chunks.sort(key=lambda x: x.get('rerank_score', x.get('score', 0)), reverse=True)
        
        # Update display score
        for chunk in chunks:
            if 'rerank_score' in chunk:
                chunk['score'] = chunk['rerank_score']
        
        return chunks
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved chunks with better formatting."""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            source_info = f"[Document {i}: {metadata['file_name']}"
            
            if metadata.get('file_type') == 'pdf' and 'estimated_page' in metadata:
                source_info += f", Page {metadata['estimated_page']}"
            
            # Add relevance score for transparency
            if 'score' in chunk:
                source_info += f", Relevance: {chunk['score']:.0%}"
            
            source_info += "]"
            
            # Clean up the chunk text
            chunk_text = chunk['text'].strip()
            # Remove excessive whitespace
            chunk_text = ' '.join(chunk_text.split())
            
            context_parts.append(f"{source_info}\n{chunk_text}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _build_prompt(
        self, 
        question: str, 
        context: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build the prompt for the LLM (T5-optimized format)."""
        prompt_parts = []
        
        # System instruction for better answers
        prompt_parts.append("You are a helpful assistant that answers questions based on the provided documents.")
        prompt_parts.append("")
        
        # Add context first (T5 prefers context before question)
        prompt_parts.append("Reference Documents:")
        prompt_parts.append(context)
        prompt_parts.append("")
        
        # Add chat history for context continuity
        if chat_history and len(chat_history) > 0:
            prompt_parts.append("Previous conversation:")
            for msg in chat_history[-4:]:  # Last 4 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt_parts.append(f"{role}: {msg['content'][:200]}")
            prompt_parts.append("")
        
        # Add question
        prompt_parts.append(f"Question: {question}")
        prompt_parts.append("")
        
        # Enhanced instruction for complete, clear answers
        prompt_parts.append("Instructions: Based on the reference documents above, provide a detailed, accurate, and easy-to-understand answer. Include specific facts, definitions, and examples from the documents. If the documents contain relevant information, explain it clearly. Answer:")
        
        return "\n".join(prompt_parts)
    
    def _generate_with_llm(self, prompt: str) -> str:
        """Generate answer using the LLM with guaranteed complete output."""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Generate with optimized parameters for comprehensive answers
        outputs = self.llm.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=512,  # Allow longer answers
            min_length=80,       # Ensure substantive answer
            num_beams=6,         # More beams = better quality
            length_penalty=1.5,  # Favor complete answers
            no_repeat_ngram_size=3,
            early_stopping=True,
            do_sample=False,     # Deterministic for factual answers
            repetition_penalty=1.2  # Reduce repetition
        )
        
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Ensure answer ends with proper punctuation
        if answer and not answer.endswith(('.', '!', '?')):
            # Find last complete sentence
            last_period = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
            if last_period > len(answer) // 2:  # If we have at least half the answer
                answer = answer[:last_period + 1]
        
        return answer.strip()
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from retrieved chunks."""
        sources = []
        seen_sources = set()
        
        for chunk in chunks:
            metadata = chunk['metadata']
            file_name = metadata['file_name']
            file_type = metadata.get('file_type', 'unknown')
            
            # Build source identifier
            source_id = file_name
            if file_type == 'pdf' and 'estimated_page' in metadata:
                page = metadata['estimated_page']
                source_id += f"_page_{page}"
                source_detail = f"Page {page}"
            elif file_type in ['txt', 'md']:
                source_detail = f"Line ~{metadata.get('chunk_start', 0)}"
            else:
                source_detail = "Document section"
            
            # Avoid duplicate sources
            if source_id not in seen_sources:
                sources.append({
                    'file_name': file_name,
                    'file_type': file_type,
                    'detail': source_detail,
                    'score': chunk['score']
                })
                seen_sources.add(source_id)
        
        return sources
    
    def reset_documents(self):
        """Clear all documents from the vector store."""
        self.vector_store.clear()
        self.vector_store.save_to_disk()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed documents."""
        return self.vector_store.get_stats()
    
    # === FEATURE 2: Document Summarization ===
    def generate_document_summary(self, chunks: List[Dict[str, Any]], file_name: str) -> str:
        """
        Generate a summary for a document based on its chunks.
        
        Args:
            chunks: List of document chunks
            file_name: Name of the file
            
        Returns:
            Summary string
        """
        # Combine first few chunks for summary
        combined_text = " ".join([chunk['text'] for chunk in chunks])
        
        # Truncate if too long
        max_chars = 2000
        if len(combined_text) > max_chars:
            combined_text = combined_text[:max_chars] + "..."
        
        # Build summary prompt
        prompt = f"""Summarize the following document excerpt in 2-3 concise sentences:

{combined_text}

Summary:"""
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(self.device)
        
        outputs = self.llm.generate(
            **inputs,
            max_new_tokens=100,
            min_length=20,
            temperature=0.5,
            do_sample=True,
            top_p=0.9
        )
        
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary.strip()
    
    # === FEATURE 3: Streaming Answer Generation ===
    def generate_answer_stream(self, question: str, chat_history: Optional[List[Dict[str, str]]] = None):
        """
        Generate an answer with streaming (token by token).
        
        Args:
            question: User's question
            chat_history: Optional chat history
            
        Yields:
            Dictionaries with streaming tokens and final result
        """
        if self.vector_store.is_empty():
            yield {
                'type': 'done',
                'content': "⚠️ No documents have been uploaded yet. Please upload some documents first!",
                'sources': []
            }
            return
        
        # Embed the question
        question_embedding = self.embedding_model.encode(
            question,
            convert_to_numpy=True
        )
        
        # Retrieve relevant chunks
        retrieved_chunks = self.vector_store.search(question_embedding)
        
        if not retrieved_chunks:
            yield {
                'type': 'done',
                'content': "I couldn't find any relevant information in your documents to answer this question.",
                'sources': []
            }
            return
        
        # Build context and prompt
        context = self._build_context(retrieved_chunks)
        prompt = self._build_prompt(question, context, chat_history)
        
        # Stream the answer
        for token in self._generate_with_llm_stream(prompt):
            yield {'type': 'token', 'content': token}
        
        # Extract sources
        sources = self._extract_sources(retrieved_chunks)
        
        # Send done signal with sources
        yield {
            'type': 'done',
            'sources': sources
        }
    
    def _generate_with_llm_stream(self, prompt: str):
        """
        Generate answer with streaming (yields tokens one by one).
        """
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Generate complete answer first
        outputs = self.llm.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=600,
            min_length=60,
            num_beams=5,
            length_penalty=2.0,
            no_repeat_ngram_size=3,
            early_stopping=True
        )
        
        # Decode complete text
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Ensure complete sentence
        if full_text and not full_text.endswith(('.', '!', '?')):
            last_period = max(full_text.rfind('.'), full_text.rfind('!'), full_text.rfind('?'))
            if last_period > len(full_text) // 2:
                full_text = full_text[:last_period + 1]
        
        # Yield word by word for streaming effect
        words = full_text.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word
