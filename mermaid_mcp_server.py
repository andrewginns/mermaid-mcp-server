# /// script
# dependencies = [
#     "pydantic>=2.11.5",
#     "mcp[cli]>=1.9.2",
# ]
# ///

import os
import tempfile
import subprocess
import base64
import json
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mermaid-validator")


class MermaidValidationResult(BaseModel):
    """Result of mermaid diagram validation."""

    is_valid: bool = Field(description="Whether the mermaid diagram is valid")
    error_message: Optional[str] = Field(
        None, description="Error message if the diagram is invalid"
    )
    diagram_image: Optional[str] = Field(
        None, description="Base64-encoded PNG image of the rendered diagram if valid"
    )


@mcp.tool()
async def validate_mermaid_diagram(
    diagram_text: str, return_image: bool = False
) -> MermaidValidationResult:
    """
    Validate a mermaid diagram and optionally render it as a PNG image.

    Uses mermaid-cli to validate and render the diagram. Requires mermaid-cli
    to be installed globally via npm: npm install -g @mermaid-js/mermaid-cli

    Args:
        diagram_text: The mermaid diagram text to validate
        return_image: Whether to return the base64-encoded PNG image (default: False)
                     Set to True only when you specifically need the image data.
                     Warning: Images can be very long strings that impact context length.

    Returns:
        A MermaidValidationResult object containing validation results
    """
    temp_file_path = None
    output_file_name = None
    puppeteer_config_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mmd", mode="w", delete=False
        ) as temp_file:
            temp_file.write(diagram_text)
            temp_file_path = temp_file.name

        # Always create output file for validation, but only read it if return_image=True
        output_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        output_file.close()
        output_file_name = output_file.name

        puppeteer_config = {"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as config_file:
            json.dump(puppeteer_config, config_file)
            puppeteer_config_path = config_file.name

        result = subprocess.run(
            [
                "npx",
                "-y",
                "@mermaid-js/mermaid-cli@11.4.2",
                "-i",
                temp_file_path,
                "-o",
                output_file_name,
                "--puppeteerConfigFile",
                puppeteer_config_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            diagram_image = None
            if return_image and output_file_name:
                with open(output_file_name, "rb") as f:
                    diagram_image = base64.b64encode(f.read()).decode("utf-8")

            return MermaidValidationResult(
                is_valid=True, error_message=None, diagram_image=diagram_image
            )
        else:
            return MermaidValidationResult(
                is_valid=False,
                error_message=f"Mermaid diagram is invalid: {result.stderr}",
                diagram_image=None,
            )
    except Exception as e:
        return MermaidValidationResult(
            is_valid=False,
            error_message=f"Error validating mermaid diagram: {str(e)}",
            diagram_image=None,
        )
    finally:
        for file_path in [temp_file_path, output_file_name, puppeteer_config_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")
                    pass


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    mcp.run(transport=transport)
