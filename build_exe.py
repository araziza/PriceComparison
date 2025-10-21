"""
Build script for creating a portable executable of the Nitro Price Comparison tool
"""

import os
import sys
import subprocess
import shutil


def build_executable():
    """Build portable executable using PyInstaller"""

    print("=" * 60)
    print("Nitro Price Comparison - Executable Builder")
    print("=" * 60)
    print()

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

    print()

    # Clean previous builds
    if os.path.exists("build"):
        print("Cleaning build directory...")
        shutil.rmtree("build")

    if os.path.exists("dist"):
        print("Cleaning dist directory...")
        shutil.rmtree("dist")

    if os.path.exists("NitroPriceComparison.spec"):
        print("Removing old spec file...")
        os.remove("NitroPriceComparison.spec")

    print()

    # PyInstaller command
    print("Building executable...")
    print()

    pyinstaller_args = [
        "pyinstaller",
        "--name=NitroPriceComparison",
        "--onefile",
        "--windowed",
        "--add-data=config.py:.",
        "--add-data=data_handler.py:.",
        "--add-data=scrapers.py:.",
        "--hidden-import=streamlit",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=selenium",
        "--hidden-import=bs4",
        "--hidden-import=fuzzywuzzy",
        "--collect-all=streamlit",
        "--icon=NONE",
        "app.py"
    ]

    # On Windows, adjust the separator
    if sys.platform == "win32":
        pyinstaller_args = [arg.replace(":", ";") if "--add-data" in arg else arg for arg in pyinstaller_args]

    try:
        subprocess.check_call(pyinstaller_args)
        print()
        print("=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print()
        print(f"Executable location: {os.path.join(os.getcwd(), 'dist', 'NitroPriceComparison')}")
        print()
        print("To run the executable:")
        print("  1. Navigate to the 'dist' folder")
        print("  2. Run 'NitroPriceComparison' (or NitroPriceComparison.exe on Windows)")
        print()

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Please check the error messages above and ensure all dependencies are installed.")
        return False

    return True


def create_launcher_script():
    """Create a simple launcher script for the Streamlit app"""

    print("Creating launcher script...")

    # Windows batch file
    if sys.platform == "win32":
        launcher_content = """@echo off
echo Starting Nitro Price Comparison Tool...
echo.
echo The application will open in your default web browser.
echo Press Ctrl+C to stop the application.
echo.
streamlit run app.py
pause
"""
        with open("run_nitro_price_comparison.bat", "w") as f:
            f.write(launcher_content)

        print("✓ Created run_nitro_price_comparison.bat")

    # Unix shell script
    else:
        launcher_content = """#!/bin/bash
echo "Starting Nitro Price Comparison Tool..."
echo ""
echo "The application will open in your default web browser."
echo "Press Ctrl+C to stop the application."
echo ""
streamlit run app.py
"""
        with open("run_nitro_price_comparison.sh", "w") as f:
            f.write(launcher_content)

        # Make executable
        os.chmod("run_nitro_price_comparison.sh", 0o755)

        print("✓ Created run_nitro_price_comparison.sh")

    print()


if __name__ == "__main__":
    print()
    print("Choose build option:")
    print("1. Create portable executable (PyInstaller)")
    print("2. Create launcher script (requires Python)")
    print("3. Both")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        build_executable()
    elif choice == "2":
        create_launcher_script()
    elif choice == "3":
        create_launcher_script()
        print()
        build_executable()
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print()
    print("Build process complete!")
    print()
