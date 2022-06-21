from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
BASE_DIR_NAME = Path(BASE_DIR).name
APP_DIR = Path(BASE_DIR, 'app')

DEBUG = bool(int(os.environ.get('DEBUG', 1)))
DEV = bool(int(os.environ.get('DEV', 0)))
