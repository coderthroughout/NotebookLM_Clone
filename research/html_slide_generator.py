"""
HTML-based Slide Generator for NotebookLM-style videos.
Creates modern, clean slides with rich educational content.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess


class HTMLSlideGenerator:
    """
    Generate modern, NotebookLM-style slides using HTML/CSS.
    This approach gives us much better control over design and content.
    """
    
    def __init__(self):
        self.output_dir = "temp_video"
        self.slide_width = 1920
        self.slide_height = 1080
        self.margin = 80
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_slides(self, slides_data: List[Dict[str, Any]], 
                            question_id: str) -> List[Dict[str, Any]]:
        """Generate HTML-based slides and convert to images."""
        try:
            print(f"🎨 Generating {len(slides_data)} HTML slides for {question_id}")
            
            generated_slides = []
            
            for i, slide_spec in enumerate(slides_data):
                slide_id = i + 1
                print(f"  📝 Creating slide {slide_id}: {slide_spec.get('title', 'Untitled')}")
                
                # Generate HTML slide
                html_content = await self._create_html_slide(slide_spec, slide_id)
                
                # Convert HTML to image
                slide_image_path = await self._html_to_image(
                    html_content, slide_id, question_id
                )
                
                # Create slide metadata
                slide_metadata = {
                    'id': slide_id,
                    'title': slide_spec.get('title', f'Slide {slide_id}'),
                    'content': slide_spec.get('content', ''),
                    'file_path': slide_image_path,
                    'duration': slide_spec.get('duration', 5.0),
                    'type': slide_spec.get('type', 'content'),
                    'visual_elements': slide_spec.get('visual_elements', []),
                    'layout': slide_spec.get('layout', 'standard')
                }
                
                generated_slides.append(slide_metadata)
            
            print(f"✅ Generated {len(generated_slides)} HTML slides successfully")
            return generated_slides
            
        except Exception as e:
            print(f"❌ HTML slide generation failed: {e}")
            raise
    
    async def _create_html_slide(self, slide_spec: Dict[str, Any], slide_id: int) -> str:
        """Create HTML content for a single slide."""
        title = slide_spec.get('title', 'Untitled Slide')
        content = slide_spec.get('content', '')
        bullets = slide_spec.get('bullets', [])
        visual_elements = slide_spec.get('visual_elements', [])
        slide_type = slide_spec.get('type', 'content')
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    width: {self.slide_width}px;
                    height: {self.slide_height}px;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #f8fafc;
                    overflow: hidden;
                    position: relative;
                }}
                
                .slide-container {{
                    width: 100%;
                    height: 100%;
                    padding: {self.margin}px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }}
                
                .slide-header {{
                    width: 100%;
                    text-align: center;
                    margin-bottom: 60px;
                }}
                
                .slide-title {{
                    font-size: 64px;
                    font-weight: 700;
                    color: #3b82f6;
                    margin-bottom: 20px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }}
                
                .slide-subtitle {{
                    font-size: 32px;
                    color: #94a3b8;
                    font-weight: 300;
                }}
                
                .slide-content {{
                    width: 100%;
                    max-width: 1400px;
                    text-align: center;
                }}
                
                .content-text {{
                    font-size: 36px;
                    line-height: 1.6;
                    color: #e2e8f0;
                    margin-bottom: 40px;
                }}
                
                .bullet-list {{
                    text-align: left;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                .bullet-item {{
                    font-size: 32px;
                    color: #e2e8f0;
                    margin-bottom: 24px;
                    display: flex;
                    align-items: flex-start;
                }}
                
                .bullet-point {{
                    color: #3b82f6;
                    font-size: 40px;
                    margin-right: 20px;
                    margin-top: -4px;
                }}
                
                .formula-box {{
                    background: rgba(59, 130, 246, 0.1);
                    border: 2px solid #3b82f6;
                    border-radius: 12px;
                    padding: 30px;
                    margin: 40px auto;
                    max-width: 800px;
                }}
                
                .formula-text {{
                    font-size: 48px;
                    color: #3b82f6;
                    font-family: 'Courier New', monospace;
                    text-align: center;
                    font-weight: bold;
                }}
                
                .highlight-box {{
                    background: rgba(16, 185, 129, 0.1);
                    border-left: 6px solid #10b981;
                    padding: 30px;
                    margin: 40px 0;
                    border-radius: 8px;
                }}
                
                .highlight-text {{
                    font-size: 32px;
                    color: #10b981;
                    font-weight: 600;
                }}
                
                .slide-footer {{
                    position: absolute;
                    bottom: {self.margin}px;
                    right: {self.margin}px;
                    font-size: 24px;
                    color: #64748b;
                }}
                
                .visual-element {{
                    margin: 30px 0;
                }}
                
                .chart-container {{
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 40px;
                    margin: 40px 0;
                }}
            </style>
        </head>
        <body>
            <div class="slide-container">
                <div class="slide-header">
                    <h1 class="slide-title">{title}</h1>
                </div>
                
                <div class="slide-content">
        """
        
        # Add content based on slide type
        if slide_type == 'title':
            html_content += f"""
                    <div class="content-text">
                        {content}
                    </div>
            """
        elif bullets:
            html_content += """
                    <div class="bullet-list">
            """
            for bullet in bullets[:6]:  # Limit to 6 bullets
                html_content += f"""
                        <div class="bullet-item">
                            <span class="bullet-point">•</span>
                            <span>{bullet}</span>
                        </div>
                """
            html_content += """
                    </div>
            """
        elif content:
            html_content += f"""
                    <div class="content-text">
                        {content}
                    </div>
            """
        
        # Add visual elements
        for element in visual_elements:
            element_type = element.get('type', 'text')
            element_content = element.get('content', '')
            
            if element_type == 'formula':
                html_content += f"""
                    <div class="formula-box">
                        <div class="formula-text">{element_content}</div>
                    </div>
                """
            elif element_type == 'highlight':
                html_content += f"""
                    <div class="highlight-box">
                        <div class="highlight-text">{element_content}</div>
                    </div>
                """
            elif element_type == 'chart':
                html_content += f"""
                    <div class="chart-container">
                        <div class="content-text">{element_content}</div>
                    </div>
                """
        
        html_content += """
                </div>
            </div>
            
            <div class="slide-footer">
                Slide {slide_id}
            </div>
        </body>
        </html>
        """.format(slide_id=slide_id)
        
        return html_content
    
    async def _html_to_image(self, html_content: str, slide_id: int, question_id: str) -> str:
        """Convert HTML content to PNG image using Puppeteer or similar."""
        try:
            # Save HTML to temporary file
            html_file = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Convert HTML to image using Puppeteer (if available) or fallback
            image_file = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.png"
            
            # Try using Puppeteer first
            if await self._try_puppeteer_conversion(html_file, image_file):
                return image_file
            
            # Fallback to simple method
            return await self._fallback_html_conversion(html_content, slide_id, question_id)
            
        except Exception as e:
            print(f"HTML to image conversion failed: {e}")
            return await self._fallback_html_conversion(html_content, slide_id, question_id)
    
    async def _try_puppeteer_conversion(self, html_file: str, image_file: str) -> bool:
        """Try to convert HTML to image using Puppeteer."""
        try:
            # Check if Puppeteer is available
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Create a simple Node.js script to convert HTML to image
            script_content = f"""
            const puppeteer = require('puppeteer');
            const path = require('path');
            
            (async () => {{
                const browser = await puppeteer.launch({{ headless: true }});
                const page = await browser.newPage();
                await page.setViewport({{ width: 1920, height: 1080 }});
                await page.goto('file://' + path.resolve('{html_file}'));
                await page.screenshot({{ path: '{image_file}', fullPage: true }});
                await browser.close();
            }})();
            """
            
            script_file = f"{self.output_dir}/convert_{slide_id}.js"
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            # Run the conversion
            result = subprocess.run(['node', script_file], capture_output=True, text=True)
            
            # Clean up
            os.remove(script_file)
            
            return result.returncode == 0 and os.path.exists(image_file)
            
        except Exception:
            return False
    
    async def _fallback_html_conversion(self, html_content: str, slide_id: int, question_id: str) -> str:
        """Fallback method to create a simple image from HTML content."""
        try:
            # For now, create a simple placeholder image
            # In a real implementation, you'd use a proper HTML-to-image converter
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple image with the content
            img = Image.new('RGB', (self.slide_width, self.slide_height), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)
            
            # Try to load a font
            try:
                title_font = ImageFont.truetype("arial.ttf", 64)
                body_font = ImageFont.truetype("arial.ttf", 32)
            except:
                title_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
            
            # Draw title
            title = "HTML Slide (Fallback)"
            draw.text((self.margin, self.margin), title, fill=(59, 130, 246), font=title_font)
            
            # Draw content
            content = "This slide was generated using HTML fallback method."
            draw.text((self.margin, self.margin + 100), content, fill=(226, 232, 240), font=body_font)
            
            # Save image
            image_file = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.png"
            img.save(image_file, 'PNG', quality=95)
            
            return image_file
            
        except Exception as e:
            print(f"Fallback conversion failed: {e}")
            # Return a simple placeholder
            return f"{self.output_dir}/placeholder_{slide_id}.png"


# Global instance
html_slide_generator = HTMLSlideGenerator()
