"""
File loader module for extracting text from various document formats.
Supports PDF, TXT, MD, DOCX, and CSV files with metadata tracking.
"""

import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import pdfplumber
from docx import Document
import csv


class BaseLoader(ABC):
    """Abstract base class for document loaders."""
    
    @abstractmethod
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Load and extract text from a document.
        
        Args:
            file_path: Absolute path to the file
            file_name: Original filename for metadata
            
        Returns:
            Dictionary with 'text' and 'metadata' keys
        """
        pass


class PDFLoader(BaseLoader):
    """Loader for PDF files using pdfplumber."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Extract text from PDF with page number tracking."""
        all_text = []
        metadata = {
            'file_name': file_name,
            'file_type': 'pdf',
            'pages': []
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                        metadata['pages'].append({
                            'page_number': page_num,
                            'text_length': len(text)
                        })
                
                metadata['total_pages'] = len(pdf.pages)
                
            return {
                'text': '\n\n'.join(all_text),
                'metadata': metadata
            }
        except Exception as e:
            raise Exception(f"Error loading PDF {file_name}: {str(e)}")


class TextLoader(BaseLoader):
    """Loader for plain text and markdown files."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Extract text from TXT or MD files with line tracking."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            lines = text.split('\n')
            metadata = {
                'file_name': file_name,
                'file_type': 'txt' if file_name.endswith('.txt') else 'md',
                'total_lines': len(lines),
                'text_length': len(text)
            }
            
            return {
                'text': text,
                'metadata': metadata
            }
        except Exception as e:
            raise Exception(f"Error loading text file {file_name}: {str(e)}")


class DocxLoader(BaseLoader):
    """Loader for Microsoft Word documents."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Extract text from DOCX files with paragraph tracking."""
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = '\n\n'.join(paragraphs)
            
            metadata = {
                'file_name': file_name,
                'file_type': 'docx',
                'total_paragraphs': len(paragraphs),
                'text_length': len(text)
            }
            
            return {
                'text': text,
                'metadata': metadata
            }
        except Exception as e:
            raise Exception(f"Error loading DOCX file {file_name}: {str(e)}")


class CSVLoader(BaseLoader):
    """Loader for CSV files, converting tabular data to contextual text."""
    
    def load(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Extract text from CSV by converting rows to readable sentences.
        Each row is formatted as: "Column1: value1, Column2: value2, ..."
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # Convert each row to a text representation
                text_rows = []
                row_count = 0
                for row in reader:
                    row_text = ', '.join([f"{col}: {val}" for col, val in row.items() if val])
                    text_rows.append(row_text)
                    row_count += 1
                
                text = '\n'.join(text_rows)
                
                metadata = {
                    'file_name': file_name,
                    'file_type': 'csv',
                    'total_rows': row_count,
                    'total_columns': len(headers) if headers else 0,
                    'columns': list(headers) if headers else [],
                    'text_length': len(text)
                }
                
                return {
                    'text': text,
                    'metadata': metadata
                }
        except Exception as e:
            raise Exception(f"Error loading CSV file {file_name}: {str(e)}")


class FileLoaderFactory:
    """Factory class to route files to appropriate loaders."""
    
    # Mapping of file extensions to loader classes
    LOADERS = {
        '.pdf': PDFLoader,
        '.txt': TextLoader,
        '.md': TextLoader,
        '.docx': DocxLoader,
        '.csv': CSVLoader
    }
    
    @classmethod
    def get_loader(cls, file_name: str) -> BaseLoader:
        """
        Get the appropriate loader for a file based on its extension.
        
        Args:
            file_name: Name of the file
            
        Returns:
            Instance of appropriate loader class
            
        Raises:
            ValueError: If file extension is not supported
        """
        ext = os.path.splitext(file_name)[1].lower()
        
        if ext not in cls.LOADERS:
            raise ValueError(f"Unsupported file type: {ext}. Supported types: {list(cls.LOADERS.keys())}")
        
        loader_class = cls.LOADERS[ext]
        return loader_class()
    
    @classmethod
    def load_file(cls, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Convenience method to load a file using the appropriate loader.
        
        Args:
            file_path: Absolute path to the file
            file_name: Original filename
            
        Returns:
            Dictionary with extracted text and metadata
        """
        loader = cls.get_loader(file_name)
        return loader.load(file_path, file_name)
