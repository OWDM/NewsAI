import streamlit as st
import time
from langchain_utils import extract_key_info, generate_summary, translate_to_arabic

def process_article(article, progress_bar, status_text):
    """Process the article and update progress"""
    try:
        # Step 1: Extract key information (slowest fill - longest step)
        status_text.text("Reading... 📚")
        while True:
            for i in range(0, 40):
                progress_bar.progress(i)
                time.sleep(0.25)  # Slower speed for longer first step (increased from 0.15)
            key_info = extract_key_info(article)
            break

        # Step 2: Generate summary (medium fill speed)
        status_text.text("Thinking... 🧠")
        while True:
            for i in range(40, 70):
                progress_bar.progress(i)
                time.sleep(0.15)  # Medium speed for second step (increased from 0.08)
            summary = generate_summary(article, key_info)
            break

        # Step 3: Translate to Arabic (fastest fill - shortest step)
        status_text.text("Writing... 🖊️")
        while True:
            for i in range(70, 100):
                progress_bar.progress(i)
                time.sleep(0.08)  # Faster speed for final step (increased from 0.04)
            arabic_summary = translate_to_arabic(summary)
            break

        progress_bar.progress(100)
        status_text.text("Done! 🎉")
        time.sleep(0.2)

        # Save results to session state
        st.session_state.update({
            'article': article,
            'summary': summary,
            'arabic_summary': arabic_summary,
            'processing_complete': True,
            'highlighting_in_progress': True
        })

        return {'success': True}

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }