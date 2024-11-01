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
def extract_references(text):
    reference_pattern = r"(\[\d+\].*?\.)|(\d+\.\s.*?\.)"  # Capture styles with numbers or brackets
    references = re.findall(reference_pattern, text)
    return [ref[0] if ref[0] else ref[1] for ref in references] if references else ["References not found"]

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
    st.set_page_config(page_title="ReResearch for Research", page_icon="📄")
    st.title("ReResearch for Research 📄")
    st.write("Created with ❤️ by Pranshu. (Under Development)")

    st.sidebar.title("📁 Upload Your PDF")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        file_data = uploaded_file.read()  # Read file once and store data
        st.sidebar.success("File uploaded successfully!")

        # Add a spinner to indicate that processing is in progress
        with st.spinner("Extracting information... please wait."):
            # Extract text and information from PDF
            pdf_text = extract_text_from_pdf(file_data)
            title = extract_title(pdf_text)
            headings = extract_headings_from_pdf(file_data)
            authors = extract_authors(pdf_text)
            references = extract_references(pdf_text)

        # Display a quick summary
        st.header("Summary of Extraction 📝")
        st.write(f"**Title:** {title}")
        st.write(f"**Number of Headings Found:** {len(headings)}")
        st.write(f"**Number of Authors Found:** {len(authors)}")
        st.write(f"**Number of References Found:** {len(references)}")
        st.markdown("---")

        # Display detailed results
        st.subheader("Title 🎓")
        st.markdown(f"**{title}**")

        st.subheader("Headings 📌")
        if headings:
            st.write("Here are the extracted headings:")
            for heading in headings:
                st.markdown(f"- {heading}")
        else:
            st.write("No headings found.")

        st.subheader("Authors 👥")
        if authors:
            st.write("The authors identified in the document are:")
            st.write(", ".join(authors))
        else:
            st.write("No authors found.")

        st.subheader("References 📚")
        if references:
            st.write("References found in the document:")
            for ref in references:
                st.markdown(f"- {ref}")
        else:
            st.write("No references found.")

        # Option to download extracted data
        if st.button("Download Extracted Data as Text"):
            extracted_data = f"Title:\n{title}\n\nHeadings:\n" + "\n".join(headings) + "\n\nAuthors:\n" + ", ".join(authors) + "\n\nReferences:\n" + "\n".join(references)
            st.download_button("Download", data=extracted_data, file_name="extracted_data.txt", mime="text/plain")

if __name__ == "__main__":
    main()
