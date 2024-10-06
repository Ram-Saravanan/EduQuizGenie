import streamlit as st
import os
from PIL import Image
import pdfplumber
import pytesseract
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


st.set_page_config(page_title="Quiz Generation App", layout="wide")


st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        background-color: 
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .stTextInput>div>div>input {
        background-color: 
    }
    </style>
    """, unsafe_allow_html=True)

def image_to_text(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def pdf_to_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  
    return text

def generate_quiz_from_text(text):
    st.info("Generating quiz from the extracted text...")
    genai.configure(api_key=api_key)
   
    prompt = f"Make a 10 MCQ type of quiz with options on new line. If two or more files, divide the number of questions accordingly. For a single text, generate 10 questions(do not show answer key): {text}"
   
    model = genai.GenerativeModel('gemini-pro')
    res = model.generate_content(prompt)
   
    return res.text

def chatbot(prompt):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    res = model.generate_content(prompt)
    return res.text

def main():
    st.title("🧠 Quiz Generation App")
   
    tab1, tab2 = st.tabs(["Quiz Generator", "Chatbot"])
   
    with tab1:
        st.header("Upload Files")
        st.write("Upload images or PDFs, and a quiz will be generated based on the extracted text.")
        uploaded_files = st.file_uploader("Upload Images or PDFs", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)
       
        combined_text = ""
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_type = uploaded_file.type
               
                if file_type in ["image/png", "image/jpeg", "image/jpg"]:
                    st.info(f"Processing image: {uploaded_file.name}...")
                    image_text = image_to_text(uploaded_file)
                    combined_text += image_text + "\n\n"
               
                elif file_type == "application/pdf":
                    st.info(f"Processing PDF: {uploaded_file.name}...")
                    pdf_text = pdf_to_text(uploaded_file)
                    combined_text += pdf_text + "\n\n"
       
        if combined_text:
            if st.button("Generate Quiz"):
                quiz_content = generate_quiz_from_text(combined_text)
                st.success("Quiz Generated Successfully!")
                st.subheader("Generated Quiz:")
                st.write(quiz_content)
        else:
            st.warning("Please upload valid images or PDF files to extract text.")

    with tab2:
        st.header("Chat with AI")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = chatbot(prompt)
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
