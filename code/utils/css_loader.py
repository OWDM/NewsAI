import streamlit as st
import os

def load_css():
    """Load all CSS files from the styles directory"""
    css_files = [
        'base.css',
        'typography.css',
        'layout.css',
        'components.css',
        'buttons.css',
        'form-controls.css',
        'animations.css',
        'responsive.css',
    ]
    
    combined_css = ""
    styles_dir = "styles"
    
    for css_file in css_files:
        file_path = os.path.join(styles_dir, css_file)
        try:
            with open(file_path) as f:
                combined_css += f.read()
        except Exception as e:
            st.error(f"Failed to load {css_file}: {str(e)}")
    
    st.markdown(f'<style>{combined_css}</style>', unsafe_allow_html=True)