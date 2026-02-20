import os
import litellm
import logging
from litellm import completion, acompletion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

litellm.suppress_debug_info = True
for name in logging.root.manager.loggerDict:
    if 'litellm' in name.lower():
        logging.getLogger(name).setLevel(logging.ERROR)

# Automatically retry when hitting the free-tier rate limit
litellm.num_retries = 3

# Standard model to use globally unless overridden
DEFAULT_MODEL = "groq/meta-llama/llama-4-scout-17b-16e-instruct"

def get_llm_completion(messages, model=DEFAULT_MODEL, tools=None):
    """
    Wrapper for litellm.completion to ensure consistent configuration
    and full observability across all agents.
    """
    kwargs = {
        "model": model,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        # Disable parallel tool calls - Llama 3.3 generates malformed
        # XML-style calls (<function=...>) when batching is enabled
        kwargs["parallel_tool_calls"] = False

    response = completion(**kwargs)
    return response

async def get_llm_acompletion(messages, model=DEFAULT_MODEL, tools=None):
    """
    Async wrapper for litellm.acompletion to ensure consistent configuration.
    """
    kwargs = {
        "model": model,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        # Disable parallel tool calls - Llama 3.3 generates malformed
        # XML-style calls (<function=...>) when batching is enabled
        kwargs["parallel_tool_calls"] = False

    response = await acompletion(**kwargs)
    return response
