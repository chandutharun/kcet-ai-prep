"""
Configuration settings for KCET AI Prep - WITH CS + ELECTRONICS
"""

# Database paths
DATABASE_PATH = "kcet_progress.sqlite"
CHROMA_PATH = "./chroma_db"
PDF_FOLDER = "./pdfs/ncert"

# Ollama models
ENGLISH_MODEL = "llama3.1:8b"
KANNADA_MODEL = "mashriram/sarvam-1:latest"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # ← FAST EMBEDDING!

# RAG settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 4  # Number of chunks to retrieve

# LLM settings
TEMPERATURE = 0.3
TOP_K_LLM = 40
TOP_P = 0.9

# Subjects (ADDED Computer Science + Electronics)
SUBJECTS = [
    "Physics",
    "Chemistry",
    "Mathematics",
    "Biology",
    "Computer Science",  # ← ADDED
    "Electronics",        # ← ADDED
    "PYQ"
]

# Subject folder mapping (for PDF loading)
SUBJECT_FOLDER_MAP = {
    "physics": "Physics",
    "chemistry": "Chemistry",
    "maths": "Mathematics",
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "biology": "Biology",
    "cs": "Computer Science",          # ← ADDED
    "computer": "Computer Science",     # ← ADDED
    "computer science": "Computer Science",  # ← ADDED
    "computer-science": "Computer Science",  # ← ADDED
    "electronics": "Electronics",       # ← ADDED
    "electonics": "Electronics",        # ← ADDED (typo fix)
    "pyq": "PYQ",
    "previous year": "PYQ"
}
