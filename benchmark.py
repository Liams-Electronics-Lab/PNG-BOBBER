#!/usr/bin/env python3
"""
Performance benchmark script for PNG Bob Animator
Tests different optimization settings to demonstrate performance improvements.
"""

import time
import os
from png_bob_animator import PNGBobAnimator
from PIL import Image, ImageDraw


def create_test_image(size=(100, 100)):
    """Create a test PNG image for benchmarking."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a test shape
    draw.ellipse([20, 20, 80, 80], fill=(255, 100, 100, 255))
    draw.rectangle([40, 10, 60, 90], fill=(100, 255, 100, 255))
    
    test_file = 'benchmark_test.png'
    img.save(test_file)
    return test_file


def benchmark_configuration(config_name, use_multiprocessing, use_numpy, optimize_gif, frame_count=30):
    """Benchmark a specific configuration."""
    print(f"\n📊 Testing {config_name}...")
    print(f"   Multiprocessing: {use_multiprocessing}")
    print(f"   NumPy Acceleration: {use_numpy}")
    print(f"   GIF Optimization: {optimize_gif}")
    print(f"   Frame Count: {frame_count}")
    
    # Create test image
    test_file = create_test_image()
    output_file = f"benchmark_{config_name.lower().replace(' ', '_')}.gif"
    
    try:
        # Create animator
        animator = PNGBobAnimator(test_file, output_file)
        animator.set_animation_params(frame_count=frame_count, bob_height=10, frame_duration=80)
        animator.set_performance_options(
            use_multiprocessing=use_multiprocessing,
            use_numpy_acceleration=use_numpy,
            optimize_gif=optimize_gif,
            max_workers=4
        )
        
        # Benchmark animation creation
        start_time = time.time()
        animator.create_animation()
        end_time = time.time()
        
        duration = end_time - start_time
        file_size = os.path.getsize(output_file) / 1024  # KB
        
        print(f"   ✅ Time: {duration:.2f}s")
        print(f"   📁 Size: {file_size:.1f} KB")
        print(f"   ⚡ Speed: {frame_count/duration:.1f} frames/sec")
        
        # Clean up
        os.remove(output_file)
        
        return duration, file_size
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None, None
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def run_performance_benchmark():
    """Run comprehensive performance benchmark."""
    print("🚀 PNG Bob Animator Performance Benchmark")
    print("=" * 50)
    
    frame_count = 30
    results = []
    
    # Test different configurations
    configs = [
        ("No Optimizations", False, False, False),
        ("NumPy Only", False, True, False),
        ("Multiprocessing Only", True, False, False),
        ("GIF Optimization Only", False, False, True),
        ("NumPy + Multiprocessing", True, True, False),
        ("All Optimizations", True, True, True),
    ]
    
    for config_name, multiproc, numpy, gif_opt in configs:
        duration, file_size = benchmark_configuration(
            config_name, multiproc, numpy, gif_opt, frame_count
        )
        if duration is not None:
            results.append((config_name, duration, file_size))
    
    # Display comparison
    print("\n📈 Performance Summary:")
    print("-" * 50)
    print(f"{'Configuration':<25} {'Time (s)':<10} {'Size (KB)':<10} {'Speed':<10}")
    print("-" * 50)
    
    baseline_time = None
    for config_name, duration, file_size in results:
        if baseline_time is None:
            baseline_time = duration
            speedup = "1.0x"
        else:
            speedup = f"{baseline_time/duration:.1f}x"
        
        print(f"{config_name:<25} {duration:<10.2f} {file_size:<10.1f} {speedup:<10}")
    
    # Test with larger frame count
    print(f"\n🎬 Testing with {frame_count*2} frames (All Optimizations)...")
    duration, file_size = benchmark_configuration(
        "High Frame Count", True, True, True, frame_count*2
    )
    
    print("\n💡 Optimization Tips:")
    print("- Enable multiprocessing for frame counts > 10")
    print("- NumPy acceleration helps with larger images")
    print("- GIF optimization reduces file size significantly")
    print("- Optimal worker count is usually 4-8 threads")


if __name__ == "__main__":
    run_performance_benchmark()
