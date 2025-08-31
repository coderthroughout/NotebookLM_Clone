"""
Enhanced Vector Indexing Module for Phase 2.
Implements hybrid ranking, deduplication, and diversity controls.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from simhash import Simhash
from datetime import datetime, timedelta
from .config import config
from .db import get_doc_by_url, get_sections_by_doc_id


class EnhancedVectorIndex:
    """Enhanced FAISS-based vector index with hybrid ranking and deduplication."""
    
    def __init__(self, model_name: str = None, dimension: int = None, index_path: str = None):
        self.model_name = model_name or config.VECTOR_MODEL_NAME
        self.dimension = dimension or config.VECTOR_MODENSION
        self.index_path = index_path or config.FAISS_INDEX_PATH
        
        # Initialize sentence transformer model
        print(f"Loading vector model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Store mappings from index positions to document/section IDs
        self.id_mappings: List[Tuple[int, int]] = []  # (doc_id, section_id)
        
        # BM25 index for text-based ranking
        self.bm25_index = None
        self.bm25_texts = []
        
        # SimHash for deduplication
        self.simhash_threshold = 0.85  # Similarity threshold for deduplication
        
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
                
                # Load BM25 index
                bm25_path = self.index_path.replace('.faiss', '_bm25.pkl')
                if os.path.exists(bm25_path):
                    with open(bm25_path, 'rb') as f:
                        bm25_data = pickle.load(f)
                        self.bm25_index = bm25_data['index']
                        self.bm25_texts = bm25_data['texts']
                
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
            
            # Save BM25 index
            if self.bm25_index:
                bm25_path = self.index_path.replace('.faiss', '_bm25.pkl')
                with open(bm25_path, 'wb') as f:
                    pickle.dump({
                        'index': self.bm25_index,
                        'texts': self.bm25_texts
                    }, bm25_path)
            
            print(f"Saved enhanced vector index to {self.index_path}")
        except Exception as e:
            print(f"Failed to save index: {e}")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        if not texts:
            return np.array([])
        
        # Generate embeddings
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.astype('float32')
    
    def _calculate_freshness_score(self, fetched_at: str) -> float:
        """Calculate freshness score based on when content was fetched."""
        if not fetched_at:
            return 0.5  # Default score for unknown dates
        
        try:
            fetch_date = datetime.fromisoformat(fetched_at.replace('Z', '+00:00'))
            now = datetime.now(fetch_date.tzinfo)
            days_old = (now - fetch_date).days
            
            # Exponential decay: newer content gets higher scores
            freshness_score = np.exp(-days_old / 365.0)  # 1 year half-life
            return max(0.1, min(1.0, freshness_score))
        except:
            return 0.5
    
    def _calculate_diversity_score(self, results: List[Dict], current_result: Dict) -> float:
        """Calculate diversity score to encourage varied sources."""
        if not results:
            return 1.0
        
        # Check domain diversity
        current_domain = self._extract_domain(current_result.get('url', ''))
        existing_domains = [self._extract_domain(r.get('url', '')) for r in results]
        
        if current_domain not in existing_domains:
            return 1.0  # New domain gets full score
        else:
            # Penalize repeated domains
            domain_count = existing_domains.count(current_domain)
            return max(0.1, 1.0 / (domain_count + 1))
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url
    
    def _apply_domain_caps(self, results: List[Dict], max_per_domain: int = 2) -> List[Dict]:
        """Apply domain caps to ensure diversity."""
        domain_counts = {}
        filtered_results = []
        
        for result in results:
            domain = self._extract_domain(result.get('url', ''))
            if domain_counts.get(domain, 0) < max_per_domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                filtered_results.append(result)
        
        return filtered_results
    
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
        section_data = []
        
        for section in sections:
            text = section.get('text', '')
            if text and len(text.strip()) > 50:  # Only index substantial content
                texts.append(text)
                section_ids.append(section.get('id', 0))
                section_data.append(section)
        
        if not texts:
            return 0
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store ID mappings
        for section_id in section_ids:
            self.id_mappings.append((doc_id, section_id))
        
        # Update BM25 index
        if self.bm25_index is None:
            self.bm25_index = BM25Okapi(texts)
            self.bm25_texts = texts
        else:
            # Add new texts to existing BM25 index
            self.bm25_texts.extend(texts)
            self.bm25_index = BM25Okapi(self.bm25_texts)
        
        print(f"Added {len(texts)} sections from document {doc_id} to enhanced vector index")
        return len(texts)
    
    def search_hybrid(self, query: str, k: int = 12, db_conn=None, 
                     weights: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity, BM25, credibility, freshness, and diversity.
        """
        if not query.strip():
            return []
        
        # Default weights for hybrid ranking
        if weights is None:
            weights = {
                'vector': 0.55,      # Dense vector similarity
                'bm25': 0.25,        # Text-based ranking
                'credibility': 0.15, # Source credibility
                'freshness': 0.05    # Content freshness
            }
        
        # Get vector search results
        vector_results = self._vector_search(query, k * 2)  # Get more for diversity filtering
        
        # Get BM25 results
        bm25_results = self._bm25_search(query, k * 2)
        
        # Combine and rank results
        combined_results = self._combine_rankings(
            query, vector_results, bm25_results, weights, db_conn
        )
        
        # Apply diversity controls
        final_results = self._apply_diversity_controls(combined_results, k)
        
        return final_results
    
    def _vector_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Vector similarity search."""
        if not self.id_mappings:
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
                results.append({
                    'doc_id': doc_id,
                    'section_id': section_id,
                    'vector_score': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def _bm25_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """BM25 text-based search."""
        if not self.bm25_index or not self.id_mappings:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get BM25 scores
        bm25_scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top k results
        top_indices = np.argsort(bm25_scores)[::-1][:k]
        
        results = []
        for i, idx in enumerate(top_indices):
            if idx < len(self.id_mappings):
                doc_id, section_id = self.id_mappings[idx]
                results.append({
                    'doc_id': doc_id,
                    'section_id': section_id,
                    'bm25_score': float(bm25_scores[idx]),
                    'rank': i + 1
                })
        
        return results
    
    def _combine_rankings(self, query: str, vector_results: List[Dict], 
                          bm25_results: List[Dict], weights: Dict[str, float], 
                          db_conn) -> List[Dict[str, Any]]:
        """Combine different ranking signals into final scores."""
        # Create lookup for quick access
        vector_lookup = {f"{r['doc_id']}_{r['section_id']}": r for r in vector_results}
        bm25_lookup = {f"{r['doc_id']}_{r['section_id']}": r for r in bm25_results}
        
        # Combine all unique results
        all_keys = set(vector_lookup.keys()) | set(bm25_lookup.keys())
        
        combined_results = []
        for key in all_keys:
            doc_id, section_id = map(int, key.split('_'))
            
            # Get scores from different methods
            vector_score = vector_lookup.get(key, {}).get('vector_score', 0.0)
            bm25_score = bm25_lookup.get(key, {}).get('bm25_score', 0.0)
            
            # Normalize scores to 0-1 range
            vector_score_norm = max(0.0, min(1.0, (vector_score + 1) / 2))  # FAISS scores are typically -1 to 1
            bm25_score_norm = max(0.0, min(1.0, bm25_score / max(bm25_scores) if bm25_scores else 0.0))
            
            # Get additional metadata from database
            metadata = self._get_section_metadata(doc_id, section_id, db_conn)
            
            # Calculate additional scores
            credibility_score = metadata.get('credibility', 0.5)
            freshness_score = self._calculate_freshness_score(metadata.get('fetched_at'))
            
            # Calculate final hybrid score
            final_score = (
                weights['vector'] * vector_score_norm +
                weights['bm25'] * bm25_score_norm +
                weights['credibility'] * credibility_score +
                weights['freshness'] * freshness_score
            )
            
            combined_results.append({
                'doc_id': doc_id,
                'section_id': section_id,
                'final_score': final_score,
                'vector_score': vector_score_norm,
                'bm25_score': bm25_score_norm,
                'credibility_score': credibility_score,
                'freshness_score': freshness_score,
                'metadata': metadata
            })
        
        # Sort by final score
        combined_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return combined_results
    
    def _get_section_metadata(self, doc_id: int, section_id: int, db_conn) -> Dict[str, Any]:
        """Get metadata for a section from the database."""
        if not db_conn:
            return {}
        
        try:
            # Get document info
            doc_info = get_doc_by_url(db_conn, str(doc_id))
            if not doc_info:
                return {}
            
            # Get section info
            sections = get_sections_by_doc_id(db_conn, doc_id)
            section_info = next((s for s in sections if s['id'] == section_id), None)
            if not section_info:
                return {}
            
            return {
                'url': doc_info.get('url', ''),
                'title': doc_info.get('title', ''),
                'site_name': doc_info.get('site_name', ''),
                'credibility': doc_info.get('credibility', 0.5),
                'fetched_at': doc_info.get('fetched_at', ''),
                'section_heading': section_info.get('heading', ''),
                'section_text': section_info.get('text', ''),
                'section_page': section_info.get('page', ''),
            }
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {}
    
    def _apply_diversity_controls(self, results: List[Dict], k: int) -> List[Dict]:
        """Apply diversity controls including deduplication and domain caps."""
        if not results:
            return []
        
        # Apply SimHash deduplication
        deduped_results = self._apply_simhash_dedup(results)
        
        # Apply domain caps
        final_results = self._apply_domain_caps(deduped_results, max_per_domain=2)
        
        # Return top k results
        return final_results[:k]
    
    def _apply_simhash_dedup(self, results: List[Dict]) -> List[Dict]:
        """Apply SimHash deduplication to remove near-duplicate content."""
        if not results:
            return []
        
        deduped = []
        seen_hashes = set()
        
        for result in results:
            text = result.get('metadata', {}).get('section_text', '')
            if not text:
                continue
            
            # Generate SimHash
            simhash = Simhash(text)
            
            # Check if this is a near-duplicate
            is_duplicate = False
            for seen_hash in seen_hashes:
                if simhash.similarity(seen_hash) > self.simhash_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduped.append(result)
                seen_hashes.add(simhash)
        
        return deduped
    
    def search_with_context(self, query: str, k: int = 12, db_conn=None) -> List[Dict[str, Any]]:
        """
        Search and return full context for each result.
        Uses hybrid ranking for better results.
        """
        # Use hybrid search
        search_results = self.search_hybrid(query, k, db_conn)
        
        # Format results for LLM consumption
        formatted_results = []
        for i, result in enumerate(search_results):
            metadata = result.get('metadata', {})
            
            formatted_result = {
                'rank': i + 1,
                'score': result['final_score'],
                'url': metadata.get('url', ''),
                'title': metadata.get('title', ''),
                'site_name': metadata.get('site_name', ''),
                'heading': metadata.get('section_heading', ''),
                'content': metadata.get('section_text', ''),
                'page': metadata.get('section_page', ''),
                'source_info': f"Source: {metadata.get('title', 'Unknown')} - {metadata.get('site_name', 'Unknown')}",
                'ranking_details': {
                    'vector_score': result.get('vector_score', 0),
                    'bm25_score': result.get('bm25_score', 0),
                    'credibility_score': result.get('credibility_score', 0),
                    'freshness_score': result.get('freshness_score', 0)
                }
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the enhanced vector index."""
        return {
            'total_vectors': len(self.id_mappings),
            'index_size': self.index.ntotal,
            'dimension': self.dimension,
            'model_name': self.model_name,
            'index_path': self.index_path,
            'bm25_indexed': self.bm25_index is not None,
            'bm25_texts_count': len(self.bm25_texts) if self.bm25_texts else 0,
            'simhash_threshold': self.simhash_threshold
        }
    
    def rebuild_index(self, db_conn) -> int:
        """
        Rebuild the entire enhanced vector index from database content.
        """
        print("Rebuilding enhanced vector index from database...")
        
        # Clear existing index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_mappings = []
        self.bm25_index = None
        self.bm25_texts = []
        
        # Get all documents and sections from database
        cursor = db_conn.execute("SELECT id FROM normalized_doc")
        doc_ids = [row[0] for row in cursor.fetchall()]
        
        total_sections = 0
        for doc_id in doc_ids:
            sections = get_sections_by_doc_id(db_conn, doc_id)
            sections_added = self.add_sections(doc_id, sections)
            total_sections += sections_added
        
        # Save the rebuilt index
        self._save_index()
        
        print(f"Rebuilt enhanced index with {total_sections} sections from {len(doc_ids)} documents")
        return total_sections
    
    def close(self):
        """Save and close the enhanced vector index."""
        self._save_index()
        print("Enhanced vector index saved and closed")


# Global enhanced vector index instance
enhanced_vector_index = EnhancedVectorIndex()
