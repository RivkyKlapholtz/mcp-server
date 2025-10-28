# mcp_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uvicorn
import logging

# Add logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# נגדיר כלי אחד או שניים לדוגמה
TOOLS = {
    "add": {
        "name": "add",
        "description": "Add two numbers",
        "input_schema": {
            "type": "object",
            "properties": {
                "x": { "type": "number" },
                "y": { "type": "number" }
            },
            "required": ["x", "y"]
        },
        "func": lambda args: args["x"] + args["y"]
    },
    "multiply": {
        "name": "multiply",
        "description": "Multiply two numbers",
        "input_schema": {
            "type": "object",
            "properties": {
                "x": { "type": "number" },
                "y": { "type": "number" }
            },
            "required": ["x", "y"]
        },
        "func": lambda args: args["x"] * args["y"]
    },
}

class ToolRunRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

@app.get("/tools", response_model=List[ToolDefinition])
def list_tools():
    """Return list of available tools in MCP format."""
    return [ToolDefinition(
                name=tool["name"],
                description=tool["description"],
                input_schema=tool["input_schema"],
            ) for tool in TOOLS.values()]

@app.post("/call")
def call_tool(req: ToolRunRequest):
    """Invoke a tool by name with arguments."""
    tool = TOOLS.get(req.name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {req.name} not found")
    
    # simple validation of required arguments
    for req_key in tool["input_schema"]["required"]:
        if req_key not in req.arguments:
            raise HTTPException(status_code=400, detail=f"Missing required argument: {req_key}")
    
    try:
        result = tool["func"](req.arguments)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting MCP server...")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")