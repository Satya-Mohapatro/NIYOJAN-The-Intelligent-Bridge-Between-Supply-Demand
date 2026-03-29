# Niyojan - Comprehensive Project Analysis & Code Deep Dive

This document serves as an exhaustive technical reference for the **Niyojan Demand Forecasting System**. It analyzes every directory, file, and significant function within the codebase, incorporating the recently added **Agentic AI Intelligence Hub**.

---

## 1. 🏗 System Architecture Overview

Niyojan is a **Demand Forecasting & Inventory Optimization Platform** that uses a robust multi-layer architecture:

1.  **Frontend (Presentation Layer)**:
    *   **Tech**: React (Vite), TypeScript, Tailwind CSS, Recharts.
    *   **Role**: Handles user interaction, file uploads, data visualization, robust reporting, and a conversational agentic hub for natural strategic queries.
    *   **Key Files**: `Dashboard.tsx` (Core operations hub), `AgenticHub.tsx` (AI conversational interface).

2.  **Backend (Logic Layer)**:
    *   **Tech**: Python, FastAPI.
    *   **Role**: Exposes REST endpoints, runs predictive machine learning models (`lstm`), and orchestrates sophisticated generative AI agents via `LangGraph`.
    *   **Key Files**: `backend/app/main.py`, `backend/app/routes/intelligence.py`.

3.  **Data & Intelligence Layer**:
    *   **Storage**: SQLite (`database/niyojan.db`).
    *   **Forecasting**: TensorFlow/Keras LSTM globally-trained model (`lstm/global_lstm_model`).
    *   **GenAI Multi-Agent System**: `LangGraph` and Google Gemini APIs powering intent classification, RAG-based document retrieval, strategic planning, and numerical simulations.

---

## 2. 📂 Backend Code Deep Dive

### `backend/app/main.py`
The overarching entry point for the FastAPI server, bridging multiple sub-modules.

*   **Authentication Flow**:
    *   Implements secure JWT standard (`create_access_token()`).
    *   Endpoints like `/auth/login` validate hash schemas securely through `db_manager.verify_user_credentials`.
*   **Forecasting Logic (`/forecast`)**:
    *   **Input Parsing**: Takes CSV arrays and cleans dates and missing columns via `pandas`.
    *   **Prediction Map**: Iterates unique products and runs `utils.forecast_engine.predict_demand` in rolling loops to project `N` weeks out.
    *   **Alert Pipeline**: Chains to `utils.decision_engine.analyze_forecast` to label conditions (High Risk, Medium, Low/Safe).
*   **Reporting Stack (`/report/view`, `/report/download`, `/send-report`)**:
    *   Combines local stats into a formal PDF layout utilizing `ReportLab` and sends via SMTP inside `utils.email_handler.py`.

### `backend/app/agents/` (The LangGraph Intelligence Hub)
This forms the core of the **Agentic Hub**, implementing a conversational chain designed around `gemini-flash-latest`.

*   **`graph.py` & `state.py`**:
    *   `AgentState` manages the conversational payload passing context back and forth.
    *   `build_agent()` formulates a robust `StateGraph` adding nodes for intent detection, retrieval, analysis, simulation, and strategic output formatting.
*   **`nodes.py`**:
    *   **`intent_node` & `route_intent`**: LLM zero-shot capability maps raw user queries into exact intents: `retrieval`, `analysis`, `simulation`, or `strategy` handling fallback regex checks if necessary.
    *   **`retrieval_node`**: Leverages FAISS and Gemini Embeddings (`models/text-embedding-004`) to inject explicit semantic rules from uploaded PDFs.
    *   **`analysis_node`**: Sorts products by stock volatility and inventory gaps calculating the math deterministically before surfacing answers.
    *   **`simulation_node`**: Re-calculates Reorder Points (ROP) applying a dynamic Demand scenario (like +20% demand spike) with Z-Scores using `np.sqrt(lead_time)`.
    *   **`strategy_node` & `reasoning_node`**: Collects the preceding mathematical facts to invoke the central `STRATEGIC_SYSTEM_PROMPT`. Limits hallucination by forcing structured JSON extraction into a 4-week executive plan.
