import streamlit as st
from utils.highlighting import highlight_summary_and_article
from utils.article_processor import process_article
from langchain_utils import match_summary_with_article
from content_extractor import get_cleaned_article

from st_copy_to_clipboard import st_copy_to_clipboard


from urllib.parse import urlparse
import re

def display_logo_and_title():
    """Display the application title"""
    st.markdown("""
        <h1 class="title">NewsAI</h1>
        <h3 class="subtitle">Accelerating newsletter creation with AI-powered automation</h3>
    """, unsafe_allow_html=True)
    
def handle_article_input():
    """Handle article input from user"""
    content = st.text_area(
        "Enter article text or URL:",
        placeholder="Paste your article text here or enter a URL...",
        key="article_input",
        height=150
    )
    return content

def process_highlighting():
    """Process the highlighting of matched sentences"""
    try:
        matched_sentences = match_summary_with_article(
            st.session_state['article'], 
            st.session_state['summary']
        )
        highlighted_summary, highlighted_article = highlight_summary_and_article(
            st.session_state['article'],
            st.session_state['summary'],
            matched_sentences
        )
        
        st.session_state.update({
            'matched_sentences': matched_sentences,
            'highlighted_summary': highlighted_summary,
            'highlighted_article': highlighted_article,
            'highlighting_complete': True
        })
    except Exception as e:
        st.error(f"Error during highlighting: {str(e)}")

def display_content_columns(show_highlight):
    """Display the original article and English summary in columns"""
    col1, col2 = st.columns([1, 1])  # Equal width columns

    with col1:
        st.subheader("Original Article")
        content = (st.session_state["highlighted_article"] 
                   if show_highlight and st.session_state.get('highlighting_complete', False)
                   else st.session_state["article"])
        st.markdown(f'<div class="original-article-box">{content}</div>', unsafe_allow_html=True)

    with col2:
        st.subheader("English Summary")
        content = (st.session_state["highlighted_summary"]
                   if show_highlight and st.session_state.get('highlighting_complete', False)
                   else st.session_state["summary"])
        st.markdown(f'<div class="english-summary-box">{content}</div>', unsafe_allow_html=True)

def display_results():
    """Display processing results including Arabic summary and highlighting"""
    st.success("Article processed successfully!")

    # Display Arabic summary header
    st.subheader("Arabic Summary:")

    # Display Arabic summary
    st.markdown(
        f'''
        <div class="summary-box">
            {st.session_state["arabic_summary"]}
        </div>
        ''',
        unsafe_allow_html=True
    )

    # Add spacer
    st.markdown("<br>", unsafe_allow_html=True)

    # Create columns for the copy button to align it to the right
    _,_, copy_col = st.columns([1, 1,0.603])

    with copy_col:
        st_copy_to_clipboard(st.session_state["arabic_summary"])

    if st.session_state.get('just_copied', False):
        st.toast("Copied to clipboard!", icon="✅")
        st.session_state.just_copied = False

    st.divider()

    # Process highlighting automatically if not done yet
    if not st.session_state.get('highlighting_complete', False):
        with st.spinner("Processing highlights..."):
            process_highlighting()

    # Toggle switch for showing/hiding highlights
    show_highlight = st.toggle("Show Highlights", value=False, key="highlight_toggle")

    # Display content with or without highlights based on toggle
    display_content_columns(show_highlight)

def is_url(string):
    """Check if the provided string is a URL"""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def display_interface():
    """Main interface display function"""
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Limited access mode. Enter the correct passcode to unlock all features.")
        return

    # Wrap initial content in centered columns
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        display_logo_and_title()
        article_input = handle_article_input()

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Generate", type="primary"):
            if not article_input.strip():
                st.warning("Please provide an article text or URL to process.")
                return

            # Check for multiple URLs
            urls = re.findall(r'(https?://\S+)', article_input)
            if len(urls) > 1:
                st.error("Please input only one URL at a time.")
                return

            # Optional: Check for excessively long text
            word_count = len(article_input.strip().split())
            if word_count > 5000:  # Adjust the threshold as needed
                st.warning("The input text is very long and may contain multiple articles. Please input only one article at a time.")
                return

            # Reset states for new article
            st.session_state.update({
                'highlighting_complete': False,
                'highlighted_article': '',
                'highlighted_summary': '',
                'matched_sentences': [],
                'processing_complete': False
            })

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                if is_url(article_input.strip()):
                    # Input is a URL
                    progress_bar.empty()  # Remove progress bar for URL
                    with st.spinner('Extracting content from URL...'):
                        success, article_or_error = get_cleaned_article(article_input.strip())
                        if not success:
                            # Extraction failed; prompt user to input text directly
                            st.error(f"Failed to extract content from the URL. {article_or_error}")
                            st.info("Please copy and paste the article text directly into the text area.")
                            status_text.empty()
                            return
                        article = article_or_error
                else:
                    # Input is text; check word count
                    word_count = len(article_input.strip().split())
                    if word_count < 130:
                        st.warning("Article text must be more than 130 words.")
                        progress_bar.empty()
                        status_text.empty()
                        return
                    article = article_input.strip()

                # Store the article in session state
                st.session_state['article'] = article

                # Process the article
                result = process_article(article, progress_bar, status_text)

                if result['success']:
                    st.session_state.processing_complete = True
                    progress_bar.empty()
                    status_text.empty()
                else:
                    st.error(result.get('error', 'An error occurred during processing'))
                    progress_bar.empty()
                    status_text.empty()
                    return

            except Exception as e:
                st.error("An unexpected error occurred. Please try again later.")
                progress_bar.empty()
                status_text.empty()
                # Optionally log the exception details for debugging purposes
                # For example, use logging.error(str(e)) or print(str(e))
                return
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Content after this will be full-width
    if st.session_state.get('processing_complete', False):
        display_results()