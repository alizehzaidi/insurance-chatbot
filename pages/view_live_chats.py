import streamlit as st
from src.database import init_database, get_all_sessions, get_session_details, get_live_chat_transcript

# Initialize database if it doesn't exist
init_database()

st.set_page_config(page_title="Live Chat Monitor", page_icon="📊", layout="wide")

st.title("📊 Live Chat Monitor")
st.markdown("View all chat sessions and their real-time transcripts")

# Auto-refresh
if st.button("🔄 Refresh"):
    st.rerun()

sessions = get_all_sessions()

if not sessions:
    st.info("No chat sessions yet.")
else:
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    total_sessions = len(sessions)
    in_progress = sum(1 for s in sessions if s[3] == 'in_progress')
    completed = sum(1 for s in sessions if s[3] == 'completed')
    
    col1.metric("Total Sessions", total_sessions)
    col2.metric("In Progress", in_progress)
    col3.metric("Completed", completed)
    
    st.markdown("---")
    
    # Filter
    status_filter = st.selectbox("Filter by status", ["All", "in_progress", "completed"])
    
    # Display sessions
    for session in sessions:
        session_id, started_at, completed_at, status, full_name, email, zip_code = session
        
        if status_filter != "All" and status != status_filter:
            continue
        
        status_emoji = "🟢" if status == "in_progress" else "✅"
        name_display = full_name if full_name else "Anonymous"
        
        with st.expander(f"{status_emoji} {name_display} - {session_id[:8]}... ({started_at})"):
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.write("**Session Info:**")
                st.write(f"- **Status:** {status}")
                st.write(f"- **Started:** {started_at}")
                if completed_at:
                    st.write(f"- **Completed:** {completed_at}")
                if email:
                    st.write(f"- **Email:** {email}")
                if zip_code:
                    st.write(f"- **Zip:** {zip_code}")
            
            with col2:
                st.write("**Live Chat Transcript:**")
                
                # Get live transcript
                messages = get_live_chat_transcript(session_id)
                
                for timestamp, role, content in messages:
                    if role == "bot":
                        st.markdown(f"🤖 **Bot** ({timestamp}):")
                        st.info(content)
                    else:
                        st.markdown(f"👤 **User** ({timestamp}):")
                        st.success(content)
            
            # Show full details button
            if status == "completed":
                if st.button(f"View Final Data", key=f"view_{session_id}"):
                    details = get_session_details(session_id)
                    if details['final_data']:
                        st.json(details['final_data'])