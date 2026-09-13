# How an MCP Client Works?
# pip install langchain-mcp-adapters
# Create an MCP Client 
# Connect to the MCP Server
# Discover available tools, resources, and prompts (client.get_tools())
# Share these capabilities with the Host (AI App or LLM)
# Execute tools (ainvoke) when requested and return the results
#initialize_mcp(): MCP Client asks to MCP server what tools you have
import os
import asyncio

from dotenv import load_dotenv
# to create mcp client in langgraph
from langchain_mcp_adapters.client import MultiServerMCPClient

#load_dotenv()
load_dotenv(override=True)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Create an MCP Client 

client = MultiServerMCPClient(
    {
        #mcp server provided by Tavily (we are using remote MCP Server)
        #https://docs.tavily.com/documentation/mcp

        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
        
        # Since AviationStack does not provide MCP server but someone else already created on github so we will use th same
        "aviationstack": {
            "transport": "stdio",
            "command": r"C:\ai\multi-agents-travel-planner-mcp\aviationstack-mcp\.venv\Scripts\python.exe",
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
            }
        },

        # we will create complete custom MCP server for weather App on local
        "weather": {
            "transport": "stdio",
            "command": r"C:\ai\multi-agents-travel-planner-mcp\langgraph_env3\Scripts\python.exe",
            "args": [
                r"C:\ai\multi-agents-travel-planner-mcp\custom_weather_mcp_server.py"
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }

    }

)



# Discover available tools, resources, and prompts
#python .\mcp_client.py

# async def main():

#     tools = await client.get_tools()

#     print("\nAvailable MCP Tools:\n")

#     for tool in tools:
#         print(tool.name)


# async def main():
#     tools = await client.get_tools()

# using tavily has many tools available on MCP server we need for hotel search only

#     search_tool = next(
#         tool
#         for tool in tools
#         if tool.name == "tavily_search"
#     )

#   To execute the tool we will use ainvoke function

#     result = await search_tool.ainvoke(
#         {
#             "query": "Best hotels in Delhi"
#         }
#     )

#     print(result)

# asyncio.run(main()) 


# search_tool = None

# async def initialize_mcp():
#     global search_tool
#     if search_tool is not None:
#         return

#     tools = await client.get_tools()
#     print("\nAvailable MCP Tools:")

#     for tool in tools:
#         print(tool.name)

#     search_tool = next(
#         tool
#         for tool in tools
#         if tool.name == "tavily_search"
#     )



search_tool = None
aviation_tools = {}

async def initialize_mcp():

    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }





async def tavily_mcp_search(query: str):

    # when AI app will start MCP client will ask MCP server that what tools you have for that we are using initialize_mcp()
    await initialize_mcp()
    result = await search_tool.ainvoke(
        {
            "query": query
        }
    )
    return result




async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict = None
):

    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result



async def get_airports():

    await initialize_mcp()

    tool = aviation_tools.get("list_airports")

    if not tool:
        return "Airport tool unavailable"

    result = await tool.ainvoke({})

    return result


async def get_airlines():

    await initialize_mcp()

    tool = aviation_tools.get("list_airlines")

    if not tool:
        return "Airline tool unavailable"

    result = await tool.ainvoke({})

    return result





weather_tool = None
forecast_tool = None


async def initialize_weather_tools():

    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )


async def weather_mcp_search(city: str):

    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )


async def forecast_mcp_search(city: str):

    await initialize_weather_tools()

    return await forecast_tool.ainvoke(
        {
            "city": city
        }
    )




from langchain_groq import ChatGroq

# LLM
llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    temperature=0,
    max_tokens=900
)

###################################
# Destination Extractor
###################################

def extract_destination(query: str):

    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    response = llm.invoke(prompt)

    return response.content.strip()


if __name__ == "__main__":
    asyncio.run(main())