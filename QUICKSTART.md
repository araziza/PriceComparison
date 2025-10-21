# Quick Start Guide - Nitro Price Comparison Tool

## 🚀 Get Started in 5 Minutes

### Option 1: Run with Python (Recommended for Development)

1. **Install Python** (if not already installed)
   - Download from [python.org](https://python.org)
   - Version 3.8 or higher required

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

4. **Your browser will automatically open** to `http://localhost:8501`

### Option 2: Use the Launcher Script

**Windows:**
1. Double-click `run_nitro_price_comparison.bat`
2. Wait for the browser to open

**Linux/Mac:**
1. Open terminal in this folder
2. Run: `./run_nitro_price_comparison.sh`
3. Wait for the browser to open

### Option 3: Create Portable Executable

1. **Run the build script**
   ```bash
   python build_exe.py
   ```

2. **Choose option 1** (Create portable executable)

3. **Find the executable** in the `dist` folder

4. **Run it** - no Python installation needed!

## 📊 Using the Application

### Step 1: Prepare Your CSV
- Use the provided `sample_parts_template.csv` as a reference
- Ensure your CSV has:
  - **Column L**: Part Number
  - **Column M**: Part Description
  - **Column Y**: Nitro Price

### Step 2: Upload Your Data
1. Click "Upload Parts CSV" in the sidebar
2. Select your CSV file
3. Wait for the data to load

### Step 3: Scrape Competitor Prices
1. Select which competitors to check (all selected by default)
2. Click "Force Update Prices"
3. Wait for scraping to complete (may take a few minutes)

### Step 4: Analyze Results
- Review the comparison table
- Use filters to find specific insights:
  - Parts where competitors are 10%+ cheaper
  - Parts where you're more competitive
  - Equal pricing situations
- Search for specific parts

### Step 5: Export
1. Click "Export to Excel"
2. Click "Download Excel File"
3. Open in Excel for further analysis

## 💡 Tips

### For Best Results:
- **Use specific part numbers** when possible (better matching)
- **Include detailed descriptions** to improve search accuracy
- **Scrape during off-peak hours** to avoid rate limiting
- **Clear cache periodically** to ensure fresh data

### Common Use Cases:

**Find Uncompetitive Pricing:**
1. Set filter to "Competitors 10%+ Cheaper"
2. Review the highlighted parts
3. Export for pricing review

**Monitor Market Position:**
1. Upload your full catalog
2. Scrape all competitors
3. Review summary metrics
4. Export monthly for trend analysis

**Quick Price Check:**
1. Use search box to find specific part
2. Click "Force Update Prices" for that part only
3. Review competitor prices instantly

## ⚠️ Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Run: `pip install -r requirements.txt`
- Check that port 8501 is available

### Scraping fails
- Check internet connection
- Verify competitor websites are accessible
- Increase `SCRAPE_DELAY` in config.py
- Try one competitor at a time

### No matches found
- Verify part numbers are correct
- Check part descriptions are detailed
- Some products may not be available on all sites
- Try adjusting search terms manually

### Slow performance
- Clear cache (button in sidebar)
- Reduce number of parts in CSV
- Scrape one competitor at a time
- Close other browser tabs

## 📞 Need Help?

1. Read the full `README.md` for detailed documentation
2. Check `config.py` for customization options
3. Review error messages in the application
4. Ensure CSV format matches the template

## 🎯 Next Steps

Once comfortable with basic usage:
- Customize colors in `config.py`
- Adjust confidence thresholds for matching
- Set up automated exports
- Create custom filters for your needs

---

**Happy Price Comparing!** 🔧
