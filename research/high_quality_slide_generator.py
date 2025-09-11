"""
High-Quality Slide Generator for NotebookLM-style videos.
Creates visually appealing, full-canvas slides with proper content.
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from .llm import llm_client
from .config import config


class HighQualitySlideGenerator:
    """
    High-quality slide generator that creates visually appealing, full-canvas slides.
    """
    
    def __init__(self):
        self.output_dir = "temp_video"
        self.slide_width = 1920
        self.slide_height = 1080
        self.margin = 80
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_educational_video(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate a complete educational video with high-quality content."""
        try:
            print("🎓 Generating high-quality NotebookLM-style educational video...")
            
            # Step 1: Generate educational content
            educational_content = await self._generate_educational_content(question, solution)
            
            # Step 2: Create slides (3-4 slides max for 3-4 minute video)
            slides = await self._create_educational_slides(educational_content, question)
            
            return {
                "title": f"Understanding: {question}",
                "slides": slides,
                "total_slides": len(slides),
                "estimated_duration": len(slides) * 8,  # 8 seconds per slide
                "content_type": "educational"
            }
            
        except Exception as e:
            print(f"❌ Educational video generation failed: {e}")
            return await self._create_high_quality_fallback(question, solution)
    
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
        """Create educational slides with proper content (3-4 slides max)."""
        slides = []
        
        # Slide 1: Title and Introduction
        slides.append({
            "title": f"Understanding: {question}",
            "content": content.get('introduction', 'Let\'s learn this concept step by step.'),
            "type": "title",
            "duration": 8.0
        })
        
        # Slide 2: Explanation and Formula
        explanation = content.get('explanation', 'Here\'s how to solve this problem.')
        formula = content.get('formula', 'Key formula')
        combined_content = f"{explanation}\n\n{formula}"
        
        slides.append({
            "title": "Step-by-Step Solution",
            "content": combined_content,
            "type": "concept",
            "duration": 12.0
        })
        
        # Slide 3: Example and Summary
        example = content.get('example', 'Let\'s work through an example.')
        summary = content.get('summary', 'Remember these important points.')
        combined_content = f"{example}\n\n{summary}"
        
        slides.append({
            "title": "Example & Key Takeaways",
            "content": combined_content,
            "type": "example",
            "duration": 10.0
        })
        
        return slides
    
    async def create_slide_images(self, slides: List[Dict[str, Any]], question_id: str) -> List[Dict[str, Any]]:
        """Create actual slide images with proper content."""
        try:
            print(f"🎨 Creating {len(slides)} high-quality educational slide images...")
            
            generated_slides = []
            
            for i, slide in enumerate(slides):
                slide_id = i + 1
                print(f"  📝 Creating slide {slide_id}: {slide.get('title', 'Untitled')}")
                
                # Create slide image
                image_path = await self._create_high_quality_slide_image(slide, slide_id, question_id)
                
                # Create slide metadata
                slide_metadata = {
                    'id': slide_id,
                    'title': slide.get('title', f'Slide {slide_id}'),
                    'content': slide.get('content', ''),
                    'file_path': image_path,
                    'duration': slide.get('duration', 8.0),
                    'type': slide.get('type', 'content')
                }
                
                generated_slides.append(slide_metadata)
            
            print(f"✅ Created {len(generated_slides)} high-quality educational slide images")
            return generated_slides
            
        except Exception as e:
            print(f"❌ Slide image creation failed: {e}")
            raise
    
    async def _create_high_quality_slide_image(self, slide: Dict[str, Any], slide_id: int, question_id: str) -> str:
        """Create a high-quality slide image with full canvas utilization."""
        try:
            # Create image with gradient background
            img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            self._create_gradient_background(draw)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 84)
                body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
                small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 84)
                    body_font = ImageFont.truetype("arial.ttf", 48)
                    small_font = ImageFont.truetype("arial.ttf", 32)
                except:
                    title_font = ImageFont.load_default()
                    body_font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
            
            # Colors
            title_color = (59, 130, 246)  # Blue
            text_color = (226, 232, 240)  # Light gray
            accent_color = (16, 185, 129)  # Green
            
            # Draw title with better positioning
            title = slide.get('title', f'Slide {slide_id}')
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.slide_width - title_width) // 2
            title_y = 120  # More space from top
            
            # Draw title with shadow
            draw.text((title_x + 2, title_y + 2), title, fill=(0, 0, 0), font=title_font)
            draw.text((title_x, title_y), title, fill=title_color, font=title_font)
            
            # Draw content with better layout
            content = slide.get('content', '')
            if content:
                # Split content into paragraphs
                paragraphs = content.split('\n\n')
                
                y_pos = title_y + 140
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # Wrap text for this paragraph
                        lines = self._wrap_text(paragraph.strip(), body_font, self.slide_width - 2 * self.margin)
                        
                        for line in lines[:6]:  # Limit to 6 lines per paragraph
                            if y_pos < self.slide_height - 150:  # Leave space for footer
                                draw.text((self.margin, y_pos), line, fill=text_color, font=body_font)
                                y_pos += 70
                        
                        y_pos += 40  # Space between paragraphs
            
            # Add decorative elements
            self._add_decorative_elements(draw, slide_id)
            
            # Add slide number with better styling
            slide_text = f"Slide {slide_id}"
            draw.text((self.slide_width - 200, self.slide_height - 60), slide_text, 
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
    
    def _create_gradient_background(self, draw):
        """Create a gradient background for the slide."""
        # Create a subtle gradient effect
        for y in range(self.slide_height):
            # Calculate gradient color
            ratio = y / self.slide_height
            r = int(15 + (30 - 15) * ratio)
            g = int(23 + (40 - 23) * ratio)
            b = int(42 + (60 - 42) * ratio)
            
            # Draw horizontal line
            draw.line([(0, y), (self.slide_width, y)], fill=(r, g, b))
    
    def _add_decorative_elements(self, draw, slide_id):
        """Add decorative elements to make slides more visually appealing."""
        # Add subtle border
        draw.rectangle([(20, 20), (self.slide_width - 20, self.slide_height - 20)], 
                      outline=(59, 130, 246), width=3)
        
        # Add corner accents
        corner_size = 40
        # Top-left corner
        draw.rectangle([(20, 20), (20 + corner_size, 20 + corner_size)], 
                      fill=(59, 130, 246))
        # Top-right corner
        draw.rectangle([(self.slide_width - 20 - corner_size, 20), 
                       (self.slide_width - 20, 20 + corner_size)], 
                      fill=(59, 130, 246))
        # Bottom-left corner
        draw.rectangle([(20, self.slide_height - 20 - corner_size), 
                       (20 + corner_size, self.slide_height - 20)], 
                      fill=(59, 130, 246))
        # Bottom-right corner
        draw.rectangle([(self.slide_width - 20 - corner_size, self.slide_height - 20 - corner_size), 
                       (self.slide_width - 20, self.slide_height - 20)], 
                      fill=(59, 130, 246))
    
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
    
    async def _create_high_quality_fallback(self, question: str, solution: str) -> Dict[str, Any]:
        """Create high-quality fallback content."""
        return {
            "title": f"Understanding: {question}",
            "slides": [
                {
                    "title": f"Question: {question}",
                    "content": "Let's work through this step by step.",
                    "type": "title",
                    "duration": 8.0
                },
                {
                    "title": "Solution",
                    "content": solution,
                    "type": "concept",
                    "duration": 12.0
                },
                {
                    "title": "Key Points",
                    "content": "Remember these important concepts.",
                    "type": "summary",
                    "duration": 10.0
                }
            ],
            "total_slides": 3,
            "estimated_duration": 30,
            "content_type": "educational"
        }


# Global instance
high_quality_slide_generator = HighQualitySlideGenerator()
