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

# Download the NLTK names dataset (This section is Copied from ChatGPT to get more accurate results)
nltk.download("names")
all_names = set(names.words())  # Contains common first names (male and female)

# To extract the title from the PDF
def extract_title(text):
    lines = text.split("\n")
    for line in lines[:10]:  # Check only the first few lines
        if len(line.strip()) > 10:
            return line.strip()
    return "Title not found"

# Function to extract headings based on font size and bold text
# To extract headings
def extract_headings(text):
    heading_pattern = r"(^[A-Z\s]+$)|(^\d+\.\s[A-Za-z\s]+$)"
    matches = re.findall(heading_pattern, text, re.MULTILINE)
    headings = [h[0] or h[1] for h in matches if h[0] or h[1]]
    return headings

# Text --> Authors
def extract_authors(text):
    # Limit search to the first 15 lines (common for author names)
    lines = text.split("\n")[:15]
    limited_text = "\n".join(lines)
    
    # ReGex pattern to capture names
    author_pattern = r"\b[A-Z][a-z]+(?:\s[A-Z]\.)?(?:\s[A-Z][a-z]+)\b"
    potential_authors = re.findall(author_pattern, limited_text)
    
    # Only return unique potential author names
    return list(set(potential_authors))

# Text --> references
def extract_references(text):
    reference_pattern = r"(\[\d+\].*?\.)|(\d+\.\s.*?\.)"  # Capture styles with numbers or brackets
    references = re.findall(reference_pattern, text)
    return [ref[0] if ref[0] else ref[1] for ref in references] if references else ["References not found"]

# Uses Streamlit to make GUI 
def main():
    st.set_page_config(page_title="ReResearch for Research", page_icon="🤠")
    st.title("ReResearch for Research 📄")
    st.write("Created with ❤️ by Pranshu.")

    st.title("📁 Upload Your PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        file_data = uploaded_file.read()  # Read file once and store data
        st.success("File uploaded successfully! 🥹")
        st.success("Research is working 😎")

        with st.spinner("Have a cup of ☕️ Until we cook... please wait."):
            pdf_text = extract_text_from_pdf(file_data)
            title = extract_title(pdf_text)
            headings = extract_headings(pdf_text)  # Pass pdf_text instead of file_data
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

if __name__ == "__main__":
    main()
