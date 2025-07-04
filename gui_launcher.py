#!/usr/bin/env python3
"""
GUI Launcher for PNG Bob Animator
This script launches the GUI version of the PNG Bob Animator.
"""

import tkinter as tk
from png_bob_animator import PNGBobAnimatorGUI


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = PNGBobAnimatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
