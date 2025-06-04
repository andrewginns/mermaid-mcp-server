import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()


async def main():
    """Test the mermaid validator MCP server using Pydantic AI."""
    example_diagram = """
    graph TD
        A[Start] --> B{Is it valid?}
        B -->|Yes| C[Output valid result]
        B -->|No| D[Output error message]
        C --> E[End]
        D --> E
    """

    mermaid_server = MCPServerStdio(
        command="uv",
        args=[
            "run",
            "mermaid_mcp_server.py",
        ],
    )

    agent = Agent(
        "gemini-2.5-pro-preview-05-06",
        system_prompt="""
        You are a helpful assistant that validates mermaid diagrams.
        You will be given a mermaid diagram and you need to validate it using the MCP mermaid validator tool.
        Return whether the diagram is valid, and if not, provide the error message.
        """,
        mcp_servers=[mermaid_server],
    )
    Agent.instrument_all()

    async with agent.run_mcp_servers():
        result = await agent.run(
            "Validate the following mermaid diagram: " + example_diagram
        )
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
