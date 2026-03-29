from typing import TypedDict, Optional

class AgentState(TypedDict):
    query: str
    forecast_data: list
    intent: str
    simulation_percent: Optional[float]
    rag_context: list
    analysis_result: dict
    simulation_result: dict
    strategic_context: dict
    final_response: dict
