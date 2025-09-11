"""
Advanced Slide Generation Module.
Creates actual visual slides with content, diagrams, and visual elements.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import math
import random

# Image processing imports
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    from PIL.Image import Resampling
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL/Pillow not available. Install with: pip install Pillow")

# Plotting imports
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Matplotlib not available. Install with: pip install matplotlib seaborn")

from .config import config


class SlideGenerator:
    """Advanced slide generator with visual content support."""
    
    def __init__(self):
        self.output_dir = "temp_video"
        self.slide_width = 1920
        self.slide_height = 1080
        self.margin = 80
        self.content_width = self.slide_width - (2 * self.margin)
        self.content_height = self.slide_height - (2 * self.margin)
        
        # Color schemes
        self.color_schemes = {
            'default': {
                'background': '#0B1020',
                'primary': '#5B9DFF',
                'secondary': '#9AA3B2',
                'accent': '#FF6B6B',
                'text': '#E6EAF2',
                'muted': '#6B7280'
            },
            'blue': {
                'background': '#1a1a2e',
                'primary': '#16213e',
                'secondary': '#0f3460',
                'accent': '#e94560',
                'text': '#ffffff',
                'muted': '#8b9dc3'
            },
            'dark': {
                'background': '#0d1117',
                'primary': '#21262d',
                'secondary': '#30363d',
                'accent': '#f85149',
                'text': '#f0f6fc',
                'muted': '#7d8590'
            }
        }
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_slides(self, slides_data: List[Dict[str, Any]], 
                            question_id: str) -> List[Dict[str, Any]]:
        """Generate actual slide images from slide specifications."""
        try:
            print(f"🎨 Generating {len(slides_data)} slides for {question_id}")
            
            generated_slides = []
            color_scheme = self.color_schemes['default']
            
            for i, slide_spec in enumerate(slides_data):
                slide_id = i + 1
                print(f"  📝 Creating slide {slide_id}: {slide_spec.get('title', 'Untitled')}")
                
                # Generate slide image
                slide_image_path = await self._create_slide_image(
                    slide_spec, slide_id, color_scheme, question_id
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
            
            print(f"✅ Generated {len(generated_slides)} slides successfully")
            return generated_slides
            
        except Exception as e:
            print(f"❌ Slide generation failed: {e}")
            raise
    
    async def _create_slide_image(self, slide_spec: Dict[str, Any], 
                                slide_id: int, color_scheme: Dict[str, str],
                                question_id: str) -> str:
        """Create a single slide image."""
        try:
            if PIL_AVAILABLE:
                return await self._create_pil_slide(slide_spec, slide_id, color_scheme, question_id)
            elif MATPLOTLIB_AVAILABLE:
                return await self._create_matplotlib_slide(slide_spec, slide_id, color_scheme, question_id)
            else:
                return await self._create_fallback_slide(slide_spec, slide_id, question_id)
                
        except Exception as e:
            print(f"Failed to create slide {slide_id}: {e}")
            return await self._create_fallback_slide(slide_spec, slide_id, question_id)
    
    async def _create_pil_slide(self, slide_spec: Dict[str, Any], 
                              slide_id: int, color_scheme: Dict[str, str],
                              question_id: str) -> str:
        """Create slide using PIL/Pillow."""
        try:
            # Create base image
            img = Image.new('RGB', (self.slide_width, self.slide_height), color_scheme['background'])
            draw = ImageDraw.Draw(img)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", 72)
                body_font = ImageFont.truetype("arial.ttf", 40)
                small_font = ImageFont.truetype("arial.ttf", 28)
            except:
                try:
                    title_font = ImageFont.load_default()
                    body_font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
                except:
                    title_font = None
                    body_font = None
                    small_font = None
            
            # Draw slide content based on type
            slide_type = slide_spec.get('type', 'content')
            
            if slide_type == 'title':
                await self._draw_title_slide(draw, slide_spec, color_scheme, title_font, body_font)
            elif slide_type == 'content':
                await self._draw_content_slide(draw, slide_spec, color_scheme, title_font, body_font, small_font)
            elif slide_type == 'diagram':
                await self._draw_diagram_slide(draw, slide_spec, color_scheme, title_font, body_font)
            elif slide_type == 'conclusion':
                await self._draw_conclusion_slide(draw, slide_spec, color_scheme, title_font, body_font)
            else:
                await self._draw_content_slide(draw, slide_spec, color_scheme, title_font, body_font, small_font)
            
            # Add slide number and branding
            await self._add_slide_footer(draw, slide_id, color_scheme, small_font)
            
            # Save image
            slide_path = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.png"
            img.save(slide_path, 'PNG', quality=95)
            
            return slide_path
            
        except Exception as e:
            print(f"PIL slide creation failed: {e}")
            raise
    
    async def _draw_title_slide(self, draw, slide_spec: Dict[str, Any], 
                              color_scheme: Dict[str, str], title_font, body_font):
        """Draw a title slide."""
        title = slide_spec.get('title', 'Untitled')
        subtitle = slide_spec.get('subtitle', '')
        
        # Draw title
        if title_font:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.slide_width - title_width) // 2
            title_y = self.slide_height // 2 - 100
            
            draw.text((title_x, title_y), title, fill=color_scheme['text'], font=title_font)
        
        # Draw subtitle
        if subtitle and body_font:
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=body_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (self.slide_width - subtitle_width) // 2
            subtitle_y = title_y + 120
            
            draw.text((subtitle_x, subtitle_y), subtitle, fill=color_scheme['secondary'], font=body_font)
    
    async def _draw_content_slide(self, draw, slide_spec: Dict[str, Any], 
                                color_scheme: Dict[str, str], title_font, body_font, small_font):
        """Draw a content slide with text and visual elements."""
        title = slide_spec.get('title', 'Content')
        content = slide_spec.get('content', '')
        bullets = slide_spec.get('bullets', [])
        
        # Draw title
        if title_font:
            draw.text((self.margin, self.margin), title, fill=color_scheme['primary'], font=title_font)
        
        y_pos = self.margin + 120
        
        # Draw bullets if available
        if bullets and body_font:
            for bullet in bullets[:6]:  # Limit to 6 bullets
                # Draw bullet point
                draw.text((self.margin, y_pos), "•", fill=color_scheme['accent'], font=body_font)
                
                # Draw bullet text
                bullet_text = str(bullet)
                draw.text((self.margin + 30, y_pos), bullet_text, fill=color_scheme['text'], font=body_font)
                y_pos += 50
        elif content and body_font:
            # Draw content as paragraphs
            # Split content into lines
            words = content.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = draw.textbbox((0, 0), test_line, font=body_font)
                if bbox[2] - bbox[0] <= self.content_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw lines
            for line in lines[:8]:  # Limit to 8 lines
                draw.text((self.margin, y_pos), line, fill=color_scheme['text'], font=body_font)
                y_pos += 50
        
        # Add visual elements
        await self._add_visual_elements(draw, slide_spec, color_scheme)
    
    async def _draw_diagram_slide(self, draw, slide_spec: Dict[str, Any], 
                                color_scheme: Dict[str, str], title_font, body_font):
        """Draw a diagram slide."""
        title = slide_spec.get('title', 'Diagram')
        
        # Draw title
        if title_font:
            draw.text((self.margin, self.margin), title, fill=color_scheme['primary'], font=title_font)
        
        # Draw simple diagram
        center_x = self.slide_width // 2
        center_y = self.slide_height // 2
        
        # Draw a simple flowchart
        box_width = 200
        box_height = 80
        
        # Box 1
        draw.rectangle([center_x - box_width - 50, center_y - box_height//2, 
                       center_x - 50, center_y + box_height//2], 
                      outline=color_scheme['primary'], width=3)
        draw.text((center_x - box_width - 50 + 20, center_y - 10), "Start", 
                 fill=color_scheme['text'], font=body_font)
        
        # Arrow
        draw.line([center_x - 50, center_y, center_x + 50, center_y], 
                 fill=color_scheme['accent'], width=3)
        
        # Box 2
        draw.rectangle([center_x + 50, center_y - box_height//2, 
                       center_x + box_width + 50, center_y + box_height//2], 
                      outline=color_scheme['primary'], width=3)
        draw.text((center_x + 50 + 20, center_y - 10), "Process", 
                 fill=color_scheme['text'], font=body_font)
    
    async def _draw_conclusion_slide(self, draw, slide_spec: Dict[str, Any], 
                                   color_scheme: Dict[str, str], title_font, body_font):
        """Draw a conclusion slide."""
        title = slide_spec.get('title', 'Conclusion')
        content = slide_spec.get('content', 'Thank you for watching!')
        
        # Draw title
        if title_font:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.slide_width - title_width) // 2
            title_y = self.slide_height // 2 - 50
            
            draw.text((title_x, title_y), title, fill=color_scheme['primary'], font=title_font)
        
        # Draw content
        if content and body_font:
            content_bbox = draw.textbbox((0, 0), content, font=body_font)
            content_width = content_bbox[2] - content_bbox[0]
            content_x = (self.slide_width - content_width) // 2
            content_y = title_y + 100
            
            draw.text((content_x, content_y), content, fill=color_scheme['text'], font=body_font)
    
    async def _add_visual_elements(self, draw, slide_spec: Dict[str, Any], 
                                 color_scheme: Dict[str, str]):
        """Add visual elements to the slide."""
        visual_elements = slide_spec.get('visual_elements', [])
        
        for element in visual_elements:
            element_type = element.get('type', 'text')
            content = element.get('content', '')
            
            if element_type == 'formula':
                # Draw mathematical formula in a highlighted box
                x1 = self.slide_width - self.margin - 300
                y1 = self.margin + 200
                x2 = self.slide_width - self.margin - 20
                y2 = y1 + 60
                
                # Draw formula box
                draw.rectangle([x1, y1, x2, y2], fill=color_scheme['background'], 
                             outline=color_scheme['accent'], width=2)
                
                # Draw formula text
                if content:
                    draw.text((x1 + 10, y1 + 15), content, fill=color_scheme['primary'], 
                             font=ImageFont.load_default())
                
            elif element_type == 'highlight':
                # Draw highlight box
                x1 = self.margin + 20
                y1 = self.margin + 150
                x2 = self.slide_width - self.margin - 20
                y2 = y1 + 40
                draw.rectangle([x1, y1, x2, y2], outline=color_scheme['accent'], width=2)
                
            elif element_type == 'bullet':
                # Draw bullet points
                x = self.margin + 50
                y = self.margin + 200
                draw.ellipse([x-10, y-5, x+10, y+5], fill=color_scheme['accent'])
                
            elif element_type == 'text' and content:
                # Draw additional text content
                x = self.slide_width - self.margin - 300
                y = self.margin + 300
                draw.text((x, y), content, fill=color_scheme['text'], 
                         font=ImageFont.load_default())
    
    async def _add_slide_footer(self, draw, slide_id: int, 
                              color_scheme: Dict[str, str], small_font):
        """Add slide footer with slide number."""
        if small_font:
            footer_text = f"Slide {slide_id}"
            draw.text((self.margin, self.slide_height - 40), footer_text, 
                     fill=color_scheme['muted'], font=small_font)
    
    async def _create_matplotlib_slide(self, slide_spec: Dict[str, Any], 
                                     slide_id: int, color_scheme: Dict[str, str],
                                     question_id: str) -> str:
        """Create slide using matplotlib."""
        try:
            fig, ax = plt.subplots(figsize=(self.slide_width/100, self.slide_height/100))
            fig.patch.set_facecolor(color_scheme['background'])
            ax.set_facecolor(color_scheme['background'])
            
            # Remove axes
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Add title
            title = slide_spec.get('title', f'Slide {slide_id}')
            ax.text(0.5, 0.9, title, fontsize=24, ha='center', va='top', 
                   color=color_scheme['text'], weight='bold')
            
            # Add content
            content = slide_spec.get('content', '')
            if content:
                ax.text(0.1, 0.7, content[:200] + ('...' if len(content) > 200 else ''), 
                       fontsize=16, ha='left', va='top', color=color_scheme['text'],
                       wrap=True)
            
            # Add slide number
            ax.text(0.05, 0.05, f'Slide {slide_id}', fontsize=12, 
                   color=color_scheme['muted'])
            
            # Save slide
            slide_path = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.png"
            plt.savefig(slide_path, dpi=100, bbox_inches='tight', 
                       facecolor=color_scheme['background'], edgecolor='none')
            plt.close()
            
            return slide_path
            
        except Exception as e:
            print(f"Matplotlib slide creation failed: {e}")
            raise
    
    async def _create_fallback_slide(self, slide_spec: Dict[str, Any], 
                                   slide_id: int, question_id: str) -> str:
        """Create a fallback slide when no image libraries are available."""
        try:
            # Create a simple text file with slide info
            slide_path = f"{self.output_dir}/slide_{question_id}_{slide_id:03d}.txt"
            
            with open(slide_path, 'w', encoding='utf-8') as f:
                f.write(f"SLIDE {slide_id}\n")
                f.write("=" * 50 + "\n")
                f.write(f"Title: {slide_spec.get('title', 'Untitled')}\n")
                f.write(f"Type: {slide_spec.get('type', 'content')}\n")
                f.write(f"Duration: {slide_spec.get('duration', 5.0)}s\n")
                f.write("\nContent:\n")
                f.write(slide_spec.get('content', 'No content available') + "\n")
                f.write("\nVisual Elements:\n")
                for element in slide_spec.get('visual_elements', []):
                    f.write(f"- {element}\n")
            
            print(f"  📝 Created fallback slide {slide_id}")
            return slide_path
            
        except Exception as e:
            print(f"Fallback slide creation failed: {e}")
            raise
    
    def get_slide_stats(self) -> Dict[str, Any]:
        """Get slide generation statistics."""
        return {
            "pil_available": PIL_AVAILABLE,
            "matplotlib_available": MATPLOTLIB_AVAILABLE,
            "slide_dimensions": f"{self.slide_width}x{self.slide_height}",
            "color_schemes": list(self.color_schemes.keys()),
            "output_directory": self.output_dir
        }


# Global slide generator instance
slide_generator = SlideGenerator()


# Convenience functions
async def generate_slides(slides_data: List[Dict[str, Any]], 
                         question_id: str) -> List[Dict[str, Any]]:
    """Convenience function to generate slides."""
    return await slide_generator.generate_slides(slides_data, question_id)

def get_slide_generator_stats() -> Dict[str, Any]:
    """Get slide generator statistics."""
    return slide_generator.get_slide_stats()
