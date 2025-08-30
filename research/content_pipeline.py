"""
Content Generation Pipeline for Phase 2.
Orchestrates the entire workflow from question analysis to content generation.
"""

import asyncio
from typing import Dict, Any, Optional, List
from .llm import llm_client
from .context_search import context_search
from .vector_index import vector_index
from .pipeline import run_research
from .db import init_db, upsert_citations


class ContentGenerationPipeline:
    """Main pipeline for generating educational video content."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "citations.db"
        self.db_conn = None
    
    async def __aenter__(self):
        """Initialize database connection."""
        self.db_conn = init_db(self.db_path)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close database connection and save vector index."""
        if self.db_conn:
            self.db_conn.close()
        vector_index.close()
    
    async def generate_video_content(self, question_id: str, question: str, solution: str) -> Dict[str, Any]:
        """
        Main pipeline: Generate complete video content from question and solution.
        This is the core function that orchestrates the entire Phase 2 workflow.
        """
        print(f"🚀 Starting content generation for Question {question_id}")
        print(f"Question: {question}")
        print(f"Solution: {solution}")
        
        try:
            # Step 1: LLM Analysis - Determine what to research
            print("\n🔍 Step 1: LLM Analysis - Determining research focus...")
            search_query = await llm_client.analyze_question(question, solution)
            print(f"Generated search query: {search_query}")
            
            # Step 2: Research - Gather knowledge base
            print("\n📚 Step 2: Research - Gathering knowledge base...")
            citations = await run_research(
                question_id=question_id,
                query=search_query,
                top_k=12,  # Get more content for comprehensive coverage
                provider="serpapi",
                db_conn=self.db_conn
            )
            
            if not citations:
                raise ValueError("No research content found. Cannot generate video content.")
            
            print(f"Research complete: {len(citations)} citations gathered")
            
            # Step 3: Build Vector Index - Enable semantic search
            print("\n🔢 Step 3: Building vector index for semantic search...")
            # Rebuild index with new content
            sections_added = vector_index.rebuild_index(self.db_conn)
            print(f"Vector index built: {sections_added} sections indexed")
            
            # Step 4: Get Research Context - RAG retrieval
            print("\n🔍 Step 4: Retrieving research context...")
            research_context = context_search.get_research_context(question, solution, self.db_conn)
            print(f"Research context retrieved: {len(research_context)} characters")
            
            # Step 5: Generate Video Outline
            print("\n📝 Step 5: Generating video outline...")
            outline_result = await llm_client.generate_outline(question, solution, research_context)
            print(f"Outline generated: {outline_result['tokens_used']} tokens used")
            
            # Step 6: Generate Video Script
            print("\n📜 Step 6: Generating video script...")
            script_result = await llm_client.generate_script(
                outline_result['outline'], 
                research_context
            )
            print(f"Script generated: {script_result['tokens_used']} tokens used")
            
            # Step 7: Generate Slide Specifications
            print("\n🎨 Step 7: Generating slide specifications...")
            slides_result = await llm_client.generate_slide_specs(script_result['script'])
            print(f"Slide specs generated: {slides_result['tokens_used']} tokens used")
            
            # Compile results
            result = {
                'question_id': question_id,
                'question': question,
                'solution': solution,
                'search_query': search_query,
                'research_stats': {
                    'citations_count': len(citations),
                    'sections_indexed': sections_added,
                    'context_length': len(research_context)
                },
                'content': {
                    'outline': outline_result['outline'],
                    'script': script_result['script'],
                    'slide_specs': slides_result['slide_specs']
                },
                'generation_stats': {
                    'outline_tokens': outline_result['tokens_used'],
                    'script_tokens': script_result['tokens_used'],
                    'slides_tokens': slides_result['tokens_used'],
                    'total_tokens': (
                        outline_result['tokens_used'] + 
                        script_result['tokens_used'] + 
                        slides_result['tokens_used']
                    )
                },
                'models_used': {
                    'outline': outline_result['model'],
                    'script': script_result['model'],
                    'slides': slides_result['model']
                }
            }
            
            print(f"\n🎉 Content generation complete!")
            print(f"Total tokens used: {result['generation_stats']['total_tokens']}")
            print(f"Content ready for video production")
            
            return result
            
        except Exception as e:
            print(f"❌ Content generation failed: {e}")
            raise
    
    async def generate_outline_only(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate only the video outline (useful for planning)."""
        print(f"📝 Generating outline for: {question}")
        
        # Get basic context (without full research)
        basic_context = f"Question: {question}\nSolution: {solution}"
        
        outline_result = await llm_client.generate_outline(question, solution, basic_context)
        
        return {
            'outline': outline_result['outline'],
            'tokens_used': outline_result['tokens_used'],
            'model': outline_result['model']
        }
    
    async def generate_script_from_outline(self, outline: str, question: str, solution: str) -> Dict[str, Any]:
        """Generate script from an existing outline."""
        print(f"📜 Generating script from outline for: {question}")
        
        # Get research context for the specific question
        research_context = context_search.get_research_context(question, solution, self.db_conn)
        
        script_result = await llm_client.generate_script(outline, research_context)
        
        return {
            'script': script_result['script'],
            'tokens_used': script_result['tokens_used'],
            'model': script_result['model']
        }
    
    async def test_llm_connection(self) -> bool:
        """Test LLM API connection."""
        return await llm_client.test_connection()
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current status of the pipeline components."""
        return {
            'llm_connection': await self.test_llm_connection(),
            'vector_index_stats': vector_index.get_index_stats(),
            'database_path': self.db_path,
            'config_validation': {
                'openai': llm_client.client.api_key is not None,
                'serpapi': True  # We'll check this in the research phase
            }
        }


# Convenience function for quick content generation
async def generate_video_content(question_id: str, question: str, solution: str, db_path: str = None) -> Dict[str, Any]:
    """
    Convenience function to generate video content in one call.
    """
    async with ContentGenerationPipeline(db_path) as pipeline:
        return await pipeline.generate_video_content(question_id, question, solution)


# Convenience function for testing
async def test_phase2_setup() -> Dict[str, Any]:
    """
    Test the Phase 2 setup to ensure all components are working.
    """
    print("🧪 Testing Phase 2 Setup...")
    
    try:
        # Test LLM connection
        print("Testing LLM connection...")
        llm_working = await llm_client.test_connection()
        
        # Test vector index
        print("Testing vector index...")
        index_stats = vector_index.get_index_stats()
        
        # Test configuration
        print("Testing configuration...")
        config_valid = llm_client.client.api_key is not None
        
        result = {
            'llm_connection': llm_working,
            'vector_index': index_stats,
            'configuration': config_valid,
            'overall_status': 'ready' if all([llm_working, config_valid]) else 'issues'
        }
        
        if result['overall_status'] == 'ready':
            print("✅ Phase 2 setup is ready!")
        else:
            print("⚠️ Phase 2 setup has issues. Check the details above.")
        
        return result
        
    except Exception as e:
        print(f"❌ Phase 2 setup test failed: {e}")
        return {
            'overall_status': 'failed',
            'error': str(e)
        }
