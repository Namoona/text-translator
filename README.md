# Multilingual Translator + Text-to-Speech (Gemini + Streamlit)

A Streamlit app that translates **English** text into a target language using **Google Gemini** and then converts the translation to speech using **gTTS**. It supports typed text and file uploads (PDF, TXT, CSV, XLSX) and runs entirely in the browser UI.

---

## Overview

This project provides a simple end-to-end workflow: input or upload text, translate it with Gemini, synthesize speech as an MP3 with gTTS, and play or download the results. The app is designed to be easy to demo locally and deploy on **Streamlit Community Cloud**.

**Key technologies:** Streamlit, Google Generative AI (`google-generativeai`), gTTS, PyPDF2, pandas, openpyxl.

---

## Features

* Translate English to many target languages (e.g., Spanish, French, German, Chinese, Japanese, Korean, Arabic, Hindi, Nepali, Bengali, Portuguese, Italian, Russian, English TTS).
* Upload **PDF, TXT, CSV, XLS/XLSX**; the app extracts text automatically.
* Chunking for long inputs to improve reliability with LLM calls.
* Play translated audio in-app and download as **MP3**.
* Secure configuration: no hard-coded API keys (use environment variables or Streamlit secrets).

---

## Project Structure

```
.
├─ app.py                  # Streamlit app (UI, translation, TTS)
├─ requirements.txt        # Python dependencies (Py 3.13 friendly)
├─ .gitignore              # Ignore env & artifacts
└─ README.md               # This file
```

*Optional (local only):* `Dockerfile`, `.streamlit/` with `secrets.toml`.

---

## Prerequisites

* **Python 3.13+** (Streamlit Community Cloud currently runs on 3.13).
* A **Google Gemini API key** from **Google AI Studio**.
* For Excel support: `openpyxl` (already listed in `requirements.txt`).

---

## Getting a Google Gemini API key

1. Open **Google AI Studio** and sign in.
2. Click **Get API key** → create/select a project → **Create key**.
3. Copy the key and keep it **out of your code**.

---

## Local Setup

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# Install dependencies
pip install -r requirements.txt

# Create a .env file for local development
echo "GEMINI_API_KEY=your_real_key_here" > .env

# Run the app
streamlit run app.py
```

Open the local URL shown by Streamlit in your browser.

---

## Configuration & Secrets

The app looks for the Gemini key in this order:

1. `st.secrets["GEMINI_API_KEY"]` (Streamlit Cloud)
2. Environment variable `GEMINI_API_KEY`
3. `.env` file loaded by `python-dotenv`

**Local dev:** place `GEMINI_API_KEY=...` in a `.env` file in the project root.
**Streamlit Cloud:** go to **App → Settings → Secrets** and add:

```
GEMINI_API_KEY = "your_real_key_here"
```

*Never commit real keys to Git.*

---

## Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In **Streamlit Cloud**, click **New app**, select the repo/branch, and set the main file to `app.py`.
3. Under **App → Settings → Secrets**, add:

   ```
   GEMINI_API_KEY = "your_real_key_here"
   ```
4. Deploy. Streamlit Cloud installs from `requirements.txt` (it ignores Dockerfiles).

---

## Using the App

1. Choose the **target language** in the sidebar.
2. Either:

   * Enter text on the **“Enter Text”** tab and click **Translate & Speak (Text)**, or
   * Upload a file (PDF, TXT, CSV, XLS/XLSX) on the **“Upload File”** tab and click **Translate & Speak (File)**.
3. View the **translated text**, **play the MP3**, and **download** both text and audio.

**Supported file types & extraction:**

* **PDF** → PyPDF2 text extraction (non-OCR; scanned PDFs may need OCR).
* **TXT** → decoded as UTF-8.
* **CSV/XLS/XLSX** → loaded via pandas and rendered to CSV text for translation.

---

## Language Mapping (TTS)

The app maps display names to gTTS codes (e.g., Spanish → `es`, French → `fr`, German → `de`, Chinese (Simplified) → `zh-CN`, Japanese → `ja`, Korean → `ko`, Arabic → `ar`, Russian → `ru`, Hindi → `hi`, Nepali → `ne`, Bengali → `bn`, Portuguese → `pt`, Italian → `it`, English → `en`). The TTS follows your selected target language.

---

## Notes on Translation Prompts

The app uses a clear, deterministic prompt:
“Translate the following English text into `<target language>`. Return only the translation, with no extra commentary or quotation marks.”

The model is `gemini-1.5-flash` with a low temperature for faithful output. Large inputs are split into chunks and reassembled to improve reliability.

---

## Troubleshooting

**Dependency install fails with NumPy/distutils error on Streamlit Cloud**
If you see an error about `distutils` and `numpy==1.23.x`, you’re likely on Python 3.13 where `distutils` is removed. This project’s `requirements.txt` avoids pinning NumPy; pandas will install a compatible version automatically. Use the provided `requirements.txt`.

**PDF extracts no text**
Your PDF may be scanned images or use non-extractable encodings. Consider adding OCR (e.g., Tesseract) before translation.

**Audio player error**
Ensure the MP3 was actually written. The app saves `translated_audio.mp3`, then streams raw bytes to `st.audio`. If you changed file paths/names, make sure they match.

**Rate limits or empty responses**
Add small retries/backoff in production. Very long inputs should be chunked (the app already does this).

---

## Security & Privacy

* Keep API keys in environment variables or Streamlit secrets.
* Do not commit `.env` or real secrets to Git.
* Be mindful of sending sensitive documents to external APIs; redact or summarize if necessary.

---

## License

Add a `LICENSE` file (e.g., MIT) if you plan to distribute this project.

---

## Acknowledgments

* [Streamlit](https://streamlit.io/)
* [Google Generative AI (Gemini)](https://ai.google.dev/)
* [gTTS](https://pypi.org/project/gTTS/)
* [PyPDF2](https://pypi.org/project/PyPDF2/)
* [pandas](https://pandas.pydata.org/) and [openpyxl](https://openpyxl.readthedocs.io/)

---

**Happy translating!**
