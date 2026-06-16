"""
Ollama model initialization
"""

from langchain_ollama import OllamaLLM
from src.config import ENGLISH_MODEL, KANNADA_MODEL, TEMPERATURE, TOP_K_LLM, TOP_P


def get_english_llm():
    """Get English LLM for RAG"""
    return OllamaLLM(
        model=ENGLISH_MODEL,
        temperature=TEMPERATURE,
        top_k=TOP_K_LLM,
        top_p=TOP_P
    )


def get_kannada_llm():
    """Get Kannada LLM for translation"""
    return OllamaLLM(
        model=KANNADA_MODEL,
        temperature=TEMPERATURE,
        top_k=TOP_K_LLM,
        top_p=TOP_P
    )


def get_models():
    """Get all LLM models"""
    return {
        'english': get_english_llm(),
        'kannada': get_kannada_llm()
    }
