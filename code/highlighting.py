import colorsys

# Function to normalize sentences (remove trailing period)
def normalize_sentence(sentence):
    return sentence.rstrip(".")

# Function to generate distinct colors based on HSV
def generate_distinct_colors(n):
    HSV_tuples = [(x * 1.0 / n, 0.5, 0.8) for x in range(n)]
    RGB_tuples = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
    hex_colors = ['#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255)) for r, g, b in RGB_tuples]
    return hex_colors

# Function to highlight matched sentences in the text
def highlight_text(text, matched_sentences, color):
    for sentence in matched_sentences:
        normalized_sentence = normalize_sentence(sentence)
        if normalized_sentence in text:
            text = text.replace(normalized_sentence, f'<mark style="background-color: {color};">{normalized_sentence}</mark>')
    return text