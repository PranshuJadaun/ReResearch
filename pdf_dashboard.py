import fitz  # PyMuPDF
import re
import streamlit as st
import requests
from io import BytesIO
from transformers import pipeline
import time

# Load the model locally (fallback)
generator = pipeline("text-generation", model="distilgpt2")

# Hugging Face Inference API query function
def query_huggingface_api(prompt, api_token, model="distilgpt2", retries=5):
    headers = {"Authorization": f"Bearer {api_token}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt, "parameters": {"max_length": 150}}

    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()  # Raises an error for bad HTTP status codes
            return response.json()[0]["generated_text"]
        except requests.exceptions.Timeout:
            st.warning("The request timed out. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            if response.status_code == 503 and attempt < retries - 1:
                st.warning(f"Attempt {attempt + 1}: Service unavailable, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                st.error(f"API request failed: {e}")
                return None

    st.error("Max retries reached. Unable to complete the request.")
    return None

# Function to extract text from PDF
def extract_text_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    pdf_document.close()
    return text

# Local processing function
def local_query(prompt):
    return generator(prompt, max_length=150)[0]['generated_text']

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

        st.write("Extracting information...")

        # Define prompts for information extraction
        title_prompt = f"Extract the title from this document:\n{extracted_text[:500]}"
        authors_prompt = f"Identify the authors of this document:\n{extracted_text[:500]}"
        headings_prompt = f"List the headings in this document:\n{extracted_text[:1000]}"
        references_prompt = f"Identify the references in this document:\n{extracted_text[-2000:]}"

        # Query the API for each prompt
        title = query_huggingface_api(title_prompt, api_token)
        if title is None:  # If API fails, fall back to local model
            title = local_query(title_prompt)

        authors = query_huggingface_api(authors_prompt, api_token)
        if authors is None:
            authors = local_query(authors_prompt)

        headings = query_huggingface_api(headings_prompt, api_token)
        if headings is None:
            headings = local_query(headings_prompt)

        references = query_huggingface_api(references_prompt, api_token)
        if references is None:
            references = local_query(references_prompt)

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
