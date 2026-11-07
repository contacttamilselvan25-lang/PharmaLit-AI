import os
import sys
import webbrowser
import subprocess
import time
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent
    main_file = root_dir / "app" / "main.py"

    print("=" * 70)
    print("  💊 PharmaLit AI — Biomedical Research Intelligence Platform")
    print("=" * 70)
    print(f"Project Root: {root_dir}")
    print(f"Launching Streamlit on http://127.0.0.1:8501 ...")
    print("Press Ctrl+C to terminate the application.")
    print("=" * 70)

    def open_browser():
        time.sleep(2.0)
        webbrowser.open("http://127.0.0.1:8501")

    import threading
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(main_file),
        "--server.port=8501",
        "--server.address=127.0.0.1",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[PharmaLit AI] Shutting down gracefully...")

if __name__ == "__main__":
    main()
