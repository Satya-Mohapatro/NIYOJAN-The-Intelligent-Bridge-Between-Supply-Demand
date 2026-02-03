# Niyojan - Comprehensive Project Analysis & Code Deep Dive

This document serves as an exhaustive technical reference for the **Niyojan Demand Forecasting System**. It analyzes every directory, file, and significant function within the codebase.

---

## 1. 🏗 System Architecture Overview

Niyojan is a **Demand Forecasting & Inventory Optimization Platform** that uses a three-tier architecture:

1.  **Frontend (Presentation Layer)**:
    *   **Tech**: React (Vite), TypeScript, Tailwind CSS, Recharts.
    *   **Role**: Handles user interaction, file uploads, data visualization, and requesting AI insights.
    *   **Key File**: `frontend/src/pages/Dashboard.tsx` is the central hub.

2.  **Backend (Logic Layer)**:
    *   **Tech**: Python, FastAPI.
    *   **Role**: Exposes REST endpoints, manages authentication, runs forecast models (`lstm`), and orchestrates Generative AI (`genai`).
    *   **Key File**: `backend/app/main.py`.

3.  **Data & AI Layer**:
    *   **Storage**: SQLite (`database/niyojan.db`).
    *   **Forecasting**: TensorFlow/Keras LSTM model (`lstm/global_lstm_model`).
    *   **GenAI**: Google Gemini Pro/Flash (`genai/llm_client.py`).

---

## 2. 📂 Backend Code Deep Dive

### `backend/app/main.py`
The entry point for the FastAPI server. It stitches together all utilities.

*   **Authentication**:
    *   `create_access_token()`: Generates JWTs using `HS256`.
    *   `get_current_user()`: Dependency that decodes the JWT and validates the user against the DB.
    *   `login()`: Endpoint `/auth/login`. Validates email/password hash using `db_manager.verify_user_credentials`.

*   **Forecasting Logic (`/forecast`)**:
    1.  **Input Parsing**: Reads CSV using `pandas`. Validates columns (`Product_ID`, `Week`, `Sales_Quantity`).
    2.  **Prediction Loop**: Iterates through each unique product:
        *   Calls `predict_demand(product_id, history)` from `utils.forecast_engine`.
        *   Appends prediction to history to forecast the *next* week (Rolling Forecast).
    3.  **Trend Calculation**: Compares last two history points. If change > 5%, marks as `↑` or `↓`.
    4.  **Persistence**: Calls `db_manager.bulk_insert_forecasts` to save results.
    5.  **Alert Generation**: Calls `analyze_forecast()` to determine risk (Restock/Hold) and saves via `bulk_insert_alerts`.

*   **Reporting (`/report/view`, `/report/download`)**:
    *   Fetches latest forecast data.
    *   Calls `generate_pdf_report()` from `utils.pdf_report_generator`.
    *   Returns the PDF file inline or as an attachment.

*   **GenAI Insights (`/insight`)**:
    *   Receives structured data (Product Name, Current Stock, Forecast).
    *   Constructs a prompt using `ForecastSummary` and `InventoryStatus` schemas.
    *   Calls `generate_insights_async` to query Google Gemini.

### `database/`
*   **`schema.sql`**:
    *   `users`: Stores `email`, `password_hash`, `salt`, `role`.
    *   `forecasts`: Stores `product`, `forecast`, `category`, `last_week_sales`.
    *   `alerts`: Stores `product`, `alert`, `forecast`.
*   **`db_manager.py`**:
    *   `init_db()`: Executes `schema.sql`.
    *   `create_user()`, `verify_user_credentials()`: Handles secure password hashing (PBKDF2-HMAC-SHA256) with unique salts.
    *   `bulk_insert_forecasts/alerts()`: Optimized `executemany` calls for high performance.
    *   `get_latest_batch_timestamp()`: Finds the timestamp of the most recent forecast run to filter reports.

### `genai/` (Google Gemini Integration)
*   **`llm_client.py`**:
    *   `call_llm()`: Wrapper for `google.generativeai`. Uses model `gemini-flash-latest` (optimized for speed/cost).
    *   `temperature=0.2`: Sets a low temperature for consistent, factual outputs.
*   **`insight_engine.py`**:
    *   `generate_insights()`:
        *   Takes `InsightInput` Pydantic model.
        *   Serializes it to JSON.
        *   Fills `USER_PROMPT_TEMPLATE`.
        *   Calls LLM.
        *   `extract_json()`: Robustly parses the response, handling potential Markdown code blocks (````json ... ````) returned by the LLM.
*   **`prompt_templates.py`**:
    *   Contains the "System Prompt" that defines the AI persona ("Supply Chain Intelligence Assistant").
    *   Requests output in **bilingual JSON** (English + Hindi).

