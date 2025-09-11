"""
NotebookLM-style Content Generator.
Creates rich, educational content similar to Google's NotebookLM.
"""

import asyncio
import json
from typing import List, Dict, Any
from .llm import llm_client
from .config import config


class NotebookLMContentGenerator:
    """
    Generate NotebookLM-style educational content.
    Focuses on creating rich, engaging educational materials.
    """
    
    def __init__(self):
        self.llm_client = llm_client
    
    async def generate_educational_slides(self, question: str, solution: str, 
                                        context_results: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate educational slides in NotebookLM style.
        Creates 8-12 slides with rich educational content.
        """
        try:
            print("🎓 Generating NotebookLM-style educational content...")
            
            # Step 1: Analyze the question and solution
            analysis = await self._analyze_educational_content(question, solution)
            
            # Step 2: Generate structured educational content
            educational_content = await self._generate_structured_content(
                question, solution, analysis, context_results
            )
            
            # Step 3: Create slide specifications
            slides = await self._create_slide_specifications(educational_content)
            
            return {
                "title": f"Understanding: {question}",
                "slides": slides,
                "total_slides": len(slides),
                "estimated_duration": len(slides) * 6,  # 6 seconds per slide
                "content_type": "educational"
            }
            
        except Exception as e:
            print(f"❌ Educational content generation failed: {e}")
            return await self._create_fallback_content(question, solution)
    
    async def _analyze_educational_content(self, question: str, solution: str) -> Dict[str, Any]:
        """Analyze the question and solution to understand the educational needs."""
        prompt = f"""
        You are an expert educational content analyst. Analyze this question and solution to understand what needs to be taught.
        
        QUESTION: {question}
        SOLUTION: {solution}
        
        Provide a structured analysis including:
        1. Core concept being taught
        2. Prerequisites needed
        3. Key learning objectives
        4. Common misconceptions
        5. Real-world applications
        6. Difficulty level (beginner/intermediate/advanced)
        
        Return a JSON structure with your analysis.
        """
        
        response = await self.llm_client.client.chat.completions.create(
            model=config.OPENAI_MODEL_GPT4,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "core_concept": "Mathematical concept",
                "prerequisites": ["Basic algebra"],
                "learning_objectives": ["Understand the concept", "Apply the solution"],
                "difficulty": "intermediate"
            }
    
    async def _generate_structured_content(self, question: str, solution: str, 
                                         analysis: Dict, context_results: List[Dict]) -> Dict[str, Any]:
        """Generate structured educational content."""
        prompt = f"""
        You are an expert educational content creator. Create structured educational content for this topic.
        
        QUESTION: {question}
        SOLUTION: {solution}
        ANALYSIS: {analysis}
        
        Create educational content that includes:
        1. Introduction to the concept
        2. Step-by-step explanation
        3. Key formulas or rules
        4. Worked examples
        5. Common mistakes to avoid
        6. Practice applications
        7. Summary and key takeaways
        
        Make the content engaging, clear, and educational. Use analogies and real-world examples where appropriate.
        Focus on helping students understand the concept, not just memorize the solution.
        
        Return a JSON structure with detailed educational content.
        """
        
        response = await self.llm_client.client.chat.completions.create(
            model=config.OPENAI_MODEL_GPT4,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.4
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "introduction": "Let's learn about this concept step by step.",
                "explanation": solution,
                "examples": ["Example 1: Basic application"],
                "summary": "Key points to remember"
            }
    
    async def _create_slide_specifications(self, educational_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create detailed slide specifications for NotebookLM-style presentation."""
        prompt = f"""
        You are an expert presentation designer creating NotebookLM-style educational slides.
        
        EDUCATIONAL CONTENT: {educational_content}
        
        Create 8-12 slides that follow this structure:
        
        1. TITLE SLIDE: Engaging title with subtitle
        2. INTRODUCTION: What we'll learn today
        3. CONCEPT OVERVIEW: The main concept explained simply
        4. STEP-BY-STEP: Detailed explanation with clear steps
        5. FORMULA/RULE: Key mathematical rules or formulas
        6. EXAMPLE 1: First worked example
        7. EXAMPLE 2: Second worked example (if applicable)
        8. COMMON MISTAKES: What to avoid
        9. PRACTICE: How to apply this knowledge
        10. SUMMARY: Key takeaways
        11. CONCLUSION: What we learned
        
        For each slide, provide:
        - title: Clear, descriptive title
        - content: Main educational content
        - bullets: Key points (3-5 bullets max)
        - visual_elements: Formulas, diagrams, or highlights
        - duration: 5-8 seconds
        - type: title, concept, example, formula, summary, etc.
        
        IMPORTANT: 
        - Use ACTUAL educational content, not generic placeholders
        - Include specific formulas, examples, and explanations
        - Make titles descriptive and educational
        - Focus on learning and understanding
        
        Return a JSON structure with slides array.
        """
        
        response = await self.llm_client.client.chat.completions.create(
            model=config.OPENAI_MODEL_GPT4,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('slides', [])
        except:
            return await self._create_fallback_slides(educational_content)
    
    async def _create_fallback_slides(self, educational_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fallback slides if JSON parsing fails."""
        return [
            {
                "title": "Understanding the Concept",
                "content": educational_content.get('introduction', 'Let\'s learn about this concept step by step.'),
                "bullets": [
                    "We'll explore the main concept",
                    "Learn the key principles",
                    "See practical examples"
                ],
                "duration": 6.0,
                "type": "title"
            },
            {
                "title": "Step-by-Step Explanation",
                "content": educational_content.get('explanation', 'Here\'s how to solve this step by step.'),
                "bullets": [
                    "Identify the key components",
                    "Apply the appropriate method",
                    "Check your work"
                ],
                "duration": 7.0,
                "type": "concept"
            },
            {
                "title": "Key Takeaways",
                "content": educational_content.get('summary', 'Remember these important points.'),
                "bullets": [
                    "Understand the concept",
                    "Practice regularly",
                    "Apply to real problems"
                ],
                "duration": 5.0,
                "type": "summary"
            }
        ]
    
    async def _create_fallback_content(self, question: str, solution: str) -> Dict[str, Any]:
        """Create fallback content if generation fails."""
        return {
            "title": f"Understanding: {question}",
            "slides": [
                {
                    "title": f"Question: {question}",
                    "content": "Let's work through this step by step.",
                    "bullets": ["Read the question carefully", "Identify what's being asked", "Plan your approach"],
                    "duration": 6.0,
                    "type": "title"
                },
                {
                    "title": "Solution Approach",
                    "content": solution,
                    "bullets": ["Break down the problem", "Apply the right method", "Verify your answer"],
                    "duration": 7.0,
                    "type": "concept"
                },
                {
                    "title": "Key Points",
                    "content": "Remember these important concepts.",
                    "bullets": ["Understand the method", "Practice similar problems", "Check your work"],
                    "duration": 5.0,
                    "type": "summary"
                }
            ],
            "total_slides": 3,
            "estimated_duration": 18,
            "content_type": "educational"
        }


# Global instance
notebooklm_content_generator = NotebookLMContentGenerator()
