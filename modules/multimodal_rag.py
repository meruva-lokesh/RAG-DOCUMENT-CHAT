"""
Multi-modal RAG Pipeline
Extends the standard RAG pipeline to support Image + Text retrieval.
Uses CLIP for image embeddings and PyMuPDF for extraction.
"""

import os
import fitz  # PyMuPDF
import io
from PIL import Image
import torch
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, util
from modules.rag_pipeline import RAGPipeline
import config

class MultiModalRAG(RAGPipeline):
    """
    Multi-modal RAG pipeline that handles both text and images.
    Inherits from standard RAGPipeline to keep existing functionality.
    """
    
    def __init__(self):
        # Initialize standard text RAG
        super().__init__()
        
        print("🖼️ Initializing Multi-modal components...")
        
        # Load CLIP model for image-text matching
        # We use a lightweight CLIP model compatible with sentence-transformers
        self.clip_model_name = "clip-ViT-B-32"
        print(f"📥 Loading CLIP model: {self.clip_model_name}")
        self.clip_model = SentenceTransformer(self.clip_model_name)
        self.clip_model.to(self.device)
        
        # Store for image embeddings
        # Structure: [{'embedding': tensor, 'image': PIL.Image, 'metadata': dict}]
        self.image_store = []
        
        print("✅ Multi-modal RAG ready!")

    def process_uploaded_files(self, uploaded_files: List[Any]) -> Dict[str, Any]:
        """
        Process files for BOTH text (via super) and images.
        """
        # 1. Run standard text processing first
        print("📝 Processing text content...")
        results = super().process_uploaded_files(uploaded_files)
        
        # 2. Process images from PDFs
        print("🖼️ Extracting images from documents...")
        images_found = 0
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_path = os.path.join(config.UPLOADED_FILES_DIR, file_name)
            
            # Only process PDFs for images
            if file_name.lower().endswith('.pdf'):
                extracted_images = self._extract_images_from_pdf(file_path, file_name)
                
                # Generate embeddings for images
                for img_data in extracted_images:
                    embedding = self.clip_model.encode(img_data['image'], convert_to_tensor=True)
                    
                    self.image_store.append({
                        'embedding': embedding,
                        'image': img_data['image'],
                        'metadata': img_data['metadata']
                    })
                
                images_found += len(extracted_images)
        
        results['images_processed'] = images_found
        print(f"✅ Extracted and indexed {images_found} images")
        
        return results

    def _extract_images_from_pdf(self, pdf_path: str, file_name: str) -> List[Dict]:
        """Extract images from PDF pages using PyMuPDF."""
        images = []
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Filter small images (likely icons/logos)
                    if len(image_bytes) < 2000:  # Skip images < 2KB
                        continue
                        
                    try:
                        # Convert to PIL Image
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

    def generate_answer(
        self, 
        question: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate answer using text RAG + retrieve relevant images.
        """
        # 1. Get standard text answer
        result = super().generate_answer(question, chat_history)
        
        # 2. Retrieve relevant images
        relevant_images = self._retrieve_images(question)
        
        # 3. Add images to result
        result['relevant_images'] = relevant_images
        
        return result
    
    def _retrieve_images(self, query: str, top_k: int = 2) -> List[Dict]:
        """Find images matching the text query using CLIP."""
        if not self.image_store:
            return []
            
        # Embed query text
        query_embedding = self.clip_model.encode(query, convert_to_tensor=True)
        
        # Calculate similarities
        image_embeddings = torch.stack([item['embedding'] for item in self.image_store])
        cos_scores = util.cos_sim(query_embedding, image_embeddings)[0]
        
        # Get top k results
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.image_store)))
        
        retrieved_images = []
        for score, idx in zip(top_results[0], top_results[1]):
            if score > 0.25:  # Similarity threshold
                item = self.image_store[idx]
                retrieved_images.append({
                    'image': item['image'],
                    'metadata': item['metadata'],
                    'score': float(score)
                })
                
        return retrieved_images
