import os

# Maximum upload size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Document types currently supported by the analysis route
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Optional API key for any remaining API-key-protected endpoints
GHOSTTEXT_API_KEY = os.getenv("GHOSTTEXT_API_KEY", "")