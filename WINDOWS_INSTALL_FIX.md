# Windows Installation Fix

## The Problem
Windows has a path length limitation (260 characters) that causes issues when installing certain Python packages like pandas and numpy.

## Solutions (Try in Order)

### Solution 1: Update pip and use pre-built wheels (EASIEST)

```cmd
# Upgrade pip, setuptools, and wheel first
python -m pip install --upgrade pip setuptools wheel

# Install packages individually using pre-built wheels
pip install streamlit pandas openpyxl requests beautifulsoup4 selenium webdriver-manager lxml python-dateutil fuzzywuzzy python-Levenshtein
```

This avoids building from source and uses pre-compiled packages.

---

### Solution 2: Install with --no-cache-dir

```cmd
pip install -r requirements.txt --no-cache-dir --prefer-binary
```

The `--prefer-binary` flag forces pip to use pre-built wheels instead of building from source.

---

### Solution 3: Enable Windows Long Path Support (Requires Admin)

**Option A: Via Registry (Windows 10 version 1607+)**

1. Press `Windows + R`
2. Type `regedit` and press Enter
3. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
4. Find `LongPathsEnabled` (or create it as DWORD if it doesn't exist)
5. Set value to `1`
6. Restart your computer
7. Try: `pip install -r requirements.txt`

**Option B: Via Group Policy (Windows 10 Pro/Enterprise)**

1. Press `Windows + R`
2. Type `gpedit.msc` and press Enter
3. Navigate to: Computer Configuration → Administrative Templates → System → Filesystem
4. Enable "Enable Win32 long paths"
5. Restart your computer
6. Try: `pip install -r requirements.txt`

---

### Solution 4: Use Conda (Alternative Package Manager)

If you have Anaconda or Miniconda:

```cmd
conda create -n nitro python=3.11
conda activate nitro
conda install -c conda-forge streamlit pandas openpyxl requests beautifulsoup4 selenium lxml python-dateutil
pip install webdriver-manager fuzzywuzzy python-Levenshtein
```

---

## Recommended Quick Fix (No Admin Required)

**Just run these commands one by one:**

```cmd
# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. Install core packages
pip install streamlit==1.31.0
pip install pandas
pip install openpyxl requests beautifulsoup4 lxml python-dateutil

# 3. Install selenium and web scraping tools
pip install selenium==4.17.2 webdriver-manager

# 4. Install fuzzy matching
pip install fuzzywuzzy python-Levenshtein

# 5. Verify installation
python -c "import streamlit, pandas, selenium; print('Success!')"
```

---

## If All Else Fails: Use Different Versions

Replace your `requirements.txt` with `requirements-windows.txt` (see next section) and run:

```cmd
pip install -r requirements-windows.txt
```

---

## After Installing

Once dependencies are installed, run:

```cmd
streamlit run app.py
```

---

## Troubleshooting

### "python: command not found"
Try `py` instead:
```cmd
py -m pip install --upgrade pip
py -m streamlit run app.py
```

### Still getting path errors?
Your temp folder path is too long. Set a shorter TEMP directory:
```cmd
set TEMP=C:\Temp
set TMP=C:\Temp
mkdir C:\Temp
pip install -r requirements.txt
```

### Permission errors?
Run Command Prompt as Administrator:
1. Search for "cmd"
2. Right-click → "Run as administrator"
3. Try the install commands again
