import inspect
import json
from pydantic import BaseModel
from typing import get_type_hints, Callable, Dict, Any, List

def type_to_json_schema(py_type) -> str:
    if py_type == str: return "string"
    if py_type == int: return "integer"
    if py_type == float: return "number"
    if py_type == bool: return "boolean"
    return "string"

def mcp_to_litellm_tools(mcp_server) -> List[Dict]:
    """
    Takes a FastMCP server instance and converts its registered tools 
    into LiteLLM / OpenAI compatible function schemas.
    """
    litellm_tools = []
    
    # fastmcp tools are usually in mcp_server._tools or similar.
    # We will inspect the registered functions directly if we can't access _tools easily.
    # Looking at standard FastMCP, it has a `.tools` async list or we can just 
    # extract the functions if we know them. Since we own the server files, 
    # we can just write a wrapper that takes a list of python functions and makes them litellm tools.
    return litellm_tools

def function_to_schema(func: Callable) -> Dict:
    """
    Converts a Python function to LiteLLM tool schema.
    """
    sig = inspect.signature(func)
    doc = func.__doc__ or ""
    
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
        properties[name] = {"type": type_to_json_schema(param_type)}
        if param.default == inspect.Parameter.empty:
            required.append(name)
            
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": doc.strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }

class ToolExecutor:
    def __init__(self, functions: List[Callable]):
        self.functions = {f.__name__: f for f in functions}
        self.schemas = [function_to_schema(f) for f in functions]
        
    def execute(self, tool_call) -> str:
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        if func_name in self.functions:
            try:
                # Our MCP tools currently return JSON strings
                res = self.functions[func_name](**args)
                return str(res)
            except Exception as e:
                return json.dumps({"error": str(e)})
        return json.dumps({"error": f"Unknown tool {func_name}"})
