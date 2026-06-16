"""
RAG pipeline with ChromaDB + Kannada Translation
"""


import warnings
import logging
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough



from src.config import CHROMA_PATH, PDF_FOLDER, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, EMBEDDING_MODEL, SUBJECT_FOLDER_MAP



warnings.filterwarnings("ignore", category=Warning)
logging.getLogger("pypdf").setLevel(logging.ERROR)




def get_embeddings():
    """Get embeddings"""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )




def load_pdfs():
    """Load PDFs"""
    docs = []
    
    PDF_PATH = Path(PDF_FOLDER)
    
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF folder not found: {PDF_PATH}")
    
    pdf_files = list(PDF_PATH.rglob("*.pdf"))
    
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in: {PDF_FOLDER}")
    
    for pdf_file in pdf_files:
        print(f"Loading: {pdf_file}")
        
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            documents = loader.load()
            
            if len(documents) == 0:
                continue
            
            folder_path = pdf_file.parent
            folder_name = folder_path.name.lower()
            
            subject = SUBJECT_FOLDER_MAP.get(folder_name, "Unknown")
            
            for doc in documents:
                doc.metadata['source'] = pdf_file.name
                doc.metadata['subject'] = subject
                doc.metadata['page'] = doc.metadata.get('page', 0)
            
            docs.extend(documents)
            print(f"  ✓ Loaded {len(documents)} pages ({subject})")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nTotal: {len(docs)} pages from {len(pdf_files)} PDFs")
    return docs




def create_vectorstore(docs):
    """Create vector store"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    splits = text_splitter.split_documents(docs)
    print(f"Total chunks: {len(splits)}")
    
    BATCH_SIZE = 5000
    embedding_func = get_embeddings()
    
    print("Creating embeddings...")
    
    first_batch = splits[:BATCH_SIZE]
    vectorstore = Chroma.from_documents(
        documents=first_batch,
        embedding=embedding_func,
        collection_name="kcet_ncert",
        persist_directory=CHROMA_PATH
    )
    print(f"  ✓ Batch 1: {len(first_batch)} chunks")
    
    for i in range(BATCH_SIZE, len(splits), BATCH_SIZE):
        batch = splits[i:i + BATCH_SIZE]
        vectorstore.add_documents(batch)
        print(f"  ✓ Batch {i//BATCH_SIZE + 2}: {len(batch)} chunks")
    
    print("✓ ChromaDB index created!")
    return vectorstore




def create_rag_pipeline(vectorstore, llm, subject_filter=None):
    """Create RAG pipeline - FIXED with BETTER identity detection"""
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K}
    )
    
    # FIXED: More aggressive name/identity detection in prompt
    PROMPT_TEMPLATE = """You are a KCET exam preparation assistant.

Subject: {subject}
Textbook Content:
{context}
Question: {question}

IMPORTANT INSTRUCTIONS - READ CAREFULLY:

STEP 1: Check if question is about YOUR identity:
- "what is your name", "who are you", "tell me your name" → NOT_FOUND_IN_TEXTBOOK
- Greetings ("hi", "hello") → NOT_FOUND_IN_TEXTBOOK
- Personal info questions (name, age, birthday) → NOT_FOUND_IN_TEXTBOOK

STEP 2: Check if textbook HAS the answer:
- If textbook DOES NOT contain answer → Output: NOT_FOUND_IN_TEXTBOOK
- If context contains "My name is [person]" (like "Rohan", "John") → NOT about you → NOT_FOUND_IN_TEXTBOOK
- If question is about YOU (the assistant) → NOT_FOUND_IN_TEXTBOOK

STEP 3: If found in textbook:
- Provide clear, detailed, exam-relevant answer
- Include formulas, examples, explanations
- Write in KCET exam style

DO NOT:
- Say "My name is Rohan" or any person's name
- Talk about yourself as a human
- Use personal info from textbook (not about KCET)
- Include names of people unless related to the topic (like "Isaac Newton")

