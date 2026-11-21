import sys
import unittest
from datetime import timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_discover_and_call_tools_over_stdio(self):
        server = StdioServerParameters(
            command=sys.executable,
            args=["-B", str(Path(__file__).with_name("server.py").resolve())],
        )
        async with stdio_client(server) as (reader, writer):
            async with ClientSession(
                reader, writer, read_timeout_seconds=timedelta(seconds=10)
            ) as client:
                initialized = await client.initialize()
                self.assertEqual(initialized.serverInfo.name, "Developer Toolbox")

                discovered = await client.list_tools()
                self.assertCountEqual(
                    [tool.name for tool in discovered.tools],
                    ["count_lines", "analyze_json", "search_todos"],
                )
                for tool in discovered.tools:
                    self.assertEqual(tool.inputSchema["required"], ["path"])
                    self.assertEqual(tool.inputSchema["properties"]["path"]["type"], "string")
                    self.assertTrue(tool.annotations.readOnlyHint)

                examples = [
                    ("count_lines", "notes.txt", {"line_count": 3}),
                    (
                        "analyze_json",
                        "example.json",
                        {"type": "object", "keys": ["project", "tools"]},
                    ),
                    (
                        "search_todos",
                        "notes.txt",
                        {
                            "matches": [
                                {"line_number": 2, "text": "TODO: Try listing tools in Inspector."},
                                {"line_number": 3, "text": "TODO: Run the line counter on this file."},
                            ]
                        },
                    ),
                ]
                for name, path, expected in examples:
                    with self.subTest(tool=name):
                        result = await client.call_tool(name, {"path": path})
                        self.assertFalse(result.isError, result.content)
                        self.assertEqual(result.structuredContent, expected)

                for name, _, _ in examples:
                    with self.subTest(rejected_path=name):
                        result = await client.call_tool(name, {"path": "../notes.txt"})
                        self.assertTrue(result.isError)
                        self.assertIn("Use a file path inside the sandbox", result.content[0].text)

                invalid_json = await client.call_tool("analyze_json", {"path": "notes.txt"})
                self.assertTrue(invalid_json.isError)
                self.assertIn("Invalid JSON", invalid_json.content[0].text)
