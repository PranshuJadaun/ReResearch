import fitz  # PyMuPDF
import re
import streamlit as st
import requests
from io import BytesIO

# Hugging Face Inference API query function
def query_huggingface_api(prompt, api_token, model="gpt-2"):
    headers = {"Authorization": f"Bearer {api_token}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt, "parameters": {"max_length": 150}}
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

# Function to extract text from the PDF
def extract_text_from_pdf(file_data):
    pdf_document = fitz.open(stream=BytesIO(file_data), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text("text")
    pdf_document.close()
    return text

# Streamlit app
def main():
    st.title("Hugging Face API PDF Extractor")
    st.write("Upload a PDF file and extract structured information (title, authors, headings, and references) using the Hugging Face API.")

    # Get API token from user input
    api_token = st.text_input("Enter your Hugging Face API token:", type="password")
    
    # Upload PDF file
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file and api_token:
        file_data = uploaded_file.read()  # Read file once and store data

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_data)

        st.write("Extracting information with Hugging Face API...")

        # Define prompts for information extraction
        title_prompt = f"Extract the title from this document:\n{extracted_text[:500]}"
        authors_prompt = f"Identify the authors of this document:\n{extracted_text[:500]}"
        headings_prompt = f"List the headings in this document:\n{extracted_text[:1000]}"
        references_prompt = f"Identify the references in this document:\n{extracted_text[-2000:]}"

        # Query the API for each prompt
        try:
            title = query_huggingface_api(title_prompt, api_token)
            authors = query_huggingface_api(authors_prompt, api_token)
            headings = query_huggingface_api(headings_prompt, api_token)
            references = query_huggingface_api(references_prompt, api_token)

            # Display results
            st.subheader("Title")
            st.write(title)

            st.subheader("Authors")
            st.write(authors)

            st.subheader("Headings")
            st.write(headings)

            st.subheader("References")
            st.write(references)
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
