import streamlit as st
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid

from src.questions import questions
from src.session import InsuranceChatbotSession
from src.database import (
    init_database, create_session, save_message, 
    update_session_data, complete_session
)

# Load environment variables
load_dotenv()

# Validate OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ **Error: OPENAI_API_KEY not found!**")
    st.info("""
    Please create a `.env` file in the project root with your OpenAI API key:
```
    OPENAI_API_KEY=sk-proj-your-key-here
```
    
    Then restart the application.
    """)
    st.stop()

if not api_key.startswith("sk-"):
    st.error("❌ **Error: Invalid OpenAI API key format!**")
    st.info("OpenAI API keys should start with 'sk-'")
    st.stop()

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="Insurance Survey Chatbot",
    page_icon="🚗",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .stTextInput input {
        font-size: 16px;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .bot-message {
        background-color: #f0f2f6;
    }
    .user-message {
        background-color: #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = InsuranceChatbotSession(questions)
    st.session_state.chat_history = []
    st.session_state.session_id = str(uuid.uuid4())
    
    # Create session in database
    create_session(st.session_state.session_id)
    
    # Add initial bot message
    first_question = st.session_state.session.get_next_question()
    first_message = first_question['text']
    
    st.session_state.chat_history.append({
        "role": "bot",
        "content": first_message
    })
    
    # Save to database
    save_message(st.session_state.session_id, "bot", first_message)

# Title
st.title("🚗 Insurance Survey Chatbot")
st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
st.markdown("---")

# Chat history display
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        if message['role'] == 'bot':
            st.markdown(f'<div class="chat-message bot-message"><b>🤖 Bot:</b><br>{message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message user-message"><b>👤 You:</b><br>{message["content"]}</div>', 
                       unsafe_allow_html=True)

# Input area
with st.form(key='message_form', clear_on_submit=True):
    user_input = st.text_input("Your answer:", key="user_input", label_visibility="collapsed")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    # Add user message to chat
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # SAVE USER MESSAGE TO DATABASE
    save_message(st.session_state.session_id, "user", user_input)
    
    # ADD LOADING INDICATOR
    with st.spinner("🤖 Thinking..."):
        # Process response
        response = st.session_state.session.process_response(user_input)
        
    # Handle response - check for both 'message' and 'error' keys
    bot_message = response.get('message') or response.get('error', 'Sorry, something went wrong.')
    
    # Add bot response
    st.session_state.chat_history.append({
        "role": "bot",
        "content": bot_message
    })
    
    # SAVE BOT MESSAGE TO DATABASE
    save_message(st.session_state.session_id, "bot", bot_message)
    
    # Update session data with collected info
    current_data = st.session_state.session.compile_final_data()
    update_session_data(st.session_state.session_id, current_data)
    
    # Check if survey is complete
    if response.get('done'):
        if 'data' in response:
            # SAVE FINAL COMPLETED DATA
            complete_session(st.session_state.session_id, response['data'])
            
            st.success("✅ Survey Complete!")
            st.info(f"💾 Session saved: {st.session_state.session_id}")
            
            # Display collected data
            with st.expander("📊 View Collected Data", expanded=True):
                st.json(response['data'])
            
            # Download button
            json_data = json.dumps(response['data'], indent=2)
            st.download_button(
                label="📥 Download Survey Data",
                data=json_data,
                file_name=f"insurance_survey_{st.session_state.session_id}.json",
                mime="application/json"
            )
            
            # Restart button
            if st.button("🔄 Start New Survey"):
                st.session_state.session = InsuranceChatbotSession(questions)
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                
                create_session(st.session_state.session_id)
                
                first_question = st.session_state.session.get_next_question()
                first_message = first_question['text']
                
                st.session_state.chat_history.append({
                    "role": "bot",
                    "content": first_message
                })
                
                save_message(st.session_state.session_id, "bot", first_message)
                st.rerun()
    
    st.rerun()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This chatbot collects insurance information including:")
    st.write("- Personal details")
    st.write("- Vehicle information (validated via NHTSA)")
    st.write("- License information")
    
    st.markdown("---")
    
    st.header("🎯 Progress")
    current_q = st.session_state.session.get_next_question()
    if current_q:
        progress = (st.session_state.session.current_index / len(questions)) * 100
        st.progress(progress / 100)
        st.write(f"{int(progress)}% complete")
    
    st.markdown("---")
    
    if st.button("🔄 Reset Survey"):
        st.session_state.session = InsuranceChatbotSession(questions)
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        
        create_session(st.session_state.session_id)
        
        first_question = st.session_state.session.get_next_question()
        first_message = first_question['text']
        
        st.session_state.chat_history.append({
            "role": "bot",
            "content": first_message
        })
        
        save_message(st.session_state.session_id, "bot", first_message)
        st.rerun()