import json
import asyncio
from config import get_llm_completion, get_llm_acompletion
from adk.mcp_client import ToolExecutor
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Callable

class AgentState(BaseModel):
    user_id: str
    messages: List[Dict[str, Any]]
    shared_context: Dict[str, Any] = {}
    current_agent: str = "Discovery"

class Agent:
    def __init__(self, name: str, instructions: str, tools: List[Callable]):
        self.name = name
        self.instructions = instructions
        self.tool_executor = ToolExecutor(tools) if tools else None

    def run(self, state: AgentState) -> AgentState:
        # Prepend system prompt
        base_instructions = (
            f"{self.instructions}\n\n"
            "STRICT SYSTEM CONSTRAINTS:\n"
            "1. You must STRICTLY adhere to your persona. Do not hallucinate capabilities or information outside of your instructions.\n"
            "2. Keep your conversational responses clean, professional, and concise.\n"
            "3. CRITICAL: You have access to tools/functions. Always call them using the proper tool-calling mechanism provided by the API. NEVER output tool calls as plain text or in any text-based format inside your response. Your text response is ONLY for human reading."
        )
        system_msg = {"role": "system", "content": base_instructions}
        
        # Inject shared context into system prompt
        if state.shared_context:
            system_msg["content"] += f"\n\nContext from previous agents: {json.dumps(state.shared_context)}"
            
        messages = [system_msg] + state.messages
        
        while True:
            # Call LLM
            tools = self.tool_executor.schemas if self.tool_executor else None
            response = get_llm_completion(messages=messages, tools=tools)
            msg = response.choices[0].message # type: ignore
            
            # Append to history
            messages.append(msg.model_dump())
            state.messages.append(msg.model_dump())
            
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"[{self.name}] Tool Call: {tool_call.function.name}")
                    if self.tool_executor:
                        result = self.tool_executor.execute(tool_call)
                    else:
                        result = "Error: Tool executor not initialized."
                    
                    # Add tool response
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result
                    }
                    messages.append(tool_msg)
                    state.messages.append(tool_msg)
                    
                    # Intercept handoffs
                    if "handoff_to" in result:
                        try:
                            res_val = json.loads(result)
                            if "handoff_to" in res_val:
                                state.current_agent = res_val["handoff_to"]
                                state.shared_context[f"{self.name}_handoff_reason"] = res_val.get("reason", "")
                                return state
                        except:
                            pass
            else:
                # Agent replied to user or decided to wait
                break
                
        return state

    async def run_async(self, state: AgentState, emit_event: Callable) -> AgentState:
        # Prepend system prompt
        base_instructions = (
            f"{self.instructions}\n\n"
            "STRICT SYSTEM CONSTRAINTS:\n"
            "1. You must STRICTLY adhere to your persona. Do not hallucinate capabilities or information outside of your instructions.\n"
            "2. Keep your conversational responses clean, professional, and concise.\n"
            "3. CRITICAL: You have access to tools/functions. Always call them using the proper tool-calling mechanism provided by the API. NEVER output tool calls as plain text or in any text-based format inside your response. Your text response is ONLY for human reading."
        )
        system_msg = {"role": "system", "content": base_instructions}
        
        # Inject shared context into system prompt
        if state.shared_context:
            system_msg["content"] += f"\n\nContext from previous agents: {json.dumps(state.shared_context)}"
            
        messages = [system_msg] + state.messages
        
        while True:
            # Call LLM
            tools = self.tool_executor.schemas if self.tool_executor else None
            response = await get_llm_acompletion(messages=messages, tools=tools)
            msg = response.choices[0].message # type: ignore
            
            # Append to history
            messages.append(msg.model_dump())
            state.messages.append(msg.model_dump())
            
            # Pass text content directly if it's there
            if msg.content:
                cleaned_content = []
                for line in msg.content.split('\n'):
                    line = line.strip()
                    if not (line.startswith('{') and line.endswith('}')):
                        cleaned_content.append(line)
                cleaned = '\n'.join(cleaned_content).strip()
                if cleaned:
                    await emit_event("chat_stream", cleaned)

            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"[{self.name}] Tool Call: {tool_call.function.name}")
                    
                    # Send tool call event to frontend
                    await emit_event("tool_call", {
                        "tool": tool_call.function.name,
                        "status": "running"
                    })
                    
                    if self.tool_executor:
                        result = await asyncio.to_thread(self.tool_executor.execute, tool_call)
                    else:
                        result = "Error: Tool executor not initialized."
                    
                    # Notify tool complete
                    await emit_event("tool_call", {
                        "tool": tool_call.function.name,
                        "status": "success",
                        "output": result
                    })

                    # Add tool response
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result
                    }
                    messages.append(tool_msg)
                    state.messages.append(tool_msg)
                    
                    # Special Case Events from Tool Returns
                    if tool_call.function.name == "handoff_to_inventory" and "agreed_price" in result:
                        try:
                            res_val = json.loads(result)
                            await emit_event("price_update", {
                                "product_id": res_val.get("product_id"),
                                "new_price": res_val.get("agreed_price"),
                                "reason": "Negotiated Deal"
                            })
                            await emit_event("cart_update", {
                                "items": [{"id": res_val.get("product_id"), "qty": 1}],
                                "total": res_val.get("agreed_price"),
                                "status": "pending_inventory"
                            })
                        except:
                            pass

                    # Intercept handoffs
                    if "handoff_to" in result:
                        try:
                            res_val = json.loads(result)
                            if "handoff_to" in res_val:
                                next_agent = res_val["handoff_to"]
                                state.current_agent = next_agent
                                reason = res_val.get("reason", "")
                                state.shared_context[f"{self.name}_handoff_reason"] = reason
                                
                                await emit_event("agent_transition", {
                                    "from": self.name,
                                    "to": next_agent,
                                    "reason": reason
                                })
                                return state
                        except:
                            pass
            else:
                # Agent replied to user or decided to wait
                break
                
        return state
