# PNG Bob Animator

A Python application that converts transparent PNG images into animated GIFs with a gentle bobbing motion effect. Perfect for creating floating icons, animated characters, or any object that needs a subtle bouncing animation.

## Features

- **Smooth Bobbing Animation**: Creates gentle sine-wave based bobbing motion
- **PNG Transparency Support**: Preserves transparent backgrounds
- **Performance Optimized**: Multi-threading and NumPy acceleration for fast rendering
- **User-Friendly GUI**: Easy-to-use interface with real-time preview
- **Command Line Interface**: Batch processing and automation support
- **Customizable Parameters**: Adjust animation speed, height, and frame count

## Installation

```bash
pip install pillow numpy
```

## Usage

### GUI Interface
```bash
python gui_launcher.py
```

### Command Line
```bash
# Basic usage
python png_bob_animator.py input.png

# Custom settings
python png_bob_animator.py input.png -o output.gif -f 40 -b 15 -d 60

# Performance options
python png_bob_animator.py input.png --max-workers 8
```

### Command Line Options
- `-o, --output`: Output GIF file path
- `-f, --frames`: Number of frames (10-60, default: 30)
- `-b, --bob-height`: Bobbing height in pixels (2-30, default: 10)
- `-d, --duration`: Frame duration in milliseconds (20-200, default: 80)
- `--max-workers`: Number of parallel workers for performance
- `--gui`: Launch GUI interface

## Requirements

- Python 3.7+
- Pillow (PIL)
- NumPy
- tkinter (usually included with Python)

## License

MIT License - See LICENSE file for details



---

**Created with ❤️ using Python, Pillow, and NumPy**

**Made by [Liams Electronics Lab](https://www.youtube.com/channel/UCps0V_MhxlnIvX6RsPZBlxw)**
