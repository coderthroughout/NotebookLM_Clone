"""
Simple NotebookLM-style Video Generator.
Creates clean, educational videos with proper content.
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from .llm import llm_client
from .config import config


class SimpleNotebookLMGenerator:
    """
    Simple, working NotebookLM-style video generator.
    Creates clean slides with actual educational content.
    """
    
    def __init__(self):
        self.output_dir = "temp_video"
        self.slide_width = 1920
        self.slide_height = 1080
        self.margin = 100
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_educational_video(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate a complete educational video with proper content."""
        try:
            print("🎓 Generating simple NotebookLM-style educational video...")
            
            # Step 1: Generate educational content
            educational_content = await self._generate_educational_content(question, solution)
            
            # Step 2: Create slides
            slides = await self._create_educational_slides(educational_content, question)
            
            return {
                "title": f"Understanding: {question}",
                "slides": slides,
                "total_slides": len(slides),
                "estimated_duration": len(slides) * 6,
                "content_type": "educational"
            }
            
        except Exception as e:
            print(f"❌ Educational video generation failed: {e}")
            return await self._create_simple_fallback(question, solution)
    
    async def _generate_educational_content(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate structured educational content."""
        prompt = f"""
        You are an expert math teacher. Create educational content for this question and solution.
        
        QUESTION: {question}
        SOLUTION: {solution}
        
        Create educational content that includes:
        1. A clear introduction to the concept
        2. Step-by-step explanation
        3. Key formulas or rules
        4. Worked example
        5. Key takeaways
        
        Make it educational and clear. Focus on teaching the concept, not just giving the answer.
        
        Return a JSON structure with:
        - introduction: Brief intro to the concept
        - explanation: Step-by-step explanation
        - formula: Key formula or rule
        - example: Worked example
        - summary: Key points to remember
        """
        
        try:
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT4,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                return json.loads(content)
            except:
                # If JSON parsing fails, create structured content
                return {
                    "introduction": f"Let's learn about {question}",
                    "explanation": solution,
                    "formula": "Key formula will be shown",
                    "example": "Worked example",
                    "summary": "Key points to remember"
                }
                
        except Exception as e:
            print(f"LLM content generation failed: {e}")
            return {
                "introduction": f"Understanding {question}",
                "explanation": solution,
                "formula": "Mathematical formula",
                "example": "Example problem",
                "summary": "Key takeaways"
            }
    
    async def _create_educational_slides(self, content: Dict[str, Any], question: str) -> List[Dict[str, Any]]:
        """Create educational slides with proper content."""
        slides = []
        
        # Slide 1: Title
        slides.append({
            "title": f"Understanding: {question}",
            "content": content.get('introduction', 'Let\'s learn this concept step by step.'),
            "type": "title",
            "duration": 6.0
        })
        
        # Slide 2: Explanation
        slides.append({
            "title": "Step-by-Step Explanation",
            "content": content.get('explanation', 'Here\'s how to solve this problem.'),
            "type": "concept",
            "duration": 8.0
        })
        
        # Slide 3: Formula
        if content.get('formula'):
            slides.append({
                "title": "Key Formula",
                "content": content.get('formula', 'Important mathematical formula'),
                "type": "formula",
                "duration": 6.0
            })
        
        # Slide 4: Example
        slides.append({
            "title": "Worked Example",
            "content": content.get('example', 'Let\'s work through an example.'),
            "type": "example",
            "duration": 7.0
        })
        
        # Slide 5: Summary
        slides.append({
            "title": "Key Takeaways",
            "content": content.get('summary', 'Remember these important points.'),
            "type": "summary",
            "duration": 5.0
        })
        
        return slides
    
    async def create_slide_images(self, slides: List[Dict[str, Any]], question_id: str) -> List[Dict[str, Any]]:
        """Create actual slide images with proper content."""
        try:
            print(f"🎨 Creating {len(slides)} educational slide images...")
            
            generated_slides = []
            
            for i, slide in enumerate(slides):
                slide_id = i + 1
                print(f"  📝 Creating slide {slide_id}: {slide.get('title', 'Untitled')}")
                
                # Create slide image
                image_path = await self._create_slide_image(slide, slide_id, question_id)
                
                # Create slide metadata
                slide_metadata = {
                    'id': slide_id,
                    'title': slide.get('title', f'Slide {slide_id}'),
                    'content': slide.get('content', ''),
                    'file_path': image_path,
                    'duration': slide.get('duration', 6.0),
                    'type': slide.get('type', 'content')
                }
                
                generated_slides.append(slide_metadata)
            
            print(f"✅ Created {len(generated_slides)} educational slide images")
            return generated_slides
            
        except Exception as e:
            print(f"❌ Slide image creation failed: {e}")
            raise
    
    async def _create_slide_image(self, slide: Dict[str, Any], slide_id: int, question_id: str) -> str:
        """Create a single slide image with proper content."""
        try:
            # Create image
            img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))  # Dark blue
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 72)
                body_font = ImageFont.truetype("arial.ttf", 40)
                small_font = ImageFont.truetype("arial.ttf", 28)
            except:
                try:
                    title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 72)
                    body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
                    small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
                except:
                    title_font = ImageFont.load_default()
                    body_font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
            
            # Colors
            title_color = (59, 130, 246)  # Blue
            text_color = (226, 232, 240)  # Light gray
            accent_color = (16, 185, 129)  # Green
            
            # Draw title
            title = slide.get('title', f'Slide {slide_id}')
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.slide_width - title_width) // 2
            title_y = self.margin
            
            draw.text((title_x, title_y), title, fill=title_color, font=title_font)
            
            # Draw content
            content = slide.get('content', '')
            if content:
                # Wrap text
                lines = self._wrap_text(content, body_font, self.slide_width - 2 * self.margin)
                
                y_pos = title_y + 120
                for line in lines[:8]:  # Limit to 8 lines
                    draw.text((self.margin, y_pos), line, fill=text_color, font=body_font)
                    y_pos += 60
            
            # Add slide number
            slide_text = f"Slide {slide_id}"
            draw.text((self.slide_width - 200, self.slide_height - 50), slide_text, 
                     fill=(100, 116, 139), font=small_font)
            
            # Save image
            image_path = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.png"
            img.save(image_path, 'PNG', quality=95)
            
            return image_path
            
        except Exception as e:
            print(f"Failed to create slide {slide_id}: {e}")
            # Create a simple fallback
            img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)
            draw.text((self.margin, self.margin), f"Slide {slide_id}", fill=(59, 130, 246))
            image_path = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.png"
            img.save(image_path, 'PNG')
            return image_path
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        lines = []
        if not text:
            return lines
        
        words = text.split(' ')
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    async def _create_simple_fallback(self, question: str, solution: str) -> Dict[str, Any]:
        """Create simple fallback content."""
        return {
            "title": f"Understanding: {question}",
            "slides": [
                {
                    "title": f"Question: {question}",
                    "content": "Let's work through this step by step.",
                    "type": "title",
                    "duration": 6.0
                },
                {
                    "title": "Solution",
                    "content": solution,
                    "type": "concept",
                    "duration": 8.0
                },
                {
                    "title": "Key Points",
                    "content": "Remember these important concepts.",
                    "type": "summary",
                    "duration": 5.0
                }
            ],
            "total_slides": 3,
            "estimated_duration": 19,
            "content_type": "educational"
        }


# Global instance
simple_notebooklm_generator = SimpleNotebookLMGenerator()
