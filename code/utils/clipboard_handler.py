import streamlit as st
import clipboard

def on_copy_click():
    """Handle copying the Arabic summary to clipboard"""
    summary_text = st.session_state.get("arabic_summary", "")
    clipboard.copy(summary_text)
    st.session_state.just_copied = True