import json
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from datetime import datetime, timezone


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

def get_date():
    return datetime.now().strftime("%m-%d-%Y")

# we give the LLM UTC time that's timezone aware and let it do any calculations accordingly
def get_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now.strftime("%H:%M")

# --------------
# Dictionary map
# --------------

available_functions = {
    "search": search,
    "get_date": get_date,
    "get_time": get_time
}

# -------------------
# Function Definitions
# -------------------

tools = [


    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "search the web based on the user's query, utilize metods, to include scraping, to extract the requested data, and return the results as consicely as possible.",
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

    },

    {
        "type": "function",
        "function": {
        "name": "get_date",
        "description": "Get the current date in Month - Day - Year",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
     },
    },


    {
        "type": "function",
        "function": {
        "name": "get_time",
        "description": "Get UTC time in Hour:Minute so that tmmezone offset can be applied based on user request.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
     },
    }


]












