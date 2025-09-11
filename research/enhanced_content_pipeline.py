"""
Enhanced Content Pipeline for Phase 3.
Integrates content generation with video production.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import config
from .llm import llm_client
from .simple_vector_index import simple_vector_index
from .video_production import video_production_pipeline
from .models import OutlineModel, ScriptModel, SlidesModel


class EnhancedContentPipeline:
    """Enhanced pipeline that combines content generation and video production."""
    
    def __init__(self):
        self.pipeline_status = "initialized"
        self.last_run = None
        self.total_generations = 0
        self.total_videos = 0
        
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
            "total_videos": self.total_videos,
            "llm_models": {
                "gpt4": config.OPENAI_MODEL_GPT4,
                "gpt35": config.OPENAI_MODEL_GPT35,
                "embedding": config.OPENAI_MODEL_EMBEDDING
            },
            "vector_index": "simple_openai",
            "video_production": "enabled"
        }
    
    async def generate_complete_video(
        self, 
        question_id: str, 
        question: str, 
        solution: str, 
        db_conn=None
    ) -> Dict[str, Any]:
        """
        Complete pipeline: Generate content AND create video.
        """
        try:
            self.pipeline_status = "running"
            start_time = datetime.now()
            
            print(f"🎬 Starting COMPLETE video generation for question: {question_id}")
            
            # Phase 2: Content Generation
            print("\n📝 PHASE 2: Content Generation...")
            
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
            
            # Step 5: Generate ultimate NotebookLM-style slide specifications
            slides = await self._generate_ultimate_notebooklm_slides(question, solution)
            print(f"  🖼️ Generated {len(slides.get('slides', []))} ultimate NotebookLM-style slides")
            
            # Phase 3: Video Production
            print("\n🎬 PHASE 3: Video Production...")
            
            # Step 6: Create video from generated content
            video_result = await video_production_pipeline.create_video_from_content(
                question_id, outline, script, slides
            )
            
            if video_result['status'] == 'success':
                print(f"  🎬 Video created: {video_result['video_file']}")
                print(f"  ⏱️ Video duration: {video_result['video_duration']} seconds")
                print(f"  🖼️ Slides used: {video_result['slide_count']}")
            else:
                print(f"  ❌ Video creation failed: {video_result['error']}")
                return video_result
            
            # Update pipeline status
            self.pipeline_status = "completed"
            self.last_run = datetime.now().isoformat()
            self.total_generations += 1
            self.total_videos += 1
            
            # Calculate total duration
            total_duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "question_id": question_id,
                "question": question,
                "solution": solution,
                "outline": outline,
                "script": script,
                "slides": slides,
                "video": video_result,
                "context_used": len(context_results),
                "total_generation_time": total_duration,
                "content_generation_time": total_duration - video_result.get('production_time', 0),
                "video_production_time": video_result.get('production_time', 0),
                "timestamp": self.last_run,
                "phase": "complete_pipeline"
            }
            
        except Exception as e:
            self.pipeline_status = "error"
            print(f"❌ Complete video generation failed: {e}")
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
            
            # Try to parse JSON response and validate
            raw = response.choices[0].message.content
            try:
                data = json.loads(raw)
            except Exception:
                # Retry with JSON-extraction instruction
                retry = await llm_client.client.chat.completions.create(
                    model=config.OPENAI_MODEL_GPT4,
                    messages=[{"role": "user", "content": prompt + "\n\nReturn valid JSON only."}],
                    max_tokens=config.MAX_TOKENS_OUTLINE,
                    temperature=config.TEMPERATURE
                )
                data = json.loads(retry.choices[0].message.content)
            # Validate against model; coerce to dict
            validated = OutlineModel.model_validate(data).model_dump()
            return validated
                
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
            
            raw = response.choices[0].message.content
            try:
                data = json.loads(raw)
            except Exception:
                retry = await llm_client.client.chat.completions.create(
                    model=config.OPENAI_MODEL_GPT4,
                    messages=[{"role": "user", "content": prompt + "\n\nReturn valid JSON only."}],
                    max_tokens=config.MAX_TOKENS_SCRIPT,
                    temperature=config.TEMPERATURE
                )
                data = json.loads(retry.choices[0].message.content)
            validated = ScriptModel.model_validate(data).model_dump()
            return validated
                
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
            You are an expert educational content creator. Create detailed slide specifications for an educational video.
            
            QUESTION: {question}
            SOLUTION: {solution}
            
            OUTLINE: {outline}
            SCRIPT: {script.get('content', '')[:1000]}...
            
            Create 8-12 educational slides that:
            1. TEACH the concept step-by-step
            2. Include ACTUAL educational content (not generic placeholders)
            3. Use the research data and citations
            4. Support the narration with visual elements
            5. Are engaging and informative
            
            For each slide, provide:
            - title: Descriptive title (e.g., "Power Rule: d/dx(x^n) = n*x^(n-1)")
            - content: Detailed educational content explaining the concept
            - bullets: Key points to highlight
            - visual_elements: Charts, diagrams, formulas, examples
            - duration: Time in seconds (5-8 seconds per slide)
            - type: "title", "concept", "example", "formula", "summary"
            
            IMPORTANT: Use ACTUAL educational content from the question and solution. 
            Include formulas, examples, step-by-step explanations, and visual elements.
            Do NOT use generic titles like "Slide 1", "Slide 2" - use descriptive educational titles.
            
            Return a JSON structure with this format:
            {{
                "slides": [
                    {{
                        "title": "Introduction to Derivatives",
                        "content": "A derivative measures the rate of change of a function...",
                        "bullets": ["Rate of change", "Slope of tangent line", "Applications"],
                        "visual_elements": [{{"type": "formula", "content": "f'(x) = lim[h→0] (f(x+h) - f(x))/h"}}],
                        "duration": 6.0,
                        "type": "concept"
                    }}
                ]
            }}
            """
            
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT4,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config.MAX_TOKENS_SLIDES,
                temperature=config.TEMPERATURE
            )
            
            raw = response.choices[0].message.content
            try:
                data = json.loads(raw)
            except Exception:
                retry = await llm_client.client.chat.completions.create(
                    model=config.OPENAI_MODEL_GPT4,
                    messages=[{"role": "user", "content": prompt + "\n\nReturn valid JSON only."}],
                    max_tokens=config.MAX_TOKENS_SLIDES,
                    temperature=config.TEMPERATURE
                )
                data = json.loads(retry.choices[0].message.content)
            validated = SlidesModel.model_validate(data).model_dump()
            # Enforce hard cap 40 slides
            if len(validated.get("slides", [])) > 40:
                validated["slides"] = validated["slides"][:40]
            return validated
                
        except Exception as e:
            print(f"Slide generation failed: {e}")
            return {
                "title": "Slide Specifications",
                "slides": ["Slide generation failed. Please try again."]
            }
    
    async def _generate_notebooklm_slides(self, question: str, solution: str, 
                                        context_results: List[Dict]) -> Dict[str, Any]:
        """Generate NotebookLM-style educational slides."""
        try:
            from .notebooklm_content_generator import notebooklm_content_generator
            
            # Use the NotebookLM-style content generator
            slides_result = await notebooklm_content_generator.generate_educational_slides(
                question, solution, context_results
            )
            
            return slides_result
            
        except Exception as e:
            print(f"NotebookLM slide generation failed: {e}")
            # Fallback to original method
            return await self._generate_slide_specs(question, solution, {}, {})
    
    async def _generate_simple_notebooklm_slides(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate simple NotebookLM-style educational slides."""
        try:
            from .simple_notebooklm_generator import simple_notebooklm_generator
            
            # Use the simple NotebookLM generator
            slides_result = await simple_notebooklm_generator.generate_educational_video(question, solution)
            
            return slides_result
            
        except Exception as e:
            print(f"Simple NotebookLM slide generation failed: {e}")
            # Fallback to original method
            return await self._generate_slide_specs(question, solution, {}, {})
    
    async def _generate_high_quality_notebooklm_slides(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate high-quality NotebookLM-style educational slides."""
        try:
            from .high_quality_slide_generator import high_quality_slide_generator
            
            # Use the high-quality generator
            slides_result = await high_quality_slide_generator.generate_educational_video(question, solution)
            
            return slides_result
            
        except Exception as e:
            print(f"High-quality NotebookLM slide generation failed: {e}")
            # Fallback to simple method
            return await self._generate_simple_notebooklm_slides(question, solution)
    
    async def _generate_ultimate_notebooklm_slides(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate ultimate NotebookLM-style educational slides."""
        try:
            from .ultimate_slide_generator import ultimate_slide_generator
            
            # Use the ultimate generator - completely bypass old system
            slides_result = await ultimate_slide_generator.generate_educational_video(question, solution)
            
            return slides_result
            
        except Exception as e:
            print(f"Ultimate NotebookLM slide generation failed: {e}")
            # Fallback to high-quality method
            return await self._generate_high_quality_notebooklm_slides(question, solution)
    
    async def create_sample_complete_video(self, question_id: str = "sample_001") -> Dict[str, Any]:
        """Create a sample complete video for testing."""
        try:
            sample_question = "What is machine learning?"
            sample_solution = "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed."
            
            return await self.generate_complete_video(question_id, sample_question, sample_solution)
            
        except Exception as e:
            print(f"Sample complete video creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "question_id": question_id
            }


# Global enhanced pipeline instance
enhanced_content_pipeline = EnhancedContentPipeline()


# Convenience functions
async def generate_complete_video(
    question_id: str, 
    question: str, 
    solution: str, 
    db_conn=None
) -> Dict[str, Any]:
    """Convenience function to generate complete video."""
    return await enhanced_content_pipeline.generate_complete_video(
        question_id, question, solution, db_conn
    )

async def create_sample_complete_video(question_id: str = "sample_001") -> Dict[str, Any]:
    """Convenience function to create a sample complete video."""
    return await enhanced_content_pipeline.create_sample_complete_video(question_id)

async def test_phase3_setup() -> bool:
    """Test if Phase 3 setup is working."""
    try:
        # Test LLM connection
        llm_working = await llm_client.test_connection()
        
        # Test video production pipeline
        video_pipeline = video_production_pipeline
        video_working = video_pipeline.get_pipeline_status()['phase'] == 'video_production'
        
        # Test enhanced content pipeline
        enhanced_pipeline = EnhancedContentPipeline()
        enhanced_working = True
        
        return llm_working and video_working and enhanced_working
        
    except Exception as e:
        print(f"Phase 3 setup test failed: {e}")
        return False
