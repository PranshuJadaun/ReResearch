import fitz  # PyMuPDF
import requests
from io import BytesIO
import streamlit as st

# Hugging Face Inference API query function
def query_huggingface_api(prompt, api_token, model="facebook/bart-large-cnn"):
    headers = {"Authorization": f"Bearer {api_token}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt}  # Removed max_length
    
    response = requests.post(api_url, headers=headers, json=payload)

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

# Function to split text into chunks
def split_text(text, max_chunk_size=1000):
    """Splits the input text into smaller chunks."""
    words = text.split()
    for i in range(0, len(words), max_chunk_size):
        yield ' '.join(words[i:i + max_chunk_size])

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
        prompts = {
            "Title": f"Extract the title from this document:\n{extracted_text}",
            "Authors": f"Identify the authors of this document:\n{extracted_text}",
            "Headings": f"List the headings in this document:\n{extracted_text}",
            "References": f"Identify the references in this document:\n{extracted_text}"
        }

        results = {}
        for key, prompt in prompts.items():
            # Process the text in chunks to avoid API limits
            chunks = list(split_text(prompt))
            full_result = ""
            for chunk in chunks:
                response = query_huggingface_api(chunk, api_token)
                if response:
                    full_result += response + "\n"
            results[key] = full_result.strip()

        # Display results in an organized manner
        for key in results:
            st.subheader(key)
            st.write(results[key] if results[key] else f"{key} extraction failed.")

if __name__ == "__main__":
    main()
