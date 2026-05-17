# URGENT FIX - Run this to clear cache and restart properly

import os
import shutil
import subprocess
import sys

print("🔧 Universal Document Chat - Cache Clear & Restart")
print("=" * 60)

# Step 1: Clear Streamlit cache
cache_dir = os.path.expanduser("~/.streamlit")
if os.path.exists(cache_dir):
    try:
        shutil.rmtree(cache_dir)
        print("✅ Cleared Streamlit cache")
    except:
        print("⚠️  Could not clear cache (may not exist)")
else:
    print("ℹ️  No cache to clear")

# Step 2: Clear Python cache
pycache_dirs = []
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        pycache_dirs.append(os.path.join(root, "__pycache__"))

for cache in pycache_dirs:
    try:
        shutil.rmtree(cache)
        print(f"✅ Cleared {cache}")
    except:
        pass

# Step 3: Verify key features exist in files
print("\n🔍 Verifying features in code...")

with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()
    
features_check = {
    "Streaming": "generate_answer_stream" in app_content,
    "Export": "Download Chat History" in app_content,
    "Summaries": "Document Summaries" in app_content,
    "Auto-save": "save_chat_history()" in app_content
}

all_good = True
for feature, exists in features_check.items():
    status = "✅" if exists else "❌"
    print(f"{status} {feature}: {'Found' if exists else 'MISSING'}")
    if not exists:
        all_good = False

print("\n" + "=" * 60)

if all_good:
    print("✅ ALL FEATURES VERIFIED IN CODE!")
    print("\n📋 Next steps:")
    print("1. Close your browser completely")
    print("2. Stop Streamlit (Ctrl+C in terminal)")
    print("3. Run: streamlit run app.py --server.runOnSave=false")
    print("4. Open fresh browser window")
else:
    print("❌ SOME FEATURES MISSING - Code may be corrupted")
    print("Please restore from backup or re-download files")

print("=" * 60)
