# Nitro Price Comparison - Setup Guide

## Step 1: Get the Latest Code

If you're working from a fresh location or need to update:

```bash
# If you already have the repository, pull the latest changes:
cd /path/to/PriceComparison
git pull origin claude/debug-exe-startup-011CULaiiDjHiEnw6fS1fDur

# OR if you need to clone fresh:
git clone <your-repo-url>
cd PriceComparison
git checkout claude/debug-exe-startup-011CULaiiDjHiEnw6fS1fDur
```

## Step 2: Install Python Dependencies

Make sure you're in the PriceComparison directory, then:

```bash
pip install -r requirements.txt
```

**Note:** If you get a packaging error, use:
```bash
pip install -r requirements.txt --ignore-installed packaging
```

## Step 3: Choose How to Run

### Option A: Run Directly (Recommended for Development)

```bash
streamlit run app.py
```

**What happens:**
- A terminal message appears: "You can now view your Streamlit app in your browser"
- Your browser automatically opens to http://localhost:8501
- The app is now running!

**To stop:** Press `Ctrl+C` in the terminal

---

### Option B: Build Executable (For Distribution)

```bash
python build_exe.py
```

**What happens:**
1. You'll see a menu - choose option 1
2. PyInstaller will build the executable (takes a few minutes)
3. When done, find it in: `dist/NitroPriceComparison/`

**To run the executable:**
- **Windows:** Double-click `dist/NitroPriceComparison/NitroPriceComparison.exe`
- **Linux/Mac:** `./dist/NitroPriceComparison/NitroPriceComparison`

**Console window will stay open** - this is normal and required!

---

## Where Should I Run These Commands?

### Windows (Command Prompt or PowerShell):
```cmd
# Navigate to your project folder
cd C:\Users\YourName\Documents\PriceComparison

# Then run the commands
streamlit run app.py
```

### Mac/Linux (Terminal):
```bash
# Navigate to your project folder
cd ~/Documents/PriceComparison

# Then run the commands
streamlit run app.py
```

---

## Verifying Your Location

Make sure you're in the right folder:

```bash
# List files - you should see app.py, launcher.py, etc.
ls    # Mac/Linux
dir   # Windows

# Or check your current directory
pwd   # Mac/Linux
cd    # Windows
```

You should see these files:
- app.py
- launcher.py
- config.py
- data_handler.py
- scrapers.py
- requirements.txt
- build_exe.py

---

## Quick Troubleshooting

### "command not found: streamlit"
**Solution:** Install dependencies first:
```bash
pip install -r requirements.txt
```

### "No module named 'streamlit'"
**Solution:** You're trying to run `python app.py` instead of `streamlit run app.py`
```bash
# Wrong:
python app.py

# Correct:
streamlit run app.py
```

### "No such file or directory: app.py"
**Solution:** You're not in the right folder. Navigate to PriceComparison:
```bash
cd /path/to/PriceComparison
```

### "pip: command not found"
**Solution:** Try `pip3` instead:
```bash
pip3 install -r requirements.txt
```

---

## Complete Fresh Setup (Start to Finish)

```bash
# 1. Clone or pull latest changes
git pull

# 2. Verify you're in the right location
ls   # Should see app.py and other files

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py

# 5. Browser opens automatically - you're ready!
```

---

## Using the Application

Once running:

1. **Upload CSV:** Click "Browse files" in the sidebar
2. **Upload your parts CSV** with columns:
   - Column L: Part Number
   - Column M: Part Description
   - Column Y: Nitro Price (CAD)
3. **Select competitors** from the sidebar checkboxes
4. **Click "Force Update Prices"** to scrape competitor data
5. **Export to Excel** when done

---

## Need Help?

**Common Issues:**

1. **Already have a Streamlit app running?**
   - Error: "Port 8501 is already in use"
   - Solution: Close the other app or use: `streamlit run app.py --server.port 8502`

2. **Want to run in the background?**
   ```bash
   # Linux/Mac:
   nohup streamlit run app.py &

   # Windows: Just minimize the window
   ```

3. **Building executable fails?**
   - Make sure all dependencies installed: `pip install -r requirements.txt`
   - Install PyInstaller: `pip install pyinstaller`
   - Try again: `python build_exe.py`

---

## File Locations Summary

- **Source code:** Current directory (where app.py is)
- **Built executable:** `dist/NitroPriceComparison/`
- **Cached price data:** `price_cache.json` (created automatically)
- **Uploaded CSV files:** `temp_parts.csv` (temporary)

---

## What Changed in Latest Commit?

The fixes I made include:
- ✅ Fixed executable startup issues
- ✅ Added proper Streamlit launcher
- ✅ Comprehensive dependency bundling
- ✅ Console stays visible for debugging
- ✅ Better error messages

**You need to pull these changes** to get the fixes!
