# 🚀 Universal Document Chat - Complete Installation Guide

## ✅ Tested & Working Installation Steps

This guide contains the **exact steps** that successfully installed all dependencies for the Universal Document Chat RAG application.

---

## 📋 Prerequisites

- **Python 3.9 or higher** (Check: `python --version`)
- **Internet connection** (for downloading packages and AI models)
- **4GB+ RAM** recommended
- **2GB free disk space** (for packages and AI models)

---

## 🔧 Step-by-Step Installation

### **Step 1: Navigate to Project Directory**

```bash
cd "d:\RAG PROJECT"
```

---

### **Step 2: Create Virtual Environment**

```bash
python -m venv venv
```

This creates an isolated Python environment in the `venv` folder.

---

### **Step 3: Activate Virtual Environment**

**Windows PowerShell:**
```bash
.\venv\Scripts\activate
```

You should see `(venv)` appear at the start of your command prompt.

**To deactivate later (optional):**
```bash
deactivate
```

---

### **Step 4: Upgrade pip (Optional but Recommended)**

```bash
.\venv\Scripts\python.exe -m pip install --upgrade pip
```

---

### **Step 5: Install Core Document Processing Libraries**

These are lightweight and install quickly:

```bash
.\venv\Scripts\python.exe -m pip install python-docx reportlab pdfplumber
```

**What this installs:**
- `python-docx` - Read Word documents
- `reportlab` - Generate PDF files
- `pdfplumber` - Extract text from PDFs

---

### **Step 6: Install NumPy**

```bash
.\venv\Scripts\python.exe -m pip install numpy
```

**What this installs:**
- `numpy` - Numerical computing library (required by ML packages)

---

### **Step 7: Install PyTorch (CPU Version)**

```bash
.\venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**What this installs:**
- `torch` - PyTorch deep learning framework (~200MB)
- Uses CPU-only version (smaller and faster to install)

⏱️ **Time:** ~2-3 minutes

---

### **Step 8: Install Streamlit Dependencies**

```bash
.\venv\Scripts\python.exe -m pip install blinker altair click protobuf tornado watchdog gitpython pydeck cachetools requests packaging tenacity toml validators pyarrow-hotfix
```

**What this installs:**
- All required dependencies for Streamlit to work properly

⏱️ **Time:** ~1-2 minutes

---

### **Step 9: Install Streamlit**

```bash
.\venv\Scripts\python.exe -m pip install streamlit
```

**What this installs:**
- `streamlit` - Web framework for the UI

⏱️ **Time:** ~30 seconds

**Note:** You may see errors about `pyarrow` failing to build - this is normal and won't affect the app.

---

### **Step 10: Install Machine Learning Libraries**

```bash
.\venv\Scripts\python.exe -m pip install transformers sentence-transformers faiss-cpu
```

**What this installs:**
- `transformers` - HuggingFace library for AI models (~50MB)
- `sentence-transformers` - Creates text embeddings
- `faiss-cpu` - Vector database for fast similarity search

⏱️ **Time:** ~2-3 minutes

---

### **Step 11: Verify Installation**

Check that Streamlit installed correctly:

```bash
.\venv\Scripts\streamlit.exe --version
```

Expected output: `Streamlit, version 1.51.0` (or higher)

---

## 🎯 Running the Application

### **Start the App:**

```bash
streamlit run app.py
```

Or with full path:

```bash
.\venv\Scripts\streamlit.exe run app.py
```

The app will:
1. Open automatically in your browser at `http://localhost:8501`
2. **First time only:** Download AI models (~500MB, takes 2-5 minutes)
   - `all-MiniLM-L6-v2` - Embedding model (~90MB)
   - `flan-t5-base` - Text generation model (~220MB)
3. Show "🚀 Initializing AI models..." status
4. Display the chat interface when ready

---

## 📁 Testing with Sample Documents

### **Step 1: Upload Documents**

