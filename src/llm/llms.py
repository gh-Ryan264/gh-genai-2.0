from langchain_groq import ChatGroq
import time
import os
import utility.config as config
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
                return result.content.strip()
        except Exception as e:
            last_error = e
        attempt += 1
        time.sleep(config.RETRY_DELAY)

    try:
        print("[WARN] Primary LLM failed, using fallback...")
        result = llm_fallback.invoke(prompt)
        if hasattr(result, "content"):
            return result.content.strip()
        return str(result).strip()
    except Exception as e:
        raise RuntimeError(
            f"Both primary and fallback LLM failed. Last primary error: {last_error}, fallback error: {e}"
        )


def invoke_llm(prompt) -> str:
    return invoke_llm_with_fallback(prompt)
