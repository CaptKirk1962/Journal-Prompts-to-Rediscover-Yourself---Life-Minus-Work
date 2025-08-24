
# Life Minus Work — Streamlit Quiz (Full 15Q)

This package contains a ready-to-deploy Streamlit app:
- Robust loader for `questions.json` using `Path(__file__).parent`
- Writes responses to `/tmp/responses.csv` (Cloud-safe)
- Generates instant PDF with FPDF
- Optional AI narrative if `OPENAI_API_KEY` is set

## Deploy on Streamlit Cloud
1) Upload all files to the root of your GitHub repo.
2) Ensure App Settings → Main file path = `app.py`.
3) `runtime.txt` pins Python 3.10.
4) (Optional) Add `OPENAI_API_KEY` in **Settings → Secrets**.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
