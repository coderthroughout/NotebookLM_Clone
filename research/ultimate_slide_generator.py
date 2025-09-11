"""
Ultimate Slide Generator - Bypasses all old systems.
Creates 30-40 high-quality slides for 2-4 minute videos.
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from .html_renderer import html_renderer
from .llm import llm_client
from .config import config


class UltimateSlideGenerator:
    """
    Ultimate slide generator that completely bypasses old systems.
    Creates 30-40 high-quality slides for 2-4 minute videos.
    """
    
    def __init__(self):
        self.output_dir = "temp_video"
        self.slide_width = 1920
        self.slide_height = 1080
        self.margin = 80
        # Parallelism tuning (Phase G): number of slides processed concurrently per batch
        self.batch_size = 5
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_educational_video(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate a complete educational video with 30-40 high-quality slides."""
        try:
            print("🎓 Generating ultimate NotebookLM-style educational video...")
            
            # Step 1: Generate educational content
            educational_content = await self._generate_educational_content(question, solution)
            
            # Step 2: Create 30-40 slides for 2-4 minute video
            slides = await self._create_educational_slides(educational_content, question)
            
            return {
                "title": f"Understanding: {question}",
                "slides": slides,
                "total_slides": len(slides),
                "estimated_duration": len(slides) * 4,  # 4 seconds per slide for 2-4 minute video
                "content_type": "educational"
            }
            
        except Exception as e:
            print(f"❌ Educational video generation failed: {e}")
            return await self._create_ultimate_fallback(question, solution)
    
    async def _generate_educational_content(self, question: str, solution: str) -> Dict[str, Any]:
        """Generate structured educational content."""
        prompt = f"""
        You are an expert educator. Create comprehensive educational content for this question and solution.
        
        QUESTION: {question}
        SOLUTION: {solution}
        
        Create educational content that includes:
        1. A clear introduction to the concept
        2. Step-by-step explanation with multiple steps
        3. Key formulas, rules, or principles
        4. Multiple worked examples
        5. Common mistakes to avoid
        6. Real-world applications
        7. Key takeaways and summary
        
        Make it educational and clear. Focus on teaching the concept thoroughly.
        
        Return a JSON structure with:
        - introduction: Brief intro to the concept
        - explanation: Detailed step-by-step explanation
        - formula: Key formula or rule
        - example1: First worked example
        - example2: Second worked example
        - applications: Real-world applications
        - mistakes: Common mistakes to avoid
        - summary: Key points to remember
        """
        
        try:
            response = await llm_client.client.chat.completions.create(
                model=config.OPENAI_MODEL_GPT4,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
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
                    "example1": "First worked example",
                    "example2": "Second worked example",
                    "applications": "Real-world applications",
                    "mistakes": "Common mistakes to avoid",
                    "summary": "Key points to remember"
                }
                
        except Exception as e:
            print(f"LLM content generation failed: {e}")
            return {
                "introduction": f"Understanding {question}",
                "explanation": solution,
                "formula": "Mathematical formula",
                "example1": "Example problem 1",
                "example2": "Example problem 2",
                "applications": "Real-world applications",
                "mistakes": "Common mistakes",
                "summary": "Key takeaways"
            }
    
    async def _create_educational_slides(self, content: Dict[str, Any], question: str) -> List[Dict[str, Any]]:
        """Create 30-40 educational slides with proper content."""
        slides = []
        
        def to_bullets(text: str, max_bullets: int = 6) -> List[str]:
            if not text:
                return []
            # naive sentence split; keep non-empty trimmed
            parts = [s.strip() for s in text.replace('\n', ' ').split('. ') if s.strip()]
            bullets = []
            for p in parts:
                if not p.endswith('.'):
                    p = p + '.'
                bullets.append(p)
                if len(bullets) >= max_bullets:
                    break
            return bullets or [text]
        
        # Slide 1: Title and Introduction
        slides.append({
            "title": f"Understanding: {question}",
            "bullets": to_bullets(content.get('introduction', 'Let\'s learn this concept step by step.'), 4),
            "type": "title",
            "duration": 4.0
        })
        
        # Slides 2-8: Step-by-step explanation (7 slides)
        explanation = content.get('explanation', 'Here\'s how to solve this problem.')
        explanation_parts = self._split_into_parts(explanation, 7)
        
        for i, part in enumerate(explanation_parts):
            slides.append({
                "title": f"Step {i+1}: {self._get_step_title(i+1)}",
                "bullets": to_bullets(part, 6),
                "type": "concept",
                "duration": 4.0
            })
        
        # Slide 9: Formula
        if content.get('formula'):
            slides.append({
                "title": "Key Formula",
                "visual_elements": [{"type": "formula", "content": content.get('formula', '')}],
                "bullets": ["Understand variables and units.", "Note where it applies."],
                "type": "formula",
                "duration": 4.0
            })
        
        # Slides 10-15: Examples (6 slides)
        example1 = content.get('example1', 'Let\'s work through the first example.')
        example1_parts = self._split_into_parts(example1, 3)
        
        for i, part in enumerate(example1_parts):
            slides.append({
                "title": f"Example 1 - Part {i+1}",
                "bullets": to_bullets(part, 6),
                "type": "example",
                "duration": 4.0
            })
        
        example2 = content.get('example2', 'Let\'s work through the second example.')
        example2_parts = self._split_into_parts(example2, 3)
        
        for i, part in enumerate(example2_parts):
            slides.append({
                "title": f"Example 2 - Part {i+1}",
                "bullets": to_bullets(part, 6),
                "type": "example",
                "duration": 4.0
            })
        
        # Slides 16-20: Applications (5 slides)
        applications = content.get('applications', 'Real-world applications of this concept.')
        app_parts = self._split_into_parts(applications, 5)
        
        for i, part in enumerate(app_parts):
            slides.append({
                "title": f"Application {i+1}",
                "bullets": to_bullets(part, 6),
                "type": "application",
                "duration": 4.0
            })
        
        # Slides 21-25: Common Mistakes (5 slides)
        mistakes = content.get('mistakes', 'Common mistakes to avoid.')
        mistake_parts = self._split_into_parts(mistakes, 5)
        
        for i, part in enumerate(mistake_parts):
            slides.append({
                "title": f"Common Mistake {i+1}",
                "bullets": to_bullets(part, 6),
                "type": "mistake",
                "duration": 4.0
            })
        
        # Slides 26-30: Summary and Key Points (5 slides)
        summary = content.get('summary', 'Key points to remember.')
        summary_parts = self._split_into_parts(summary, 5)
        
        for i, part in enumerate(summary_parts):
            slides.append({
                "title": f"Key Point {i+1}",
                "bullets": to_bullets(part, 6),
                "type": "summary",
                "duration": 4.0
            })
        
        return slides
    
    def _split_into_parts(self, text: str, num_parts: int) -> List[str]:
        """Split text into specified number of parts."""
        if not text:
            return ["Content will be shown here."] * num_parts
        
        words = text.split()
        words_per_part = max(1, len(words) // num_parts)
        
        parts = []
        for i in range(num_parts):
            start_idx = i * words_per_part
            if i == num_parts - 1:  # Last part gets remaining words
                end_idx = len(words)
            else:
                end_idx = (i + 1) * words_per_part
            
            part_words = words[start_idx:end_idx]
            if part_words:
                parts.append(' '.join(part_words))
            else:
                parts.append("Content will be shown here.")
        
        return parts
    
    def _get_step_title(self, step_num: int) -> str:
        """Get appropriate step title."""
        titles = [
            "Introduction",
            "Understanding the Problem",
            "Identifying the Approach",
            "Applying the Method",
            "Working Through the Solution",
            "Verifying the Answer",
            "Final Result"
        ]
        return titles[min(step_num - 1, len(titles) - 1)]
    
    async def create_slide_images(self, slides: List[Dict[str, Any]], question_id: str) -> List[Dict[str, Any]]:
        """Create actual slide images with proper content."""
        try:
            print(f"🎨 Creating {len(slides)} ultimate educational slide images...")
            
            # Use per-run directory
            run_dir = os.path.join(self.output_dir, str(question_id))
            os.makedirs(run_dir, exist_ok=True)
            html_dir = os.path.join(run_dir, "html")
            os.makedirs(html_dir, exist_ok=True)
            
            generated_slides = []
            
            # Process slides in parallel batches (configurable)
            for i in range(0, len(slides), self.batch_size):
                batch = slides[i:i + self.batch_size]
                batch_tasks = []
                
                for slide in batch:
                    slide_id = slides.index(slide) + 1
                    task = self._process_single_slide(slide, slide_id, question_id, run_dir, html_dir)
                    batch_tasks.append(task)
                
                # Process batch in parallel
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        print(f"❌ Slide processing failed: {result}")
                        continue
                    generated_slides.extend(result)
            
            # Generate end card with sources
            end_card_path = await self._create_end_card(slides, question_id, run_dir)
            if end_card_path:
                generated_slides.append({
                    "file_path": end_card_path,
                    "duration": 8.0,  # 8 seconds for end card
                    "type": "end_card"
                })
            
            print(f"✅ Created {len(generated_slides)} ultimate educational slide images")
            return generated_slides
            
        except Exception as e:
            print(f"❌ Slide image creation failed: {e}")
            raise
    
    async def _create_ultimate_slide_image(self, slide: Dict[str, Any], slide_id: int, question_id: str, run_dir: str) -> str:
        """Create an ultimate slide image with full canvas utilization."""
        try:
            # Create image with gradient background
            img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            self._create_gradient_background(draw)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 72)
                body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 44)
                small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 72)
                    body_font = ImageFont.truetype("arial.ttf", 44)
                    small_font = ImageFont.truetype("arial.ttf", 28)
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
            title_y = 100
            
            # Draw title with shadow (use high-contrast color)
            draw.text((title_x + 2, title_y + 2), title, fill=(0, 0, 0), font=title_font)
            draw.text((title_x, title_y), title, fill=(236, 245, 255), font=title_font)
            
            # Draw content with better layout (bullets preferred)
            y_pos = title_y + 120
            bullets = slide.get('bullets') or []
            if bullets:
                for b in bullets[:10]:
                    # wrap each bullet
                    lines = self._wrap_text(f"• {b}", body_font, self.slide_width - 2 * self.margin)
                    for line in lines:
                        if y_pos < self.slide_height - 120:
                            draw.text((self.margin, y_pos), line, fill=text_color, font=body_font)
                            y_pos += 48
            else:
                content = slide.get('content', '')
                if content:
                    lines = self._wrap_text(content, body_font, self.slide_width - 2 * self.margin)
                    for line in lines[:12]:  # Allow more lines for better content
                        if y_pos < self.slide_height - 120:
                            draw.text((self.margin, y_pos), line, fill=text_color, font=body_font)
                            y_pos += 48
            
            # Add decorative elements
            self._add_decorative_elements(draw, slide_id)
            
            # Add slide number with better styling
            slide_text = f"Slide {slide_id}"
            draw.text((self.slide_width - 200, self.slide_height - 50), slide_text, 
                     fill=(100, 116, 139), font=small_font)
            
            # Save image
            image_path = os.path.join(run_dir, f"slide_{question_id}_{slide_id:03d}.png")
            img.save(image_path, 'PNG', quality=95)

            # Debug watermark overlay ensures legibility regardless of HTML path
            try:
                overlay = Image.new('RGBA', (self.slide_width, self.slide_height), (0,0,0,0))
                odraw = ImageDraw.Draw(overlay)
                first_bullet = ''
                if slide.get('bullets'):
                    first_bullet = slide['bullets'][0]
                odraw.text((self.margin, self.slide_height-90), f"{title}  |  {first_bullet[:60]}", fill=(255,255,255,200), font=small_font)
                composed = Image.alpha_composite(img.convert('RGBA'), overlay)
                composed.convert('RGB').save(image_path, 'PNG', quality=95)
            except Exception:
                pass
            
            return image_path
            
        except Exception as e:
            print(f"Failed to create slide {slide_id}: {e}")
            # Create a simple fallback
            img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)
            draw.text((self.margin, self.margin), f"Slide {slide_id}", fill=(59, 130, 246))
            image_path = os.path.join(run_dir, f"slide_{question_id}_{slide_id:03d}.png")
            img.save(image_path, 'PNG')
            return image_path

    async def _rasterize_html_to_png(self, html_path: str, run_dir: str, question_id: str, slide_id: int, suffix: str = "") -> str:
        """Rasterize HTML to PNG using Playwright Chromium (if available)."""
        from .cache_manager import cache_manager
        
        # Check raster cache first
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        slide_data = {"html_content": html_content, "question_id": question_id, "slide_id": slide_id}
        cached_path = cache_manager.get_raster_cache(slide_data, question_id)
        if cached_path:
            return cached_path
        
        try:
            from playwright.sync_api import sync_playwright
        except Exception:
            raise

        image_path = os.path.join(run_dir, f"slide_{question_id}_{slide_id:03d}{suffix}.png")
        # Phase G: add retries for more robust rasterization
        last_err = None
        for attempt in range(3):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(args=["--disable-web-security"])  # allow local loads
                    page = browser.new_page(viewport={"width":1920, "height":1080, "deviceScaleFactor":1})
                    page.goto("file://" + os.path.abspath(html_path))
                    page.wait_for_load_state("domcontentloaded")
                    page.wait_for_timeout(600)  # allow fonts/KaTeX and layout
                    page.screenshot(path=image_path, full_page=False)
                    browser.close()
                last_err = None
                break
            except Exception as e:
                last_err = e
        if last_err is not None:
            # Fallback to simple PIL render indicating failure
            try:
                img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))
                draw = ImageDraw.Draw(img)
                draw.text((self.margin, self.margin), f"Slide {slide_id}", fill=(59, 130, 246))
                img.save(image_path, 'PNG')
            except Exception:
                raise last_err
        
        # Cache the result (disabled during debug to ensure fresh frames)
        # cache_manager.set_raster_cache(slide_data, image_path, question_id)
        return image_path
    
    async def _process_single_slide(self, slide: Dict[str, Any], slide_id: int, question_id: str, run_dir: str, html_dir: str) -> List[Dict[str, Any]]:
        """Process a single slide and return its metadata."""
        print(f"  📝 Creating slide {slide_id}: {slide.get('title', 'Untitled')}")
        
        # Render HTML and rasterize via Chromium fallback to PIL if needed
        html_content = html_renderer.render_html(slide)
        html_path = os.path.join(html_dir, f"slide_{question_id}_{slide_id:03d}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        try:
            # Add citation mapping to bullets
            if slide.get('citations') and slide.get('bullets'):
                # Map citations to bullets (1:1 mapping)
                slide['citations'] = slide['citations'][:len(slide['bullets'])]
            
            # Build frames: if build_sequence, create multiple frames with incremental bullets
            build_frames = []
            build_count = 0
            if slide.get('build_sequence') and slide.get('bullets'):
                total = len(slide['bullets'])
                for visible in range(1, total + 1):
                    slide_build = dict(slide)
                    slide_build['_build_visible_count'] = visible
                    # Include citations for visible bullets only
                    if slide.get('citations'):
                        slide_build['citations'] = slide['citations'][:visible]
                    html_content_b = html_renderer.render_html(slide_build)
                    html_path_b = os.path.join(html_dir, f"slide_{question_id}_{slide_id:03d}_b{visible}.html")
                    with open(html_path_b, 'w', encoding='utf-8') as fb:
                        fb.write(html_content_b)
                    img_path_b = await self._rasterize_html_to_png(html_path_b, run_dir, question_id, slide_id, suffix=f"_b{visible}")
                    build_frames.append({"file_path": img_path_b, "duration": 2.0})
                    build_count += 1
            # Base frame
            image_path = await self._rasterize_html_to_png(html_path, run_dir, question_id, slide_id)
            slide['_build_frames'] = build_frames
        except Exception:
            # Fallback to PIL renderer
            image_path = await self._create_ultimate_slide_image(slide, slide_id, question_id, run_dir)
        
        # Create slide metadata
        slide_metadata = {
            'id': slide_id,
            'title': slide.get('title', f'Slide {slide_id}'),
            'content': slide.get('content', ''),
            'file_path': image_path,
            'duration': slide.get('duration', 4.0),
            'type': slide.get('type', 'content')
        }
        
        return [slide_metadata]
    
    async def _create_end_card(self, slides: List[Dict[str, Any]], question_id: str, run_dir: str) -> str:
        """Create an end card with all sources used in the video."""
        try:
            # Collect all unique sources from slides
            all_sources = []
            seen_urls = set()
            
            for slide in slides:
                if slide.get('citations'):
                    for citation in slide['citations']:
                        if isinstance(citation, dict) and citation.get('url') not in seen_urls:
                            all_sources.append({
                                'title': citation.get('title', 'Untitled'),
                                'url': citation.get('url', ''),
                                'domain': citation.get('domain', '')
                            })
                            seen_urls.add(citation.get('url', ''))
            
            if not all_sources:
                return None
            
            # Render end card HTML
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader('research/templates'))
            template = env.get_template('end_card.html')
            html_content = template.render(sources=all_sources)
            
            # Save HTML
            html_path = os.path.join(run_dir, f"end_card_{question_id}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Convert to PNG
            image_path = await self._rasterize_html_to_png(html_path, run_dir, question_id, 999, suffix="_end")
            return image_path
            
        except Exception as e:
            print(f"❌ End card creation failed: {e}")
            return None
    
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
        
        words = text.split()
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
    
    async def _create_ultimate_fallback(self, question: str, solution: str) -> Dict[str, Any]:
        """Create ultimate fallback content."""
        return {
            "title": f"Understanding: {question}",
            "slides": [
                {
                    "title": f"Question: {question}",
                    "content": "Let's work through this step by step.",
                    "type": "title",
                    "duration": 4.0
                },
                {
                    "title": "Solution",
                    "content": solution,
                    "type": "concept",
                    "duration": 4.0
                },
                {
                    "title": "Key Points",
                    "content": "Remember these important concepts.",
                    "type": "summary",
                    "duration": 4.0
                }
            ],
            "total_slides": 3,
            "estimated_duration": 12,
            "content_type": "educational"
        }


# Global instance
ultimate_slide_generator = UltimateSlideGenerator()
