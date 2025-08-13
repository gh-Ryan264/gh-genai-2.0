import json
import re
from typing import TypedDict, Literal

def extract_category(text: str) -> str:
    """Extract category from LLM output using regex."""
    match = re.search(r"(navigation|summarization|task_execution|unknown)", text.lower())
    return match.group(1) if match else "unknown"


def parse_llm_json(text: str):
    """Extract and parse JSON from LLM output, even if wrapped in code fences."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
