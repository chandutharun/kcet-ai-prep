"""
Streamlit UI for KCET AI Prep
"""


import streamlit as st
from src.rag import initialize_rag
from src.config import DATABASE_PATH, TOP_K
from src.database import init_database, login_student, get_chat_history, add_to_chat_history, get_analytics



def main():
    """Main app"""
    
    init_database()
    
    st.set_page_config(
        page_title="KCET AI Prep",
        page_icon="🎓",
        layout="wide"
    )
    
    if "student_id" not in st.session_state or st.session_state.student_id == "":
        st.title("🎓 KCET AI Prep - Student Login")
        
        student_id = st.text_input("Student ID", placeholder="e.g., KCET2024001")
        student_name = st.text_input("Your Name", placeholder="e.g., Rajesh Kumar")
        
        if st.button("Login"):
            if student_id and student_name:
                result = login_student(student_id, student_name)
                st.session_state.student_id = result["student_id"]
                st.session_state.student_name = result["name"]
                st.success(result["message"])
                st.rerun()
            else:
                st.error("Student ID and Name required!")
        
        st.info("New Student? Enter any ID and name - history saved!")
        return
    
    app()



def app():
    """Main app"""
    
    student_id = st.session_state.student_id
    student_name = st.session_state.student_name
    
    st.title("🎓 KCET AI Prep Assistant")
    st.markdown(f"**Welcome, {student_name}!** | NCERT Q&A | English + Kannada")
    
    with st.sidebar:
        st.header("👤 Profile")
        st.text("ID: " + student_id)
        st.text("Name: " + student_name)
        
        st.divider()
        
        # stats = get_analytics(student_id)
        # st.metric("Questions Asked", stats['total_questions'])
        
        # st.divider()
        
        language = st.selectbox(
            "Language",
            ["English + Kannada (Hybrid)", "English", "Kannada"],
            index=0
        )
        
        # FIXED: Added Computer Science and Electronics
        subject = st.selectbox(
            "Subject",
            ["All", "Physics", "Chemistry", "Mathematics", "Biology", "Computer Science", "Electronics"],
            index=0
        )
        
        st.divider()
        
        st.info("🤖 Models: llama3.1 + sarvam-1")
        st.success("📡 100% Offline")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("📖 View History", use_container_width=True):
            st.session_state.show_history = True
            st.rerun()
        
        if st.session_state.get('show_history', False):
            st.divider()
            st.subheader("📖 Chat History")
            history = get_chat_history(student_id)
            for msg in history[:20]:
                st.markdown(f"**{msg['role']}**: {msg['content'][:80]}...")
            
            if st.button("Back to Chat", use_container_width=True):
                st.session_state.show_history = False
                st.rerun()
        
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            st.session_state.student_id = ""
            st.session_state.student_name = ""
            st.rerun()
    
    if "rag_system" not in st.session_state:
        with st.status("Loading PDFs...", expanded=True):
            st.session_state.rag_system = initialize_rag(subject_filter=None)
        st.success("✅ Ready!")
    
    st.divider()
    
    if "messages" not in st.session_state:
        st.session_state.messages = get_chat_history(student_id)
    
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])
    
    st.divider()
    
    if prompt := st.chat_input("Ask about NCERT..."):
        handle_question(prompt, st.session_state, subject, language, student_id)



