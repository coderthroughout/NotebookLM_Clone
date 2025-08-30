"""
LLM integration module for Phase 2.
Handles OpenAI API calls and prompt templates for content generation.
"""

import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import config
from .models import ExtractedPage, NormalizedDoc, Section


class LLMClient:
    """OpenAI LLM client for content generation."""
    
    def __init__(self):
        if not config.validate_openai_config():
            raise ValueError("OpenAI configuration is incomplete. Please check your .env file.")
        
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            project=config.OPENAI_PROJECT_ID,
            organization=config.OPENAI_ORG_ID
        )
        
        # Model configurations
        self.gpt4_model = config.OPENAI_MODEL_GPT4
        self.gpt35_model = config.OPENAI_MODEL_GPT35
        self.embedding_model = config.OPENAI_MODEL_EMBEDDING
        
        # Token limits
        self.max_tokens_outline = config.MAX_TOKENS_OUTLINE
        self.max_tokens_script = config.MAX_TOKENS_SCRIPT
        self.max_tokens_slides = config.MAX_TOKENS_SLIDES
        self.temperature = config.TEMPERATURE
    
    async def analyze_question(self, question: str, solution: str) -> str:
        """
        Analyze question and solution to generate an intelligent search query.
        This is the first step in Phase 2 - determining what to research.
        """
        prompt = f"""
You are an expert educational content researcher. Your task is to analyze a question and its solution to determine what topics need to be researched to create comprehensive educational content.

Question: {question}
Solution: {solution}

Based on this question and solution, generate a comprehensive search query that will help find the most relevant educational content. Consider:
1. Core concepts that need explanation
2. Background knowledge required
3. Related topics that would enhance understanding
4. Specific terminology to search for

Return only the search query, nothing else. Make it specific enough to find relevant content but broad enough to cover all necessary aspects.
"""

        response = await self.client.chat.completions.create(
            model=self.gpt35_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_outline(self, question: str, solution: str, research_context: str) -> Dict[str, Any]:
        """
        Generate a video outline based on research context.
        This creates the structure for the educational video.
        """
        prompt = f"""
You are an expert educational video producer. Create a comprehensive outline for an educational video based on the following:

Question: {question}
Solution: {solution}
Research Context: {research_context}

Create a structured outline with:
1. Introduction (hook and overview)
2. Main sections (3-5 key concepts)
3. Conclusion (summary and key takeaways)

For each section, provide:
- Section title
- Key points to cover
- Estimated duration
- Visual elements needed

Return the response as a structured outline that can be used to generate a script.
"""

        response = await self.client.chat.completions.create(
            model=self.gpt4_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens_outline,
            temperature=self.temperature
        )
        
        # For now, return the raw response. Later we can parse this into structured data
        return {
            "outline": response.choices[0].message.content.strip(),
            "model": self.gpt4_model,
            "tokens_used": response.usage.total_tokens
        }
    
    async def generate_script(self, outline: str, research_context: str) -> Dict[str, Any]:
        """
        Generate a video script based on the outline and research context.
        This creates the actual narration content for the video.
        """
        prompt = f"""
You are an expert educational script writer. Create a compelling video script based on this outline and research:

Outline: {outline}
Research Context: {research_context}

Create a script that:
1. Follows the outline structure exactly
2. Uses clear, engaging language
3. Incorporates key information from the research
4. Includes timing cues for video production
5. Uses conversational tone suitable for narration

Format the script with clear scene breaks and timing information.
"""

        response = await self.client.chat.completions.create(
            model=self.gpt4_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens_script,
            temperature=self.temperature
        )
        
        return {
            "script": response.choices[0].message.content.strip(),
            "model": self.gpt4_model,
            "tokens_used": response.usage.total_tokens
        }
    
    async def generate_slide_specs(self, script: str) -> Dict[str, Any]:
        """
        Generate slide specifications based on the script.
        This creates the visual content requirements for each slide.
        """
        prompt = f"""
You are an expert presentation designer. Based on this video script, create detailed slide specifications:

Script: {script}

For each major section, specify:
1. Slide title
2. Key content points
3. Visual elements needed (images, charts, diagrams)
4. Layout suggestions
5. Duration for each slide

Create specifications that will guide the creation of engaging, educational slides.
"""

        response = await self.client.chat.completions.create(
            model=self.gpt35_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens_slides,
            temperature=self.temperature
        )
        
        return {
            "slide_specs": response.choices[0].message.content.strip(),
            "model": self.gpt35_model,
            "tokens_used": response.usage.total_tokens
        }
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using OpenAI's embedding model.
        This will be used for vector indexing and semantic search.
        """
        if not texts:
            return []
        
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        
        return [embedding.embedding for embedding in response.data]
    
    async def test_connection(self) -> bool:
        """Test the OpenAI API connection."""
        try:
            response = await self.client.chat.completions.create(
                model=self.gpt35_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"OpenAI API connection failed: {e}")
            return False


# Global LLM client instance
llm_client = LLMClient()
