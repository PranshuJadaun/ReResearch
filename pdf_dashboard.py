'''import streamlit as st
import fitz
import re

# To extract text from PDF
def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text") + "\n"
    pdf_document.close()
    return text

# To extract title
def extract_title(text):
    title_pattern = r"^[A-Z][A-Za-z\s\-]+$"
    match = re.search(title_pattern, text, re.MULTILINE)
    return match.group(0) if match else "Title not found"

# To extract authors
def extract_authors(text):
    author_pattern = r"\b[A-Z][a-zA-Z]*\s(?:[A-Z]\.\s)?[A-Z][a-zA-Z]*\b"
    authors = re.findall(author_pattern, text)
    return authors if authors else ["Authors not found"]

# # To extract headings
# def extract_headings(text):
#     heading_pattern = r"(^[A-Z\s]+$)|(^\d+\.\s[A-Za-z\s]+$)"
#     matches = re.findall(heading_pattern, text, re.MULTILINE)
#     headings = [h[0] or h[1] for h in matches if h[0] or h[1]]
#     return headings

# Function to extract headings with an improved pattern
def extract_headings(text):
    # Pattern to capture typical headings (numbered sections or lines in all caps)
    heading_pattern = r"(^[A-Z\s]{3,}$)|(^\d+\.\s.+$)|(^[A-Z][a-z]+\s[A-Z][a-z]+)"
    matches = re.findall(heading_pattern, text, re.MULTILINE)
    # Flatten the result as re.findall returns tuples when there are multiple groups
    headings = [match[0] if match[0] else match[1] if match[1] else match[2] for match in matches if any(match)]
    return headings if headings else ["No headings found"]

# To extract references
def extract_references(text):
    reference_pattern = r"\[\d+\]\s.*?\.\s.*?\."
    references = re.findall(reference_pattern, text)
    return references if references else ["References not found"]

# Streamlit
st.title("ReResearch For Research")
st.write("Upload a PDF file, ReResearch will extract the title, authors, headings, and references just for you.")

# File upload widget By streamlit
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(uploaded_file)

    # Extract individual elements
    title = extract_title(pdf_text)
    authors = extract_authors(pdf_text)
    headings = extract_headings(pdf_text)
    references = extract_references(pdf_text)

    # Display extracted data
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

st.subheader("Created by Us for You")
st.write("Created by Pranshu. ReResearch V1.0")'''
import fitz  # PyMuPDF
import re
import streamlit as st

# Function to extract the title from the PDF
def extract_title(text):
    # Assuming the title is the first non-empty line with a large font size
    lines = text.split("\n")
    for line in lines[:10]:  # Check only the first few lines
        if len(line.strip()) > 5:
            return line.strip()
    return "Title not found"

# Function to extract headings based on font size and bold text
def extract_headings_from_pdf(file):
    pdf_document = fitz.open(file)
    headings = []

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] > 12 and span["flags"] & 2:  # flags & 2 checks for bold text
                            headings.append(span["text"])

    pdf_document.close()
    return headings

# Function to extract authors using a regular expression
def extract_authors(text):
    author_pattern = r"\b[A-Z][a-zA-Z]*\s[A-Z]\.?\s?[A-Z][a-zA-Z]*\b|\b[A-Z][a-zA-Z]*\s[A-Z][a-zA-Z]*\b"
    authors = re.findall(author_pattern, text)
    return authors

# Function to extract references from the PDF
def extract_references(text):
    # Assuming references are at the end and start with "References" or similar heading
    references = []
    ref_start = text.lower().find("references")
    if ref_start != -1:
        references_text = text[ref_start:].split("\n")
        for line in references_text:
            if len(line.strip()) > 5:
                references.append(line.strip())
    return references

# Function to process the entire PDF as text
def extract_text_from_pdf(file):
    pdf_document = fitz.open(file)
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    pdf_document.close()
    return text

# Streamlit app for PDF extraction
def main():
    st.title("PDF Research Paper Extractor")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        pdf_text = extract_text_from_pdf(uploaded_file)
        
        # Extract information
        title = extract_title(pdf_text)
        headings = extract_headings_from_pdf(uploaded_file)
        authors = extract_authors(pdf_text)
        references = extract_references(pdf_text)

        # Display results
        st.subheader("Title")
        st.write(title)

        st.subheader("Headings")
        if headings:
            for heading in headings:
                st.write(f"- {heading}")
        else:
            st.write("No headings found.")

        st.subheader("Authors")
        if authors:
            st.write(", ".join(authors))
        else:
            st.write("No authors found.")

        st.subheader("References")
        if references:
            for ref in references:
                st.write(f"- {ref}")
        else:
            st.write("No references found.")

if __name__ == "__main__":
    main()
