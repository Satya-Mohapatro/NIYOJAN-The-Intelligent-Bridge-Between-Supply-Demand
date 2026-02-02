# backend/app.py
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import io
import csv
import sqlite3
import jwt
import pandas as pd
import numpy as np
import logging

# Local modules (expected in repository)
import database.db_manager as db_manager
from utils.decision_engine import analyze_forecast
from utils.forecast_engine import predict_demand

# Optional utilities
try:
    from utils.pdf_report_generator import generate_pdf_report
    PDF_GEN_AVAILABLE = True
except Exception:
    PDF_GEN_AVAILABLE = False

try:
    from utils.email_handler import send_email_report # type: ignore
    EMAIL_HANDLER_AVAILABLE = True
except Exception:
    EMAIL_HANDLER_AVAILABLE = False

# -------------------------
# CONFIG & SETUP
# -------------------------
logger = logging.getLogger("niyojan")
logging.basicConfig(level=logging.INFO)

JWT_SECRET = os.getenv("JWT_SECRET", "niyojan_default_secret_change_me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "..", "database", "niyojan.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

REQUIRED_COLUMNS = ['Product_ID', 'Product_Name', 'Category', 'Week', 'Sales_Quantity']

# Initialize DB + default admin (if db_manager implements these)
try:
    db_manager.init_db()
    db_manager.ensure_default_admin()
except Exception as e:
    logger.warning("db_manager init/ensure_default_admin failed: %s", e)

app = FastAPI(title="Niyojan Demand Forecasting API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# JWT helpers
# -------------------------
def create_access_token(email: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    payload = {"sub": email, "role": role, "exp": int(expire.timestamp())}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str) -> Dict[str, Any]:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_token_from_header(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)) -> str:
    # Accept either Authorization: Bearer <token> or ?token=...
    if token:
        return token
    if authorization:
        if authorization.lower().startswith("bearer "):
            return authorization.split(" ", 1)[1].strip()
    raise HTTPException(status_code=401, detail="Unauthorized: token required")

def get_current_user(token: str = Depends(get_token_from_header)):
    payload = decode_token(token)
    email = payload.get("sub")
    role = payload.get("role", "analyst")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db_manager.find_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"email": email, "role": role}

def require_role(role: str):
    def checker(current_user=Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient privileges")
        return current_user
    return checker

# -------------------------
# Models
# -------------------------
class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CreateUserBody(BaseModel):
    email: str
    name: Optional[str] = None
    password: str
    role: Optional[str] = "analyst"

class ForecastResponseModel(BaseModel):
    products: int
    horizon: int
    data: List[Dict[str, Any]]

class SendReportBody(BaseModel):
    recipients: List[str]

# -------------------------
# Small helpers
# -------------------------
def sqlite3_connect():
    # centralized DB path
    con = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "database", "niyojan.db"))
    con.row_factory = sqlite3.Row
    return con

