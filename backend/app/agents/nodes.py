import json
import re
import numpy as np
import google.generativeai as genai
from datetime import datetime
from .state import AgentState

GEMINI_MODEL = "gemini-flash-latest"
Z_SCORE      = 1.65

# ════════════════════════════════════════════════════════
# INTENT PROMPT
# ════════════════════════════════════════════════════════
INTENT_PROMPT = """
You are an intent classifier for a supply chain planning AI.
Classify the user query into EXACTLY ONE of these 4 intents:
  retrieval  — User asks about the uploaded report, wants explanations from context/documents
  analysis   — User asks about inventory stats, volatility, risk rankings (no scenario change)
  simulation — User asks a "what if" scenario involving demand percentage change
  strategy   — User asks for a procurement plan, what to do, or general strategy

Also extract simulation_percent ONLY if intent=simulation.
  Example: "increase by 15%" → 15.0 | "drop by 20%" → -20.0 | not applicable → null

User Query: "{query}"
Respond with ONLY valid JSON, no markdown:
{{"intent": "...", "simulation_percent": null}}
"""

# ════════════════════════════════════════════════════════
# STRATEGIC SYSTEM PROMPT
# ════════════════════════════════════════════════════════
STRATEGIC_SYSTEM_PROMPT = """
You are NIYOJAN — an expert Supply Chain Planning AI.
You receive STRUCTURED DATA from deterministic calculations. Your role is:
  ✅ Synthesize data into strategic insights
  ✅ Prioritize SKUs by risk and urgency
  ✅ Generate actionable 4-week procurement plans
  ✅ Explain WHY risks exist in business terms
  ❌ NEVER perform calculations yourself
  ❌ NEVER invent numbers not present in the input
  ❌ NEVER guess or hallucinate inventory data

Respond in structured JSON matching this exact schema:
{
  "executive_summary": "2-3 sentence overview of the situation",
  "high_risk_products": [
    {"product": "name", "risk_level": "High/Medium/Low", "reason": "why risky", "urgency": "Immediate/Soon/Monitor"}
  ],
  "key_risk_drivers": ["driver 1", "driver 2", "driver 3"],
  "recommended_actions": [
    {"action": "specific action", "target_skus": ["P001"], "priority": "High/Medium"}
  ],
  "four_week_plan": {
    "week_1": "actions for week 1",
    "week_2": "actions for week 2",
    "week_3": "actions for week 3",
    "week_4": "actions for week 4"
  },
  "monitoring_strategy": "what to track and how often"
}
"""

USER_PROMPT_TEMPLATE = """
User Query: {query}

Structured Context:
{context_json}

Generate a strategic executive planning response.
"""


# ════════════════════════════════════════════════════════
# NODE FUNCTIONS
# ════════════════════════════════════════════════════════

def _fallback_classify(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["what if", "increase", "decrease", "scenario", "demand rise", "demand drop", "%"]):
        return "simulation"
    if any(w in q for w in ["report", "explain", "why", "what does", "tell me about"]):
        return "retrieval"
    if any(w in q for w in ["volatility", "gap", "metric", "highest", "lowest", "which product", "rank"]):
        return "analysis"
    return "strategy"


def _extract_percent(query: str):
    match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*%", query)
    if match:
        val = float(match.group(1))
        if any(w in query.lower() for w in ["drop", "decrease", "reduce", "fall", "decline"]):
            val = -abs(val)
        return val
    return None


def intent_node(state: AgentState) -> dict:
    query = state["query"]
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=genai.GenerationConfig(temperature=0.0)
    )
    try:
        response = model.generate_content(INTENT_PROMPT.format(query=query))
        raw = re.sub(r"^```(?:json)?\s*", "", response.text.strip())
        raw = re.sub(r"\s*```$", "", raw)
        parsed  = json.loads(raw)
        intent  = parsed.get("intent", "strategy")
        sim_pct = parsed.get("simulation_percent")
        if sim_pct is not None:
            sim_pct = float(sim_pct)
    except Exception:
        intent  = _fallback_classify(query)
        sim_pct = _extract_percent(query)

    if intent not in {"retrieval", "analysis", "simulation", "strategy"}:
        intent = "strategy"
    return {"intent": intent, "simulation_percent": sim_pct}


