import json
import streamlit as st
from highlighting import normalize_sentence, generate_distinct_colors, highlight_text

def highlight_summary_and_article(article, summary, matched_sentences):
    """
    Highlight matching sentences in both the article and summary.
    """
    try:
        parsed_sentences = (json.loads(matched_sentences) 
                          if isinstance(matched_sentences, str) 
                          else matched_sentences)
        colors = generate_distinct_colors(len(parsed_sentences))

        highlighted_article = article
        highlighted_summary = summary
        
        for index, mapping in enumerate(parsed_sentences):
            color = colors[index]
            summary_sentence = normalize_sentence(mapping["summary_sentence"])
            highlighted_summary = highlight_text(highlighted_summary, [summary_sentence], color)
            
            for article_sentence in mapping["article_sentences"]:
                normalized_article_sentence = normalize_sentence(article_sentence)
                highlighted_article = highlight_text(
                    highlighted_article, 
                    [normalized_article_sentence], 
                    color
                )

        return highlighted_summary, highlighted_article
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON format in matched_sentences")
        return summary, article
    except Exception as e:
        st.error(f"Error in highlight_summary_and_article: {str(e)}")
        return summary, article