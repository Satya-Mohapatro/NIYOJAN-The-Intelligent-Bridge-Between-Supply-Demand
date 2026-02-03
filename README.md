# 🌾 Niyojan — Assitive AI for Demand Forecasting & Inventory Optimization

Niyojan is an **AI-driven demand forecasting platform** that combines **LSTM Time-Series Forecasting** with **GenAI (Google Gemini)** to predict demand, generate actionable inventory insights, and automate reporting.

It empowers businesses to optimize stock levels, avoid stockouts/overstocking, and make data-driven decisions through a modern, interactive dashboard.

---

## 🚀 Key Features

### 🧠 **Intelligent Forecasting**
*   **Time-Series Analysis**: Uses **LSTM (Long Short-Term Memory)** networks to predict sales demand for up to 12 weeks.
*   **Trend Detection**: Automatically identifies upward (↗), downward (↘), or stable (→) demand trends.

### 🤖 **GenAI Insight Engine**
*   **Powered by Google Gemini**: Analyzes forecast data to provide qualitative insights.
*   **Actionable Advice**: Suggests **Restock**, **Hold**, or **Reduce** decisions based on predicted demand vs. current inventory.
*   **Risk Assessment**: Flags inventory decisions as Low, Medium, or High risk.

### 📊 **Operational Dashboard**
*   **Interactive Visualization**: Visual charts for category-wise demand and product trends using Recharts.
*   **Real-time Alerts**: Automatic flagging of critical stock levels.
*   **PDF Reporting**: One-click generation of professional forecast reports with visualizations.
*   **Email Automation**: Send reports directly to managers via SMTP (Gmail).

---

## 🧩 Repository Structure

```
niyojan-new/
│
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entrypoint
│   │   ├── core/            # Core configurations
│   │   └── services/        # Business logic services
│   ├── reports/             # Generated PDF reports storage
│   └── tests/               # Backend tests
│
├── frontend/                # React + Vite Application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Application pages
│   │   └── assets/          # Static assets
│   └── package.json
│
├── database/
│   ├── niyojan.db           # SQLite database
│   ├── db_manager.py        # Database handling logic
│   └── schema.sql           # Database schema definitions
│
├── genai/                   # GenAI & LLM Integration
│   ├── insight_engine.py    # Logic for generating insights
│   ├── llm_client.py        # Google Gemini Client wrapper
│   └── prompt_templates.py  # System & User prompts for LLM
│
├── lstm/                    # Forecasting Models
│   ├── global_lstm_model/   # Trained LSTM model artifacts
│   └── global_lstm_demand_forecasting.ipynb # Training notebook
│
├── utils/
│   ├── email_handler.py     # SMTP Email utility
│   ├── decision_engine.py   # Rule-based decision logic
│   └── pdf_report_generator.py # PDF generation using ReportLab
│
├── .env                     # Environment variables (Sensitive)
├── pyproject.toml           # Poetry dependency management
└── README.md                # Project Documentation
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, FastAPI, Pydantic |
| **Frontend** | React, Vite, TypeScript, Tailwind CSS, Recharts |
| **AI / ML** | TensorFlow (LSTM), Google Gemini (GenAI) |
| **Database** | SQLite |
| **Reporting** | ReportLab (PDF), Python `email` lib |

---

## 📦 Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/r0hi7/Niyojan.git
cd Niyojan
```

### 2. Backend Setup
You can use **Poetry** (recommended) or **pip**.

#### Option A: Using Poetry
```bash
poetry install
poetry shell
```

#### Option B: Using Pip
```bash
# Create virtual environment
python -m venv venv
# Activate it (Windows)
venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

---

## ⚙️ Configuration

Create a `.env` file in the **project root** and add the following keys:

```ini
# --- Security ---
JWT_SECRET=your_super_secret_jwt_key
JWT_EXPIRE_MINUTES=720

# --- GenAI (Google Gemini) ---
GEMINI_API_KEY=your_google_gemini_api_key

# --- Email (Gmail App Password) ---
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

> **Note**: For `SMTP_PASSWORD`, generate an **App Password** from your Google Account settings if 2FA is enabled.

---

## ▶️ Running the Application

### 1. Initialize Database
Ensure the database is set up before running the app.
```bash
cd database
python create_db.py
cd ..
```
*This creates a default admin user:* `admin@niyojan.ai` / `admin123`

### 2. Start Backend
From the project root:
```bash
uvicorn backend.app:app --reload
```
*API Docs available at:* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Start Frontend
Open a new terminal:
```bash
cd frontend
npm run dev
```
*App available at:* [http://localhost:5173](http://localhost:5173)

---

## 💡 User Guide

1.  **Login**: Use the admin credentials (`admin@niyojan.ai` / `admin123`).
2.  **Upload Data**: Go to the **Dashboard** and upload a CSV file with columns: `Product_ID`, `Product_Name`, `Category`, `Week`, `Sales_Quantity`.
3.  **Run Forecast**: The system handles the rest—predicting sales and generating alerts.
4.  **View Insights**: Click on individual products to see **GenAI-powered insights** (Restock/Hold recommendations).
5.  **Reports**: Navigate to the **Reports** tab to view or email the PDF summary.

---

## 🤝 Contributing
Contributions are welcome! Please fork the repo and submit a Pull Request.

## ⭐ Support
If you like Niyojan, please start the repository!
