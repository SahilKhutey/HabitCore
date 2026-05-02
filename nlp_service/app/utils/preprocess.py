import re

def clean_text(text: str) -> str:
    if not text: return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text
