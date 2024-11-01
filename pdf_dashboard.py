import streamlit as st
import fitz  # PyMuPDF
import re

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text") + "\n"
    pdf_document.close()
    return text

# Function to extract title
def extract_title(text):
    title_pattern = r"^[A-Z][A-Za-z\s]+$"
    match = re.search(title_pattern, text, re.MULTILINE)
    return match.group(0) if match else "Title not found"

# Function to extract authors
def extract_authors(text):
    author_pattern = r"\b[A-Z][a-zA-Z]*\s[A-Z]\.?\s?[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\s[A-Z][a-zA-Z]*\b"
    authors = re.findall(author_pattern, text)
    return authors if authors else ["Authors not found"]

# Function to extract headings
def extract_headings(text):
    heading_pattern = r"(^[A-Z\s]+$)|(^\d+\.\s[A-Za-z\s]+$)"
    matches = re.findall(heading_pattern, text, re.MULTILINE)
    headings = [h[0] or h[1] for h in matches if h[0] or h[1]]
    return headings

# Function to extract references
def extract_references(text):
    reference_pattern = r"\[\d+\]\s[A-Za-z.,\s]+\(.*?\)\.\s.*?\."
    references = re.findall(reference_pattern, text)
    return references if references else ["References not found"]

# Streamlit app setup
st.title("ReResearch by Pranshu")
st.write("Upload a PDF file, and the dashboard will extract the title, authors, headings, and references.")

# File upload widget
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(uploaded_file)

    # Extract information
    title = extract_title(pdf_text)
    authors = extract_authors(pdf_text)
    headings = extract_headings(pdf_text)
    references = extract_references(pdf_text)

    # Display extracted information
    st.header("Extracted Information")
    st.subheader("Title")
    st.write(title)
    
    st.subheader("Authors")
    st.write(", ".join(authors))
    
    st.subheader("Headings")
    for heading in headings:
        st.write(f"- {heading}")
    
    st.subheader("References")
    for reference in references:
        st.write(f"- {reference}")