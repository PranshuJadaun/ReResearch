import fitz  # PyMuPDF
import streamlit as st
import requests
from io import BytesIO

# Hugging Face Inference API query function
def query_huggingface_api(prompt, api_token, model="facebook/bart-large-cnn"):
    headers = {"Authorization": f"Bearer {api_token}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt, "parameters": {"max_length": 300}}
    
    response = requests.post(api_url, headers=headers, json=payload)

    # Check if the response is valid
    if response.status_code == 200:
        try:
            return response.json()[0]["summary_text"]
        except (IndexError, KeyError):
            st.error("Unexpected response structure.")
            return None
    else:
        st.error(f"API request failed: {response.status_code} - {response.text}")
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

# Streamlit app
def main():
    st.title("PDF Information Extractor Using Hugging Face API")
    st.write("Upload a PDF file to extract structured information (title, authors, headings, and references).")

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
        title_prompt = f"Extract the title from this document:\n{extracted_text}"
        authors_prompt = f"Identify the authors of this document:\n{extracted_text}"
        headings_prompt = f"List the headings in this document:\n{extracted_text}"
        references_prompt = f"Identify the references in this document:\n{extracted_text}"

        # Query the API for each prompt
        title = query_huggingface_api(title_prompt, api_token)
        authors = query_huggingface_api(authors_prompt, api_token)
        headings = query_huggingface_api(headings_prompt, api_token)
        references = query_huggingface_api(references_prompt, api_token)

        # Display results in an organized manner
        st.subheader("Title")
        st.write(title if title else "Title extraction failed.")

        st.subheader("Authors")
        st.write(authors if authors else "Authors extraction failed.")

        st.subheader("Headings")
        st.write(headings if headings else "Headings extraction failed.")

        st.subheader("References")
        st.write(references if references else "References extraction failed.")

if __name__ == "__main__":
    main()
