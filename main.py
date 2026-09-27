import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure root workspace is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Load .env if present
load_dotenv()

import uvicorn
from presentation.api import app


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print("==================================================")
    print("Carik Editorial Studio Server Starting")
    print(f"Local URL: http://{host}:{port}")
    print("==================================================")
    uvicorn.run("presentation.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