1. Look at the **left sidebar** in the web interface
2. Click **"Browse files"** under "📁 Document Management"
3. Navigate to `d:\RAG PROJECT\examples\`
4. Select **all 5 files** (Ctrl+Click):
   - `sample.pdf` - AI overview
   - `sample.docx` - Python guide
   - `sample.md` - Machine learning intro
   - `sample.txt` - Meeting notes
   - `sample.csv` - Product data
5. Click **"Open"**
6. Wait for: **"✅ Ready to chat!"**

### **Step 2: Ask Questions**

Try these test questions:

**About AI (PDF):**
```
What is artificial intelligence?
What are the types of AI?
What are AI applications in healthcare?
```

**About Python (DOCX):**
```
What are Python's key features?
What data types does Python support?
```

**About Machine Learning (MD):**
```
What is supervised learning?
What are the applications of machine learning?
```

**About Business (TXT):**
```
What were the Q4 goals?
What is the budget allocation?
When is the next meeting?
```

**About Products (CSV):**
```
Which product has the highest rating?
List all electronics under $100
Which products have low stock?
```

**Multi-Document Questions:**
```
Compare AI and machine learning
What topics are covered in all documents?
```

---

## 🎨 UI Features

- **📊 Statistics Panel** (sidebar): Shows document and chunk counts
- **📚 Sources Section** (below answers): Displays citations with file names and page numbers
- **🗑️ Clear Chat Button**: Resets conversation (keeps documents)
- **🔄 Reset Docs Button**: Removes all documents and starts fresh

---

## 📦 Complete Package List

After successful installation, your environment includes:

### **Web Framework:**
- streamlit 1.51.0

### **Machine Learning:**
- torch 2.5.1+cpu
- transformers 4.48.0
- sentence-transformers 3.3.1
- faiss-cpu 1.9.0.post1

### **Document Processing:**
- pdfplumber 0.11.4
- python-docx 1.2.0
- reportlab 4.4.5

### **Utilities:**
- numpy 2.2.2
- And ~40 other dependency packages

**Total size:** ~800MB (packages + AI models)

---

## 🐛 Troubleshooting

### **Issue: `streamlit: command not found`**
**Solution:** Use the full path:
```bash
.\venv\Scripts\streamlit.exe run app.py
```

### **Issue: `ModuleNotFoundError: No module named 'X'`**
**Solution:** Activate venv first, then install the missing package:
```bash
.\venv\Scripts\activate
.\venv\Scripts\python.exe -m pip install X
```

### **Issue: PyArrow build errors**
**Status:** Normal! The app works without pyarrow.
**Reason:** We removed pandas dependency and use Python's built-in csv module instead.

### **Issue: App says "No documents uploaded"**
**Solution:** Upload documents using the sidebar file browser, not just asking questions.

### **Issue: Models downloading very slowly**
**Solution:** 
- Ensure stable internet connection
- Models are cached in `C:\Users\lokes\.cache\huggingface\`
- First download takes 2-5 minutes (only happens once)

### **Issue: Out of memory errors**
**Solution:**
- Close other applications
- Use `flan-t5-small` instead of `flan-t5-base` (edit `config.py`)
- Reduce `CHUNK_SIZE` in `config.py`

---

## 🔄 Reinstalling from Scratch

If you need to start over:

```bash
# Deactivate venv
deactivate

# Delete virtual environment
Remove-Item -Recurse -Force venv

# Delete downloaded models (optional)
Remove-Item -Recurse -Force C:\Users\lokes\.cache\huggingface\

# Start from Step 2 again
```

---

## ⚡ Quick Reference Commands

**Activate venv:**
```bash
.\venv\Scripts\activate
```

**Run app:**
```bash
streamlit run app.py
```

**Stop app:**
Press `Ctrl+C` in the terminal

**Check Python version:**
```bash
python --version
```

**List installed packages:**
```bash
.\venv\Scripts\python.exe -m pip list
```

**Update a package:**
```bash
.\venv\Scripts\python.exe -m pip install --upgrade PACKAGE_NAME
```

---

## 📚 Next Steps

1. ✅ Installation complete
2. ✅ App running
3. ✅ Documents uploaded
4. ✅ Tested with questions

**Now you can:**
- Upload your own documents (PDF, DOCX, TXT, MD, CSV)
- Build a knowledge base from your files
- Ask complex questions across multiple documents
- Get answers with source citations

---

## 🎉 Success Criteria

You've successfully installed everything when:
- ✅ `streamlit run app.py` opens the browser
- ✅ You see "🚀 Initializing AI models..."
- ✅ Upload example documents shows "✅ Ready to chat!"
- ✅ Questions get answered with source citations
- ✅ Statistics panel shows document/chunk counts

**Congratulations! Your RAG application is ready to use! 🚀**
