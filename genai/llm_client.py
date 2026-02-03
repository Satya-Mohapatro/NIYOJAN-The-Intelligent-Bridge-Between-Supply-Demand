import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Use a stable text model
MODEL_NAME = "gemini-flash-latest"  # stable & fast (1.5-flash equivalent)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Calls Gemini and returns raw text output.
    No parsing, no validation here.
    """

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt
    )

    response = model.generate_content(
        user_prompt,
        generation_config={
            "temperature": 0.2,     # low = deterministic
            "top_p": 0.9,
            "max_output_tokens": 8000
        }
    )

    if not response.text:
        raise RuntimeError("Empty response from Gemini")

    return response.text


async def call_llm_async(system_prompt: str, user_prompt: str) -> str:
    """
    Async version of call_llm
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt
    )

    response = await model.generate_content_async(
        user_prompt,
        generation_config={
            "temperature": 0.2,
            "top_p": 0.9,
            "max_output_tokens": 8000
        }
    )

    if not response.text:
        raise RuntimeError("Empty response from Gemini")

    return response.text
