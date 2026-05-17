# 🚀 Quick Start Guide - Universal Document Chat

## The Problem You're Facing:
Every time you open a new terminal, you need to activate the virtual environment. Otherwise, Windows won't find `streamlit`.

---

## ✅ **SOLUTION 1: Use the Run Script (Easiest)**

I created two auto-run scripts for you:

### **Option A: Double-Click to Run**
1. Go to `d:\RAG PROJECT\`
2. **Double-click:** `run_app.bat`
3. Done! App starts automatically

### **Option B: Right-Click PowerShell**
1. **Right-click** on `run_app.ps1`
2. Select **"Run with PowerShell"**
3. Done!

---

## ✅ **SOLUTION 2: Manual Start (Every Time)**

If you prefer to type commands:

```bash
# Step 1: Go to project folder
cd "d:\RAG PROJECT"

# Step 2: Activate venv
.\venv\Scripts\activate

# Step 3: Run app
streamlit run app.py
```

You'll see `(venv)` appear before your prompt when activated.

---

## ✅ **SOLUTION 3: Use Full Path (No Activation Needed)**

You can skip activation by using the full path:

```bash
cd "d:\RAG PROJECT"
.\venv\Scripts\streamlit.exe run app.py
```

This works even without activating the venv!

---

## 🎯 **Recommended: Use run_app.bat**

**Easiest way:**
1. Navigate to `d:\RAG PROJECT\` in File Explorer
2. Double-click `run_app.bat`
3. App launches automatically!

---

## 📝 **What Activating the Venv Does:**

When you activate the virtual environment:
- ✅ Makes `streamlit` command available
- ✅ Uses the Python and packages IN the venv folder
- ✅ Isolates your project from system Python

**Visual indicator:**
```
PS D:\RAG PROJECT>           # NOT activated
(venv) PS D:\RAG PROJECT>    # ACTIVATED ✅
```

---

## 🔧 **To Fix PowerShell Execution Policy (If run_app.ps1 Doesn't Work):**

If you get an error about "execution policy", run this ONCE:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try `run_app.ps1` again.

---

## ✅ **Summary:**

**From now on, to start your app:**

### **Method 1 (Easiest):**
Double-click `run_app.bat` ✨

### **Method 2 (Command line):**
```bash
cd "d:\RAG PROJECT"
.\venv\Scripts\activate
streamlit run app.py
```

### **Method 3 (Full path):**
```bash
cd "d:\RAG PROJECT"
.\venv\Scripts\streamlit.exe run app.py
```

---

Choose whichever method you prefer! 🚀
