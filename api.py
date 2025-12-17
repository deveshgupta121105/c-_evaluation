from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import app_graph

app = FastAPI(title="Code Eval Agent")

class CodeRequest(BaseModel):
    code: str

@app.get("/")
def home():
    return {"status": "Active", "model": "Llama3-70b-Groq"}

@app.post("/evaluate")
async def evaluate_code(request: CodeRequest):
    try:
        # Initial state
        initial_state = {"code": request.code, "reviews": []}
        
        # Invoke LangGraph
        result = app_graph.invoke(initial_state)
        
        return {
            "reviews": result["reviews"],
            "final_report": result["final_report"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)