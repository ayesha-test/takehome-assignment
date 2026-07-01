import os

BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://november7-730026606190.europe-west1.run.app",
).rstrip("/")

MOVIES_PATH = "/movies/"
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
MAX_RESPONSE_TIME_SECONDS = float(os.getenv("MAX_RESPONSE_TIME_SECONDS", "2.0"))

# Catalogue-wide fetch uses a limit above the known dataset size (35 as of exploration).
CATALOGUE_FETCH_LIMIT = int(os.getenv("CATALOGUE_FETCH_LIMIT", "100"))
