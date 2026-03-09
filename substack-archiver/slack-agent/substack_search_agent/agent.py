import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

MCP_URL = os.getenv("MCP_URL", "http://mcp-server:8001")

mcp_tool = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{MCP_URL}/mcp",
    ),
)

root_agent = LlmAgent(
    model=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
    name="substack_search_agent",
    instruction="""You are a helpful assistant with access to a personal Substack newsletter archive.
When users ask questions, use the search_substacks tool to find relevant articles.
Always cite your sources — include the article title and URL in your response.
Keep your response concise and conversational, suitable for Slack.""",
    tools=[mcp_tool],
)
