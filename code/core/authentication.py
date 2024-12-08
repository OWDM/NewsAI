import streamlit as st
import hashlib
from datetime import datetime, timedelta
import json
import base64
import os

def get_auth_token():
    """Generate a unique authentication token based on user session"""
    user_agent = st.context.headers.get('User-Agent', '')
    unique_id = f"{user_agent}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.sha256(unique_id.encode()).hexdigest()[:16]

@st.cache_data(ttl=24*60*60)
def validate_auth_token(token):
    """Validate the authentication token"""
    return True if token else False

def authenticate():
    """Handle user authentication with session persistence"""
    
    # Read logo file once and store the base64 string
    logo_base64 = base64.b64encode(open(os.path.join("static", "logo512.png"), "rb").read()).decode()
    
    # Initialize authentication state if not already set
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        auth_token = st.query_params.get("auth_token", None)
        if auth_token and validate_auth_token(auth_token):
            st.session_state.authenticated = True
    
    # Sidebar content - ONLY ONE HEADER
    with st.sidebar:
        # Custom title with logo - removing the title text
        st.markdown(f"""
            <style>
                .sidebar-header {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    padding: 1rem 0;
                    margin-bottom: 1rem;
                }}
                .sidebar-logo {{
                    width: 80px;
                    height: 80px;
                    transition: all 0.3s ease;
                }}
                .sidebar-logo:hover {{
                    transform: scale(1.1);
                    filter: drop-shadow(0 0 5px rgba(0,0,0,0.2));
                }}
            </style>
            <div class="sidebar-header">
                <img src="data:image/png;base64,{logo_base64}" class="sidebar-logo" alt="NewsAI Logo">
            </div>
        """, unsafe_allow_html=True)
        
        # Welcome message - shown for both authenticated and non-authenticated users
        st.markdown("""
        **Welcome to NewsAI!**
        
        To get started, simply paste the text of an article or enter its URL.
        """)
        
        if not st.session_state.authenticated:
            st.markdown("---")
            
            # Access control section
            st.header("🔒 Access Control")
            passcode_input = st.text_input("Enter Passcode", type="password")
            
            valid_passcodes = ["1234", "SDAIA2019"]
            remember_me = st.checkbox("Remember me", value=True)
            
            if st.button("Submit Passcode", use_container_width=True):
                if passcode_input in valid_passcodes:
                    st.session_state.authenticated = True
                    
                    if remember_me:
                        auth_token = get_auth_token()
                        st.query_params["auth_token"] = auth_token
                    
                    st.success("Access Granted! ✅")
                    st.rerun()
                else:
                    st.error("Incorrect passcode ❌")
                    st.session_state.authenticated = False
        else:
            st.markdown("---")
            st.success("Authenticated ✅")
            st.markdown('<div style="min-height: 20px;"></div>', unsafe_allow_html=True)
            
            if st.button("LOGOUT", type="secondary", use_container_width=True):
                st.session_state.authenticated = False
                st.query_params.clear()
                st.rerun()