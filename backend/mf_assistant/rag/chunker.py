"""Document chunking service with document-type-aware strategies."""
import hashlib
import logging
import re
from typing import Dict, List, Optional
from uuid import uuid4

from mf_assistant.models.schemas import Chunk, ExtractedData

logger = logging.getLogger(__name__)


class ChunkingConfig:
    """Configuration for different document types."""
    
    FACTSHEET = {
        "chunk_size": 800,
        "chunk_overlap": 150,
        "strategy": "section_based"
    }
    
    SID_KIM = {
        "chunk_size": 1200,
        "chunk_overlap": 200,
        "strategy": "heading_based"
    }
    
    FAQ = {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "strategy": "qa_pair"
    }
    
    GENERIC = {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "strategy": "semantic"
    }


class DocumentChunker:
    """
    Document chunker with document-type-aware strategies.
    """
    
    def __init__(self):
        self.configs = {
            'factsheet': ChunkingConfig.FACTSHEET,
            'sid': ChunkingConfig.SID_KIM,
            'kim': ChunkingConfig.SID_KIM,
            'faq': ChunkingConfig.FAQ,
            'generic': ChunkingConfig.GENERIC
        }
    
    def chunk_document(self, extracted_data: ExtractedData) -> List[Chunk]:
        """
        Chunk a document based on its type.
        
        Args:
            extracted_data: Extracted document data
            
        Returns:
            List of Chunk objects
        """
        doc_type = extracted_data.doc_type or 'generic'
        config = self.configs.get(doc_type, ChunkingConfig.GENERIC)
        
        logger.info(f"Chunking document {extracted_data.source_url} as {doc_type}")
        
        # Get text to chunk
        text = extracted_data.raw_text or ""
        
        # Add extracted fields as structured chunks
        field_chunks = self._create_field_chunks(extracted_data)
        
        # Chunk the raw text based on strategy
        if config['strategy'] == 'section_based':
            text_chunks = self._chunk_section_based(text, config)
        elif config['strategy'] == 'heading_based':
            text_chunks = self._chunk_heading_based(text, config)
        elif config['strategy'] == 'qa_pair':
            text_chunks = self._chunk_qa_pairs(text, config)
        else:
            text_chunks = self._chunk_semantic(text, config)
        
        # Combine field chunks and text chunks
        all_chunks = field_chunks + text_chunks
        
        # Add metadata to each chunk
        for chunk in all_chunks:
            chunk.metadata.update({
                'source_url': extracted_data.source_url,
                'doc_type': doc_type,
                'scraped_at': extracted_data.scraped_at
            })
            if hasattr(extracted_data, 'metadata'):
                chunk.metadata.update(extracted_data.metadata)
        
        logger.info(f"Created {len(all_chunks)} chunks for {extracted_data.source_url}")
        return all_chunks
    
    def chunk_documents(self, documents: List[ExtractedData]) -> List[Chunk]:
        """Chunk multiple documents."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
    
    def _create_field_chunks(self, extracted_data: ExtractedData) -> List[Chunk]:
        """Create chunks from extracted fields."""
        chunks = []
        
        for field_name, value in extracted_data.extracted_fields.items():
            if value:
                # Create a chunk for each field
                chunk_text = f"{field_name.replace('_', ' ').title()}: {value}"
                chunk_id = self._generate_chunk_id(extracted_data.source_url, field_name)
                
                chunk = Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    metadata={
                        'field_name': field_name,
                        'chunk_type': 'extracted_field'
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_section_based(self, text: str, config: Dict) -> List[Chunk]:
        """Chunk based on sections (for factsheets)."""
        chunks = []
        chunk_size = config['chunk_size']
        chunk_overlap = config['chunk_overlap']
        
        # Split by common section headers
        section_pattern = r'(?:\n\s*(?:\d+\.|\(?\d+\)|[A-Z][A-Z\s]{2,}|Key\s+Information|Fund\s+Details|Performance|Portfolio))'
        sections = re.split(section_pattern, text)
        
        current_chunk = ""
        chunk_num = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # If adding this section would exceed chunk size, save current chunk
            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunk_id = self._generate_chunk_id(str(uuid4()), f"section_{chunk_num}")
                chunks.append(Chunk(
                    id=chunk_id,
                    text=current_chunk.strip(),
                    metadata={'chunk_type': 'section'}
                ))
                
                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_text = ' '.join(words[-chunk_overlap:]) if len(words) > chunk_overlap else current_chunk
                current_chunk = overlap_text + "\n" + section
                chunk_num += 1
            else:
                current_chunk += "\n" + section if current_chunk else section
        
        # Add final chunk
        if current_chunk.strip():
            chunk_id = self._generate_chunk_id(str(uuid4()), f"section_{chunk_num}")
            chunks.append(Chunk(
                id=chunk_id,
                text=current_chunk.strip(),
                metadata={'chunk_type': 'section'}
            ))
        
        return chunks
    
    def _chunk_heading_based(self, text: str, config: Dict) -> List[Chunk]:
        """Chunk based on headings (for SID/KIM)."""
        chunks = []
        chunk_size = config['chunk_size']
        
        # Split by headings (numbered or capitalized)
        heading_pattern = r'(?:\n\s*(?:\d+\.\s+|\(?\d+\)\s*|[A-Z][A-Z\s]{3,}:))'
        parts = re.split(heading_pattern, text)
        
        current_chunk = ""
        chunk_num = 0
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if len(current_chunk) + len(part) > chunk_size and current_chunk:
                chunk_id = self._generate_chunk_id(str(uuid4()), f"heading_{chunk_num}")
                chunks.append(Chunk(
                    id=chunk_id,
                    text=current_chunk.strip(),
                    metadata={'chunk_type': 'heading_section'}
                ))
                current_chunk = part
                chunk_num += 1
            else:
                current_chunk += "\n\n" + part if current_chunk else part
        
        if current_chunk.strip():
            chunk_id = self._generate_chunk_id(str(uuid4()), f"heading_{chunk_num}")
            chunks.append(Chunk(
                id=chunk_id,
                text=current_chunk.strip(),
                metadata={'chunk_type': 'heading_section'}
            ))
        
        return chunks
    
    def _chunk_qa_pairs(self, text: str, config: Dict) -> List[Chunk]:
        """Chunk Q&A pairs (for FAQ pages)."""
        chunks = []
        
        # Look for Q&A patterns
        qa_patterns = [
            r'(?:Q[:.]?\s*|Question[:\s]+)(.+?)(?:\n\s*(?:A[:.]?\s*|Answer[:\s]+)(.+?))(?=\n\s*(?:Q[:.]?|Question[:\s]+)|$)',
            r'(?:\d+[.)]\s*)(.+?\?)(.+?)(?=\n\s*\d+[.)]|$)',
        ]
        
        for pattern in qa_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for i, match in enumerate(matches):
                if isinstance(match, tuple):
                    question = match[0].strip()
                    answer = match[1].strip() if len(match) > 1 else ""
                    qa_text = f"Q: {question}\nA: {answer}"
                else:
                    qa_text = match.strip()
                
                chunk_id = self._generate_chunk_id(str(uuid4()), f"qa_{i}")
                chunks.append(Chunk(
                    id=chunk_id,
                    text=qa_text,
                    metadata={'chunk_type': 'qa_pair'}
                ))
        
        # If no Q&A patterns found, fall back to semantic chunking
        if not chunks:
            return self._chunk_semantic(text, config)
        
        return chunks
    
    def _chunk_semantic(self, text: str, config: Dict) -> List[Chunk]:
        """Semantic chunking with overlap (default strategy)."""
        chunks = []
        chunk_size = config['chunk_size']
        chunk_overlap = config['chunk_overlap']
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunk_num = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunk_id = self._generate_chunk_id(str(uuid4()), f"semantic_{chunk_num}")
                chunks.append(Chunk(
                    id=chunk_id,
                    text=current_chunk.strip(),
                    metadata={'chunk_type': 'semantic'}
                ))
                
                # Overlap
                words = current_chunk.split()
                if len(words) > chunk_overlap:
                    overlap_text = ' '.join(words[-chunk_overlap:])
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
                chunk_num += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunk_id = self._generate_chunk_id(str(uuid4()), f"semantic_{chunk_num}")
            chunks.append(Chunk(
                id=chunk_id,
                text=current_chunk.strip(),
                metadata={'chunk_type': 'semantic'}
            ))
        
        return chunks
    
    def _generate_chunk_id(self, source: str, suffix: str) -> str:
        """Generate unique chunk ID."""
        hash_input = f"{source}_{suffix}_{uuid4()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
