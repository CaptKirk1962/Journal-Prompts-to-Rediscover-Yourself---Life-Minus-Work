
import os
import io
import json
import datetime
import streamlit as st
from fpdf import FPDF

# ---------- CONFIG ----------
APP_TITLE = "Life Minus Work — Reflection Quiz (15 questions)"
REPORT_TITLE = "Your Reflection Report"
THEMES = ["Identity", "Growth", "Connection", "Peace", "Adventure", "Contribution"]

# Optional: Use OpenAI for personalized text if key provided
USE_AI = True if os.getenv("OPENAI_API_KEY") else False

if USE_AI:
    try:
        from openai import OpenAI
        openai_client = OpenAI()
    except Exception:
        USE_AI = False

# ---------- UTILS ----------
def load_questions(path="questions.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"], data["themes"]

def compute_scores(answers, questions):
    scores = {t: 0 for t in THEMES}
    for q in questions:
        qid = q["id"]
        choice_idx = answers.get(qid)
        if choice_idx is None:
            continue
        try:
            choice = q["choices"][choice_idx]
        except IndexError:
            continue
        for theme, val in choice.get("weights", {}).items():
            scores[theme] = scores.get(theme, 0) + val
    return scores

def top_themes(scores, k=3):
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in sorted_items[:k]]

def ai_paragraph(prompt):
    if not USE_AI:
        return None
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a warm, practical life coach. Be concise and supportive."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return None

def generate_report_text(email, scores, top3):
    # Deterministic fallback copy if no AI
    base_copy = []
    base_copy.append("Thank you for completing the Reflection Quiz. Below are your top themes and next-step ideas tailored for you.")
    for theme in top3:
        base_copy.append(f"- {theme}: Consider one simple action this week to build momentum in this area.")
    base_copy.append("Tip: Small consistent actions beat big one-off efforts. Be kind to yourself as you experiment.")
    fallback = "\n".join(base_copy)

    if USE_AI:
        score_lines = ", ".join([f"{k}: {v}" for k, v in scores.items()])
        prompt = f\"\"\"Create a friendly, empowering summary (140-200 words) for a user with these theme scores: {score_lines}.
Top 3 themes: {', '.join(top3)}.
Voice: empathetic, practical, and encouraging; avoid medical claims.
Give 3 short bullet-point actions for the next 7 days, tailored to the themes.
Do not mention scores. Address the reader as 'you'.\"\"\"
        ai_text = ai_paragraph(prompt)
        if ai_text:
            return ai_text
    return fallback

def make_pdf_bytes(name_email, scores, top3, narrative):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, REPORT_TITLE, ln=True)
    pdf.set_font("Arial", "", 12)
    today = datetime.date.today().strftime("%d %b %Y")
    pdf.cell(0, 8, f"Date: {today}", ln=True)
    if name_email:
        pdf.cell(0, 8, f"Email: {name_email}", ln=True)
    pdf.ln(6)

    # Scores
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Your Theme Snapshot", ln=True)
    pdf.set_font("Arial", "", 12)
    for t in THEMES:
        pdf.cell(0, 7, f"- {t}: {scores.get(t, 0)}", ln=True)
    pdf.ln(4)

    # Top themes
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Top Themes", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 6, ", ".join(top3))
    pdf.ln(2)

    # Narrative / Guidance
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Your Personalized Guidance", ln=True)
    pdf.set_font("Arial", "", 12)
    for line in narrative.split("\n"):
        pdf.multi_cell(0, 6, line)

    # Footer
    pdf.ln(6)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 6, "Life Minus Work • This report is a starting point for reflection. Nothing here is medical or financial advice.")

    # Export to bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes

# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="centered")
st.title(APP_TITLE)
st.write("Answer 15 questions, get an instant personalized PDF.")

with st.form("email_form"):
    email = st.text_input("Your email (to save your results and for your download link)", placeholder="you@example.com")
    consent = st.checkbox("I agree to receive my results and occasional updates from Life Minus Work.")
    submitted = st.form_submit_button("Start Quiz")
    if submitted and (not email or not consent):
        st.error("Please enter your email and give consent to continue.")

if submitted and email and consent:
    st.session_state["email"] = email
    st.success("Great! Scroll down to begin.")

if "email" in st.session_state:
    questions, _ = load_questions("questions.json")
    st.header("Your Questions")
    st.caption("You can scroll and answer at your own pace.")

    answers = {}
    for q in questions:
        st.subheader(q["text"])
        options = [c["label"] for c in q["choices"]]
        choice = st.radio("Choose one:", options, index=None, key=q["id"])
        if choice is not None:
            answers[q["id"]] = options.index(choice)
        st.divider()

    if len(answers) < len(questions):
        st.info(f"Answered {len(answers)} of {len(questions)} questions. Keep going!")
    else:
        if st.button("Finish and Generate My Report"):
            scores = compute_scores(answers, questions)
            top3 = top_themes(scores, 3)
            narrative = generate_report_text(st.session_state["email"], scores, top3)
            pdf_bytes = make_pdf_bytes(st.session_state["email"], scores, top3, narrative)

            # Instant download button
            st.success("Your personalized report is ready!")
            st.download_button(
                label="Download Your PDF Report",
                data=pdf_bytes,
                file_name="LifeMinusWork_Reflection_Report.pdf",
                mime="application/pdf"
            )

            # Save raw data locally (CSV-ish) for quick testing
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            row = {
                "timestamp": ts,
                "email": st.session_state["email"],
                "scores": scores,
                "top3": top3,
            }
            try:
                import csv, os
                csv_path = "responses.csv"
                file_exists = os.path.exists(csv_path)
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["timestamp", "email", "scores", "top3"])
                    writer.writerow([row["timestamp"], row["email"], json.dumps(scores), json.dumps(top3)])
                st.caption("Saved locally to responses.csv (for demo/testing).")
            except Exception as e:
                st.caption("Could not save responses locally (demo only).")

else:
    st.info("Enter your email above and tick the consent box to begin.")
