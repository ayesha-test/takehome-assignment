import os

BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://november7-730026606190.europe-west1.run.app",
).rstrip("/")

SUMMARIES_PATH = "/summaries"
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))

# Layer weights (must sum to 1.0)
WEIGHT_STRUCTURE = 0.20
WEIGHT_COVERAGE = 0.50
WEIGHT_SIMILARITY = 0.30

PASS_THRESHOLD = 0.75

# Structure bounds
MIN_SUMMARY_LENGTH = 10
MAX_SUMMARY_LENGTH = 500

# Sentence-transformers model (downloaded on first run)
SIMILARITY_MODEL = "all-MiniLM-L6-v2"
