"""
Context Search API module for Phase 2.
Provides RAG retrieval capabilities for LLM content generation.
"""

from typing import List, Dict, Any, Optional
from .vector_index import vector_index
from .db import get_doc_by_url, get_sections_by_doc_id


class ContextSearchAPI:
    """API for retrieving relevant context from the knowledge base."""
    
    def __init__(self):
        self.vector_index = vector_index
    
    def search_context(self, query: str, k: int = 12, db_conn=None) -> List[Dict[str, Any]]:
        """
        Search for relevant context using vector similarity.
        This is the core RAG retrieval function for LLMs.
        """
        if not query.strip():
            return []
        
        # Use vector search to find relevant sections
        search_results = self.vector_index.search_with_context(query, k, db_conn)
        
        # Format results for LLM consumption
        formatted_results = []
        for result in search_results:
            formatted_result = {
                'rank': result['rank'],
                'score': result['score'],
                'url': result.get('url', ''),
                'title': result.get('title', ''),
                'site_name': result.get('site_name', ''),
                'heading': result.get('section_heading', ''),
                'content': result.get('section_text', ''),
                'page': result.get('section_page', ''),
                'source_info': f"Source: {result.get('title', 'Unknown')} - {result.get('site_name', 'Unknown')}"
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def get_research_context(self, question: str, solution: str, db_conn=None) -> str:
        """
        Get comprehensive research context for content generation.
        This combines multiple search queries to provide rich context.
        """
        # Create multiple search queries for comprehensive coverage
        search_queries = [
            question,  # Direct question search
            solution,  # Solution-related content
            f"{question} {solution}",  # Combined search
        ]
        
        # Add concept-based searches
        if "how" in question.lower():
            search_queries.append(f"process steps {question}")
        if "what" in question.lower():
            search_queries.append(f"definition explanation {question}")
        if "why" in question.lower():
            search_queries.append(f"causes reasons {question}")
        
        # Collect context from all queries
        all_context = []
        seen_content = set()  # Avoid duplicates
        
        for query in search_queries:
            results = self.search_context(query, k=6, db_conn=db_conn)
            
            for result in results:
                # Create a unique identifier for deduplication
                content_hash = hash(result['content'][:100])
                
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    
                    # Format context for LLM consumption
                    context_entry = f"""
Source {result['rank']}: {result['source_info']}
Heading: {result['heading']}
Content: {result['content'][:500]}{'...' if len(result['content']) > 500 else ''}
Relevance Score: {result['score']:.3f}
---
"""
                    all_context.append(context_entry)
        
        # Combine all context
        if all_context:
            combined_context = f"""
Research Context for: {question}
Solution: {solution}

Relevant Sources and Information:
{''.join(all_context)}

Total Sources: {len(all_context)}
"""
            return combined_context
        else:
            return f"No relevant research context found for: {question}"
    
    def get_focused_context(self, topic: str, db_conn=None, k: int = 8) -> str:
        """
        Get focused context for a specific topic.
        Useful for generating specific sections of content.
        """
        results = self.search_context(topic, k, db_conn)
        
        if not results:
            return f"No context found for topic: {topic}"
        
        context_parts = []
        for result in results:
            context_part = f"""
Source {result['rank']}: {result['source_info']}
Content: {result['content'][:300]}{'...' if len(result['content']) > 300 else ''}
"""
            context_parts.append(context_part)
        
        return f"Focused Context for '{topic}':\n{''.join(context_parts)}"
    
    def get_citation_context(self, question_id: str, db_conn=None) -> str:
        """
        Get context from previously stored citations for a question.
        This provides continuity and reference to previous research.
        """
        if not db_conn:
            return "Database connection required for citation context"
        
        # Get citations for the question
        from .db import get_citations_for_question
        citations = get_citations_for_question(db_conn, question_id, limit=10)
        
        if not citations:
            return f"No previous citations found for question: {question_id}"
        
        context_parts = []
        for i, citation in enumerate(citations, 1):
            context_part = f"""
Citation {i}: {citation.title or 'Untitled'}
Source: {citation.site_name or 'Unknown'}
Credibility: {citation.credibility:.2f}
Snippet: {citation.snippet or 'No snippet available'}
"""
            context_parts.append(context_part)
        
        return f"Previous Research Citations for Question {question_id}:\n{''.join(context_parts)}"
    
    def search_by_domain(self, query: str, domain: str, db_conn=None, k: int = 6) -> List[Dict[str, Any]]:
        """
        Search for context within a specific domain (e.g., .edu, .gov, specific sites).
        Useful for finding authoritative sources.
        """
        # Get all results first
        all_results = self.search_context(query, k=k*2, db_conn=db_conn)
        
        # Filter by domain
        domain_results = []
        for result in all_results:
            if domain.lower() in result.get('url', '').lower():
                domain_results.append(result)
                if len(domain_results) >= k:
                    break
        
        return domain_results
    
    def get_context_summary(self, question: str, db_conn=None) -> Dict[str, Any]:
        """
        Get a summary of available context for a question.
        Useful for understanding what information is available.
        """
        # Get comprehensive context
        full_context = self.get_research_context(question, "", db_conn)
        
        # Analyze context
        context_stats = {
            'question': question,
            'context_length': len(full_context),
            'has_content': len(full_context) > 100,
            'context_preview': full_context[:500] + "..." if len(full_context) > 500 else full_context
        }
        
        # Get vector index stats
        index_stats = self.vector_index.get_index_stats()
        context_stats['index_stats'] = index_stats
        
        return context_stats


# Global context search API instance
context_search = ContextSearchAPI()