def route_intent(state: AgentState) -> str:
    return state["intent"]


def retrieval_node(state: AgentState) -> dict:
    # vector_store is passed via state["_vector_store"] (extra key injected per-request)
    vector_store = state.get("_vector_store")
    if not vector_store:
        return {"rag_context": ["No report PDF was uploaded. Showing analysis based on forecast CSV only."]}
    chunks = vector_store.search(state["query"], top_k=4)
    return {"rag_context": chunks}


def analysis_node(state: AgentState) -> dict:
    data = state["forecast_data"]
    if not data:
        return {"analysis_result": {"error": "No forecast data"}}

    by_volatility = sorted(data, key=lambda x: x["volatility"], reverse=True)
    by_gap        = sorted(data, key=lambda x: x["inv_gap"],    reverse=True)
    high_risk     = [p for p in data if p["base_risk"] == "High"]
    overstock     = [p for p in data if "Overstock" in p["base_risk"]]
    avg_vol       = round(float(np.mean([p["volatility"] for p in data])), 4)
    total_gap     = round(sum(p["inv_gap"] for p in data), 2)

    return {"analysis_result": {
        "total_products":        len(data),
        "high_risk_count":       len(high_risk),
        "overstock_count":       len(overstock),
        "avg_volatility":        avg_vol,
        "total_inventory_gap":   total_gap,
        "avg_lead_time_weeks":   round(float(np.mean([p["lead_time"] for p in data])), 1),
        "highest_volatility_skus": [
            {"id": p["product_id"], "name": p["product_name"], "volatility": p["volatility"]}
            for p in by_volatility[:3]
        ],
        "largest_gap_skus": [
            {"id": p["product_id"], "name": p["product_name"],
             "gap": p["inv_gap"], "rop": p["reorder_point"], "stock": p["current_stock"]}
            for p in by_gap[:3]
        ],
        "high_risk_skus": [
            {"id": p["product_id"], "name": p["product_name"],
             "forecast": p["week1_forecast"], "stock": p["current_stock"], "risk": p["base_risk"]}
            for p in high_risk
        ],
    }}


def _classify_gap_risk(gap: float) -> str:
    if gap > 200:   return "High"
    if gap > 100:   return "Medium"
    if gap > 0:     return "Low"
    return "Safe (Stock Sufficient)"


def simulation_node(state: AgentState) -> dict:
    data   = state["forecast_data"]
    pct    = state.get("simulation_percent") or 0.0
    factor = 1 + (pct / 100)
    simulated = []

    for p in data:
        new_demand   = round(p["mean_demand"] * factor, 2)
        safety_stock = round(Z_SCORE * p["std_dev"] * np.sqrt(p["lead_time"]), 2)
        new_rop      = round((new_demand * p["lead_time"]) + safety_stock, 2)
        new_gap      = round(new_rop - p["current_stock"], 2)
        new_risk     = _classify_gap_risk(new_gap)
        simulated.append({
            "product_id":     p["product_id"],
            "product_name":   p["product_name"],
            "category":       p["category"],
            "base_demand":    p["mean_demand"],
            "new_demand":     new_demand,
            "demand_change":  round(new_demand - p["mean_demand"], 2),
            "current_stock":  p["current_stock"],
            "safety_stock":   safety_stock,
            "new_rop":        new_rop,
            "new_gap":        new_gap,
            "base_risk":      p["base_risk"],
            "simulated_risk": new_risk,
            "risk_escalated": (new_risk == "High" and p["base_risk"] != "High"),
        })

    high_risk_sim  = [p for p in simulated if p["simulated_risk"] == "High"]
    newly_at_risk  = [p for p in simulated if p["risk_escalated"]]
    return {"simulation_result": {
        "scenario":             f"{'+' if pct >= 0 else ''}{pct}% demand change",
        "simulation_factor":    factor,
        "high_risk_count":      len(high_risk_sim),
        "newly_at_risk_count":  len(newly_at_risk),
        "total_simulated_gap":  round(sum(p["new_gap"] for p in simulated), 2),
        "high_risk_products":   sorted(high_risk_sim, key=lambda x: x["new_gap"], reverse=True),
        "newly_at_risk":        newly_at_risk,
        "all_products":         simulated,
    }}


