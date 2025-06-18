import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "<api key comes here>")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-4-maverick:free"

# Paths
RAW_CONTENT_DIR = BASE_DIR / "data" / "raw_content"
PROCESSED_CONTENT_DIR = BASE_DIR / "data" / "processed_content"
CHROMA_DB_DIR = BASE_DIR / "data" / "chroma_db"

# Create directories if they don't exist
RAW_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
