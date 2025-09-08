from langchain_groq import ChatGroq
import time
import os
import utility.config as config
from utility.logging import get_logger
# Initialize logger
llm_logger = get_logger("llms", "llms.log")
# Primary LLM
llm_primary = ChatGroq(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0,
)

llm_fallback = ChatGroq(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    temperature=0,
)




def invoke_llm_with_fallback(prompt) -> str:
    """Call primary LLM, retry on failure, then use fallback."""
    attempt = 0
    last_error = None

    while attempt < config.MAX_RETRIES:
        try:
            result = llm_primary.invoke(prompt)
            if hasattr(result, "content") and result.content.strip():
                llm_logger.debug(f"Primary LLM responded successfully on attempt {attempt + 1}")
                return result.content.strip()
        except Exception as e:
            last_error = e
            llm_logger.warning(f"Primary LLM attempt {attempt + 1} failed: {e}")
        attempt += 1
        time.sleep(config.RETRY_DELAY)

    try:
        print("[WARN] Primary LLM failed, using fallback...")
        result = llm_fallback.invoke(prompt)
        if hasattr(result, "content"):
            llm_logger.debug("Fallback LLM responded successfully")
            return result.content.strip()
        return str(result).strip()
    except Exception as e:
        llm_logger.error(f"Fallback LLM also failed: {e}")
        raise RuntimeError(
            f"Both primary and fallback LLM failed. Last primary error: {last_error}, fallback error: {e}"
        )


def invoke_llm(prompt) -> str:
    return invoke_llm_with_fallback(prompt)
