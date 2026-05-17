# Quick Install Script - Run this with: .\venv\Scripts\python.exe install_deps.py

import subprocess
import sys

def install(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("📦 Installing dependencies...")

# Core dependencies (in order of importance)
packages = [
    "numpy",
    "torch --index-url https://download.pytorch.org/whl/cpu",  #CPU version
    "streamlit",
    "transformers",
    "sentence-transformers",
    "faiss-cpu",
    "pdfplumber",
]

for pkg in packages:
    try:
        print(f"\n✅ Installing {pkg.split()[0]}...")
        install(pkg)
    except Exception as e:
        print(f"❌ Failed to install {pkg}: {e}")
        print("Continuing with next package...")

print("\n🎉 Installation complete!")
print("\nTo run the app: streamlit run app.py")