*   **`rag.py`**: Reads binary bytes from memory, runs `PyPDFLoader`, splits documents via `RecursiveCharacterTextSplitter`, and embeds them to vectorize standard operational procedures dynamically.

### `database/`
*   **`schema.sql`**:
    *   `users`: Stores `email`, `password_hash`, `salt`, `role`.
    *   `forecasts`: Logs the `product`, `forecast`, `category`, and scalar sales.
    *   `alerts`: Records trigger messages based on forecast/stock imbalance.
*   **`db_manager.py`**: Fast insertion queries logic handling bulk operations (`executemany`) tracking timestamps (`created_at`) allowing the app to filter the latest runs seamlessly.

### `lstm/` (Machine Learning Module)
*   Provides `global_lstm_model` implemented dynamically.
*   The system scales normalized sequences and runs backward lookbacks (history) to infer trend continuation. The resulting prediction handles realistic padding on edge cases where product histories are too short.

### `utils/`
*   **`decision_engine.py`**: Calculates Ratios (`Forecast / Current_Stock`) generating dynamic alert string warnings.
*   **`pdf_report_generator.py`**: High-end PDF drawer dealing with custom logic to inject UI emojis directly by rendering local fallback png images preventing breaking PDF encoding errors.
*   **`forecast_engine.py`**: The singleton-loaded model runner linking inference to raw FastAPI inputs.

---

## 3. 🖥 Frontend Code Deep Dive

The frontend handles complex views leveraging Vite with robust component mapping.

### Core Screens in `frontend/src/pages/`
*   **`Dashboard.tsx`**:
    *   **Function**: A unified interface showing raw statistical facts.
    *   **Components**: Handles CSV batch uploads. Displays total aggregate Revenue, Category Maps, Avg Weekly Growth chips.
    *   **Insight Integration**: Single item deep-dives via the "Generate Insights" button which polls GenAI to parse localized single-product actions directly into Hindi/English formats.
*   **`AgenticHub.tsx`**:
    *   **Function**: Advanced interactive multi-agent chat terminal.
    *   **Flow**: Users pass the entire workspace context along with a secondary operational guidelines PDF. The Chat window streams inputs into the `LangGraph` backend generating interactive UI elements in response (Executive Summaries, Simulated Graphs, Ranked Tables) depending on the parsed intent.
*   **`Landing.tsx` & `Login.tsx`**: Responsible for the visual entry logic and JWT persistent caching.

### Functional Components (`frontend/src/components/`)
*   Provides reusable interactive layers like `ForecastChart.tsx` (using Recharts library bounding logic onto responsive SVG containers) and structural `Layout.tsx` for managing system menus.

### API Layer (`frontend/src/api.ts`)
*   Manages the global `fetch` overrides automatically enforcing `Bearer` token attachments for synchronous security and standardized error catches allowing React components to handle promise failures gracefully without tearing down the UI tree.

---

## 4. 🗄 Database Schema Snapshots
```sql
-- forecasts
id (PK), product, category, last_week_sales, forecast, created_at

-- alerts
id (PK), product, category, forecast, alert (text), created_at

-- users
id (PK), email (Unique), name, password_hash, salt, role (default 'analyst')
```

## 5. 🔄 The Agentic Data Flow (Full Cycle)

1.  **Ingestion**: CSV (+ Optional PDF) traverses the API to `backend/app/routes/intelligence.py`.
2.  **Inference**: Forecast sequences pass through `global_lstm_model`, scaling numeric bounds back to readable numbers.
3.  **Graph Orchestration**:
    *   The user issues a prompt in the `AgenticHub`.
    *   Prompt is parsed by `intent_node`.
    *   Dependent on intent, logic reroutes: Semantic `retrieval` runs RAG, Numerical `simulation` modifies limits dynamically, or `analysis` does pure ranking computations.
4.  **Actionable Intelligence**: The compiled arrays stream into the `reasoning` node which locks the LLM into producing a 4-week executive planning scheme.
5.  **Return**: The structured JSON parses backwards to `AgenticChat.tsx` which dynamically paints risk cards and summary tables in real-time.
