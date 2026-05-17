# ⚠️ INSTALLATION FIX

There were some build errors with pandas/pyarrow. Here's the simple fix:

## Run these commands ONE BY ONE:

```bash
# 1. Install core dependencies
.\venv\Scripts\python.exe -m pip install numpy

# 2. Install PyTorch (CPU version)
.\venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu

# 3. Install Streamlit
.\venv\Scripts\python.exe -m pip install streamlit

# 4. Install ML libraries
.\venv\Scripts\python.exe -m pip install transformers sentence-transformers

# 5. Install FAISS
.\venv\Scripts\python.exe -m pip install faiss-cpu

# 6. Install PDF loader
.\venv\Scripts\python.exe -m pip install pdfplumber
```

## Then run the app:

```bash
.\venv\Scripts\streamlit.exe run app.py
```

---

## Alternative: Use System Python

If the venv keeps failing, you can use system Python:

```bash
# Deactivate venv
deactivate

# Install globally
pip install streamlit torch transformers sentence-transformers faiss-cpu pdfplumber

# Run with system Python  
streamlit run app.py
```

The app will still work perfectly!
