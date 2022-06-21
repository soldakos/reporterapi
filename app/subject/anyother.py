import os
import sys
from pathlib import Path


def admin():
    error = ''
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    print(BASE_DIR, sys.path[1])
    try:
        os.system(f"{BASE_DIR}\sqlite-gui\sqlite-gui.exe {BASE_DIR}\db.sqlite3")
    except Exception as e:
        error = str(e)

    return {"error": error}