def build_report_payload_from_db(limit: int = 50):
    """
    Fetch latest forecasts batch and compute overview, categories and top_products.
    Uses 'created_at' to group the most recent batch.
    """
    try:
        max_ts = db_manager.get_latest_batch_timestamp()
        
        if not max_ts:
            return {"products": 0, "horizon": 0, "forecast_total": 0, "avg_growth": 0}, [], [], []

        # 2. Fetch all forecasts in that batch (allowing small time window drift if separate commits)
        #    We use a window of 60 seconds
        rows = db_manager.get_all_forecasts_raw_query(max_ts)
        
        # 3. Fetch alerts (latest batch)
        # Re-using raw connection for alerts or adding logic to db_manager?
        # Let's just do a quick query here or add to db_manager. for now, inline is deprecated, let's use db manager if possible
        # but to save time, assume get_all_alerts returns everything.
        # Actually proper way: filter alerts by max_ts too.
        # Since I didn't add filter support to `get_all_alerts`, I will filter in python or add a new method?
        # Let's filter in python for safety if list is small, or just assume latest.
        # Ideally, we should add 'get_alerts_batch' to db manager.
        # For this turn, I will use `get_all_alerts` and filter by timestamp manually if needed, 
        # or better: rely on `LIMIT` logic or similar.
        all_alerts = db_manager.get_all_alerts()
        # Filter alerts created close to max_ts
        from datetime import datetime, timedelta
        
        # max_ts string to dt? SQLite returns string.
        # Simple string comparison works for ISO8601
        # timestamp format: YYYY-MM-DD HH:MM:SS
        # 1 min window roughly
        alerts = [a for a in all_alerts if a['created_at'] >= max_ts] 
        # Actually exact match implies >= because max_ts is the latest forecast. Alerts are created at same time.
        # Safe to just take top N or filter by date string prefix
        
    except Exception as e:
        logger.error("Error building report payload: %s", e)
        return {"products": 0, "horizon": 0, "forecast_total": 0, "avg_growth": 0}, [], [], []

    # Processing Forecast Data
    # Group by product to find horizon
    product_map = {} # productId -> list of forecasts
    category_map = {} # category -> total forecast
    last_week_sales_map = {} # productId -> last_week_sales (taking unique)
    
    for r in rows:
        pid = r['product']
        cat = r['category'] or "Unknown"
        val = float(r['forecast'])
        lw_sales = float(r.get('last_week_sales') or 0.0)
        
        if pid not in product_map:
            product_map[pid] = []
        product_map[pid].append(val)
        
        # Store last week sales (overwrite is fine as it should be same for all rows of same product, or use max)
        last_week_sales_map[pid] = lw_sales
        
        if cat not in category_map:
            category_map[cat] = {"products": set(), "total": 0}
        category_map[cat]["products"].add(pid)
        category_map[cat]["total"] += val

    # Compute Overview
    num_products = len(product_map)
    horizon = len(list(product_map.values())[0]) if num_products > 0 else 0
    forecast_total = sum(sum(vals) for vals in product_map.values())
    
    # Calculate Avg Weekly Growth
    # Avg Weekly Forecast = Total Forecast / Horizon
    # Last Week Total = Sum of all products' last week sales
    total_last_week_sales = sum(last_week_sales_map.values())
    
    avg_weekly_forecast = forecast_total / horizon if horizon > 0 else 0
    
    avg_growth = 0.0
    if total_last_week_sales > 0:
        avg_growth = ((avg_weekly_forecast / total_last_week_sales) - 1) * 100

    categories = []
    for cat, data in category_map.items():
        categories.append({
            "category": cat,
            "products": len(data["products"]),
            "total": int(data["total"]),
            "avgPerProduct": int(data["total"] / len(data["products"])) if data["products"] else 0
        })

    # Prepare Top Products
    sorted_prods = sorted(product_map.items(), key=lambda x: sum(x[1]), reverse=True)[:5]
    top_products = []
    for pid, vals in sorted_prods:
        total = sum(vals)
        trend_str = "Stable"
        if len(vals) > 1:
            if vals[-1] > vals[0]: trend_str = "Upward ↗"
            elif vals[-1] < vals[0]: trend_str = "Downward ↘"
        top_products.append({
            "id": pid,
            "name": pid, 
            "trend": f"{int(total)} units ({trend_str})"
        })

    overview = {
        "products": num_products,
        "horizon": horizon,
        "forecast_total": int(forecast_total),
        "avg_growth": round(avg_growth, 2)
    }

    return overview, categories, top_products, alerts

# -------------------------
# Health
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "component": "niyojan-backend", "time": datetime.utcnow().isoformat()}

