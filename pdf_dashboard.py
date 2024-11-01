import re
import fitz  # PyMuPDF
import streamlit as st
from io import BytesIO
import nltk
from nltk.corpus import names

# Download the NLTK names dataset
nltk.download("names")
all_names = set(names.words())  # Contains common first names (male and female)

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

# Enhanced Function to extract authors
def extract_authors(text):
    # Limit search to the first 15 lines (common for author names)
    lines = text.split("\n")[:15]
    limited_text = "\n".join(lines)
    
    # Improved regex pattern to capture names in common formats
    author_pattern = r"\b[A-Z][a-z]+(?:\s[A-Z]\.)?(?:\s[A-Z][a-z]+)\b"
    potential_authors = re.findall(author_pattern, limited_text)

    # Exclusion of known non-name terms and filtering against common names
    exclusions = {
        "Motion", "Sensor", "Electricity", "Engineering", "Research", "University", "School", "Institute",
        "Indonesia", "Control", "Materials", "Review", "Analysis", "Method", "Result", "System", "IEEE",
        "Journal", "Conclusion", "Department", "Technology", "College", "International", "Methodology",
        "Testing", "Study", "Objective", "Development"
    }
    
    authors = [name for name in potential_authors 
               if name not in exclusions and name.split()[0] in all_names]

    # Return unique names as authors
    return list(set(authors))

# Function to extract references from the PDF
def extract_references(text):
    reference_pattern = r"(\[\d+\].*?\.)|(\d+\.\s.*?\.)"  # Capture styles with numbers or brackets
    references = re.findall(reference_pattern, text)
    return [ref[0] if ref[0] else ref[1] for ref in references] if references else ["References not found"]

# Function to process the entire PDF as text
def extract_text_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")
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

        with st.spinner("Extracting information... please wait."):
            pdf_text = extract_text_from_pdf(file_data)
            title = extract_title(pdf_text)
            headings = extract_headings_from_pdf(file_data)
            authors = extract_authors(pdf_text)
            references = extract_references(pdf_text)

        # Display a summary
        st.header("Summary of Extraction 📝")
        st.write(f"**Title:** {title}")
        st.write(f"**Number of Headings Found:** {len(headings)}")
        st.write(f"**Number of Authors Found:** {len(authors)}")
        st.write(f"**Number of References Found:** {len(references)}")
        st.markdown("---")

        # Display results
        st.subheader("Title 🎓")
        st.markdown(f"**{title}**")

        st.subheader("Headings 📌")
        if headings:
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
            for ref in references:
                st.markdown(f"- {ref}")
        else:
            st.write("No references found.")

if __name__ == "__main__":
    main()
