import json
from adk.engine import AgentState
from agents.discovery_agent import discovery_agent
from agents.negotiator_agent import negotiator_agent
from agents.inventory_agent import inventory_agent
from agents.order_agent import order_agent

# Map agent names to instances
AGENTS = {
    "Discovery": discovery_agent,
    "Negotiator": negotiator_agent,
    "Inventory": inventory_agent,
    "OrderTaking": order_agent
}

def run_retail_workflow():
    print("=" * 60)
    print("Welcome to the Autonomous Retail Store!")
    print("=" * 60)
    
    # Pre-fetch the catalog to show automatically in the welcome prompt
    from mcp_servers.catalog_server import CATALOG_DB
    print("\nOur Featured Catalog:")
    for item in CATALOG_DB:
        print(f"  • {item['name']} - Rs. {item['price']}")
    print("-" * 60)
        
    state = AgentState(user_id="user_456", messages=[], shared_context={}, current_agent="Discovery")
    
    while True:
        # Prompt user
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        state.messages.append({"role": "user", "content": user_input})
        
        break_to_user = False
        while state.current_agent in AGENTS and not break_to_user:
            current_name = state.current_agent
            agent = AGENTS[current_name]
            
            print(f"\n--- {agent.name} is active ---")
            state = agent.run(state)
            
            # Print the agent's last unprinted response
            import re
            for msg in reversed(state.messages):
                if msg.get("role") == "assistant" and msg.get("content"):
                    content = msg['content']
                    # Strip out any lines that are just raw JSON tool calls from Groq Llama 3
                    clean_lines = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if not (line.startswith('{') and line.endswith('}')):
                            clean_lines.append(line)
                    cleaned_content = '\n'.join(clean_lines).strip()
                    
                    if cleaned_content:
                        print(f"\n{agent.name}: {cleaned_content}")
                    break
            
            # If the agent handed off, state.current_agent will be different.
            if state.current_agent != current_name:
                print(f"\n>>> Internal Handoff to {state.current_agent} <<<")
            else:
                # If agent didn't hand off, it is waiting for user input
                break_to_user = True
                
        if state.current_agent == "Completed":
            print("\n*** Transaction successfully completed. Thank you! ***")
            break
            
        if state.current_agent == "None":
            print("\n*** Transaction ended. Have a great day! ***")
            break

if __name__ == "__main__":
    run_retail_workflow()
