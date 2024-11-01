import fitz  # PyMuPDF
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
from io import BytesIO
import torch

# Load GPT-J model and tokenizer
model_name = "EleutherAI/gpt-j-6B"  # Replace with 'EleutherAI/gpt-neox-20b' if you have the resources
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).to("cuda" if torch.cuda.is_available() else "cpu")

# Function to query the model with specific prompts
def query_model(model, tokenizer, prompt, max_length=200):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(inputs["input_ids"], max_length=max_length, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

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
    st.title("GPT-J Enhanced PDF Extractor")
    st.write("Upload a PDF file and extract structured information (title, authors, headings, and references) using GPT-J.")

    # Upload PDF file
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        file_data = uploaded_file.read()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_data)
        
        st.write("Extracting information with GPT-J...")

        # Run extraction tasks
        title = query_model(model, tokenizer, f"Extract the title:\n{extracted_text[:500]}")
        authors = query_model(model, tokenizer, f"Identify the authors:\n{extracted_text[:500]}")
        headings = query_model(model, tokenizer, f"List section headings:\n{extracted_text[:1000]}")
        references = query_model(model, tokenizer, f"Extract references:\n{extracted_text[-2000:]}")

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
