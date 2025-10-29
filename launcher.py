"""
Launcher for Nitro Price Comparison executable
This script starts the Streamlit server programmatically
"""

import os
import sys
from streamlit.web import cli as stcli


def main():
    """Launch the Streamlit application"""

    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = sys._MEIPASS
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Change to the application directory so relative imports work
    os.chdir(application_path)

    # Add application path to Python path for imports
    if application_path not in sys.path:
        sys.path.insert(0, application_path)

    # Set the path to the Streamlit app
    app_path = os.path.join(application_path, 'app.py')

    # Verify app.py exists
    if not os.path.exists(app_path):
        print(f"ERROR: Cannot find app.py at {app_path}")
        print(f"Application path: {application_path}")
        print(f"Files in directory: {os.listdir(application_path)}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Prepare Streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=false",  # Changed to false to auto-open browser
        "--browser.gatherUsageStats=false",
    ]

    # Start Streamlit
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
