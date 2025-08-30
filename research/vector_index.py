"""
Vector indexing module for Phase 2.
Implements FAISS-based semantic search for RAG retrieval.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from .config import config
from .db import get_doc_by_url, get_sections_by_doc_id


class VectorIndex:
    """FAISS-based vector index for semantic search of research content."""
    
    def __init__(self, model_name: str = None, dimension: int = None, index_path: str = None):
        self.model_name = model_name or config.VECTOR_MODEL_NAME
        self.dimension = dimension or config.VECTOR_DIMENSION
        self.index_path = index_path or config.FAISS_INDEX_PATH
        
        # Initialize sentence transformer model
        print(f"Loading vector model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Store mappings from index positions to document/section IDs
        self.id_mappings: List[Tuple[int, int]] = []  # (doc_id, section_id)
        
        # Load existing index if available
        self._load_index()
    
    def _load_index(self):
        """Load existing FAISS index and mappings if available."""
        if os.path.exists(self.index_path):
            try:
                print(f"Loading existing vector index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
                
                # Load ID mappings
                mappings_path = self.index_path.replace('.faiss', '_mappings.pkl')
                if os.path.exists(mappings_path):
                    with open(mappings_path, 'rb') as f:
                        self.id_mappings = pickle.load(f)
                
                print(f"Loaded index with {len(self.id_mappings)} vectors")
            except Exception as e:
                print(f"Failed to load existing index: {e}")
                print("Creating new index...")
                self.index = faiss.IndexFlatIP(self.dimension)
                self.id_mappings = []
    
    def _save_index(self):
        """Save FAISS index and mappings to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save ID mappings
            mappings_path = self.index_path.replace('.faiss', '_mappings.pkl')
            with open(mappings_path, 'wb') as f:
                pickle.dump(self.id_mappings, f)
            
            print(f"Saved vector index to {self.index_path}")
        except Exception as e:
            print(f"Failed to save index: {e}")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        if not texts:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.astype('float32')
    
    def add_sections(self, doc_id: int, sections: List[Dict[str, Any]]) -> int:
        """
        Add sections from a document to the vector index.
        Returns the number of sections added.
        """
        if not sections:
            return 0
        
        # Extract text content for embedding
        texts = []
        section_ids = []
        
        for section in sections:
            text = section.get('text', '')
            if text and len(text.strip()) > 50:  # Only index substantial content
                texts.append(text)
                section_ids.append(section.get('id', 0))
        
        if not texts:
            return 0
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store ID mappings
        for section_id in section_ids:
            self.id_mappings.append((doc_id, section_id))
        
        print(f"Added {len(texts)} sections from document {doc_id} to vector index")
        return len(texts)
    
    def search(self, query: str, k: int = 8) -> List[Dict[str, Any]]:
        """
        Search for most similar content to the query.
        Returns list of search results with scores and metadata.
        """
        if not query.strip():
            return []
        
        # Generate query embedding
        query_embedding = self.embed_texts([query])
        
        # Search the index
        scores, indices = self.index.search(query_embedding, min(k, len(self.id_mappings)))
        
        # Collect results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.id_mappings):
                doc_id, section_id = self.id_mappings[idx]
                
                # Get section details from database
                # Note: This requires database connection, so we'll return basic info for now
                results.append({
                    'doc_id': doc_id,
                    'section_id': section_id,
                    'score': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def search_with_context(self, query: str, k: int = 8, db_conn=None) -> List[Dict[str, Any]]:
        """
        Search and return full context for each result.
        Requires database connection for full content retrieval.
        """
        if not db_conn:
            return self.search(query, k)
        
        # Get basic search results
        search_results = self.search(query, k)
        
        # Enrich with full context
        enriched_results = []
        for result in search_results:
            doc_id = result['doc_id']
            section_id = result['section_id']
            
            # Get document info
            doc_info = get_doc_by_url(db_conn, str(doc_id))  # This needs to be fixed
            if not doc_info:
                continue
            
            # Get section info
            sections = get_sections_by_doc_id(db_conn, doc_id)
            section_info = next((s for s in sections if s['id'] == section_id), None)
            if not section_info:
                continue
            
            # Create enriched result
            enriched_result = {
                'doc_id': doc_id,
                'section_id': section_id,
                'score': result['score'],
                'rank': result['rank'],
                'url': doc_info.get('url', ''),
                'title': doc_info.get('title', ''),
                'site_name': doc_info.get('site_name', ''),
                'section_heading': section_info.get('heading', ''),
                'section_text': section_info.get('text', ''),
                'section_page': section_info.get('page', ''),
            }
            
            enriched_results.append(enriched_result)
        
        return enriched_results
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index."""
        return {
            'total_vectors': len(self.id_mappings),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'model_name': self.model_name,
            'index_path': self.index_path
        }
    
    def rebuild_index(self, db_conn) -> int:
        """
        Rebuild the entire vector index from database content.
        This is useful for initial setup or after major changes.
        """
        print("Rebuilding vector index from database...")
        
        # Clear existing index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_mappings = []
        
        # Get all documents and sections from database
        # This is a simplified approach - in production you'd want pagination
        cursor = db_conn.execute("SELECT id FROM normalized_doc")
        doc_ids = [row[0] for row in cursor.fetchall()]
        
        total_sections = 0
        for doc_id in doc_ids:
            sections = get_sections_by_doc_id(db_conn, doc_id)
            sections_added = self.add_sections(doc_id, sections)
            total_sections += sections_added
        
        # Save the rebuilt index
        self._save_index()
        
        print(f"Rebuilt index with {total_sections} sections from {len(doc_ids)} documents")
        return total_sections
    
    def close(self):
        """Save and close the vector index."""
        self._save_index()
        print("Vector index saved and closed")


# Global vector index instance
vector_index = VectorIndex()
