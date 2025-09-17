import os
from io import BytesIO
from typing import List

import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from gtts import gTTS
from dotenv import load_dotenv
import google.generativeai as genai


# --------------------------
# Config & constants
# --------------------------
st.set_page_config(page_title="Gemini Translator + TTS", page_icon="🌐", layout="centered")

LANG_CHOICES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Portuguese": "pt",
    "Italian": "it",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Russian": "ru",
    "Hindi": "hi",
    "Nepali": "ne",
    "Bengali": "bn",
}

MODEL_NAME = "gemini-1.5-flash"
TEMPERATURE = 0.2
MAX_CHARS_PER_CHUNK = 4500  # conservative; Gemini can handle more, but chunking is safer


# --------------------------
# Secrets / API key helpers
# --------------------------
def get_gemini_api_key() -> str:
    """
    Priority:
      1) st.secrets["GEMINI_API_KEY"] (Streamlit Cloud)
      2) environment variable
      3) .env file in local dev (via python-dotenv)
    """
    key = None
    try:
        key = st.secrets.get("GEMINI_API_KEY")  # works on Streamlit Cloud
    except Exception:
        pass

    if not key:
        load_dotenv()
        key = os.getenv("GEMINI_API_KEY")

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it in Streamlit Cloud (App settings → Secrets) "
            "or create a local .env file with GEMINI_API_KEY=... "
        )
    return key


def get_model():
    genai.configure(api_key=get_gemini_api_key())
    return genai.GenerativeModel(MODEL_NAME)


# --------------------------
# Text utilities
# --------------------------
def _split_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> List[str]:
    """Split long text into (roughly) sentence/paragraph chunks under max_chars."""
    if len(text) <= max_chars:
        return [text]

    chunks, current = [], []
    total = 0
    # Prefer splitting on double newlines or periods
    units = [u for u in text.replace("\r\n", "\n").split("\n\n") if u.strip()]
    for block in units:
        if len(block) > max_chars:
            # fallback: split by sentences if a block is too big
            sentences = [s.strip() for s in block.split(". ") if s.strip()]
            for s in sentences:
                s2 = s if s.endswith(".") else s + "."
                if total + len(s2) > max_chars and current:
                    chunks.append(" ".join(current))
                    current, total = [], 0
                current.append(s2)
                total += len(s2)
        else:
            if total + len(block) + 2 > max_chars and current:
                chunks.append("\n\n".join(current))
                current, total = [], 0
            current.append(block)
            total += len(block) + 2

    if current:
        # join with paragraph breaks
        chunks.append("\n\n".join(current))
    return chunks


def translate_text(model, text: str, target_language_name: str) -> str:
    """Translate text using Gemini with clear, deterministic instructions."""
    chunks = _split_text(text, MAX_CHARS_PER_CHUNK)
    outputs = []
    for idx, chunk in enumerate(chunks, start=1):
        prompt = (
            f"Translate the following English text into {target_language_name}.\n"
            f"Return only the translation, with no extra commentary or quotation marks.\n\n"
            f"{chunk}"
        )
        resp = model.generate_content(
            prompt,
            generation_config={"temperature": TEMPERATURE},
        )
        outputs.append((resp.text or "").strip())
    return "\n\n".join(outputs).strip()


# --------------------------
# File extraction
# --------------------------
def extract_text_from_file(uploaded) -> str:
    """Return extracted text or raise a ValueError with a friendly message."""
    mime = uploaded.type or ""
    name = uploaded.name.lower()

    if mime == "application/pdf" or name.endswith(".pdf"):
        reader = PdfReader(uploaded)
        pages = []
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        text = "\n\n".join(pages).strip()
        if not text:
            raise ValueError("No extractable text found. The PDF may be scanned; consider OCR.")
        return text

    if mime == "text/plain" or name.endswith(".txt"):
        return uploaded.read().decode("utf-8", errors="ignore")

    if mime in ("text/csv",) or name.endswith(".csv"):
        df = pd.read_csv(uploaded)
        return df.to_csv(index=False)

    if mime in (
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ) or name.endswith((".xls", ".xlsx")):
        df = pd.read_excel(uploaded)
        # Represent as CSV text for translation (simple and readable)
        return df.to_csv(index=False)

    raise ValueError("Unsupported file type. Please upload PDF, TXT, CSV, or XLSX.")


# --------------------------
# Text-to-Speech
# --------------------------
def synthesize_speech(text: str, lang_code: str, out_path: str = "translated_audio.mp3") -> str:
    tts = gTTS(text=text, lang=lang_code)
    tts.save(out_path)
    return out_path


# --------------------------
# UI
# --------------------------
st.title("🌐 Multilingual Translator + Text-to-Speech (Gemini + gTTS)")
st.write(
    "Translate English text into a target language using Google Gemini, then convert the result to speech with gTTS. "
    "Type text directly or upload PDF, TXT, CSV, or XLSX files."
)

with st.sidebar:
    st.header("Settings")
    target_name = st.selectbox("Target language", list(LANG_CHOICES.keys()), index=1)
    tts_lang_code = LANG_CHOICES[target_name]
    st.caption("Note: TTS language follows your selected target language.")
    st.divider()
    st.markdown(
        "Add your **GEMINI_API_KEY** in Streamlit Cloud (App → Settings → Secrets) or in a local `.env`."
    )

tab_text, tab_file = st.tabs(["📝 Enter Text", "📎 Upload File"])

with tab_text:
    input_text = st.text_area("English text", height=180, placeholder="Type or paste English text here...")
    go_text = st.button("Translate & Speak (Text)")

with tab_file:
    uploaded = st.file_uploader("Upload PDF, TXT, CSV, or XLSX", type=["pdf", "txt", "csv", "xls", "xlsx"])
    go_file = st.button("Translate & Speak (File)")

# Decide what to translate
to_process = None
if go_text:
    to_process = (input_text or "").strip()
elif go_file and uploaded:
    try:
        to_process = extract_text_from_file(uploaded).strip()
    except Exception as e:
        st.error(str(e))

if to_process:
    if not to_process.strip():
        st.warning("Please provide some English text.")
    else:
        try:
            with st.spinner("Initializing model..."):
                model = get_model()

            with st.spinner(f"Translating to {target_name}..."):
                translated = translate_text(model, to_process, target_name)

            st.subheader("Translated Text")
            st.text_area("Result", translated, height=220)

            # Download translated text
            st.download_button(
                "⬇️ Download Translation (TXT)",
                data=translated.encode("utf-8"),
                file_name="translation.txt",
                mime="text/plain",
            )

            # TTS
            with st.spinner("Generating speech (MP3)..."):
                mp3_path = synthesize_speech(translated, tts_lang_code)

            with open(mp3_path, "rb") as f:
                audio_bytes = f.read()

            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                "⬇️ Download Audio (MP3)",
                data=audio_bytes,
                file_name="translation.mp3",
                mime="audio/mpeg",
            )
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.caption("Tip: For large files, the app splits text into chunks to keep translations reliable.")
