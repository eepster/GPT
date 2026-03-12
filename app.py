import streamlit as st
import re
from difflib import SequenceMatcher
from PyPDF2 import PdfReader

# -------------------------------
# 1. Extract text from PDFs or TXT
def extract_text(file):
    text = ""
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        elif file.type == "text/plain":
            text = str(file.read(), "utf-8")
    except Exception as e:
        st.warning(f"Could not read file {file.name}: {e}")
    return text.strip()

# -------------------------------
# 2. Split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

# -------------------------------
# 3. Score sentence based on keyword + similarity
def score_sentence(query, sentence):
    query_words = query.lower().split()
    sentence_lower = sentence.lower()
    # keyword overlap
    overlap = sum(1 for word in query_words if word in sentence_lower)
    # similarity
    similarity = SequenceMatcher(None, query.lower(), sentence_lower).ratio()
    # keyword boost
    return overlap * 2 + similarity

# -------------------------------
# 4. Get top sentences and highlight keywords
def ask_question(query, sentences, top_n=5):
    scored = [(score_sentence(query, s), s) for s in sentences]
    top_sentences = [s for score, s in sorted(scored, key=lambda x: x[0], reverse=True)[:top_n] if score > 0]

    if not top_sentences:
        return "No relevant information found."

    # Highlight matched keywords
    highlighted = []
    for sentence in top_sentences[:2]:  # top 1-2 sentences
        s = sentence
        for word in query.split():
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            s = pattern.sub(f"**{word}**", s)
        highlighted.append(s)
    return " ".join(highlighted)

# -------------------------------
# 5. Streamlit UI
st.title("Notes Q&A Tool (Free)")
st.write("Upload digital PDFs or TXT notes. Ask a question, get highlighted, concise answers.")

uploaded_files = st.file_uploader("Upload your notes", type=["txt", "pdf"], accept_multiple_files=True)

all_sentences = []
if uploaded_files:
    for file in uploaded_files:
        text = extract_text(file)
        if not text:
            st.warning(f"No text found in {file.name}")
        else:
            sentences = split_into_sentences(text)
            all_sentences.extend(sentences)

if uploaded_files and not all_sentences:
    st.info("Uploaded files were read but contained no extractable text.")

query = st.text_input("Ask a question about your notes:")

if query:
    if not all_sentences:
        st.write("Please upload notes first!")
    else:
        answer = ask_question(query, all_sentences)
        st.subheader("Answer:")
        st.markdown(answer)
