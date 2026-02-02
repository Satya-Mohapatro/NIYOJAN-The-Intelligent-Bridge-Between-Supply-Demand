# 🌾 Niyojan — Intelligent Demand Forecasting System

Niyojan is an AI-driven demand forecasting platform that uses machine learning to predict product demand, generate visual insights, and automatically email PDF reports.  
It integrates a **FastAPI backend**, **React + Vite frontend**, and **TensorFlow-based forecasting engine**.


---

## 🧩 Repository Structure 
```
niyojan-new/
│
├── backend/
│ ├── app.py # FastAPI app entrypoint
│ └── reports/ # Generated PDF reports
│
├── database/
│ ├── niyojan.db # SQLite database
│ └── schema.sql # Database schema
│
├── frontend/
│ ├── src/ # React + Vite source
│ ├── package.json
│ └── vite.config.ts
│
├── utils/   
│ ├── email_handler.py # Handles the email sending
│ ├── decision_engine.py # generate an inventory alert message.
│ ├── forecast_engine.py # Not used in the current version
│ ├── report_generator.py # Not used in the current version
│ └── pdf_generator.py # Generate PDF reports
│ 
├── .env # Environment variables (ignored in git)
├── poetry.lock / pyproject.toml # Python dependency management
└── README.md
```
---

## 🚀 Key Features  
✅ Upload CSV files and get real-time demand forecasts  
✅ Visual charts for weekly and category-wise insights  
✅ AI-generated alerts for stock management  
✅ Automatically generate and download forecast PDF reports  
✅ Send forecast reports via email with Gmail App Password authentication   

---

## 🛠 Tech Stack  
- **Backend**: FastAPI, TensorFlow, ReportLab
- **Frontend**: React (Vite + TypeScript), Tailwind CSS, Recharts
- **Machine Learning / Time Series**: Python, LSTM models (in `lstm/`)  
- **Database**: SQLite    
- **Project management**: Poetry (`pyproject.toml`), or pip + `requirements.txt`  

---

## 📦 Installation & Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/r0hi7/Niyojan.git
cd Niyojan
```

---

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

#### Backend (Python + FastAPI)

If you are using **Poetry**:

```bash
poetry install
poetry env activate
```

Or using plain **pip**:

```bash
cd backend
pip install -r requirements.txt
```

#### Frontend (React + Vite)

```bash
cd frontend
npm install
```

---

### 4. Configure environment variables

Create a `.env` file in the **project root** (same level as `backend/` and `frontend/`) and add the following:

```bash
# JWT Secret
JWT_SECRET=super_secret_key_change_this

# Gmail SMTP setup
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Optional - runtime settings
JWT_EXPIRE_MINUTES=720
```

> ⚠️ **Important:**
> The `SMTP_PASSWORD` must be a **Gmail App Password**, not your regular Gmail password.
> To generate it:
>
> 1. Visit [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 2. Select **Mail** and **Windows Computer**
> 3. Copy the 16-character password and paste it here.

---

### 5. Initialize the database

Run this inside the `database` directory:

```bash
cd database
python create_db.py
```

This will automatically create:

* `niyojan.db` — the main SQLite database
* a default admin user:

  ```
  Email: admin@niyojan.ai
  Password: admin123
  ```

---

### 6. Run the Backend

From the project root or backend directory:

```bash
uvicorn backend.app:app --reload
```

Then open your browser and visit:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 7. Run the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

Now visit:
👉 [http://localhost:5173](http://localhost:5173)

Login with:

```
Email: admin@niyojan.ai
Password: admin123
```

---

## 🧮 Model Workflow

1. **Upload Data** → User uploads a CSV (columns: `Product_ID`, `Product_Name`, `Category`, `Week`, `Sales_Quantity`).
2. **Forecasting Engine** → LSTM / ML-based model predicts multi-week sales horizon.
3. **Alert Generation** → System flags products showing high or low demand using decision rules (`utils/decision_engine.py`).
4. **Database Storage** → Forecasts and alerts are saved in `niyojan.db`.
5. **PDF Report Generation** → A styled report (with emojis/icons) is created via `utils/pdf_report_generator.py`.
6. **Email Dispatch (Admin Only)** → Admin can send the report via email to one or more recipients.

---

## 📄 Reports & Alerts

### 📊 Reports

* Generated automatically when a forecast is made.
* Stored in `/backend/reports/`.
* Accessible through:

  * `/report/view` → View inline in browser
  * `/report/download` → Download the PDF
  * `/send-report` → Email the report (admin only)

### ⚠️ Alerts

* Alerts summarize forecast conditions:

  * ⚠️ High demand → "Consider restocking"
  * ✅ Balanced → "Stock levels are stable"
* Displayed in the **Alerts tab** of the UI and saved to the database.

---

## 💡 Example Workflow

| Step | Action                 | Output                              |
| ---- | ---------------------- | ----------------------------------- |
| 1    | Upload a CSV file      | Data parsed and validated           |
| 2    | Click “Run Forecast”   | Predictions generated               |
| 3    | View “Results” Tab     | Charts and tables                   |
| 4    | Switch to “Alerts” Tab | Forecast-based alerts               |
| 5    | Go to “Report” Tab     | View, download, or email PDF report |

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are always welcome!
To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m "Add feature"`)
4. Push to your fork and submit a Pull Request

---

## ⭐ Support the Project

If you found **Niyojan** helpful:

* 🌟 Star the repository on GitHub
* 🐛 Report bugs or suggest features via Issues tab
* 📣 Share your feedback!

---
