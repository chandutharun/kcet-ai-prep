"""
KCET AI Prep - Source Package
"""


from src.config import DATABASE_PATH, CHROMA_PATH, PDF_FOLDER
from src.database import init_database, track_question, get_analytics
from src.models import get_models, get_english_llm, get_kannada_llm
from src.rag import (
    initialize_rag,
    create_rag_pipeline,
    translate_to_kannada,
    get_general_kcet_answer,
    get_hybrid_response,
    is_gibberish
)
from src.utils import extract_subject, explain_like_12


__all__ = [
    'DATABASE_PATH', 'CHROMA_PATH', 'PDF_FOLDER',
    'init_database', 'track_question', 'get_analytics',
    'get_models', 'get_english_llm', 'get_kannada_llm',
    'initialize_rag', 'create_rag_pipeline',
    'extract_subject', 'translate_to_kannada', 'explain_like_12',
    'get_hybrid_response', 'is_gibberish', 'get_general_kcet_answer'
]