import fitz  # PyMuPDF
import re
import streamlit as st
import requests
from io import BytesIO

# Hugging Face Inference API query function
def query_huggingface_api(prompt, api_token, model="facebook/bart-large-cnn"):
    headers = {"Authorization": f"Bearer {api_token}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt, "parameters": {"max_length": 150}}
    response = requests.post(api_url, headers=headers, json=payload)

    # Check if the response is valid
    if response.status_code == 200:
        try:
            return response.json()[0]["generated_text"]
        except (IndexError, KeyError):
            st.error(f"Unexpected response structure: {response.json()}")
            raise Exception("The response does not contain 'generated_text'. Please check the model's output.")
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

# Function to extract text from PDF
def extract_text_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    pdf_document.close()
    return text

# Local extraction function for title and authors
def extract_title_and_authors(text):
    title_pattern = r"(?<=\n)[^\n]+\n"  # Basic title pattern
    author_pattern = r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b"  # Simple pattern for names
    
    title = re.findall(title_pattern, text)
    authors = re.findall(author_pattern, text)
    
    return title[0].strip() if title else "Title not found", authors if authors else "Authors not found"

# Streamlit app
def main():
    st.title("Hugging Face API PDF Extractor")
    st.write("Upload a PDF file and extract structured information (title, authors, headings, and references) using the Hugging Face API.")

    # Securely retrieve the API token
    api_token = st.secrets["HUGGINGFACE_API_TOKEN"]
    
    # Upload PDF file
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file and api_token:
        file_data = uploaded_file.read()

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_data)

        st.write("Extracting information with Hugging Face API...")

        # Define prompts for information extraction
        title_prompt = f"Extract the title from the following text:\n\n{extracted_text[:500]}"
        authors_prompt = f"Identify the authors of the following text:\n\n{extracted_text[:500]}"
        headings_prompt = f"List the headings in the following text:\n\n{extracted_text[:1000]}"
        references_prompt = f"Identify the references in the following text:\n\n{extracted_text[-2000:]}"

        # Try to query the API for each prompt
        title, authors, headings, references = "Not extracted", "Not extracted", "Not extracted", "Not extracted"

        # Try extracting title
        try:
            title = query_huggingface_api(title_prompt, api_token)
        except Exception as e:
            st.error(f"Failed to extract title using API: {e}")
            title, authors = extract_title_and_authors(extracted_text)  # Fallback extraction

        # Try extracting authors
        try:
            authors = query_huggingface_api(authors_prompt, api_token)
        except Exception as e:
            st.error(f"Failed to extract authors using API: {e}")
            authors = extract_title_and_authors(extracted_text)[1]  # Fallback extraction

        # Try extracting headings
        try:
            headings = query_huggingface_api(headings_prompt, api_token)
        except Exception as e:
            st.error(f"Failed to extract headings using API: {e}")
            headings = "Headings extraction failed."

        # Try extracting references
        try:
            references = query_huggingface_api(references_prompt, api_token)
        except Exception as e:
            st.error(f"Failed to extract references using API: {e}")
            references = "References extraction failed."

        # Display results
        st.subheader("Title")
        st.write(title)

        st.subheader("Authors")
        st.write(authors)

        st.subheader("Headings")
        st.write(headings)

        st.subheader("References")
        st.write(references)

if __name__ == "__main__":
    main()
