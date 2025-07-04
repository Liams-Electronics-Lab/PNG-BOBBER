#!/usr/bin/env python3
"""
Example usage script for PNG Bob Animator
This script demonstrates how to use the PNG Bob Animator with different settings.
"""

import os
from png_bob_animator import PNGBobAnimator


def create_sample_png():
    """Create a sample PNG for testing if none exists."""
    from PIL import Image, ImageDraw
    
    # Create a simple test image
    img = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple shape
    draw.ellipse([20, 20, 80, 80], fill=(255, 100, 100, 255))
    draw.rectangle([40, 10, 60, 90], fill=(100, 255, 100, 255))
    
    img.save('sample.png')
    print("✅ Created sample.png for testing")
    return 'sample.png'


def example_basic_usage():
    """Example of basic usage."""
    print("🎬 Basic Animation Example")
    print("-" * 30)
    
    # Create sample if no PNG exists
    png_file = 'sample.png'
    if not os.path.exists(png_file):
        png_file = create_sample_png()
    
    # Create basic animation
    animator = PNGBobAnimator(png_file, 'basic_bob.gif')
    animator.create_animation()
    print(f"✅ Basic animation saved as: basic_bob.gif\n")


def example_custom_settings():
    """Example with custom animation settings."""
    print("🎬 Custom Settings Example")
    print("-" * 30)
    
    # Create sample if no PNG exists
    png_file = 'sample.png'
    if not os.path.exists(png_file):
        png_file = create_sample_png()
    
    # Create animation with custom settings
    animator = PNGBobAnimator(png_file, 'custom_bob.gif')
    
    # Set custom parameters
    animator.set_animation_params(
        frame_count=40,      # More frames for smoother animation
        bob_height=15,       # Higher bobbing
        frame_duration=60    # Faster animation
    )
    
    animator.create_animation()
    print(f"✅ Custom animation saved as: custom_bob.gif\n")


def example_slow_gentle_bob():
    """Example with slow, gentle bobbing."""
    print("🎬 Slow & Gentle Bob Example")
    print("-" * 30)
    
    # Create sample if no PNG exists
    png_file = 'sample.png'
    if not os.path.exists(png_file):
        png_file = create_sample_png()
    
    # Create slow, gentle animation
    animator = PNGBobAnimator(png_file, 'gentle_bob.gif')
    
    # Set gentle parameters
    animator.set_animation_params(
        frame_count=50,      # More frames
        bob_height=5,        # Subtle bobbing
        frame_duration=120   # Slower animation
    )
    
    animator.create_animation()
    print(f"✅ Gentle animation saved as: gentle_bob.gif\n")


def main():
    """Run all examples."""
    print("🎨 PNG Bob Animator Examples")
    print("=" * 40)
    
    try:
        example_basic_usage()
        example_custom_settings()
        example_slow_gentle_bob()
        
        print("🎉 All examples completed successfully!")
        print("\nGenerated files:")
        print("- basic_bob.gif")
        print("- custom_bob.gif")
        print("- gentle_bob.gif")
        
        print("\n🖥️  To use the GUI version:")
        print("Run: python gui_launcher.py")
        print("Or:  python png_bob_animator.py --gui")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    main()
