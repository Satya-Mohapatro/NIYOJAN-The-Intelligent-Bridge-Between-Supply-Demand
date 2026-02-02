import sqlite3
import os
from transformers import pipeline

# Summarizer model (LLM-based)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/niyojan.db")

def generate_report():
    """
    Reads forecasts & alerts from DB and generates a summarized report.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT product, forecast, created_at FROM forecasts ORDER BY created_at DESC LIMIT 10")
    forecasts = cur.fetchall()

    cur.execute("SELECT product, forecast, alert, created_at FROM alerts ORDER BY created_at DESC LIMIT 10")
    alerts = cur.fetchall()

    conn.close()

    # Build a plain-text report
    report_text = "===  Niyojan Forecast & Alerts Report ===\n\n"

    report_text += "Recent Forecasts:\n"
    for p, f, t in forecasts:
        report_text += f"- {p}: {f:.2f} (at {t})\n"

    report_text += "\nRecent Alerts:\n"
    for p, f, a, t in alerts:
        report_text += f"- {p}: {a} [Forecast: {f:.2f}] ({t})\n"

    # Generate AI summary
    summary = summarizer(report_text, max_length=120, min_length=30, do_sample=False)[0]["summary_text"]

    final_report = f"{report_text}\n\n=== Summary ===\n{summary}"
    return final_report
