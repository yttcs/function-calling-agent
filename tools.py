import json
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(
    api_key=os.getenv('TAVILY_API_KEY')
)

# ---------
# functions
# ---------
def search(query) -> str:
    search_result = tavily_client.search(query, max_results=1, topic="general", search_depth="basic", max_tokens=500)
    extracted_urls = [result['url'] for result in search_result['results']]
    extract_result = tavily_client.extract(urls=extracted_urls, extract_depth="basic", max_tokens=1000)
    return extract_result

# --------------
# Dictionary map
# --------------

available_functions = {
    "search": search
}

# -------------------
# Function Definitions
# -------------------

tools = [{

     "type": "function",
     "function": {
        "name": "search",
        "description": "search the web based on the user's query, extract the requested data, and return the results as consicely as possible.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },

            "required": ["query"],
            "additionalProperties": False
        },

     },


}]












