import re

def clean_text(text):
    return re.sub(r'\[\d+\]', '', text)  # Remove citation numbers like [1], [2]
