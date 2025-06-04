# Mermaid MCP Server

A Model Context Protocol (MCP) server for validating Mermaid diagrams.

Implements a minimal Python wrapper over https://github.com/mermaid-js/mermaid-cli for simpler out of the box use.

## Overview

Python MCP server for validating Mermaid diagrams and (optionally) rendering them as PNG images. It uses the Mermaid CLI tool to perform the validation and rendering.

Also provides a simple Pydantic-AI MCP Client to invoke the MCP server using a Gemini model for testing.

## Quickstart

To use this server with an MCP client (like Claude Desktop), add the following configuration to your MCP settings:

### Configuration Format

1. Clone this repository

2. Add this to your MCP client configuration file (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mermaid-validator": {
      "command": "uv",
      "args": ["run", "/path/to/mermaid_mcp_server.py"],
    }
  }
}
```

### Configuration Options

- **command**: Use `uv` to run the server
- **args**: Run the server script with `uv run`
- **cwd**: Set to the absolute path of your cloned repository
- **env**: Environment variables for the server
  - `MCP_TRANSPORT`: Set to `"stdio"` for standard input/output communication


#### Example Extended Configuration

```json
{
  "mcpServers": {
    "mermaid-validator": {
      "command": "uv", 
      "args": ["run", "/path/to/mermaid_mcp_server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
      }
    }
  }
}
```

## Abstractions Over Mermaid-CLI

The Python wrapper significantly simplifies the usage of the Mermaid CLI by abstracting away complex file handling and command-line arguments:

### Without the wrapper (raw mermaid-cli):
```bash
# Create input file
echo "graph TD; A-->B" > diagram.mmd

# Create puppeteer config file
echo '{"args": ["--no-sandbox", "--disable-setuid-sandbox"]}' > puppeteer-config.json

# Run mermaid-cli with multiple arguments
npx @mermaid-js/mermaid-cli -i diagram.mmd -o output.png --puppeteerConfigFile puppeteer-config.json

# Handle output file and cleanup
```

### With the Python wrapper:
```python
# Simple function call with diagram text
result = await validate_mermaid_diagram("graph TD; A-->B")

# All file handling, configuration, and cleanup is automatic
# Returns structured result with validation status and base64-encoded image
```

### Key Abstractions:

1. **Temporary File Management**: Automatically creates and cleans up temporary `.mmd` input files
2. **Output File Handling**: Manages temporary `.png` output files and converts them to base64 strings
3. **Puppeteer Configuration**: Automatically generates the required sandboxing configuration for headless browser rendering
4. **Error Handling**: Captures and returns structured error messages instead of raw stderr output
5. **Command Construction**: Builds the complete `npx @mermaid-js/mermaid-cli` command with all necessary flags
6. **Resource Cleanup**: Ensures all temporary files are properly deleted after processing

This abstraction allows users to focus on diagram validation and rendering without dealing with the underlying file system operations and command-line complexities.


# Local Development

This repository can be used standalone to test the functionality of the Mermaid MCP validator programmatically.

## Requirements

- uv for Python and dependency management
- Node.js with npm
- Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`

## Quick Setup (Recommended)

Use the provided Makefile for streamlined setup:

```bash
# Install all dependencies (Python + Node.js + Mermaid CLI)
make install

# Run validation tests
make test
```

## Manual Setup

If you prefer manual setup:

1. Clone this repository
2. Install dependencies: `uv sync`
3. Install Mermaid CLI: `npm install -g @mermaid-js/mermaid-cli`
4. Copy `.env.example` to `.env` and fill in your API key
5. Run the server: `uv run mermaid_mcp_server.py`

## Usage

The server exposes a tool for validating Mermaid diagrams:

- `validate_mermaid_diagram`: Validates a Mermaid diagram and returns validation results

### Tool Parameters

- `diagram_text` (required): The Mermaid diagram text to validate
- `return_image` (optional, default: `false`): Whether to return the base64-encoded PNG image

### Context Length Optimisation

**Important**: By default, the tool does not return the base64-encoded image (`return_image=false`) to preserve context length in LLM conversations. Base64-encoded images can be very long strings (often 10KB-100KB+) that significantly impact the available context for the conversation.

**When to use each setting**:
- `return_image=false` (default): Use for diagram validation only. Fast and context-efficient.
- `return_image=true`: Use only when you specifically need the rendered image data. Warning: This will consume significant context length.

### Example Usage

```python
# Validation only (recommended for most cases)
result = await validate_mermaid_diagram("graph TD; A-->B")
# Returns: MermaidValidationResult(is_valid=True, error_message=None, diagram_image=None)

# Validation with image (use sparingly)
result = await validate_mermaid_diagram("graph TD; A-->B", return_image=True)
# Returns: MermaidValidationResult(is_valid=True, error_message=None, diagram_image="iVBORw0KGgoAAAANSUhEUg...")
```

## Testing

The project includes convenient testing commands:

```bash
# Run all tests
make test

# Or run the test script directly
uv run test_pydantic.py
```

The test script uses Pydantic AI with Gemini models to validate the MCP server functionality.