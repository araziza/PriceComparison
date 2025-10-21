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

    # Verify required files exist
    required_files = ['launcher.py', 'app.py', 'config.py', 'data_handler.py', 'scrapers.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        print("✗ Missing required files:")
        for f in missing_files:
            print(f"  - {f}")
        print()
        print("Please ensure all required files are present before building.")
        return False

    print("✓ All required files found")
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
        "--onedir",  # Changed from --onefile for better Streamlit compatibility
        # Removed --windowed to keep console visible for errors and Streamlit output
        "--add-data=app.py:.",
        "--add-data=config.py:.",
        "--add-data=data_handler.py:.",
        "--add-data=scrapers.py:.",
        # Core imports
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.runtime.scriptrunner.magic_funcs",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=selenium",
        "--hidden-import=bs4",
        "--hidden-import=fuzzywuzzy",
        # Additional Streamlit dependencies
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=streamlit.runtime.state",
        "--hidden-import=streamlit.components.v1",
        "--hidden-import=altair",
        "--hidden-import=blinker",
        "--hidden-import=cachetools",
        "--hidden-import=click",
        "--hidden-import=gitpython",
        "--hidden-import=importlib_metadata",
        "--hidden-import=packaging",
        "--hidden-import=pillow",
        "--hidden-import=protobuf",
        "--hidden-import=pyarrow",
        "--hidden-import=pympler",
        "--hidden-import=python_dateutil",
        "--hidden-import=requests",
        "--hidden-import=rich",
        "--hidden-import=tenacity",
        "--hidden-import=toml",
        "--hidden-import=tornado",
        "--hidden-import=typing_extensions",
        "--hidden-import=tzlocal",
        "--hidden-import=validators",
        "--hidden-import=watchdog",
        # Selenium dependencies
        "--hidden-import=selenium.webdriver.chrome.service",
        "--hidden-import=selenium.webdriver.common.by",
        "--hidden-import=webdriver_manager.chrome",
        # BeautifulSoup dependencies
        "--hidden-import=bs4.builder._htmlparser",
        "--hidden-import=bs4.builder._lxml",
        "--hidden-import=lxml",
        "--hidden-import=lxml.etree",
        "--hidden-import=lxml.html",
        # Openpyxl dependencies
        "--hidden-import=openpyxl.cell._writer",
        # Collect all Streamlit files
        "--collect-all=streamlit",
        "--collect-all=altair",
        "--collect-all=plotly",
        "--copy-metadata=streamlit",
        "--copy-metadata=altair",
        "--copy-metadata=plotly",
        "--icon=NONE",
        "--noconfirm",
        "launcher.py"  # Use launcher as entry point instead of app.py
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
        dist_folder = os.path.join(os.getcwd(), 'dist', 'NitroPriceComparison')
        print(f"Executable location: {dist_folder}")
        print()
        print("To run the application:")
        print("  1. Navigate to: dist/NitroPriceComparison/")
        if sys.platform == "win32":
            print("  2. Double-click 'NitroPriceComparison.exe'")
            print("     OR run from command prompt: NitroPriceComparison.exe")
        else:
            print("  2. Run: ./NitroPriceComparison")
        print()
        print("IMPORTANT:")
        print("  - The console window will stay open - this is normal")
        print("  - The Streamlit app will automatically open in your browser")
        print("  - Do NOT close the console window while using the app")
        print("  - Press Ctrl+C in the console to stop the application")
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
