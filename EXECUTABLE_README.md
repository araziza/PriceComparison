# Nitro Price Comparison - Executable Distribution

## Building the Executable

To build the portable executable:

```bash
python build_exe.py
```

Select option 1 to create the executable.

## Running the Application

After building, you'll find the executable in `dist/NitroPriceComparison/`

### Windows
1. Navigate to `dist/NitroPriceComparison/`
2. Double-click `NitroPriceComparison.exe`
3. A console window will open (this is normal - do NOT close it)
4. The application will automatically open in your default web browser
5. To stop the application, press `Ctrl+C` in the console window or close the browser and console

### Linux/Mac
1. Navigate to `dist/NitroPriceComparison/`
2. Run: `./NitroPriceComparison`
3. The application will open in your default browser
4. To stop, press `Ctrl+C` in the terminal

## Important Notes

- **Console Window**: The console window MUST stay open while using the application. This is where the Streamlit server runs.
- **First Launch**: The first launch may take a few seconds as the application initializes.
- **Browser**: If the browser doesn't open automatically, navigate to `http://localhost:8501`

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Rebuild the executable using the updated `build_exe.py` script. Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Console closes immediately
**Cause**: The `--windowed` flag was used during build, hiding errors.
**Solution**: The updated build script removes this flag. Rebuild the executable.

### Issue: "Module not found: streamlit"
**Cause**: PyInstaller didn't bundle all Streamlit dependencies.
**Solution**: The updated build script includes comprehensive dependency collection. Rebuild.

### Issue: Port 8501 already in use
**Solution**:
- Close any existing Streamlit applications
- Or manually specify a different port by editing `launcher.py`:
  ```python
  "--server.port=8502",  # Change to any available port
  ```

### Issue: Application won't start on Windows
**Solution**:
- Run `NitroPriceComparison.exe` from Command Prompt to see error messages
- Check Windows Defender or antivirus isn't blocking the executable
- Ensure you have Chrome installed (required for web scraping features)

### Issue: Web scraping features not working
**Solution**:
- Selenium requires Chrome browser to be installed
- Ensure you have an internet connection
- Some websites may block automated access

## Distribution

To distribute the application:

1. Compress the entire `dist/NitroPriceComparison/` folder
2. Share the compressed file
3. Users should extract the entire folder (not just the .exe)
4. Users can create a desktop shortcut to `NitroPriceComparison.exe`

## Technical Details

- **Build Type**: `--onedir` (folder distribution for better compatibility)
- **Console**: Visible (required for Streamlit server)
- **Entry Point**: `launcher.py` (programmatically starts Streamlit)
- **Dependencies**: All Streamlit, Selenium, and data processing libraries are bundled

## File Structure

```
dist/
└── NitroPriceComparison/
    ├── NitroPriceComparison.exe  (or NitroPriceComparison on Linux/Mac)
    ├── app.py
    ├── config.py
    ├── data_handler.py
    ├── scrapers.py
    ├── _internal/  (bundled libraries and dependencies)
    └── ...other runtime files
```

## System Requirements

- **Windows**: Windows 7 or later
- **Mac**: macOS 10.13 or later
- **Linux**: Most modern distributions
- **RAM**: 4GB minimum (8GB recommended)
- **Chrome Browser**: Required for web scraping features
- **Internet**: Required for competitor price lookups

## Limitations

- The executable is platform-specific (build on Windows for Windows, etc.)
- Chrome WebDriver is downloaded automatically on first scraping attempt
- Some antivirus software may flag the executable (false positive)

## Support

For issues or questions:
1. Check the console window output for error messages
2. Review this troubleshooting guide
3. Ensure all system requirements are met
4. Try rebuilding the executable with the latest `build_exe.py`
