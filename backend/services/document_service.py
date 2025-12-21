import os
import uuid
import hashlib
from typing import Optional, Dict, List
from pathlib import Path
import json

# Document parsing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[DocumentService] WARNING PyPDF2 not installed. PDF parsing disabled.")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("[DocumentService] WARNING python-docx not installed. DOCX parsing disabled.")


class DocumentService:
    """Service for processing and storing documents"""
    
    def __init__(self):
        # Create documents directory if it doesn't exist
        self.base_dir = Path("documents")
        self.base_dir.mkdir(exist_ok=True)
        
        # Metadata file to track documents
        self.metadata_file = self.base_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
        print(f"[DocumentService] OK Document service initialized")
        print(f"[DocumentService]   PDF support: {PDF_AVAILABLE}")
        print(f"[DocumentService]   DOCX support: {DOCX_AVAILABLE}")
    
    def _load_metadata(self) -> Dict:
        """Load document metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[DocumentService] Error loading metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save document metadata to file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"[DocumentService] Error saving metadata: {e}")
    
    def _generate_document_id(self, filename: str) -> str:
        """Generate a unique document ID"""
        # Use filename + timestamp to generate unique ID
        unique_string = f"{filename}_{uuid.uuid4().hex[:8]}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    async def save_document(self, file_content: bytes, filename: str, content_type: str) -> Dict:
        """Save uploaded document and extract text content"""
        try:
            # Generate document ID
            doc_id = self._generate_document_id(filename)
            
            # Save file
            file_path = self.base_dir / f"{doc_id}_{filename}"
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Extract text content
            text_content = await self.extract_text(file_path, content_type)
            
            # Save metadata
            self.metadata[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "file_path": str(file_path),
                "content_type": content_type,
                "size": len(file_content),
                "text_content": text_content,
                "text_length": len(text_content),
                "created_at": str(Path(file_path).stat().st_mtime)
            }
            self._save_metadata()
            
            print(f"[DocumentService] OK Document saved: {filename} (ID: {doc_id})")
            print(f"[DocumentService]   Extracted {len(text_content)} characters")
            
            return {
                "document_id": doc_id,
                "filename": filename,
                "size": len(file_content),
                "text_length": len(text_content)
            }
        
        except Exception as e:
            print(f"[DocumentService] Error saving document: {e}")
            raise Exception(f"Failed to save document: {str(e)}")
    
    async def extract_text(self, file_path: Path, content_type: str) -> str:
        """Extract text content from document based on file type"""
        try:
            file_path = Path(file_path)
            
            # PDF files
            if content_type == 'application/pdf' or str(file_path).lower().endswith('.pdf'):
                if not PDF_AVAILABLE:
                    raise Exception("PDF parsing not available. Install PyPDF2: pip install PyPDF2")
                return self._extract_pdf_text(file_path)
            
            # DOCX files
            elif 'wordprocessingml' in content_type or str(file_path).lower().endswith('.docx'):
                if not DOCX_AVAILABLE:
                    raise Exception("DOCX parsing not available. Install python-docx: pip install python-docx")
                return self._extract_docx_text(file_path)
            
            # DOC files (old Word format - limited support)
            elif content_type == 'application/msword' or str(file_path).lower().endswith('.doc'):
                return self._extract_doc_text(file_path)
            
            # TXT files
            elif content_type == 'text/plain' or str(file_path).lower().endswith('.txt'):
                return self._extract_txt_text(file_path)
            
            else:
                raise Exception(f"Unsupported file type: {content_type}")
        
        except Exception as e:
            print(f"[DocumentService] Error extracting text: {e}")
            raise Exception(f"Failed to extract text from document: {str(e)}")
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text_parts = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return '\n\n'.join(text_parts)
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return '\n'.join(text_parts)
    
    def _extract_doc_text(self, file_path: Path) -> str:
        """Extract text from DOC file (old Word format)"""
        # DOC files are binary and harder to parse without additional libraries
        # For now, return a placeholder - could add support with python-docx or antiword
        return f"[Document] Content from {file_path.name} - DOC format support is limited. Please convert to DOCX or PDF for better results."
    
    def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document metadata and text content"""
        if document_id not in self.metadata:
            return None
        
        return self.metadata[document_id]
    
    def get_document_text(self, document_id: str) -> Optional[str]:
        """Get just the text content of a document"""
        doc = self.get_document(document_id)
        if doc:
            return doc.get('text_content', '')
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents (metadata only, no text content)"""
        docs = []
        for doc_id, metadata in self.metadata.items():
            # Return metadata without full text content to save bandwidth
            doc_summary = {
                "id": metadata.get("id"),
                "filename": metadata.get("filename"),
                "size": metadata.get("size"),
                "text_length": metadata.get("text_length"),
                "created_at": metadata.get("created_at")
            }
            docs.append(doc_summary)
        return docs
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its metadata"""
        if document_id not in self.metadata:
            return False
        
        try:
            # Delete file
            file_path = Path(self.metadata[document_id]['file_path'])
            if file_path.exists():
                file_path.unlink()
            
            # Remove from metadata
            del self.metadata[document_id]
            self._save_metadata()
            
            print(f"[DocumentService] OK Document deleted: {document_id}")
            return True
        
        except Exception as e:
            print(f"[DocumentService] Error deleting document: {e}")
            return False
    
    def get_documents_context(self, document_ids: List[str]) -> str:
        """Get combined text context from multiple documents"""
        contexts = []
        for doc_id in document_ids:
            text = self.get_document_text(doc_id)
            if text:
                doc_meta = self.get_document(doc_id)
                filename = doc_meta.get('filename', 'Unknown') if doc_meta else 'Unknown'
                contexts.append(f"=== Document: {filename} ===\n{text}\n")
        
        return '\n\n'.join(contexts)


















