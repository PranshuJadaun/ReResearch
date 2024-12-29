import re
import fitz  # PyMuPDF
import streamlit as st
from io import BytesIO
import nltk
from nltk.corpus import names

# PDF --> text
def extract_text_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    pdf_document.close()
    return text

# Download the NLTK names dataset
nltk.download("names")
all_names = set(names.words())  # Contains common first names (male and female)

def main():
    st.set_page_config(page_title="ReResearch for Research", page_icon="🤠")
    st.title("Welcome to ReResearch 📄")
    st.write("Created with ❤️ by Pranshu.")

    # Ask the user to select functionality
    choice = st.selectbox("Choose a functionality:", ["Copy Text from PDF", "Search in Research File"])

    if choice == "Copy Text from PDF":
        st.subheader("Copy Text from PDF")
        uploaded_file = st.file_uploader("Choose a PDF file to extract text:", type="pdf")
        
        if uploaded_file is not None:
            file_data = uploaded_file.read()  # Read the file
            st.success("File uploaded successfully! 🥹 \n Processing the text now...")
            
            # Extract the text from the PDF
            with st.spinner("Extracting text... Please wait!"):
                pdf_text = extract_text_from_pdf(file_data)
            
            st.subheader("Extracted Text (Linewise) 📝")
            # Split text into lines and display them line by line
            lines = pdf_text.split("\n")
            for i, line in enumerate(lines, start=1):
                st.markdown(f"**{i}.** {line.strip()}")
            
            # Add Copy All Text Button
            st.subheader("Copy All Text")
            with st.expander("Click to expand and copy the full text"):
                st.text_area("Extracted Text:", pdf_text, height=300, key="full_text")
            
            # Copy Button using JavaScript
            copy_button_code = f"""
                <button onclick="navigator.clipboard.writeText(document.getElementById('full_text').value)">
                Copy All Text
                </button>
            """
            st.markdown(copy_button_code, unsafe_allow_html=True)

    elif choice == "Search in Research File":
        st.subheader("Search in Research File")
        st.write("This feature allows you to search for specific information such as titles, headings, authors, and references in a research PDF.")
        uploaded_file = st.file_uploader("Choose a research PDF file:", type="pdf")
        
        if uploaded_file is not None:
            file_data = uploaded_file.read()
            st.success("File uploaded successfully! 🥹")

            with st.spinner("Analyzing the file..."):
                pdf_text = extract_text_from_pdf(file_data)
                title = extract_title(pdf_text)
                headings = extract_headings(pdf_text)  
                authors = extract_authors(pdf_text)
                references = extract_references(pdf_text)

            # Display results
            st.subheader("Title 🎓")
            st.markdown(f"**{title}**")

            st.subheader("Headings 📌")
            if headings:
                for heading in headings:
                    st.markdown(f"- {heading}")
            else:
                st.write("No headings found. 😢")

            st.subheader("Authors 👥")
            if authors:
                st.write("The authors identified in the document are:")
                st.write(", ".join(authors))
            else:
                st.write("No authors found.")

            st.subheader("References 📚")
            if references:
                for ref in references:
                    st.markdown(f"- {ref}")
            else:
                st.write("No references found. 😥")


# Helper functions for research PDF processing
def extract_title(text):
    lines = text.split("\n")
    for line in lines[:10]:  # Check only the first few lines
        if len(line.strip()) > 10:
            return line.strip()
    return "Title not found"

def extract_headings(text):
    heading_pattern = r"(^[A-Z\s]+$)|(^\d+\.\s[A-Za-z\s]+$)"
    matches = re.findall(heading_pattern, text, re.MULTILINE)
    headings = [h[0] or h[1] for h in matches if h[0] or h[1]]
    return headings

def extract_authors(text):
    lines = text.split("\n")[:15]  # Limit search to the first 15 lines
    limited_text = "\n".join(lines)
    author_pattern = r"\b[A-Z][a-z]+(?:\s[A-Z]\.)?(?:\s[A-Z][a-z]+)\b"
    potential_authors = re.findall(author_pattern, limited_text)
    return list(set(potential_authors))  # Only return unique names

def extract_references(text):
    reference_pattern = r"(\[\d+\].*?\.)|(\d+\.\s.*?\.)"  # Match numbered or bracketed references
    references = re.findall(reference_pattern, text)
    return [ref[0] if ref[0] else ref[1] for ref in references] if references else ["References not found"]


if __name__ == "__main__":
    main()