def handle_question(prompt, session_state, selected_subject, language, student_id):
    """Handle question - FIXED with name cleanup and better disclaimers"""
    
    session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    # FIX 1: Check for name/identity questions FIRST (before RAG)
    name_questions = [
        "what is your name", 
        "your name", 
        "who are you", 
        "tell me your name", 
        "what name are you",
        "are you",
        "yourself"
    ]
    
    if any(q in prompt.lower() for q in name_questions):
        answer = """
👋 I'm your **KCET AI Prep Assistant**!

I don't have a personal name - I'm an AI assistant here to help you prepare for KCET exams using NCERT textbooks.

You can ask me:
- Physics questions (Newton's laws, motion, etc.)
- Chemistry questions (reactions, equations, etc.)
- Biology questions (photosynthesis, cells, etc.)
- Mathematics problems
- Computer Science questions (programming, algorithms, etc.)
- Electronics questions (circuits, semiconductors, etc.)
- Previous year KCET questions

✅ **From NCERT Textbook** | For textbook questions
⚠️ **AI-generated** | For other questions (may not be 100% accurate)
"""
        st.markdown(answer)
        session_state.messages.append({"role": "assistant", "content": answer})
        add_to_chat_history(student_id, "assistant", answer)
        return
    
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            
            simple = prompt.lower().strip() in ['hi', 'hello', 'hey']
            
            if simple:
                st.markdown("""
👋 Hello! I'm your **KCET AI Prep Assistant**!

I help you study from **NCERT textbooks** (100% accurate).

If not found in NCERT → I'll provide AI-generated info

✅ **From NCERT Textbook** | For textbook questions
⚠️ **AI-generated** | For other questions
""")
                session_state.messages.append({"role": "assistant", "content": "Hello!"})
                add_to_chat_history(student_id, "assistant", "Hello!")
                return
            
            rag_pipeline = session_state.rag_system['rag_pipeline']
            vectorstore = session_state.rag_system['vectorstore']
            
            is_pyq = any(word in prompt.lower() for word in [
                'pyq', 'previous year', 'question paper', 'kcet'
            ])
            
            recent_users = [m["content"] for m in session_state.messages[-3:] if m["role"] == "user"]
            
            if is_pyq or simple or len(recent_users) < 2 or recent_users[-1] == recent_users[-2]:
                context = ""
            else:
                context = "Previous: " + recent_users[-2] + "\n\n"
            
            if is_pyq:
                if "physics" in prompt.lower():
                    search_subject = "PYQ Physics"
                elif "chemistry" in prompt.lower():
                    search_subject = "PYQ Chemistry"
                elif "biology" in prompt.lower():
                    search_subject = "PYQ Biology"
                elif "math" in prompt.lower() or "maths" in prompt.lower():
                    search_subject = "PYQ Mathematics"
                else:
                    search_subject = "PYQ"
                
                test_docs = vectorstore.similarity_search(prompt, k=TOP_K)
                test_docs = [d for d in test_docs if d.metadata.get('subject', '').startswith('PYQ')]
            else:
                if selected_subject != "All":
                    test_docs = vectorstore.similarity_search(prompt, k=TOP_K)
                    test_docs = [d for d in test_docs if d.metadata.get('subject') == selected_subject]
                else:
                    test_docs = vectorstore.similarity_search(prompt, k=TOP_K)
            
            if test_docs:
                source = test_docs[0].metadata.get('source', 'Unknown')
                page = test_docs[0].metadata.get('page', 'Unknown')
                subj = test_docs[0].metadata.get('subject', 'Unknown')
                
                st.caption(f"📚 {source} | Page {page} | {subj}")
                
                answer = rag_pipeline.invoke(f"{context}{prompt}", subject=subj)
                
                # FIX 2: CLEAN answer - remove "My name is X" and "I'm X" sentences
                import re
                answer = re.sub(r'My name is [A-Za-z]+\.', '', answer)
                answer = re.sub(r'My name is [A-Za-z]+[,]', '', answer)
                answer = re.sub(r'I\'m [A-Za-z]+[,.]', '', answer)
                answer = re.sub(r'I am [A-Za-z]+[,.]', '', answer)
                answer = re.sub(r'\n\s*\n', '\n\n', answer)
                answer = answer.strip()
                
                if "NOT_FOUND_IN_TEXTBOOK" in answer.upper():
                    test_docs = []
                else:
                    answer += f"\n\n✅ **From NCERT Textbook** | {source} | Page {page} | {subj}\n"
            
            if not test_docs:
                answer = f"""
❌ **Not found in NCERT textbooks**

I couldn't find "{prompt}" in the provided NCERT textbooks.

However, here's helpful general information for KCET preparation:

⚠️ **AI-generated** | May not be 100% accurate | Verify with textbook/teacher
"""
                
                from src.rag import get_general_kcet_answer
                ai_answer = get_general_kcet_answer(prompt, selected_subject)
                
                answer += ai_answer
                
                answer += "\n\n⚠️ **AI-generated** | Not from NCERT | Please verify with your textbook/teacher\n"
            
            # Extract tag for Kannada section
            tag = ""
            if "✅ **From NCERT Textbook**" in answer:
                tag = "\n\n✅ **From NCERT Textbook** | NCERT-based answer"
            elif "⚠️ **AI-generated**" in answer:
                tag = "\n\n⚠️ **AI-generated** | May not be 100% accurate | Verify with textbook"
            
            answer_lines = answer.split('\n---')
            actual_answer = answer_lines[0].strip()
            
            if language == "English + Kannada (Hybrid)":
                from src.rag import translate_to_kannada
                kannada_full = translate_to_kannada(actual_answer)
                
                # Tag AFTER Kannada translation
                answer = f"""
{actual_answer}

📖 **ಕನ್ನಡದಲ್ಲಿ ಸಾರಾಂಶ**:

{kannada_full}

{tag}
"""
            
            elif language == "Kannada":
                from src.rag import translate_to_kannada
                answer = translate_to_kannada(actual_answer)
                answer = f"{answer}\n\n{tag}"
            
            st.markdown(answer)
            session_state.messages.append({"role": "assistant", "content": answer})
            add_to_chat_history(student_id, "assistant", answer)


if __name__ == "__main__":
    main()