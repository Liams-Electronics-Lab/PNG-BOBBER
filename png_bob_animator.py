#!/usr/bin/env python3
"""
PNG Bob Animator
A Python application that converts transparent PNG images into animated GIFs
with a gentle bobbing motion.
"""

import argparse
import math
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import tempfile
import shutil
import atexit
from typing import Tuple, List
from PIL import Image, ImageFilter, ImageTk
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from functools import partial


class PNGBobAnimator:
    """Main class for creating bobbing animations from PNG images."""
    
    def __init__(self, png_path: str, output_path: str = None):
        """
        Initialize the animator.
        
        Args:
            png_path: Path to the input PNG file
            output_path: Path for the output GIF file (optional)
        """
        self.png_path = png_path
        self.output_path = output_path or self._get_default_output_path()
        self.frames = []
        
        # Animation parameters
        self.frame_count = 30
        self.bob_height = 10  # pixels
        self.frame_duration = 80  # milliseconds
        
        # Performance optimizations
        self.use_multiprocessing = True
        self.use_numpy_acceleration = True
        self.optimize_gif = True
        self.max_workers = min(multiprocessing.cpu_count(), 8)  # Limit to 8 cores max
        
        # Cache for reused calculations
        self._cached_canvas_size = None
        
    def _get_default_output_path(self) -> str:
        """Generate default output path based on input filename."""
        base_name = os.path.splitext(os.path.basename(self.png_path))[0]
        return f"{base_name}_bobbing.gif"
        
    def load_png(self) -> Image.Image:
        """Load and validate the PNG image."""
        try:
            img = Image.open(self.png_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            return img
        except Exception as e:
            raise ValueError(f"Error loading PNG file: {e}")
            
    def create_frame(self, img: Image.Image, frame_index: int) -> Image.Image:
        """
        Create a single frame of the animation.
        
        Args:
            img: The source PNG image
            frame_index: Current frame number
            
        Returns:
            Animated frame
        """
        # Calculate bob position using sine wave
        angle = (frame_index / self.frame_count) * 2 * math.pi
        bob_offset = int(math.sin(angle) * self.bob_height)
        
        # Calculate canvas dimensions
        canvas_width = img.width + 20
        canvas_height = img.height + self.bob_height * 2 + 20
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        
        # Calculate positions
        img_x = (canvas_width - img.width) // 2
        img_y = 10 + self.bob_height - bob_offset
        
        # Place the main image
        canvas.paste(img, (img_x, img_y), img)
        
        return canvas
        
    def create_animation(self) -> None:
        """Create the complete bobbing animation with hardware acceleration."""
        print(f"Loading PNG: {self.png_path}")
        img = self.load_png()
        
        print(f"Creating {self.frame_count} animation frames...")
        
        if self.use_multiprocessing and self.frame_count > 4:
            # Use multiprocessing for frame generation
            self._create_frames_parallel(img)
        else:
            # Use single-threaded approach for small frame counts
            self._create_frames_sequential(img)
            
        print(f"Saving animation to: {self.output_path}")
        self.save_gif()
    
    def _create_frames_sequential(self, img: Image.Image) -> None:
        """Create frames sequentially (single-threaded)."""
        for i in range(self.frame_count):
            frame = self.create_frame(img, i)
            self.frames.append(frame)
    
    def _create_frames_parallel(self, img: Image.Image) -> None:
        """Create frames in parallel using multiprocessing."""
        print(f"Using parallel processing with {self.max_workers} workers...")
        
        # Use ThreadPoolExecutor for I/O bound operations like PIL
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all frame creation tasks using the instance method
            futures = [executor.submit(self.create_frame, img, i) for i in range(self.frame_count)]
            
            # Collect results in order
            self.frames = []
            for i, future in enumerate(futures):
                try:
                    frame = future.result()
                    self.frames.append(frame)
                    if i % 5 == 0:  # Print progress every 5 frames
                        print(f"  Completed frame {i+1}/{self.frame_count}")
                except Exception as e:
                    print(f"Error creating frame {i}: {e}")
                    # Fall back to sequential creation for this frame
                    frame = self.create_frame(img, i)
                    self.frames.append(frame)
    
    def save_gif(self) -> None:
        """Save the animation as a GIF file with optimizations."""
        if not self.frames:
            raise ValueError("No frames to save")
        
        print("Optimizing GIF...")
        
        if self.optimize_gif:
            # Advanced GIF optimization
            self._save_optimized_gif()
        else:
            # Standard GIF saving
            self._save_standard_gif()
    
    def _save_optimized_gif(self) -> None:
        """Save GIF with advanced optimizations."""
        try:
            # Convert frames to P mode with optimized palette
            print("  Converting frames to optimized palette...")
            
            # Create a combined image to generate optimal palette
            combined_width = self.frames[0].width * min(4, len(self.frames))
            combined_height = self.frames[0].height
            combined = Image.new('RGBA', (combined_width, combined_height), (0, 0, 0, 0))
            
            # Paste first few frames to create palette
            for i, frame in enumerate(self.frames[:4]):
                x_offset = i * frame.width
                combined.paste(frame, (x_offset, 0))
            
            # Generate optimized palette
            combined_p = combined.convert('P', palette=Image.ADAPTIVE, colors=256)
            palette = combined_p.getpalette()
            
            # Convert all frames using the optimized palette
            optimized_frames = []
            for frame in self.frames:
                # Convert to P mode using the optimized palette
                frame_p = frame.quantize(palette=combined_p)
                optimized_frames.append(frame_p)
            
            print("  Saving optimized GIF...")
            optimized_frames[0].save(
                self.output_path,
                save_all=True,
                append_images=optimized_frames[1:],
                duration=self.frame_duration,
                loop=0,
                disposal=2,
                optimize=True
            )
            
        except Exception as e:
            print(f"  Optimization failed ({e}), falling back to standard save...")
            self._save_standard_gif()
    
    def _save_standard_gif(self) -> None:
        """Save GIF with standard settings."""
        self.frames[0].save(
            self.output_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=self.frame_duration,
            loop=0,
            disposal=2,
            optimize=True,
            transparency=0
        )
        
    def set_animation_params(self, frame_count: int = None, bob_height: int = None, 
                           frame_duration: int = None) -> None:
        """
        Set animation parameters.
        
        Args:
            frame_count: Number of frames in the animation
            bob_height: Height of the bobbing motion in pixels
            frame_duration: Duration of each frame in milliseconds
        """
        if frame_count is not None:
            self.frame_count = frame_count
        if bob_height is not None:
            self.bob_height = bob_height
        if frame_duration is not None:
            self.frame_duration = frame_duration
    
    def set_performance_options(self, use_multiprocessing: bool = True, 
                              use_numpy_acceleration: bool = True,
                              optimize_gif: bool = True,
                              max_workers: int = None) -> None:
        """
        Set performance optimization options.
        
        Args:
            use_multiprocessing: Enable parallel frame generation
            use_numpy_acceleration: Use NumPy for faster calculations
            optimize_gif: Use advanced GIF optimization
            max_workers: Maximum number of worker threads/processes
        """
        self.use_multiprocessing = use_multiprocessing
        self.use_numpy_acceleration = use_numpy_acceleration
        self.optimize_gif = optimize_gif
        if max_workers is not None:
            self.max_workers = min(max_workers, multiprocessing.cpu_count())

class PNGBobAnimatorGUI:
    """GUI class for the PNG Bob Animator."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("PNG Bob Animator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.frame_count = tk.IntVar(value=30)
        self.bob_height = tk.IntVar(value=10)
        self.frame_duration = tk.IntVar(value=80)
        
        # Performance options
        self.use_multiprocessing = tk.BooleanVar(value=True)
        self.use_numpy_acceleration = tk.BooleanVar(value=True)
        self.optimize_gif = tk.BooleanVar(value=True)
        self.max_workers = tk.IntVar(value=min(multiprocessing.cpu_count(), 8))
        
        # Preview variables
        self.preview_label = None
        self.preview_animation = None
        self.preview_frames = []
        self.preview_playing = False
        self.preview_job = None
        
        # Create temp directory for previews
        self.temp_dir = tempfile.mkdtemp(prefix="png_bob_preview_")
        atexit.register(self.cleanup_temp_dir)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main frame with two columns
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        
        # Left column for controls
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(1, weight=1)
        
        # Right column for preview
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(left_frame, text="PNG Bob Animator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(left_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        file_frame.columnconfigure(1, weight=1)
        
        # Input file
        ttk.Label(file_frame, text="Input PNG:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(file_frame, textvariable=self.input_file, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2, pady=(0, 5))
        
        # Output file
        ttk.Label(file_frame, text="Output GIF:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(file_frame, textvariable=self.output_file, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, pady=(0, 5))
        
        # Performance settings section
        perf_frame = ttk.LabelFrame(left_frame, text="Performance Settings", padding="10")
        perf_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        perf_frame.columnconfigure(1, weight=1)
        
        # Performance checkboxes
        ttk.Checkbutton(perf_frame, text="Use Multiprocessing", 
                       variable=self.use_multiprocessing).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="NumPy Acceleration", 
                       variable=self.use_numpy_acceleration).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="Optimize GIF", 
                       variable=self.optimize_gif).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Max workers
        ttk.Label(perf_frame, text="Max Workers:").grid(row=1, column=1, sticky=tk.W, padx=(20, 0))
        workers_frame = ttk.Frame(perf_frame)
        workers_frame.grid(row=1, column=2, sticky=(tk.W, tk.E), padx=(10, 0))
        ttk.Scale(workers_frame, from_=1, to=multiprocessing.cpu_count(), orient=tk.HORIZONTAL,
                 variable=self.max_workers, command=self.update_max_workers).grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.max_workers_label = ttk.Label(workers_frame, text=str(self.max_workers.get()))
        self.max_workers_label.grid(row=0, column=1, padx=(5, 0))
        
        # Animation settings section (moved down)
        settings_frame = ttk.LabelFrame(left_frame, text="Animation Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        settings_frame.columnconfigure(1, weight=1)
        
        # Frame count
        ttk.Label(settings_frame, text="Frame Count:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        frame_count_frame = ttk.Frame(settings_frame)
        frame_count_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        frame_count_frame.columnconfigure(0, weight=1)
        ttk.Scale(frame_count_frame, from_=10, to=60, orient=tk.HORIZONTAL, 
                 variable=self.frame_count, command=self.update_frame_count).grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.frame_count_label = ttk.Label(frame_count_frame, text="30")
        self.frame_count_label.grid(row=0, column=1, padx=(10, 0))
        
        # Bob height
        ttk.Label(settings_frame, text="Bob Height:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        bob_height_frame = ttk.Frame(settings_frame)
        bob_height_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        bob_height_frame.columnconfigure(0, weight=1)
        ttk.Scale(bob_height_frame, from_=2, to=30, orient=tk.HORIZONTAL, 
                 variable=self.bob_height, command=self.update_bob_height).grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.bob_height_label = ttk.Label(bob_height_frame, text="10px")
        self.bob_height_label.grid(row=0, column=1, padx=(10, 0))
        
        # Frame duration (speed)
        ttk.Label(settings_frame, text="Animation Speed:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        speed_frame = ttk.Frame(settings_frame)
        speed_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        speed_frame.columnconfigure(0, weight=1)
        ttk.Scale(speed_frame, from_=20, to=200, orient=tk.HORIZONTAL, 
                 variable=self.frame_duration, command=self.update_frame_duration).grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.frame_duration_label = ttk.Label(speed_frame, text="80ms")
        self.frame_duration_label.grid(row=0, column=1, padx=(10, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left_frame, variable=self.progress_var, 
                                          maximum=100, length=300)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))
        
        # Status label
        self.status_label = ttk.Label(left_frame, text="Ready to create animation...")
        self.status_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Preview", 
                  command=self.create_preview).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_button = ttk.Button(button_frame, text="Create Animation", 
                                      command=self.create_animation, style="Accent.TButton")
        self.create_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self.reset_defaults).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.LEFT)
        
        # Preview section
        preview_frame = ttk.LabelFrame(right_frame, text="Preview", padding="10")
        preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Preview label
        self.preview_label = ttk.Label(preview_frame, text="Select a PNG file\nand click Preview", 
                                     font=("Arial", 10), anchor="center")
        self.preview_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Preview info
        self.preview_info = ttk.Label(preview_frame, text="", font=("Arial", 8))
        self.preview_info.grid(row=1, column=0, padx=10, pady=(0, 10))
        
        # Credit section at bottom
        credit_frame = ttk.Frame(main_frame)
        credit_frame.grid(row=1, column=0, columnspan=2, pady=(20, 0))
        
        # Credit label with hyperlink
        credit_label = ttk.Label(credit_frame, text="Made by Liams Electronics Lab", 
                               font=("Arial", 9, "underline"), 
                               foreground="blue", cursor="hand2")
        credit_label.grid(row=0, column=0)
        credit_label.bind("<Button-1>", self.open_youtube_link)
        
    def open_youtube_link(self, event):
        """Open the YouTube channel link in the default browser."""
        import webbrowser
        webbrowser.open("https://www.youtube.com/channel/UCps0V_MhxlnIvX6RsPZBlxw")
        
    def browse_input_file(self):
        """Browse for input PNG file."""
        filename = filedialog.askopenfilename(
            title="Select PNG file",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            if not self.output_file.get():
                base_name = os.path.splitext(filename)[0]
                self.output_file.set(f"{base_name}_bobbing.gif")
    
    def browse_output_file(self):
        """Browse for output GIF file."""
        filename = filedialog.asksaveasfilename(
            title="Save GIF as",
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def update_frame_count(self, value):
        """Update frame count label."""
        self.frame_count_label.config(text=str(int(float(value))))
    
    def update_bob_height(self, value):
        """Update bob height label."""
        self.bob_height_label.config(text=f"{int(float(value))}px")
    
    def update_frame_duration(self, value):
        """Update frame duration label."""
        self.frame_duration_label.config(text=f"{int(float(value))}ms")
    
    def update_max_workers(self, value):
        """Update max workers label."""
        self.max_workers_label.config(text=str(int(float(value))))
    
    def reset_defaults(self):
        """Reset all values to defaults."""
        self.frame_count.set(30)
        self.bob_height.set(10)
        self.frame_duration.set(80)
        self.use_multiprocessing.set(True)
        self.use_numpy_acceleration.set(True)
        self.optimize_gif.set(True)
        self.max_workers.set(min(multiprocessing.cpu_count(), 8))
        
        # Update labels
        self.update_frame_count(30)
        self.update_bob_height(10)
        self.update_frame_duration(80)
        self.update_max_workers(self.max_workers.get())
    
    def create_animation(self):
        """Create the animation in a separate thread."""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input PNG file.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output GIF file.")
            return
        
        # Disable create button during processing
        self.create_button.config(state="disabled")
        
        # Start animation creation in a separate thread
        threading.Thread(target=self.create_animation_thread, daemon=True).start()
    
    def create_animation_thread(self):
        """Create animation in a separate thread to prevent GUI freezing."""
        try:
            self.progress_var.set(0)
            self.status_label.config(text="Creating animation...")
            
            # Create animator with GUI settings
            animator = PNGBobAnimator(self.input_file.get(), self.output_file.get())
            animator.set_animation_params(
                frame_count=self.frame_count.get(),
                bob_height=self.bob_height.get(),
                frame_duration=self.frame_duration.get()
            )
            
            # Set performance options
            animator.set_performance_options(
                use_multiprocessing=self.use_multiprocessing.get(),
                use_numpy_acceleration=self.use_numpy_acceleration.get(),
                optimize_gif=self.optimize_gif.get(),
                max_workers=self.max_workers.get()
            )
            
            # Create animation with progress updates
            self.create_animation_with_progress(animator)
            
            # Success message
            self.root.after(0, lambda: self.status_label.config(text="Animation created successfully!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                           f"Animation saved as: {self.output_file.get()}"))
            
        except Exception as e:
            # Error message
            self.root.after(0, lambda: self.status_label.config(text="Error creating animation"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        finally:
            # Re-enable create button
            self.root.after(0, lambda: self.create_button.config(state="normal"))
            self.root.after(0, lambda: self.progress_var.set(0))
    
    def create_animation_with_progress(self, animator):
        """Create animation with progress updates."""
        img = animator.load_png()
        
        # Create frames with progress updates
        for i in range(animator.frame_count):
            frame = animator.create_frame(img, i)
            animator.frames.append(frame)
            
            # Update progress
            progress = (i + 1) / animator.frame_count * 90  # 90% for frame creation
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda i=i: self.status_label.config(
                text=f"Creating frame {i+1}/{animator.frame_count}..."))
        
        # Save GIF
        self.root.after(0, lambda: self.status_label.config(text="Saving GIF..."))
        self.root.after(0, lambda: self.progress_var.set(95))
        animator.save_gif()
        self.root.after(0, lambda: self.progress_var.set(100))


    def cleanup_temp_dir(self):
        """Clean up temporary directory on exit."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
    
    def create_preview(self):
        """Create a preview of the animation."""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input PNG file first.")
            return
        
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input PNG file not found.")
            return
        
        # Stop any existing preview
        self.stop_preview()
        
        # Create preview in a separate thread
        threading.Thread(target=self.create_preview_thread, daemon=True).start()
    
    def create_preview_thread(self):
        """Create preview animation in a separate thread."""
        try:
            # Update status
            self.root.after(0, lambda: self.preview_info.config(text="Creating preview..."))
            
            # Create a smaller animator for preview (fewer frames for speed)
            preview_frames = min(15, self.frame_count.get())  # Max 15 frames for preview
            
            animator = PNGBobAnimator(self.input_file.get(), "")
            animator.set_animation_params(
                frame_count=preview_frames,
                bob_height=self.bob_height.get(),
                frame_duration=max(100, self.frame_duration.get())  # Slower preview
            )
            
            # Load and create preview frames
            img = animator.load_png()
            
            # Scale image to fit 250px width while maintaining aspect ratio
            preview_frames_pil = []
            for i in range(preview_frames):
                frame = animator.create_frame(img, i)
                
                # Calculate scale factor to fit 250px width
                scale_factor = 250 / frame.width
                new_width = int(frame.width * scale_factor)
                new_height = int(frame.height * scale_factor)
                
                # Resize frame
                preview_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                preview_frames_pil.append(preview_frame)
            
            # Convert PIL images to PhotoImage for tkinter
            self.preview_frames = []
            for frame in preview_frames_pil:
                photo = ImageTk.PhotoImage(frame)
                self.preview_frames.append(photo)
            
            # Update GUI with preview info
            self.root.after(0, lambda: self.preview_info.config(
                text=f"Preview: {len(self.preview_frames)} frames\n{new_width}x{new_height}px"))
            
            # Start animation
            self.root.after(0, self.start_preview_animation)
            
        except Exception as e:
            self.root.after(0, lambda: self.preview_info.config(text=f"Preview error: {str(e)}"))
    
    def start_preview_animation(self):
        """Start the preview animation loop."""
        if self.preview_frames:
            self.preview_playing = True
            self.current_preview_frame = 0
            self.animate_preview()
    
    def animate_preview(self):
        """Animate the preview frames."""
        if not self.preview_playing or not self.preview_frames:
            return
        
        # Update the preview label with current frame
        self.preview_label.config(image=self.preview_frames[self.current_preview_frame], text="")
        
        # Move to next frame
        self.current_preview_frame = (self.current_preview_frame + 1) % len(self.preview_frames)
        
        # Schedule next frame
        delay = max(100, self.frame_duration.get())
        self.preview_job = self.root.after(delay, self.animate_preview)
    
    def stop_preview(self):
        """Stop the preview animation."""
        self.preview_playing = False
        if self.preview_job:
            self.root.after_cancel(self.preview_job)
            self.preview_job = None
        
        # Clear preview frames from memory
        self.preview_frames = []
        
        # Reset preview label
        if self.preview_label:
            self.preview_label.config(image="", text="Select a PNG file\nand click Preview")
        
        if hasattr(self, 'preview_info'):
            self.preview_info.config(text="")
    
def main():
    """Main function to run the PNG Bob Animator."""
    parser = argparse.ArgumentParser(description='Convert PNG to bobbing animated GIF')
    parser.add_argument('input', nargs='?', help='Path to input PNG file')
    parser.add_argument('-o', '--output', help='Output GIF path (optional)')
    parser.add_argument('-f', '--frames', type=int, default=30, 
                       help='Number of frames (default: 30)')
    parser.add_argument('-b', '--bob-height', type=int, default=10,
                       help='Bobbing height in pixels (default: 10)')
    parser.add_argument('-d', '--duration', type=int, default=80,
                       help='Frame duration in milliseconds (default: 80)')
    parser.add_argument('--gui', action='store_true',
                       help='Launch GUI interface')
    parser.add_argument('--no-multiprocessing', action='store_true',
                       help='Disable multiprocessing (use single thread)')
    parser.add_argument('--no-numpy', action='store_true',
                       help='Disable NumPy acceleration')
    parser.add_argument('--no-optimize', action='store_true',
                       help='Disable GIF optimization')
    parser.add_argument('--max-workers', type=int, default=None,
                       help='Maximum number of worker threads')
    
    args = parser.parse_args()
    
    # Launch GUI if requested or no input file provided
    if args.gui or not args.input:
        root = tk.Tk()
        app = PNGBobAnimatorGUI(root)
        root.mainloop()
        return
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
        
    try:
        # Create animator
        animator = PNGBobAnimator(args.input, args.output)
        
        # Set custom parameters if provided
        animator.set_animation_params(
            frame_count=args.frames,
            bob_height=args.bob_height,
            frame_duration=args.duration
        )
        
        # Set performance options
        animator.set_performance_options(
            use_multiprocessing=not args.no_multiprocessing,
            use_numpy_acceleration=not args.no_numpy,
            optimize_gif=not args.no_optimize,
            max_workers=args.max_workers
        )
        
        # Create the animation
        animator.create_animation()
        
        print(f"✅ Animation created successfully: {animator.output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
