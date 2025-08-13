from agent.graph import app as graph
from agent.graph import AgentState
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class RequestModel(BaseModel):
    query: str
    
@app.post("/run-agent")
async def run_agent(request: RequestModel):
    initial_state = {
        "query": request.query,
        "category": "unknown",
        "context": "",
        "answer": "",
        "query_embedding": []
    }
    result = await graph.ainvoke(initial_state)
    return {
        "category": result["category"],
        "output": result["answer"]
    }

