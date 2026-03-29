import os
import google.generativeai as genai
from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import (
    intent_node, route_intent,
    retrieval_node, analysis_node,
    simulation_node, strategy_node,
    reasoning_node, formatter_node
)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))


def build_agent():
    builder = StateGraph(AgentState)
    builder.add_node("intent_classification", intent_node)
    builder.add_node("retrieval",             retrieval_node)
    builder.add_node("analysis",              analysis_node)
    builder.add_node("simulation",            simulation_node)
    builder.add_node("strategy_context",      strategy_node)
    builder.add_node("llm_reasoning",         reasoning_node)
    builder.add_node("formatter",             formatter_node)

    builder.add_edge(START, "intent_classification")
    builder.add_conditional_edges(
        "intent_classification",
        route_intent,
        {
            "retrieval":  "retrieval",
            "analysis":   "analysis",
            "simulation": "simulation",
            "strategy":   "strategy_context",
        }
    )
    builder.add_edge("retrieval",        "strategy_context")
    builder.add_edge("analysis",         "strategy_context")
    builder.add_edge("simulation",       "strategy_context")
    builder.add_edge("strategy_context", "llm_reasoning")
    builder.add_edge("llm_reasoning",    "formatter")
    builder.add_edge("formatter",        END)

    return builder.compile()


# Singleton — built once at startup
agent = build_agent()
