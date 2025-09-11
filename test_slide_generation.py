#!/usr/bin/env python3
"""
Test script to verify slide generation works properly.
"""

import sys
import asyncio
sys.path.append('.')

async def test_slide_generation():
    """Test the slide generation system."""
    try:
        print("🧪 Testing slide generation...")
        
        # Test imports
        from research.slide_generator import slide_generator
        print("✅ Slide generator imported successfully")
        
        # Test PIL availability
        from research.slide_generator import PIL_AVAILABLE, MATPLOTLIB_AVAILABLE
        print(f"📊 PIL Available: {PIL_AVAILABLE}")
        print(f"📊 Matplotlib Available: {MATPLOTLIB_AVAILABLE}")
        
        # Create test slide data
        test_slides = [
            {
                'title': 'Introduction to Derivatives',
                'content': 'A derivative represents the rate of change of a function. For f(x) = x², the derivative is f\'(x) = 2x.',
                'type': 'title',
                'duration': 5.0
            },
            {
                'title': 'Power Rule',
                'content': 'The power rule states: d/dx(x^n) = n*x^(n-1). This is the fundamental rule for finding derivatives of polynomial functions.',
                'type': 'content',
                'duration': 7.0
            },
            {
                'title': 'Example: x²',
                'content': 'For f(x) = x²: d/dx(x²) = 2*x^(2-1) = 2x. This means the slope of the tangent line at any point x is 2x.',
                'type': 'content',
                'duration': 6.0
            }
        ]
        
        print(f"🎨 Generating {len(test_slides)} test slides...")
        
        # Generate slides
        generated_slides = await slide_generator.generate_slides(test_slides, "test_slides")
        
        print(f"✅ Generated {len(generated_slides)} slides successfully!")
        
        # Check what was created
        for slide in generated_slides:
            print(f"  📄 Slide {slide['id']}: {slide['title']}")
            print(f"     File: {slide['file_path']}")
            print(f"     Type: {slide['type']}")
            print(f"     Duration: {slide['duration']}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Slide generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_slide_generation())
    if success:
        print("\n🎉 Slide generation test PASSED!")
    else:
        print("\n💥 Slide generation test FAILED!")
        sys.exit(1)
