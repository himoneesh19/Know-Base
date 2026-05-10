import subprocess
import json
import os
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader


class KBManager:
    """Wrapper for OpenKB functionality using subprocess calls."""
    
    def __init__(self, kb_path="./knowledge_base", model="inclusionai/ring-2.6-1t:free"):
        """
        Initialize the KBManager.
        
        Args:
            kb_path: Path to the knowledge base directory
            model: LLM model to use for queries
        """
        self.kb_path = Path(kb_path)
        self.model = model
        self.documents = []
        
        # Ensure API keys are set as environment variables
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        # Set both environment variables for OpenKB
        os.environ["OPENROUTER_API_KEY"] = api_key
        os.environ["LLM_API_KEY"] = api_key
        
        # Initialize the knowledge base
        self.initialize_kb()
    
    def initialize_kb(self):
        """Initialize or reinitialize the OpenKB knowledge base."""
        try:
            # Create knowledge base directory if it doesn't exist
            self.kb_path.mkdir(parents=True, exist_ok=True)
            
            # Create OpenKB config directory
            config_dir = self.kb_path / ".openkb"
            config_dir.mkdir(exist_ok=True)
            
            # Create wiki directory for OpenKB
            wiki_dir = self.kb_path / "wiki"
            wiki_dir.mkdir(exist_ok=True)
            
            # Create a basic config.yaml for OpenKB
            config_content = f"""# OpenKB Configuration
model: {self.model}
knowledge_base_path: {self.kb_path}
"""
            config_file = config_dir / "config.yaml"
            with open(config_file, "w") as f:
                f.write(config_content)
            
            print(f"Knowledge base initialized at {self.kb_path}")
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")
            raise
    
    def add_document(self, filepath):
        """
        Add a document to the knowledge base.
        Supports Markdown (.md) and PDF (.pdf) files.
        
        Args:
            filepath: Path to the markdown or PDF file to add
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                print(f"File not found: {filepath}")
                return False
            
            suffix = file_path.suffix.lower()
            if suffix == ".md":
                with open(file_path, "r", encoding="utf-8") as src:
                    content = src.read()
                return self._save_document(file_path.name, content)
            elif suffix == ".pdf":
                content = self._extract_text_from_pdf(file_path)
                return self._save_document(file_path.name, content)
            else:
                print(f"File must be a markdown (.md) or PDF (.pdf) file: {filepath}")
                return False
        except Exception as e:
            print(f"Error adding document: {e}")
            return False

    def add_document_from_upload(self, file_bytes, filename):
        """
        Add an uploaded file to the knowledge base.
        Supports markdown and PDF uploads.
        """
        try:
            suffix = Path(filename).suffix.lower()
            if suffix == ".md":
                content = file_bytes.decode("utf-8")
                return self._save_document(filename, content)
            elif suffix == ".pdf":
                content = self._extract_text_from_pdf_bytes(file_bytes)
                return self._save_document(filename, content)
            else:
                print(f"Uploaded file must be a markdown (.md) or PDF (.pdf) file: {filename}")
                return False
        except Exception as e:
            print(f"Error adding uploaded document: {e}")
            return False

    def _save_document(self, original_name, content):
        """Save document content as markdown in the wiki directory."""
        wiki_dir = self.kb_path / "wiki"
        wiki_dir.mkdir(exist_ok=True)

        dest_file = wiki_dir / f"{Path(original_name).stem}.md"
        with open(dest_file, "w", encoding="utf-8") as dst:
            dst.write(content)

        doc_entry = {
            "name": original_name,
            "path": str(dest_file),
            "size": dest_file.stat().st_size
        }

        existing = next((doc for doc in self.documents if doc["name"] == original_name), None)
        if existing:
            existing.update(doc_entry)
        else:
            self.documents.append(doc_entry)

        self._save_documents_metadata()
        print(f"Document added: {original_name}")
        return True

    def _extract_text_from_pdf(self, file_path):
        """Extract text from a PDF file path."""
        try:
            reader = PdfReader(str(file_path))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            if not text_parts:
                raise ValueError("No text content found in PDF")
            return "\n\n".join(text_parts)
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {e}")

    def _extract_text_from_pdf_bytes(self, file_bytes):
        """Extract text from uploaded PDF bytes."""
        try:
            with BytesIO(file_bytes) as stream:
                reader = PdfReader(stream)
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                if not text_parts:
                    raise ValueError("No text content found in PDF")
                return "\n\n".join(text_parts)
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {e}")
    
    def query(self, question):
        """
        Query the knowledge base with a natural language question.
        
        Args:
            question: The question to ask
            
        Returns:
            str: The answer from the LLM based on the knowledge base
        """
        try:
            # Ensure we have documents
            if not self.documents:
                return "No documents in the knowledge base. Please add documents first."
            
            # Read all documents from the wiki directory
            wiki_dir = self.kb_path / "wiki"
            if not wiki_dir.exists():
                return "Knowledge base not initialized properly."
            
            # Gather all document content
            context = self._gather_context()
            
            if not context:
                return "No documents found in the knowledge base."
            
            # Build the prompt with context
            prompt = self._build_prompt(question, context)
            
            # Call OpenRouter API directly via subprocess-style approach
            # For now, we'll use the OpenKB query command
            import httpx
            
            api_key = os.getenv("OPENROUTER_API_KEY")
            
            # Use OpenRouter API to get the answer
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "KnowBase",
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that answers questions based on the provided knowledge base documents. Answer only using information from the provided context. If the answer is not in the context, say so clearly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            with httpx.Client() as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                return answer
            else:
                return f"Error querying knowledge base: {response.text}"
                
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return f"Error: {str(e)}"
    
    def list_documents(self):
        """
        List all documents in the knowledge base.
        
        Returns:
            list: List of document metadata dictionaries
        """
        # Refresh from disk
        self._load_documents_metadata()
        return self.documents
    
    def _gather_context(self):
        """Gather all document content to use as context."""
        context = []
        wiki_dir = self.kb_path / "wiki"
        
        if not wiki_dir.exists():
            return ""
        
        # Read all markdown files
        for md_file in wiki_dir.glob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    context.append(f"--- From {md_file.name} ---\n{content}\n")
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        return "\n".join(context)
    
    def _build_prompt(self, question, context):
        """Build the prompt with context for the LLM."""
        return f"""Based on the following knowledge base documents, answer the question.

Knowledge Base:
{context}

Question: {question}

Please provide a clear, well-structured answer based only on the information in the knowledge base. If the information is not available, state that clearly."""
    
    def _save_documents_metadata(self):
        """Save document metadata to disk."""
        try:
            metadata_file = self.kb_path / ".openkb" / "documents.json"
            with open(metadata_file, "w") as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"Error saving document metadata: {e}")
    
    def _load_documents_metadata(self):
        """Load document metadata from disk."""
        try:
            metadata_file = self.kb_path / ".openkb" / "documents.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    self.documents = json.load(f)
            else:
                # Scan wiki directory for markdown files
                self.documents = []
                wiki_dir = self.kb_path / "wiki"
                if wiki_dir.exists():
                    for md_file in wiki_dir.glob("*.md"):
                        doc_entry = {
                            "name": md_file.name,
                            "path": str(md_file),
                            "size": md_file.stat().st_size
                        }
                        self.documents.append(doc_entry)
        except Exception as e:
            print(f"Error loading document metadata: {e}")
