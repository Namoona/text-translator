import os
import pandas as pd
import PyPDF2
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv
import mimetypes


#Setting up the google Generative AI API KeyboardInterrupt
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")  

#Lets write a Function to translate text written in English to any other 
#language using google generative AI API.

def translate_text(input_text, target_language):
    try:
        prompt = f"Translate the following text to {target_language}. Provide only the translated text:\ n\n{input_text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during translation: {e}"
    
# Write a function to extract texts from uploadded files such as pdf, txt, CSV, xlsx
def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        elif uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8").strip()
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            return df.to_string(index=False)
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                                    "application/vnd.ms-excel"]:
            df = pd.read_excel(uploaded_file)
            return df.to_string(index=False)
        else:
            return "Unsupported file type."
    except Exception as e:
        return f"Please upload your files only in following file format: pdf, txt, csv or xlsx: {e}"
    
# Function to convert text to speech
def text_to_speech(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language)
        audio_file = "translated_audio.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        return f"Error during text-to-speech conversion: {e}"
    
# Create a web app using Streamlit
st.set_page_config(page_title="Multilingual Text Translator and Text to Speech App",page_icon="😃", layout="wide")
st.title("Multilingual Text Translator and Text to Speech App with Google Gemini-1.5")
st.write("This app allows you to translate text written in English to other languages such as Spanish,French, German, Chinese or many more. You can either directly enter the text or upload a file in any of these file formats (PDF, TXT, CSV, XLSX). Please select a target language, and get the translated text and audio. Have fun!")

# Lets make a work for input text and file upload (txt, pdf, csv and XlSX)
input_text = st.text_area("Enter the text in English", )
uploaded_file = st.file_uploader("Upload your file here", type=["pdf", "txt", "csv", "xlsx"])

target_language = st.selectbox("Select target language", ["Spanish", "French", "German", "Chinese", "Hindi", "Arabic", "Russian", "Japanese", "Portuguese", "Italian", "Nepali"])


if st.button("Translate and Convert to Speech"):
    if uploaded_file is not None:
        text = extract_text_from_file(uploaded_file)
    elif input_text:
        text = input_text
    else:
        st.error("Please upload a file or enter text to translate.")
        text = None

    if text:
        translated_text = translate_text(text, target_language)
        st.subheader("Translated Text")
        st.write(translated_text)

# Convert translated text to speech without error in audio file in application
        audio_file = text_to_speech(translated_text, language='en')
        if os.path.exists(audio_file):
            audio_file_path = audio_file
            audio_file_name = os.path.basename(audio_file_path)
            mime_type, _ = mimetypes.guess_type(audio_file_path)
            if mime_type is None:
                mime_type = "audio/mpeg"
            with open(audio_file_path, "rb") as af:
                st.audio(af.read(), format=mime_type, start_time=0)
        else:
            st.error("Audio file not found or could not be created.")
    
# Also provide an option to download the translated text and audio file
        st.download_button("Download Translated Text", translated_text, file_name="translated_text.txt")
        with open(audio_file, "rb") as af:
            st.download_button("Download Translated Audio", af, file_name="translated_audio.mp3", mime="audio/mp3")






