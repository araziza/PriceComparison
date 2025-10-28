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

    # Set the path to the Streamlit app
    app_path = os.path.join(application_path, 'app.py')

    # Prepare Streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    # Start Streamlit
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
