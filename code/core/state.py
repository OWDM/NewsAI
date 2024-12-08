#state.py

import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    initial_states = {
        'processing_complete': False,
        'highlighting_complete': False,
        'highlighting_in_progress': False,
        'authenticated': False,
        'just_copied': False,
        'article': '',
        'summary': '',
        'arabic_summary': '',
        'highlighted_article': '',
        'highlighted_summary': '',
        'matched_sentences': []
    }

    for key, initial_value in initial_states.items():
        if key not in st.session_state:
            st.session_state[key] = initial_value