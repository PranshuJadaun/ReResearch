import fitz  # PyMuPDF
import re
import streamlit as st
from io import BytesIO

# Function to extract the title from the PDF
def extract_title(text):
    lines = text.split("\n")
    for line in lines[:10]:  # Check only the first few lines
        if len(line.strip()) > 5:
            return line.strip()
    return "Title not found"

# Function to extract headings based on font size and bold text
def extract_headings_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")
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
# To extract references
def extract_references(text):
    reference_pattern = r"\[\d+\]\s.*?\.\s.*?\."
    references = re.findall(reference_pattern, text)
    return references if references else ["References not found"]

# Corrected function to process the entire PDF as text
def extract_text_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")  # Open from binary data
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    pdf_document.close()
    return text

# Streamlit app for PDF extraction
def main():
    st.title("ReResearch for Research")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        file_data = uploaded_file.read()  # Read file once and store data

        # Extract text and information from PDF
        pdf_text = extract_text_from_pdf(file_data)
        title = extract_title(pdf_text)
        headings = extract_headings_from_pdf(file_data)
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
st.write("Created with LOVE by Pranshu. \n ReResearch V1.2")


if __name__ == "__main__":
    main()
