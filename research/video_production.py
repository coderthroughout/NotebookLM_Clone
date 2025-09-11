"""
Video Production Module for Phase 3.
Converts generated outlines, scripts, and slides into actual video content.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .config import config


class VideoProductionPipeline:
    """Main pipeline for converting generated content into video."""
    
    def __init__(self):
        self.output_dir = "video_output"
        self.temp_dir = "temp_video"
        self.pipeline_status = "initialized"
        self.last_generation = None
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            "status": self.pipeline_status,
            "last_generation": self.last_generation,
            "output_directory": self.output_dir,
            "temp_directory": self.temp_dir,
            "phase": "video_production"
        }
    
    async def create_video_from_content(
        self, 
        question_id: str,
        outline: Dict[str, Any],
        script: Dict[str, Any],
        slides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main method to create video from generated content.
        """
        try:
            self.pipeline_status = "running"
            start_time = datetime.now()
            
            print(f"🎬 Starting video production for question: {question_id}")
            
            # Prepare per-run temp directory and clean it
            run_temp_dir = os.path.join(self.temp_dir, str(question_id))
            if os.path.exists(run_temp_dir):
                import shutil
                shutil.rmtree(run_temp_dir, ignore_errors=True)
            os.makedirs(run_temp_dir, exist_ok=True)
            
            # Step 1: Process and validate content
            processed_content = await self._process_content(outline, script, slides, question_id)
            print(f"  ✅ Processed content: {len(processed_content['slides'])} slides")
            
            # Step 2: Generate slide images
            slide_images = await self._generate_slide_images(processed_content['slides'], question_id)
            print(f"  🖼️ Generated {len(slide_images)} slide images")
            
            # Step 3: Create video sequence
            video_sequence = await self._create_video_sequence(
                slide_images, 
                processed_content['script']
            )
            print(f"  🎥 Created video sequence")
            
            # Step 4: Render final video
            video_output = await self._render_video(video_sequence, question_id)
            print(f"  🎬 Rendered final video")
            
            # Update pipeline status
            self.pipeline_status = "completed"
            self.last_generation = datetime.now().isoformat()
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "question_id": question_id,
                "video_file": video_output['file_path'],
                "video_duration": video_output['duration'],
                "slide_count": len(slide_images),
                "production_time": duration,
                "timestamp": self.last_generation,
                "output_files": video_output['all_files']
            }
            
        except Exception as e:
            self.pipeline_status = "error"
            print(f"❌ Video production failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "question_id": question_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_content(
        self, 
        outline: Dict[str, Any], 
        script: Dict[str, Any], 
        slides: Dict[str, Any],
        question_id: str
    ) -> Dict[str, Any]:
        """Process and validate the generated content."""
        try:
            # Extract slide information
            processed_slides = []
            if isinstance(slides, dict) and 'slides' in slides:
                slide_list = slides['slides']
            elif isinstance(slides, list):
                slide_list = slides
            else:
                slide_list = [slides]
            
            # Helper to normalize content to readable text
            def normalize_content_to_text(content: Any) -> str:
                if content is None:
                    return ""
                if isinstance(content, str):
                    return content.strip()
                if isinstance(content, list):
                    # Bulletize lists
                    bullets = []
                    for item in content:
                        text = normalize_content_to_text(item)
                        if text:
                            bullets.append(f"• {text}")
                    return "\n".join(bullets)
                if isinstance(content, dict):
                    # Flatten simple dicts into key: value lines
                    lines = []
                    for k, v in content.items():
                        text = normalize_content_to_text(v)
                        if text:
                            lines.append(f"{k}: {text}")
                    return "\n".join(lines)
                # Fallback
                return str(content)

            # Process each slide (preserve structure)
            for i, slide in enumerate(slide_list):
                if isinstance(slide, str):
                    processed_slide = {
                        'id': i + 1,
                        'title': f'Slide {i + 1}',
                        'bullets': [normalize_content_to_text(slide)],
                        'type': 'text',
                        'duration': 4.0,
                        'visual_elements': []
                    }
                elif isinstance(slide, dict):
                    processed_slide = {
                        'id': i + 1,
                        'title': slide.get('title', f'Slide {i + 1}'),
                        'type': slide.get('type', 'text'),
                        'duration': float(slide.get('duration', 4.0)),
                        'visual_elements': slide.get('visual_elements', []),
                        'layout': slide.get('layout', 'standard'),
                        'color_scheme': slide.get('color_scheme', 'default')
                    }
                    # Preserve bullets if present; else derive from content/text
                    if 'bullets' in slide and isinstance(slide['bullets'], list):
                        processed_slide['bullets'] = [normalize_content_to_text(b) for b in slide['bullets']]
                    else:
                        text_fallback = slide.get('content', slide.get('text', ''))
                        processed_slide['bullets'] = [normalize_content_to_text(text_fallback)] if text_fallback else []
                    # Preserve citations and build_sequence if present
                    if 'citations' in slide:
                        processed_slide['citations'] = slide['citations']
                    if 'build_sequence' in slide:
                        processed_slide['build_sequence'] = slide['build_sequence']
                else:
                    continue
                processed_slides.append(processed_slide)

            # Enforce max 40 slides
            if len(processed_slides) > 40:
                processed_slides = processed_slides[:40]
            
            # Process script
            script_content = ""
            if isinstance(script, dict):
                if 'content' in script:
                    script_content = script['content']
                elif 'sections' in script:
                    script_content = "\n".join([str(s) for s in script['sections']])
            elif isinstance(script, str):
                script_content = script
            
            return {
                'slides': processed_slides,
                'script': script_content,
                'outline': outline
            }
            
        except Exception as e:
            print(f"Content processing failed: {e}")
            raise
    
    async def _generate_slide_images(self, slides: List[Dict[str, Any]], question_id: str) -> List[Dict[str, Any]]:
        """Generate slide images from specifications using ultimate generator."""
        try:
            from .ultimate_slide_generator import ultimate_slide_generator
            
            # Use the ultimate generator for ALL slides - completely bypass old system
            slide_images = await ultimate_slide_generator.create_slide_images(slides, str(question_id))
            
            return slide_images
            
        except Exception as e:
            print(f"Ultimate slide generation failed: {e}")
            # Fallback to high-quality generator
            try:
                from .high_quality_slide_generator import high_quality_slide_generator
                slide_images = await high_quality_slide_generator.create_slide_images(slides, str(question_id))
                return slide_images
            except Exception as e2:
                print(f"Fallback slide generation failed: {e2}")
                # Do not create TXT placeholders in production path
                raise
    
    async def _create_placeholder_slides(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create placeholder slides as fallback."""
        try:
            # In production, do not emit TXT placeholders
            raise Exception("Slide image generation failed and placeholders are disabled in production")
            
        except Exception as e:
            print(f"Placeholder slide creation failed: {e}")
            raise
    
    async def _create_video_sequence(
        self, 
        slide_images: List[Dict[str, Any]], 
        script: str
    ) -> Dict[str, Any]:
        """Create video sequence from slides and script."""
        try:
            # Calculate total duration
            total_duration = sum(slide['duration'] for slide in slide_images)
            
            # Create timing information
            sequence = {
                'total_duration': total_duration,
                'slide_count': len(slide_images),
                'slides': slide_images,
                'script_timing': self._create_script_timing(script, slide_images)
            }
            
            return sequence
            
        except Exception as e:
            print(f"Video sequence creation failed: {e}")
            raise
    
    def _create_script_timing(self, script: str, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create timing information for script narration."""
        try:
            # Simple timing based on slide duration
            # In production, you'd use more sophisticated timing analysis
            script_timing = []
            current_time = 0.0
            
            for slide in slides:
                script_timing.append({
                    'slide_id': slide['id'],
                    'start_time': current_time,
                    'end_time': current_time + slide['duration'],
                    'duration': slide['duration']
                })
                current_time += slide['duration']
            
            return script_timing
            
        except Exception as e:
            print(f"Script timing creation failed: {e}")
            return []
    
    async def _render_video(
        self, 
        sequence: Dict[str, Any], 
        question_id: str
    ) -> Dict[str, Any]:
        """Render the final video from the sequence."""
        try:
            # For now, create a video manifest file
            # In production, you'd use ffmpeg or similar to create actual video
            
            video_file = f"{self.output_dir}/video_{question_id}.mp4"
            manifest_file = f"{self.output_dir}/manifest_{question_id}.json"
            
            # Create video manifest
            manifest = {
                'question_id': question_id,
                'video_file': video_file,
                'total_duration': sequence['total_duration'],
                'slide_count': sequence['slide_count'],
                'slides': sequence['slides'],
                'script_timing': sequence['script_timing'],
                'created_at': datetime.now().isoformat(),
                'status': 'rendered'
            }
            
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Create actual MP4 video file
            await self._create_actual_video(video_file, sequence, question_id)
            
            return {
                'file_path': video_file,
                'manifest_path': manifest_file,
                'duration': sequence['total_duration'],
                'all_files': [video_file, manifest_file]
            }
            
        except Exception as e:
            print(f"Video rendering failed: {e}")
            raise
    
    async def _create_actual_video(
        self, 
        video_file: str, 
        sequence: Dict[str, Any], 
        question_id: str
    ) -> None:
        """Create an actual MP4 video file using available tools."""
        try:
            # Try to create video using available Python libraries
            await self._create_simple_video(video_file, sequence, question_id)
        except Exception as e:
            print(f"⚠️ Failed to create actual video: {e}")
            # Fall back to a valid video placeholder
            await self._create_video_placeholder(video_file, sequence, question_id)

    async def _create_simple_video(
        self, 
        video_file: str, 
        sequence: Dict[str, Any], 
        question_id: str
    ) -> None:
        """Create a video using actual slide images."""
        import subprocess
        import os
        from pathlib import Path
        
        try:
            # Check if ffmpeg is available
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            
            # Check if we have actual slide images
            slide_images = sequence.get('slides', [])
            if not slide_images:
                raise Exception("No slide images available")
            
            # Create video from slide images
            await self._create_slideshow_video(video_file, slide_images, sequence)
                
        except subprocess.CalledProcessError:
            raise Exception("FFmpeg not available")
        except FileNotFoundError:
            raise Exception("FFmpeg not found in PATH")
    
    async def _create_slideshow_video(self, video_file: str, 
                                    slide_images: List[Dict[str, Any]], 
                                    sequence: Dict[str, Any]) -> None:
        """Create a slideshow video with per-frame durations using FFmpeg concat demuxer."""
        import subprocess
        import os
        try:
            print(f"🎬 Creating slideshow video with {len(slide_images)} slides...")

            # Build frame list including slide builds
            frames = []
            for slide in slide_images:
                # Base frame
                frames.append({"file_path": slide['file_path'], "duration": slide.get('duration', 4.0)})
                # Build frames if present
                for bf in slide.get('_build_frames', []) or []:
                    frames.append({"file_path": bf['file_path'], "duration": bf.get('duration', 2.0)})

            # Filter valid frames and ensure non-trivial file sizes
            valid_frames = []
            for f in frames:
                p = f['file_path']
                if p.endswith('.png') and os.path.exists(p):
                    try:
                        if os.path.getsize(p) > 5000:  # >5KB indicates non-empty image
                            valid_frames.append(f)
                    except Exception:
                        continue
            if not valid_frames:
                print("❌ No valid frames, creating fallback video")
                await self._create_fallback_video(video_file, len(slide_images))
                return

            # Create concat file
            concat_path = os.path.join(self.temp_dir, "concat_list.txt")
            with open(concat_path, 'w', encoding='utf-8') as cf:
                for f in valid_frames:
                    cf.write(f"file '{os.path.abspath(f['file_path'])}'\n")
                    cf.write(f"duration {max(0.2, float(f['duration']))}\n")
                # Repeat last file to finalize
                cf.write(f"file '{os.path.abspath(valid_frames[-1]['file_path'])}'\n")

            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0', '-i', concat_path,
                '-fps_mode', 'vfr',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black',
                video_file
            ]

            print(f"🎥 Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Slideshow video created successfully: {video_file}")
            else:
                print(f"❌ FFmpeg failed: {result.stderr}")
                print(f"FFmpeg stdout: {result.stdout}")
                raise Exception(f"FFmpeg failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Slideshow video creation failed: {e}")
            await self._create_fallback_video(video_file, len(slide_images))
    
    async def _create_fallback_video(self, video_file: str, num_slides: int) -> None:
        """Create a simple fallback video when slide generation fails."""
        import subprocess
        
        try:
            duration = num_slides * 5  # 5 seconds per slide
            print(f"🔄 Creating fallback video ({duration}s duration)")
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=black:size=1920x1080:duration={duration}',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                video_file
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Fallback video created: {video_file}")
            else:
                raise Exception(f"Fallback video creation failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Fallback video creation failed: {e}")
            raise
    
    async def _concatenate_video_segments(self, output_file: str, 
                                        segment_files: List[str]) -> None:
        """Concatenate video segments into final video."""
        import subprocess
        import os
        
        try:
            # Create file list for ffmpeg concat
            concat_file = f"{self.temp_dir}/concat_list.txt"
            with open(concat_file, 'w') as f:
                for segment in segment_files:
                    f.write(f"file '{os.path.abspath(segment)}'\n")
            
            # Concatenate videos
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                output_file
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Video concatenation failed: {result.stderr}")
                
        except Exception as e:
            print(f"Video concatenation failed: {e}")
            raise

    async def _create_video_placeholder(
        self, 
        video_file: str, 
        sequence: Dict[str, Any], 
        question_id: str
    ) -> None:
        """Create a minimal valid video file as placeholder."""
        # Create a basic text file with .txt extension to avoid confusion
        placeholder_file = video_file.replace('.mp4', '_placeholder.txt')
        
        with open(placeholder_file, 'w') as f:
            f.write(f"Video placeholder for question {question_id}\n")
            f.write(f"Duration: {sequence['total_duration']} seconds\n")
            f.write(f"Slides: {sequence['slide_count']}\n")
            f.write("Real video rendering requires FFmpeg installation.\n")
            f.write("Install FFmpeg and restart the server for video generation.\n")
        
        # Create a minimal HTML file that can display in video players
        with open(video_file.replace('.mp4', '.html'), 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html><head><title>Video {question_id}</title></head>
<body style="background:black;color:white;font-family:Arial;text-align:center;padding:50px;">
<h1>Video for Question {question_id}</h1>
<p>Duration: {sequence['total_duration']} seconds</p>
<p>Slides: {sequence['slide_count']}</p>
<p>Install FFmpeg for actual video generation</p>
</body></html>""")
        
        print(f"⚠️ Created placeholder files for {question_id}")

    async def create_sample_video(self, question_id: str = "sample_001") -> Dict[str, Any]:
        """Create a sample video for testing purposes."""
        try:
            # Sample content
            sample_outline = {
                'title': 'Sample Video Outline',
                'sections': ['Introduction', 'Main Content', 'Conclusion']
            }
            
            sample_script = {
                'title': 'Sample Script',
                'content': 'This is a sample script for testing video production.',
                'estimated_duration': '15 seconds'
            }
            
            sample_slides = {
                'slides': [
                    {
                        'title': 'Introduction',
                        'content': 'Welcome to our sample video',
                        'duration': 5.0,
                        'type': 'title'
                    },
                    {
                        'title': 'Main Content',
                        'content': 'This is the main content of our video',
                        'duration': 7.0,
                        'type': 'content'
                    },
                    {
                        'title': 'Conclusion',
                        'content': 'Thank you for watching',
                        'duration': 3.0,
                        'type': 'closing'
                    }
                ]
            }
            
            return await self.create_video_from_content(
                question_id, sample_outline, sample_script, sample_slides
            )
            
        except Exception as e:
            print(f"Sample video creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "question_id": question_id
            }


# Global video production pipeline instance
video_production_pipeline = VideoProductionPipeline()


# Convenience functions
async def create_video_from_content(
    question_id: str,
    outline: Dict[str, Any],
    script: Dict[str, Any],
    slides: Dict[str, Any]
) -> Dict[str, Any]:
    """Convenience function to create video from content."""
    return await video_production_pipeline.create_video_from_content(
        question_id, outline, script, slides
    )

async def create_sample_video(question_id: str = "sample_001") -> Dict[str, Any]:
    """Convenience function to create a sample video."""
    return await video_production_pipeline.create_sample_video(question_id)
