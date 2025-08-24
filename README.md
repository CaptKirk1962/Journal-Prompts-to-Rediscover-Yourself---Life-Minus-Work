
# Life Minus Work — Streamlit Quiz (Prototype)

This is a simple, brandable Streamlit app that:
- Captures email + consent
- Asks 15 multiple-choice questions
- Scores themes (Identity, Growth, Connection, Peace, Adventure, Contribution)
- Generates a personalized PDF instantly (download button)
- (Optional) Uses OpenAI to write a tailored summary if `OPENAI_API_KEY` is set

## Quick Start

1) **Install Python 3.10+** (if you don't have it).
2) Create a new folder on your computer, then download these three files into it:
   - `app.py`
   - `questions.json`
   - `requirements.txt`
3) Open a terminal in that folder and run:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4) (Optional, for AI text) set your OpenAI key:
   - macOS/Linux:
     ```bash
     export OPENAI_API_KEY=sk-...
     ```
   - Windows (PowerShell):
     ```powershell
     setx OPENAI_API_KEY "sk-..."
     ```
   - Then close/reopen your terminal to ensure the variable is picked up.
5) Run the app:
   ```bash
   streamlit run app.py
   ```

## What You'll See
- Email capture + consent
- 15 questions (one-click answers)
- "Finish and Generate My Report" → immediate PDF download

## Where your data goes (prototype)
- Saves a line into `responses.csv` (same folder) with the scores + top 3 themes.
- PDF is generated in-memory for instant download.

## Next Steps (when you're ready)
- Add your logo and brand colors to the PDF (FPDF code in `make_pdf_bytes`).
- Persist users + responses to a database (e.g., Supabase or SQLite).
- Email the PDF automatically using a transactional email service (e.g., Resend).
- Convert this into a Next.js route for your production webapp, keeping the same JSON question format.