Answer:
"""

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    rag_pipeline = (
        {"context": retriever, "question": RunnablePassthrough(), "subject": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_pipeline




def initialize_rag(subject_filter=None):
    """Initialize RAG"""
    from src.models import get_english_llm
    
    vectorstore_path = Path(CHROMA_PATH)
    
    if vectorstore_path.exists():
        print("Loading existing ChromaDB index...")
        
        vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            collection_name="kcet_ncert",
            embedding_function=get_embeddings()
        )
        
        chunks_count = len(vectorstore.get()['ids'])
        print(f"Loaded {chunks_count} chunks from ChromaDB!")
        
        print("\nTesting retrieval:")
        test_docs = vectorstore.similarity_search("Newton", k=5)
        print(f"Found {len(test_docs)} docs for 'Newton'")
        if test_docs:
            print(f"First: {test_docs[0].metadata.get('subject')} - {test_docs[0].page_content[:100]}")
    else:
        print("Loading PDFs (first time)...")
        docs = load_pdfs()
        print("Creating vector store...")
        vectorstore = create_vectorstore(docs)
    
    llm = get_english_llm()
    
    print("Creating RAG pipeline...")
    rag_pipeline = create_rag_pipeline(vectorstore, llm, subject_filter)
    
    return {'vectorstore': vectorstore, 'rag_pipeline': rag_pipeline}




def translate_to_kannada(english_text: str) -> str:
    """Translate English to Kannada - translate ALL words including abbreviations"""
    from src.models import get_kannada_llm
    
    try:
        llm = get_kannada_llm()
        
        max_chunk = 700
        if len(english_text) <= max_chunk:
            prompt = f"""Translate this English text to Kannada completely.
CRITICAL INSTRUCTIONS:
- Translate EVERY word to Kannada
- Abbreviations (MCQ, ATP, NADPH, CO2, O2) → write in Kannada script
- Technical terms → keep in English ONLY if no Kannada word exists
- Numbers, dates, formulas → keep as is
- Regular words → translate to Kannada
- NO English words in output (except formulas/numbers)

English: {english_text}

Kannada (complete translation in Kannada script only):"""
            
            translation = llm.invoke(prompt)
            return translation.strip()
        else:
            chunks = [english_text[i:i + max_chunk] for i in range(0, len(english_text), max_chunk)]
            
            translations = []
            for chunk in chunks:
                prompt = f"""Translate this English text to Kannada completely.
CRITICAL INSTRUCTIONS:
- Translate EVERY word to Kannada
- Abbreviations (MCQ, ATP, NADPH, CO2, O2) → write in Kannada script
- Technical terms → keep in English ONLY if no Kannada word exists
- Numbers, dates, formulas → keep as is
- Regular words → translate to Kannada
- NO English words in output (except formulas/numbers)

English: {chunk}

Kannada (complete translation in Kannada script only):"""
                
                translation = llm.invoke(prompt)
                translations.append(translation.strip())
            
            return " ".join(translations)
        
    except Exception as e:
        print(f"Kannada translation error: {e}")
        return "ಈ ವಿಷಯ KCET ಪರೀಕ್ಷೆಗೆ ಪ್ರಮುಖ."

def is_gibberish(text: str) -> bool:
    """Check if text is gibberish"""
    import re
    
    text = text.lower().strip()
    
    if len(text) < 2:
        return True
    
    if re.match(r"^[\W_]+$", text):
        return True
    
    return False


def get_general_kcet_answer(prompt: str, subject: str) -> str:
    """Get AI-generated answer (when not in NCERT) - WITH Computer Science and Electronics"""
    from src.models import get_english_llm
    
    llm = get_english_llm()
    
    base_identity = "You are an AI KCET exam preparation assistant. You do NOT have a personal name, age, birthday, or human identity. "
    
    # FIXED: Added Computer Science and Electronics
    subject_prompts = {
        "Physics": base_identity + f"Teach KCET Physics about: {prompt}.\nInclude formulas, concepts, examples.",
        
        "Chemistry": base_identity + f"Teach KCET Chemistry about: {prompt}.\nInclude reactions, mechanisms, examples.",
        
        "Mathematics": base_identity + f"Teach KCET Mathematics about: {prompt}.\nInclude formulas, step-by-step solutions, examples.",
        
        "Biology": base_identity + f"Teach KCET Biology about: {prompt}.\nInclude processes, diagrams (described), examples.",
        
        "Computer Science": base_identity + f"Teach KCET Computer Science about: {prompt}.\nInclude code examples, algorithms, programming concepts, data structures.",
        
        "Electronics": base_identity + f"Teach KCET Electronics about: {prompt}.\nInclude circuits, components, semiconductors, applications, logic gates.",
        
        "PYQ": base_identity + f"Provide KCET previous year question info about: {prompt}.\nInclude typical patterns and answer strategies.",
        
        "All": base_identity + f"Provide general KCET exam info about: {prompt}.\nInclude relevant concepts, examples, exam tips."
    }
    
    full_prompt = subject_prompts.get(subject, subject_prompts["All"])
    
    try:
        answer = llm.invoke(full_prompt)
        return answer
    except Exception as e:
        return f"Unfortunately, I couldn't generate an answer. Error: {str(e)}"


def get_hybrid_response(english_answer: str, kannada_translation: str) -> str:
    """Combine English answer with Kannada translation"""
    return f"""{english_answer}


📖 **ಕನ್ನಡದಲ್ಲಿ ಸಾರಾಂಶ**:


{kannada_translation}
"""