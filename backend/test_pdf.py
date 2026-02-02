import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_report_generator import generate_pdf_report

overview = {
    "products": 8,
    "horizon": 4,
    "forecast_total": 3189,
    "avg_growth": 3.9
}

categories = [
    {"category": "Staples", "products": 3, "total": 1317, "avgPerProduct": 439},
    {"category": "Dairy", "products": 1, "total": 350, "avgPerProduct": 350},
    {"category": "Beverages", "products": 1, "total": 283, "avgPerProduct": 283}
]

top_products = [
    {"name": "Toor Dal", "id": "P008", "trend": "Highest growth (+18%)"},
    {"name": "Milk", "id": "P005", "trend": "Rising demand (+10%)"},
    {"name": "Soft Drinks", "id": "P007", "trend": "Decreasing demand (-8%)"}
]

alerts = [
    {"product": "Toor Dal (P008)", "forecast": 113, "alert": " High demand expected. Restock soon.", "created_at": "2025-11-11"},
    {"product": "Milk (P005)", "forecast": 84, "alert": " Stock level balanced.", "created_at": "2025-11-11"},
]

generate_pdf_report("forecast_report.pdf", overview, categories, top_products, alerts)
print(" Report generated: forecast_report.pdf")
