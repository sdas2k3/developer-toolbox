"""Developer Toolbox MCP server."""

import json
import re

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from sandbox_reader import read_sandbox_text


mcp = FastMCP("Developer Toolbox")
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
TODO = re.compile(r"\bTODO\b")


@mcp.tool(annotations=READ_ONLY)
def count_lines(path: str) -> dict[str, int]:
    """Count the lines in a text file. Give a path relative to the sandbox."""
    return {"line_count": len(read_sandbox_text(path).splitlines())}


def reject_invalid_json_constant(value: str) -> None:
    raise ValueError(f"{value} is not a valid JSON number.")


@mcp.tool(annotations=READ_ONLY)
def analyze_json(path: str) -> dict[str, str | int | list[str]]:
    """Summarize the top-level JSON value in a file inside the sandbox."""
    text = read_sandbox_text(path)
    try:
        value = json.loads(text, parse_constant=reject_invalid_json_constant)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error

    if isinstance(value, dict):
        return {"type": "object", "keys": list(value)}
    if isinstance(value, list):
        return {"type": "array", "item_count": len(value)}

    scalar_types = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
    }
    return {"type": scalar_types[type(value)]}


@mcp.tool(annotations=READ_ONLY)
def search_todos(path: str) -> dict[str, list[dict[str, int | str]]]:
    """Find uppercase TODO markers in a file inside the sandbox, with line numbers."""
    lines = read_sandbox_text(path).splitlines()
    return {
        "matches": [
            {"line_number": line_number, "text": line}
            for line_number, line in enumerate(lines, start=1)
            if TODO.search(line)
        ]
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
