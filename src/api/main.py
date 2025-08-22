from agent.graph import app as graph
from agent.graph import AgentState
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.auth import require_auth, lifespan
from api.logging_middleware import LoggingMiddleware
from api.logging_middleware import request_logger

app = FastAPI(lifespan=lifespan, dependencies=[Depends(require_auth)])
app.add_middleware(LoggingMiddleware)


class RequestModel(BaseModel):
    query: str
    
@app.post("/run-agent")
async def run_agent(request: RequestModel, claims: dict = Depends(require_auth)):
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