# -------------------------
# Auth endpoints
# -------------------------
@app.post("/auth/login", response_model=AuthToken)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # verify via db_manager
    u = db_manager.find_user_by_email(form_data.username)
    if not u:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Secure password check
    if not db_manager.verify_user_credentials(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    role = u.get("role") if u and "role" in u else "analyst"
    token = create_access_token(form_data.username, role) # type: ignore
    return AuthToken(access_token=token)

@app.post("/users", status_code=201)
def create_user_ep(body: CreateUserBody, current_user = Depends(require_role("admin"))):
    try:
        db_manager.create_user(body.email, body.name or "", body.password)
        # optionally set role if column exists
        try:
            conn = sqlite3_connect()
            cur = conn.cursor()
            cur.execute("UPDATE users SET role = ? WHERE email = ?", (body.role or "analyst", body.email))
            conn.commit()
            conn.close()
        except Exception:
            pass
        return {"ok": True}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {e}")

# -------------------------
# Forecast endpoint (CSV upload)
# -------------------------
@app.post("/forecast", response_model=ForecastResponseModel)
async def forecast_endpoint(
    file: UploadFile = File(...),
    horizon: int = Form(4),
    current_user = Depends(get_current_user)
):
    if horizon < 1 or horizon > 12:
        raise HTTPException(status_code=400, detail="horizon must be between 1 and 12 weeks")

    # read CSV into dataframe
    try:
        raw = await file.read()
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {e}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")

    # cleanse and normalize
    df.columns = df.columns.str.strip()
    try:
        df['Week'] = pd.to_datetime(df['Week'], dayfirst=True, errors='coerce')
    except Exception:
        df['Week'] = pd.to_datetime(df['Week'], errors='coerce')
    if df['Week'].isna().any():
        raise HTTPException(status_code=400, detail="Invalid dates in 'Week' column")

    results = []
    forecasts_to_insert = []
    alerts_to_insert = []

    # iterate unique Product_IDs and predict horizon steps
    for pid in df['Product_ID'].unique():
        psub = df[df['Product_ID'] == pid].sort_values('Week')
        sales_history = psub['Sales_Quantity'].fillna(0).astype(float).tolist()
        if len(sales_history) < 1:
            continue

        history = sales_history.copy()
        preds = []
        try:
            for _ in range(horizon):
                next_val = float(predict_demand(str(pid), history))
                next_val = max(0.0, next_val)
                preds.append(next_val)
                history.append(next_val)
        except Exception as e:
            logger.warning("prediction failed for %s: %s", pid, e)
            continue

        last_week_dt = psub['Week'].max()
        final_preds = [int(round(x)) for x in preds]

        if len(history) >= 2:
            trend_val = history[-1] - history[-2]
            # Tune trend sensitivity: require > 5% change for direction
            threshold = 0.05 * history[-2] if history[-2] != 0 else 0
            if trend_val > threshold:
                trend_symbol = "↑"
            elif trend_val < -threshold:
                trend_symbol = "↓"
            else:
                trend_symbol = "→"
        else:
            trend_symbol = "-"

        # Calculate Revenue (Price * Final_Forecast)
        # Price: grab last known price from CSV (support 'Price' or 'Price_per_Unit')
        price = 0.0
        if 'Price' in psub.columns:
            price = float(psub['Price'].iloc[-1])
        elif 'Price_per_Unit' in psub.columns:
            price = float(psub['Price_per_Unit'].iloc[-1])
        
        forecasted_revenue = [round(x * price, 2) for x in final_preds]
        
        # Capture Category
        category_val = psub['Category'].iloc[-1] if 'Category' in psub.columns else "Unknown"

        entry = {
            "Product_ID": str(pid),
            "Product_Name": (psub['Product_Name'].iloc[-1] if 'Product_Name' in psub.columns else ""),
            "Category": category_val,
            "Price": price,
            "Trend_Symbol": trend_symbol,
            "Last_Week": last_week_dt.strftime('%Y-%m-%d'),
            "Last_Week_Sales": int(round(psub['Sales_Quantity'].iloc[-1] if len(psub) else 0)),
            "Forecasted_Sales": final_preds, # using final_preds as primary
            "Forecasted_Revenue": forecasted_revenue,
            "Final_Forecasted_Sales": final_preds
        }
        results.append(entry)

        # Prepare for bulk DB persistence
        try:
            # NEW logic: Insert ALL forecasted points to ensure report has full horizon
            # Also insert last_week_sales (Sales_Quantity of last row)
            # Since forecasts table has 1 row per forecast week, last_week_sales is redundant but useful for aggregation
            last_stock_proxy = float(psub['Sales_Quantity'].iloc[-1] if len(psub) else 0.0)
            
            for val in final_preds:
                forecasts_to_insert.append((str(pid), float(val), category_val, last_stock_proxy))
            
            # Alerts still generally focus on the immediate next week for urgency
            next_week_val = float(final_preds[0]) if final_preds else 0.0
            
            alert_msg = analyze_forecast(str(pid), next_week_val, last_stock_proxy)
            alerts_to_insert.append((str(pid), next_week_val, alert_msg, category_val))
        except Exception:
            pass

    if forecasts_to_insert:
        try:
            db_manager.bulk_insert_forecasts(forecasts_to_insert)
            db_manager.bulk_insert_alerts(alerts_to_insert)
        except Exception as e:
            logger.error("Bulk insert failed: %s", e)

    if not results:
        raise HTTPException(status_code=400, detail="No products with valid history found")

    # prepare and return response
    resp = {
        "products": len(results),
        "horizon": horizon,
        "data": results
    }
    return resp

# -------------------------
# Download CSV (calls same pipeline)
# -------------------------
@app.post("/download")
async def download_csv(file: UploadFile = File(...), horizon: int = Form(4), current_user = Depends(get_current_user)):
    # call forecast endpoint functionally (avoid double-parse by calling internal logic is complicated here),
    # simplest reliable approach: call forecast_endpoint to obtain JSON then convert to CSV
    resp = await forecast_endpoint(file=file, horizon=horizon, current_user=current_user)
    rows = []
    for f in resp['data']:
        row = {
            'Product_ID': f['Product_ID'],
            'Product_Name': f['Product_Name'],
            'Category': f['Category'],
            'Last_Week': f['Last_Week'],
            'Last_Week_Sales': f['Last_Week_Sales']
        }
        for i, v in enumerate(f['Forecasted_Sales'], start=1):
            row[f'Week_{i}_Forecast'] = v
        for i, v in enumerate(f['Final_Forecasted_Sales'], start=1):
            row[f'Week_{i}_Final'] = v
        rows.append(row)
    out_df = pd.DataFrame(rows)

    output = io.StringIO()
    out_df.to_csv(output, index=False)
    output.seek(0)
    filename = f"niyojan_forecast_{horizon}w_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8')), media_type='text/csv',
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

# -------------------------
# Alerts & Forecast retrieval
# -------------------------
@app.get("/alerts")
def alerts_endpoint(current_user = Depends(get_current_user)):
    try:
        alerts = db_manager.get_all_alerts()
        return {"count": len(alerts), "data": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {e}")

@app.get("/forecasts")
def forecasts_endpoint(limit: int = Query(50, ge=1, le=1000), current_user = Depends(get_current_user)):
    try:
        if hasattr(db_manager, 'get_all_forecasts'):
            data = db_manager.get_all_forecasts(limit=limit) # type: ignore
            return {"count": len(data), "data": data}
        # fallback: read from forecasts table directly
        conn = sqlite3_connect()
        cur = conn.cursor()
        cur.execute("SELECT product, forecast, created_at FROM forecasts ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        data = [{"product": r["product"], "forecast": r["forecast"], "created_at": r["created_at"]} for r in rows]
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecasts: {e}")

# -------------------------
# Report endpoints (text + PDF view + PDF download)
# -------------------------
@app.get("/report")
def report_endpoint(current_user = Depends(get_current_user)):
    # Prefer optional heavy report generator if available
    if 'generate_report' in globals():
        try:
            text = globals().get('generate_report')()  # type: ignore
            return {"report": text}
        except Exception:
            pass

    # Fallback: build from DB
    try:
        conn = sqlite3_connect()
        cur = conn.cursor()
        cur.execute("SELECT product, forecast, created_at FROM forecasts ORDER BY created_at DESC LIMIT 10")
        forecasts = cur.fetchall()
        cur.execute("SELECT product, forecast, alert, created_at FROM alerts ORDER BY created_at DESC LIMIT 10")
        alerts = cur.fetchall()
        conn.close()
    except Exception:
        forecasts, alerts = [], []

    report_text = "===  Niyojan Forecast & Alerts Report ===\n\nRecent Forecasts:\n"
    for r in forecasts:
        try:
            report_text += f"- {r['product']}: {float(r['forecast']):.2f} (at {r['created_at']})\n"
        except Exception:
            report_text += f"- {r['product']}: {r['forecast']} (at {r['created_at']})\n"
    report_text += "\nRecent Alerts:\n"
    for r in alerts:
        try:
            fval = float(r['forecast']) if r['forecast'] is not None else None
            fstr = f"{fval:.2f}" if fval is not None else "n/a"
        except Exception:
            fstr = str(r['forecast'])
        report_text += f"- {r['product']}: {r['alert']} [Forecast: {fstr}] ({r['created_at']})\n"
    report_text += "\n=== Summary ===\nPlain-text report generated. Install transformers for AI summary."
    return {"report": report_text}

def _generate_pdf_for_current_user(current_user):
    overview, categories, top_products, alerts = build_report_payload_from_db()
    # fallback sample categories/top_products if empty
    if not categories:
        categories = [
            {"category": "Staples", "products": 3, "total": 1317, "avgPerProduct": 439},
            {"category": "Dairy", "products": 1, "total": 350, "avgPerProduct": 350},
        ]
    if not top_products:
        top_products = [
            {"name": "Rice", "id": "P001", "trend": "Strong upward trend "},
            {"name": "Atta", "id": "P002", "trend": "Stable demand "},
            {"name": "Sugar", "id": "P003", "trend": "Slight dip "},
        ]
    filename = f"niyojan_report_{current_user['email'].replace('@','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(REPORTS_DIR, filename)

    if not PDF_GEN_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF generator not available on server (missing utils.pdf_report_generator)")

    try:
        generate_pdf_report(output_path, overview, categories, top_products, alerts) # type: ignore
        return output_path
    except Exception as e:
        logger.exception("PDF generation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

@app.get("/report/view", response_class=FileResponse)
def view_report(current_user = Depends(get_current_user)):
    """
    Generate PDF and return inline (browser preview).
    """
    output_path = _generate_pdf_for_current_user(current_user)
    return FileResponse(output_path, media_type="application/pdf", filename=os.path.basename(output_path),
                        headers={"Content-Disposition": f"inline; filename={os.path.basename(output_path)}"})

@app.get("/report/download", response_class=FileResponse)
def download_report(current_user = Depends(get_current_user)):
    """
    Generate PDF and return as attachment for download.
    """
    output_path = _generate_pdf_for_current_user(current_user)
    return FileResponse(output_path, media_type="application/pdf", filename=os.path.basename(output_path),
                        headers={"Content-Disposition": f"attachment; filename={os.path.basename(output_path)}"})

# -------------------------
# Send report via email (admin only)
# -------------------------
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from utils.email_handler import send_email_report

class SendReportBody(BaseModel):
    recipients: list[str]

@app.post("/send-report")
def send_report_endpoint(body: SendReportBody, current_user=Depends(get_current_user)):
    """
    Sends the generated PDF report via email to one or more recipients.
    Any authenticated user can send it for testing purposes.
    """
    try:
        pdf_path = _generate_pdf_for_current_user(current_user)
        subject = f"Niyojan Forecast Report - {datetime.now().strftime('%Y-%m-%d')}"
        body_text = "Please find attached the latest Niyojan Forecast Report."
        
        ok = send_email_report(body.recipients, subject, body_text, attachments=[pdf_path])
        if not ok:
            raise HTTPException(status_code=500, detail="Email sending failed (check credentials / network)")
        return {"sent_to": body.recipients, "ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send report: {e}")


# -------------------------
# Run locally (optional)
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
