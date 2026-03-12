import streamlit as st
import re
from difflib import SequenceMatcher
from PyPDF2 import PdfReader

# -------------------------------
# 1. Function to extract text from PDF or TXT
def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text
    elif file.type == "text/plain":
        return str(file.read(), "utf-8")
    else:
        return ""

# -------------------------------
# 2. Split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

# -------------------------------
# 3. Scoring function
def score_sentence(query, sentence):
    query_words = query.lower().split()
    sentence_lower = sentence.lower()
    overlap = sum(1 for word in query_words if word in sentence_lower)
    similarity = SequenceMatcher(None, query.lower(), sentence_lower).ratio()
    return overlap * 2 + similarity  # keyword boost

# -------------------------------
# 4. Q&A function
def ask_question(query, sentences, top_n=5):
    scored = [(score_sentence(query, s), s) for s in sentences]
    top_sentences = [s for score, s in sorted(scored, key=lambda x: x[0], reverse=True)[:top_n] if score > 0]
    if not top_sentences:
        return "No relevant information found."
    # Return top 1–2 sentences for conciseness
    return " ".join(top_sentences[:2])

# -------------------------------
# 5. Streamlit interface
st.title("Smarter Notes Q&A Tool")
st.write("Upload your notes as TXT or PDF files, then ask a question.")

uploaded_files = st.file_uploader("Upload your notes", type=["txt", "pdf"], accept_multiple_files=True)

all_sentences = []
if uploaded_files:
    for file in uploaded_files:
        text = extract_text(file)
        sentences = split_into_sentences(text)
        all_sentences.extend(sentences)

query = st.text_input("Ask a question about your notes:")

if query:
    if not all_sentences:
        st.write("Please upload notes first!")
    else:
        answer = ask_question(query, all_sentences)
        st.subheader("Answer:")
        st.write(answer)
