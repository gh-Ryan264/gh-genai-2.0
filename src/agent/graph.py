from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Literal
import json
import re
from dotenv import load_dotenv
import os
from utility.utils import extract_category, parse_llm_json
from rag.retriever import get_top_k_documents, format_intents_plain_text
from agent.prompts import classifier_prompt, generator_prompt
from rag.embedding_model import get_embedding_query
from llm.llms import invoke_llm
import utility.config as config
from utility.logging import get_logger
import time
from agent.intent_definition import classify_intent, load_intent_vectors
# Initialize logger
graph_logger = get_logger("graph", "agent_graph.log")
load_dotenv()

class AgentState(TypedDict):
    query: str
    category: Literal["navigation", "summarization", "task_execution", "unknown"]
    context: str
    answer: str
    query_embedding: list[float]

graph_logger.info("intializing agent graph...")
llm = ChatGroq(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0,
)
graph_logger.info("llm initialized")


# ---------- Handlers ----------


def orchestrator(state: AgentState) -> AgentState:
    start_time = time.time()
    prompt = classifier_prompt.format(query=state["query"])
    graph_logger.debug(f"Classifying query: {state['query']}")# logging related
    text = invoke_llm(prompt)
    llm_time = (time.time() - start_time) * 1000
    graph_logger.debug(f"LLM response: {text}")# logging related
    graph_logger.info(f"Query classification took {llm_time:.2f} ms") # logging related
    state["category"] = extract_category(text)
    graph_logger.debug(f"Identified category: {state['category']}")
    return state


def navigation_handler(state: AgentState) -> AgentState:
    start_time = time.time()
    state["query_embedding"] = get_embedding_query(state["query"])
    embedding_time = (time.time() - start_time) * 1000
    graph_logger.debug(f"generated query embeddings for{state['query']}")# logging related
    graph_logger.info(f"Generated query embedding in {embedding_time:.2f} ms")

    graph_logger.info("retrieving top documents for navigation...") # logging related
    start_time = time.time()
    top_documents = get_top_k_documents(state["query_embedding"], k=config.TOP_K)
    retrieval_time = (time.time() - start_time) * 1000
    graph_logger.info(f"Top-{config.TOP_K} documents retrieved in {retrieval_time:.2f} ms")
    graph_logger.debug(f"Top documents retrieved: {len(top_documents)}")# logging related
    
    if not top_documents:
        state["answer"] = "No relevant information found."
        graph_logger.warning("No relevant documents found for navigation.") # logging related
        return state

    state["context"] = format_intents_plain_text(top_documents)
    prompt = generator_prompt.format(
        context=state["context"],
        query=state["query"]
    )
    graph_logger.debug(f"Generating response for query: {state['query']}")# logging
    start_time = time.time()
    text = invoke_llm(prompt)
    llm_time = (time.time() - start_time) * 1000
    graph_logger.info(f"LLM response generated ... took {llm_time:.2f} ms") # logging related
    parsed = parse_llm_json(text)

    if not parsed:
        state["answer"] = "Failed to parse response from LLM."
        graph_logger.error("Failed to parse LLM response.") # logging related
        return state

    state["answer"] = parsed
    return state


def summarization_handler(state: AgentState) -> AgentState:
    state["answer"] = "Summarization functionality is not yet implemented."
    return state


def task_execution_handler(state: AgentState) -> AgentState:
    state["answer"] = "Task execution functionality is not yet implemented."
    return state


def unknown_handler(state: AgentState) -> AgentState:
    state["answer"] = "Unknown intent. Please rephrase your query."
    return state


# ---------- Graph setup ----------

graph = StateGraph(AgentState)
graph.add_node("orchestrator", orchestrator)
graph.add_node("navigation_handler", navigation_handler)
graph.add_node("summarization_handler", summarization_handler)
graph.add_node("task_execution_handler", task_execution_handler)
graph.add_node("unknown_handler", unknown_handler)

graph.add_edge(START, "orchestrator")
graph.add_conditional_edges(
    source="orchestrator",
    path=lambda state: state["category"],
    path_map={
        "navigation": "navigation_handler",
        "summarization": "summarization_handler",
        "task_execution": "task_execution_handler",
        "unknown": "unknown_handler"
    }
)
graph.add_edge("navigation_handler", END)
graph.add_edge("summarization_handler", END)
graph.add_edge("task_execution_handler", END)
graph.add_edge("unknown_handler", END)
app = graph.compile()



if __name__ == "__main__":
    queries = [
        "navigate me to worker event details page",
        "I want to resolve an event take me to it.",
        "How do I add a new person to the system?",
        "I need to make changes to an existing product.",
        "Show me the results from the last scan I did.",
        "translate this text to French",
        " "
    ]
    for query in queries:
        final_state = app.invoke({"query": query})
        print(f"User query: {query}")
        print(f"Identified intent: {final_state['category']}")
        print(f"Answer: {final_state['answer']}")
        print("\n------------------------\n")
