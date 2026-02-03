import json
import re
from genai.schemas import InsightInput, InsightOutput
from genai.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from genai.llm_client import call_llm


def extract_json(text: str) -> dict:
    """
    Extracts JSON object from Gemini output safely by finding outermost braces.
    """
    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        json_str = text[start : end + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to fix common issues if needed, or just fail
            raise ValueError(f"JSON Decode Error: {e} in {json_str[:50]}...")
            
    raise ValueError(f"No JSON object found in LLM output. Raw: {text[:100]}...")


def generate_insights(insight_input: InsightInput) -> InsightOutput:
    input_json = insight_input.model_dump_json(indent=2)

    user_prompt = USER_PROMPT_TEMPLATE.format(data=input_json)

    raw_response = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    parsed_json = extract_json(raw_response)
    validated_output = InsightOutput(**parsed_json)

    return validated_output


async def generate_insights_async(insight_input: InsightInput) -> InsightOutput:
    from genai.llm_client import call_llm_async
    
    input_json = insight_input.model_dump_json(indent=2)
    user_prompt = USER_PROMPT_TEMPLATE.format(data=input_json)

    raw_response = await call_llm_async(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    parsed_json = extract_json(raw_response)
    validated_output = InsightOutput(**parsed_json)

    return validated_output
