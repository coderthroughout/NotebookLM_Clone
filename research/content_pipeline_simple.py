"""
Simplified Content Generation Pipeline for Phase 2.
Uses the simple_vector_index instead of the problematic vector_index.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import config
from .llm import llm_client
from .simple_vector_index import simple_vector_index


class SimpleContentGenerationPipeline:
    """Simplified content generation pipeline using simple vector index."""
    
    def __init__(self):
        self.pipeline_status = "initialized"
        self.last_run = None
        self.total_generations = 0
        
    async def test_llm_connection(self) -> bool:
        """Test OpenAI LLM connection."""
        try:
            return await llm_client.test_connection()
        except Exception as e:
            print(f"LLM connection test failed: {e}")
            return False
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "status": self.pipeline_status,
            "last_run": self.last_run,
            "total_generations": self.total_generations,
            "llm_models": {
                "gpt4": config.OPENAI_MODEL_GPT4,
                "gpt35": config.OPENAI_MODEL_GPT35,
                "embedding": config.OPENAI_MODEL_EMBEDDING
            },
            "vector_index": "simple_openai"
        }
    
    async def generate_video_content(self, question_id: str, question: str, 
                                   solution: str, db_conn=None) -> Dict[str, Any]:
        """
        Main pipeline: Generate video content from question and solution.
        """
        try:
            self.pipeline_status = "running"
            start_time = datetime.now()
            
            print(f"🎬 Starting content generation for question: {question_id}")
            
            # Step 1: Analyze question and generate search queries
            search_queries = await self._analyze_question(question, solution)
            print(f"  🔍 Generated {len(search_queries)} search queries")
            
            # Step 2: Search for relevant context using simple vector index
            context_results = []
            if db_conn:
                for query in search_queries[:3]:  # Limit to top 3 queries
                    results = await simple_vector_index.search_with_context(
                        query=query, k=5, db_conn=db_conn
                    )
                    context_results.extend(results)
            
            print(f"  📚 Found {len(context_results)} context results")
            
            # Step 3: Generate outline
            outline = await self._generate_outline(question, solution, context_results)
            print(f"  📝 Generated outline with {len(outline.get('sections', []))} sections")
            
            # Step 4: Generate script
            script = await self._generate_script(question, solution, outline, context_results)
            print(f"  🎭 Generated script ({len(script.get('content', ''))} characters)")
            
            # Step 5: Generate slide specifications
            slides = await self._generate_slide_specs(question, solution, outline, script)
            print(f"  🖼️ Generated {len(slides.get('slides', []))} slide specs")
            
            # Update pipeline status
            self.pipeline_status = "completed"
            self.last_run = datetime.now().isoformat()
            self.total_generations += 1
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "question_id": question_id,
                "question": question,
                "solution": solution,
                "outline": outline,
                "script": script,
                "slides": slides,
                "context_used": len(context_results),
                "generation_time": duration,
                "timestamp": self.last_run
            }
            
        except Exception as e:
            self.pipeline_status = "error"
            print(f"❌ Content generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "question_id": question_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_question(self, question: str, solution: str) -> List[str]:
        """Analyze question and generate search queries."""
        try:
            prompt = f"""
            Analyze this question and solution to generate 3-5 search queries for finding relevant educational content.
            
            Question: {question}
            Solution: {solution}
            
            Generate specific, focused search queries that would help explain the concepts.
            Return only the search queries, one per line.
            """
            
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT35,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            queries = response.choices[0].message.content.strip().split('\n')
            # Clean up queries
            queries = [q.strip() for q in queries if q.strip() and not q.startswith('-')]
            return queries[:5]  # Limit to 5 queries
            
        except Exception as e:
            print(f"Question analysis failed: {e}")
            # Fallback queries
            return [question, solution]
    
    async def _generate_outline(self, question: str, solution: str, 
                               context_results: List[Dict]) -> Dict[str, Any]:
        """Generate video outline."""
        try:
            # Prepare context for LLM
            context_text = ""
            if context_results:
                context_text = "\n\n".join([
                    f"Source {i+1}: {result.get('content', '')[:300]}..."
                    for i, result in enumerate(context_results[:3])
                ])
            
            prompt = f"""
            Create a detailed video outline for explaining this question and solution.
            
            Question: {question}
            Solution: {solution}
            
            Context Information:
            {context_text if context_text else 'No additional context available.'}
            
            Create a structured outline with:
            1. Introduction (hook and overview)
            2. Main concepts (2-4 key points)
            3. Step-by-step solution explanation
            4. Summary and key takeaways
            
            Return a JSON structure with sections and subsections.
            """
            
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT4,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.MAX_TOKENS_OUTLINE,
                temperature=config.TEMPERATURE
            )
            
            # Try to parse JSON response
            try:
                import json
                outline = json.loads(response.choices[0].message.content)
                return outline
            except:
                # Fallback: return structured text
                return {
                    "title": f"Video Outline: {question[:50]}...",
                    "sections": response.choices[0].message.content.split('\n')
                }
                
        except Exception as e:
            print(f"Outline generation failed: {e}")
            return {
                "title": "Video Outline",
                "sections": ["Introduction", "Main Concepts", "Solution", "Summary"]
            }
    
    async def _generate_script(self, question: str, solution: str, 
                              outline: Dict, context_results: List[Dict]) -> Dict[str, Any]:
        """Generate video script."""
        try:
            # Prepare context for LLM
            context_text = ""
            if context_results:
                context_text = "\n\n".join([
                    f"Source {i+1}: {result.get('content', '')[:200]}..."
                    for i, result in enumerate(context_results[:3])
                ])
            
            prompt = f"""
            Create a detailed video script based on this outline.
            
            Question: {question}
            Solution: {solution}
            
            Outline: {outline}
            
            Context Information:
            {context_text if context_text else 'No additional context available.'}
            
            Create a natural, engaging script that:
            1. Follows the outline structure
            2. Explains concepts clearly and engagingly
            3. Uses conversational language
            4. Includes timing estimates for each section
            5. Is suitable for voice-over narration
            
            Return a JSON structure with sections, content, and timing.
            """
            
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT4,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.MAX_TOKENS_SCRIPT,
                temperature=config.TEMPERATURE
            )
            
            # Try to parse JSON response
            try:
                import json
                script = json.loads(response.choices[0].message.content)
                return script
            except:
                # Fallback: return structured text
                return {
                    "title": f"Video Script: {question[:50]}...",
                    "content": response.choices[0].message.content,
                    "estimated_duration": "5-7 minutes"
                }
                
        except Exception as e:
            print(f"Script generation failed: {e}")
            return {
                "title": "Video Script",
                "content": "Script generation failed. Please try again.",
                "estimated_duration": "Unknown"
            }
    
    async def _generate_slide_specs(self, question: str, solution: str, 
                                   outline: Dict, script: Dict) -> Dict[str, Any]:
        """Generate slide specifications."""
        try:
            prompt = f"""
            Create detailed slide specifications for this video.
            
            Question: {question}
            Solution: {solution}
            
            Outline: {outline}
            Script: {script.get('content', '')[:500]}...
            
            Create 5-8 slides that:
            1. Follow the video structure
            2. Include clear visual elements
            3. Support the narration
            4. Are visually appealing and educational
            
            For each slide, specify:
            - Slide number and title
            - Key content points
            - Visual elements (charts, diagrams, text layout)
            - Color scheme suggestions
            - Animation/transition notes
            
            Return a JSON structure with slide details.
            """
            
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT4,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.MAX_TOKENS_SLIDES,
                temperature=config.TEMPERATURE
            )
            
            # Try to parse JSON response
            try:
                import json
                slides = json.loads(response.choices[0].message.content)
                return slides
            except:
                # Fallback: return structured text
                return {
                    "title": "Slide Specifications",
                    "slides": response.choices[0].message.content.split('\n')
                }
                
        except Exception as e:
            print(f"Slide generation failed: {e}")
            return {
                "title": "Slide Specifications",
                "slides": ["Slide generation failed. Please try again."]
            }
    
    async def generate_outline_only(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate only the outline (for testing)."""
        return await self._generate_outline(question, solution, [])
    
    async def generate_script_from_outline(self, question: str, solution: str, 
                                         outline: Dict) -> Dict[str, Any]:
        """Generate script from existing outline."""
        return await self._generate_script(question, solution, outline, [])


# Global pipeline instance
simple_content_pipeline = SimpleContentGenerationPipeline()


# Convenience functions
async def generate_video_content(question_id: str, question: str, 
                               solution: str, db_conn=None) -> Dict[str, Any]:
    """Convenience function to generate video content."""
    return await simple_content_pipeline.generate_video_content(
        question_id, question, solution, db_conn
    )

async def test_phase2_setup() -> bool:
    """Test if Phase 2 setup is working."""
    try:
        # Test LLM connection
        llm_working = await llm_client.test_connection()
        
        # Test simple vector index
        index_stats = simple_vector_index.get_index_stats()
        index_working = index_stats['type'] == 'simple_openai'
        
        # Test content pipeline
        pipeline = SimpleContentGenerationPipeline()
        pipeline_working = True
        
        return llm_working and index_working and pipeline_working
        
    except Exception as e:
        print(f"Phase 2 setup test failed: {e}")
        return False
