#!/usr/bin/env python3
"""
Radar Port Scanner - Cross-platform launcher
Automatically installs dependencies and runs the application
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Ensure Python 3.8+ is installed"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def install_requirements():
    """Install PyQt5 if not already installed"""
    try:
        import PyQt5
        print("✓ PyQt5 is already installed")
        return True
    except ImportError:
        print("📦 Installing dependencies from requirements.txt...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                stdout=subprocess.DEVNULL
            )
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Try running: pip install -r requirements.txt")
            return False


def run_app():
    """Launch the GUI application"""
    try:
        print("\n🚀 Launching Radar Port Scanner...\n")
        # Import after requirements check
        from PyQt5.QtWidgets import QApplication
        from main import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Radar Port Scanner")
    print("=" * 50 + "\n")
    
    check_python_version()
    
    if not install_requirements():
        sys.exit(1)
    
    run_app()