def strategy_node(state: AgentState) -> dict:
    intent            = state.get("intent", "strategy")
    forecast_data     = state.get("forecast_data", [])
    analysis_result   = state.get("analysis_result", {})
    simulation_result = state.get("simulation_result", {})
    rag_context       = state.get("rag_context", [])
    query             = state.get("query", "")

    if not analysis_result and forecast_data:
        analysis_result = analysis_node(state)["analysis_result"]

    high_risk    = sorted([p for p in forecast_data if p["base_risk"] == "High"],
                          key=lambda x: x["inv_gap"], reverse=True)
    top_volatile = sorted(forecast_data, key=lambda x: x["volatility"], reverse=True)[:3]

    return {"strategic_context": {
        "user_query":      query,
        "intent":          intent,
        "using_defaults":  True,
        "summary_metrics": {
            "total_products":  len(forecast_data),
            "high_risk_count": len(high_risk),
            "avg_volatility":  analysis_result.get("avg_volatility"),
            "total_gap":       analysis_result.get("total_inventory_gap"),
        },
        "high_risk_skus": [
            {"id": p["product_id"], "name": p["product_name"], "category": p["category"],
             "gap": p["inv_gap"], "stock": p["current_stock"], "forecast": p["week1_forecast"],
             "volatility": p["volatility"], "lead_time": p["lead_time"], "risk": p["base_risk"]}
            for p in high_risk[:5]
        ],
        "volatile_skus": [
            {"id": p["product_id"], "name": p["product_name"], "volatility": p["volatility"]}
            for p in top_volatile
        ],
        "simulation": {
            "ran":                 bool(simulation_result),
            "scenario":            simulation_result.get("scenario", "N/A"),
            "high_risk_count":     simulation_result.get("high_risk_count", 0),
            "newly_at_risk_count": simulation_result.get("newly_at_risk_count", 0),
            "total_gap":           simulation_result.get("total_simulated_gap", 0),
            "top_impacted":        simulation_result.get("high_risk_products", [])[:4],
        },
        "report_context": rag_context[:3] if rag_context else [],
    }}


def reasoning_node(state: AgentState) -> dict:
    context      = state.get("strategic_context", {})
    query        = state.get("query", "Give me a strategic procurement plan")
    context_json = json.dumps(context, indent=2)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=STRATEGIC_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    try:
        response = model.generate_content(
            USER_PROMPT_TEMPLATE.format(query=query, context_json=context_json)
        )
        raw = re.sub(r"^```(?:json)?\s*", "", response.text.strip())
        raw = re.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
    except Exception as e:
        result = {
            "executive_summary":  f"Error generating response: {str(e)}",
            "high_risk_products": [],
            "key_risk_drivers":   [str(e)],
            "recommended_actions":[],
            "four_week_plan":     {"week_1": "", "week_2": "", "week_3": "", "week_4": ""},
            "monitoring_strategy": ""
        }
    return {"final_response": result}


def formatter_node(state: AgentState) -> dict:
    raw     = state.get("final_response", {})
    context = state.get("strategic_context", {})
    return {"final_response": {
        "generated_at":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query":               state.get("query"),
        "intent":              state.get("intent"),
        "simulation_scenario": context.get("simulation", {}).get("scenario"),
        "using_defaults":      True,
        "executive_summary":   raw.get("executive_summary", ""),
        "high_risk_products":  raw.get("high_risk_products", []),
        "key_risk_drivers":    raw.get("key_risk_drivers", []),
        "recommended_actions": raw.get("recommended_actions", []),
        "four_week_plan":      raw.get("four_week_plan", {}),
        "monitoring_strategy": raw.get("monitoring_strategy", ""),
    }}