### `lstm/` (Machine Learning)
*   **`global_lstm_model`**: A pre-trained TensorFlow/Keras SavedModel.
*   **`scaler.pkl`**: A pickled Scikit-Learn `MinMaxScaler` or `StandardScaler`.
*   **NOTE**: The training notebook `global_lstm_demand_forecasting.ipynb` shows how the model was created (likely using a sliding window approach on time-series data).

### `utils/`
*   **`forecast_engine.py`**:
    *   `predict_demand()`:
        *   Loads model & scaler on import (singleton pattern).
        *   **Preprocessing**: Reshapes input to `(1, timesteps, features)`. Handles padding if history < required timesteps.
        *   **Postprocessing**: Inverse transforms the model output to get the real unit sales.
*   **`decision_engine.py`**:
    *   `analyze_forecast()`:
        *   **Logic**: `Ratio = Forecast / Current_Stock`.
        *   **Rules**:
            *   Ratio > 1.2 ⇒ **High Risk** (Restock).
            *   Ratio < 0.5 ⇒ **Medium Risk** (Reduce/Overstock).
            *   Else ⇒ **Low Risk** (Stable).
*   **`pdf_report_generator.py`**:
    *   Uses `ReportLab` to programmatically draw PDFs.
    *   `replace_emojis_with_icons()`: ReportLab doesn't support color emojis well, so this utility replaces specific characters (⚠️, 📈) with small PNG images from `icons/`.
*   **`email_handler.py`**:
    *   `send_email_report()`: Connects to Gmail SMTP (`smtp.gmail.com:587`). Uses `MIMEMultipart` to attach the generated PDF.

---

## 3. 🖥 Frontend Code Deep Dive

### `frontend/src/pages/Dashboard.tsx`
This is the heart of the UI (approx 800+ lines).

**State Management**:
*   `file`: The uploaded CSV.
*   `result`: Stores the JSON response from `/forecast` (products, trends, revenue).
*   `overview`: (Memoized) aggregates total revenue, growth %, and category-wise stats on the fly to avoid re-calculation.
*   `activeTab`: Switches between `results` (Table), `alerts` (Cards/List), and `report` (PDF View).

**Core Functions**:
*   `runForecast()`:
    *   Calls API -> Updates `result` -> Fetches `alerts` -> Updates `alerts` state.
*   `handleInsight(product)`:
    *   Triggered when clicking the robot icon (🤖) in the table.
    *   Scrolls to the "Generative AI" section (`scrollIntoView`).
    *   Calls `/insight` and displays the English/Hindi response with a "Demand Heatmap".
*   `generateReport()` / `download()`:
    *   Handles endpoints for CSV export and PDF generation.

**UI Components**:
*   **KPI Cards**: "Last Week Sales", "AI Forecast", "Growth Trend", "Revenue".
*   **Insight Section**: Displays "Summary", "Risk Analysis", "Action" in a 3-column grid.
*   **Heatmap**: A custom grid rendering `rgba` background opacity based on forecast intensity.

### `frontend/src/components/`
*   **`ForecastChart.tsx`**:
    *   Uses `recharts`.
    *   Transforms the flat API data into specific Week 1, Week 2... keys for the `LineChart`.
    *   Renders two charts: A multi-line trend chart and a total bar chart.
*   **`Layout.tsx`**:
    *   Wraps the application.
    *   Handles the Header (Logo "NIYOJAN"), Navigation, and **Logout Logic** (clearing `localStorage`).

### `frontend/src/api.ts`
*   Contains `fetch` wrappers.
*   Automatically appends `Authorization: Bearer <token>` to headers.
*   Handles base URL config via `import.meta.env.VITE_API_BASE`.

---

## 4. 🗄 Database Schema Detail
```sql
-- forecasts
id (PK), product, category, last_week_sales, forecast, created_at

-- alerts
id (PK), product, category, forecast, alert (text), created_at

-- users
id (PK), email (Unique), name, password_hash, salt, role (default 'analyst')
```

## 5. � Data Pipeline Summary

1.  **Upload**: CSV traverses Frontend → Backend (`main.py`).
2.  **Inference**: Backend → `utils.forecast_engine` → `lstm` model.
3.  **Logic**: Backend → `utils.decision_engine` (Rules).
4.  **Storage**: Backend → `db_manager` → SQLite.
5.  **GenAI (Optional)**: User Click → Backend → `genai.insight_engine` → Google Gemini → JSON Response → Frontend Display.
6.  **Reporting**: Database → `utils.pdf_report_generator` → PDF → Email/Download.
