"""
Helper functions - PRODUCTION READY
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.models import get_english_llm, get_kannada_llm


def extract_subject_from_folder(folder_name: str) -> str:
    """Extract subject from folder name (better than filename)"""
    folder_lower = folder_name.lower()
    
    subject_map = {
        "physics": "Physics",
        "chemistry": "Chemistry",
        "maths": "Mathematics",
        "math": "Mathematics",
        "mathematics": "Mathematics",
        "biology": "Biology",
        "cs": "Computer Science",
        "computer science": "Computer Science",
        "computer": "Computer Science",
        "electronics": "Electronics",
        "electonics": "Electronics",
        "pyq": "PYQ",
        "previous year": "PYQ"
    }
    
    return subject_map.get(folder_lower, "Unknown")


def extract_subject(filename: str) -> str:
    """Extract subject from PDF filename (fallback)"""
    filename_lower = filename.lower()
    
    if 'physics' in filename_lower:
        return 'Physics'
    elif 'chemistry' in filename_lower:
        return 'Chemistry'
    elif 'maths' in filename_lower or 'mathematics' in filename_lower:
        return 'Mathematics'
    elif 'biology' in filename_lower:
        return 'Biology'
    elif 'cs' in filename_lower or 'computer' in filename_lower:
        return 'Computer Science'
    elif 'electronics' in filename_lower:
        return 'Electronics'
    else:
        return 'Unknown'


def translate_to_kannada(english_text: str) -> str:
    """Translate English text to Kannada - FIXED"""
    try:
        llm_kannada = get_kannada_llm()
        
        translation_prompt = """Translate the following text to Kannada.
Keep technical terms in English (with Kannada script in parentheses).
Be accurate and natural.

English Text:
{text}

Kannada Translation (with English terms):
"""
        
        prompt = ChatPromptTemplate.from_template(translation_prompt)
        chain = prompt | llm_kannada | StrOutputParser()
        
        return chain.invoke({"text": english_text})
    except Exception as e:
        print(f"Translation error: {e}")
        return english_text  # Return original if translation fails


def explain_like_12(text: str) -> str:
    """Simplify explanation for 12-year-old"""
    llm_english = get_english_llm()
    
    simplifier_prompt = """Explain this to a 12-year-old student.
Use simple language, analogies, and everyday examples.
Keep it fun and easy to understand.

Original Text:
{text}

Simple Explanation (like teaching a child):
"""
    
    prompt = ChatPromptTemplate.from_template(simplifier_prompt)
    chain = prompt | llm_english | StrOutputParser()
    
    return chain.invoke({"text": text})


def get_hybrid_response(english_answer: str) -> str:
    """Get English + Kannada hybrid response"""
    kannada_answer = translate_to_kannada(english_answer)
    
    return f"""
**English:**
{english_answer}

---

**ಕನ್ನಡದಲ್ಲಿ (In Kannada):**
{kannada_answer}

---

**Key Terms:**
• Action = ಆಕ್ಷನ್ (ಪ್ರವೃತ್ತಿ)
• Reaction = ರೆಸಪಾಕ್ಸ್ (ಪ್ರತಿಕ್ರಿಯೆ)
"""


def is_simple_question(question: str) -> bool:
    """Check if question is simple (hi, hello, etc.)"""
    simple_patterns = [
        'hi', 'hello', 'hey', 'good morning', 'good evening',
        'how are you', 'what is your name', 'who are you',
        'thanks', 'thank you', 'bye', 'see you'
    ]
    question_lower = question.lower().strip()
    return any(pattern in question_lower for pattern in simple_patterns)


def is_pyy_question(question: str) -> bool:
    """Check if question is about PYQ"""
    pyq_patterns = [
        'pyq', 'previous year', 'question paper', '2024', '2023', '2022',
        'answer key', 'exam paper', 'kcet paper', 'past year'
    ]
    question_lower = question.lower()
    return any(pattern in question_lower for pattern in pyq_patterns)


def extract_topic(question: str) -> str:
    """Extract topic from question"""
    keywords = {
        "motion": "Mechanics",
        "force": "Mechanics",
        "energy": "Energy & Work",
        "power": "Energy & Work",
        "electricity": "Electricity",
        "magnetism": "Magnetism",
        "optics": "Optics",
        "thermo": "Thermodynamics",
        "organic": "Organic Chemistry",
        "integration": "Calculus",
        "derivative": "Calculus",
        "algebra": "Algebra",
        "geometry": "Geometry",
        "trigonometry": "Trigonometry",
        "cell": "Cell Biology",
        "dna": "Genetics",
        "evolution": "Evolution"
    }
    
    question_lower = question.lower()
    for keyword, topic in keywords.items():
        if keyword in question_lower:
            return topic
    
    return "General"
