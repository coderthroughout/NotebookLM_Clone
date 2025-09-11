#!/usr/bin/env python3
"""
Phase 3 Testing Script.
Tests the complete video production pipeline.
"""

import asyncio
import sys
import json
import os
sys.path.append('.')

from research.enhanced_content_pipeline import enhanced_content_pipeline
from research.video_production import video_production_pipeline
import sqlite3

async def test_phase3_setup():
    """Test if Phase 3 components are working."""
    print("🔧 Testing Phase 3 Setup...")
    
    try:
        # Test enhanced content pipeline
        pipeline = enhanced_content_pipeline
        status = pipeline.get_pipeline_status()
        print(f"  ✅ Enhanced Pipeline: {status['status']}")
        print(f"  ✅ Video Production: {status['video_production']}")
        
        # Test video production pipeline
        video_status = video_production_pipeline.get_pipeline_status()
        print(f"  ✅ Video Pipeline: {video_status['status']}")
        print(f"  ✅ Output Directory: {video_status['output_directory']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Phase 3 setup test failed: {e}")
        return False

async def test_sample_video_creation():
    """Test creating a sample video."""
    print("\n🎬 Testing Sample Video Creation...")
    
    try:
        result = await enhanced_content_pipeline.create_sample_complete_video("test_phase3")
        
        if result['status'] == 'success':
            print(f"  ✅ Sample Video Created Successfully!")
            print(f"  📹 Video File: {result['video']['video_file']}")
            print(f"  ⏱️ Duration: {result['video']['video_duration']} seconds")
            print(f"  🖼️ Slides: {result['video']['slide_count']}")
            print(f"  ⏱️ Total Time: {result['total_generation_time']:.2f} seconds")
            print(f"  📝 Content Gen: {result['content_generation_time']:.2f} seconds")
            print(f"  🎬 Video Prod: {result['video_production_time']:.2f} seconds")
            
            # Save results
            with open('phase3_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("  📁 Results saved to: phase3_test_results.json")
            
            return True
        else:
            print(f"  ❌ Sample video creation failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Sample video test failed: {e}")
        return False

async def test_video_production_only():
    """Test just the video production component."""
    print("\n🎥 Testing Video Production Component...")
    
    try:
        # Sample content
        sample_outline = {
            'title': 'Test Video Outline',
            'sections': ['Introduction', 'Main Content', 'Conclusion']
        }
        
        sample_script = {
            'title': 'Test Script',
            'content': 'This is a test script for video production testing.',
            'estimated_duration': '15 seconds'
        }
        
        sample_slides = {
            'slides': [
                {
                    'title': 'Introduction',
                    'content': 'Welcome to our test video',
                    'duration': 5.0,
                    'type': 'title'
                },
                {
                    'title': 'Main Content',
                    'content': 'This is the main content of our test video',
                    'duration': 7.0,
                    'type': 'content'
                },
                {
                    'title': 'Conclusion',
                    'content': 'Thank you for watching our test video',
                    'duration': 3.0,
                    'type': 'closing'
                }
            ]
        }
        
        result = await video_production_pipeline.create_video_from_content(
            "test_production_only", sample_outline, sample_script, sample_slides
        )
        
        if result['status'] == 'success':
            print(f"  ✅ Video Production Test Successful!")
            print(f"  📹 Video File: {result['video_file']}")
            print(f"  ⏱️ Duration: {result['video_duration']} seconds")
            print(f"  🖼️ Slides: {result['slide_count']}")
            print(f"  ⏱️ Production Time: {result['production_time']:.2f} seconds")
            
            return True
        else:
            print(f"  ❌ Video production test failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Video production test failed: {e}")
        return False

async def test_with_real_research_data():
    """Test the complete pipeline with real research data."""
    print("\n🔬 Testing with Real Research Data...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('citations.db')
        
        # Test with a real question
        result = await enhanced_content_pipeline.generate_complete_video(
            question_id="phase3_real_test",
            question="What are the main types of machine learning?",
            solution="The main types of machine learning are supervised learning, unsupervised learning, and reinforcement learning.",
            db_conn=conn
        )
        
        conn.close()
        
        if result['status'] == 'success':
            print(f"  ✅ Real Data Test Successful!")
            print(f"  📹 Video File: {result['video']['video_file']}")
            print(f"  ⏱️ Duration: {result['video']['video_duration']} seconds")
            print(f"  🖼️ Slides: {result['video']['slide_count']}")
            print(f"  📚 Context Used: {result['context_used']} sources")
            print(f"  ⏱️ Total Time: {result['total_generation_time']:.2f} seconds")
            
            # Save results
            with open('phase3_real_data_results.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("  📁 Real data results saved to: phase3_real_data_results.json")
            
            return True
        else:
            print(f"  ❌ Real data test failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Real data test failed: {e}")
        return False

async def main():
    """Run all Phase 3 tests."""
    print("🧪 PHASE 3 COMPLETE VIDEO PRODUCTION TESTING\n")
    
    tests = [
        ("Phase 3 Setup", test_phase3_setup),
        ("Video Production Component", test_video_production_only),
        ("Sample Video Creation", test_sample_video_creation),
        ("Real Research Data Test", test_with_real_research_data),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Final summary
    print(f"\n{'='*70}")
    print("🎯 PHASE 3 TESTING COMPLETE")
    print(f"{'='*70}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 PHASE 3 IS FULLY OPERATIONAL!")
        print("✅ Complete video production pipeline is working!")
        print("\n🚀 What This Means:")
        print("  🎬 End-to-end video generation from question to final video")
        print("  📝 AI-powered content generation with research context")
        print("  🖼️ Automated slide creation and video production")
        print("  📹 Output ready for distribution and sharing")
        print("\n💡 Ready for:")
        print("  🌐 Frontend integration")
        print("  🎥 Advanced video rendering")
        print("  📱 Production deployment")
    else:
        print("\n⚠️ Some Phase 3 tests failed.")
        print("Check the errors above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
