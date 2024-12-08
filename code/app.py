import streamlit as st
from core.authentication import authenticate
from core.interface import display_interface
from core.state import initialize_session_state
from utils.css_loader import load_css
from pathlib import Path

def main():
    load_css()
    authenticate()
    initialize_session_state()
    display_interface()

if __name__ == "__main__":
    # Get the favicon path
    favicon_path = Path("static/logo512.png")
    
    # Configure the page with favicon if it exists, otherwise use default settings
    if favicon_path.exists():
        st.set_page_config(
            page_title="NewsAI",  # You can customize this
            page_icon=str(favicon_path),
            layout="wide"
        )
    else:
        st.set_page_config(layout="wide")
        
    main()