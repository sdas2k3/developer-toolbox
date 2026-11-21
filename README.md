# Developer Toolbox

A small, read-only MCP server built with FastMCP from the official Python MCP SDK. It runs locally over stdio and reads UTF-8 files inside `sandbox/`.

## Setup and tests

From this folder on macOS or Linux, use Python 3.10 or newer to create an environment. If `.venv/` already exists, start at the second command.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B -m unittest -v
```

The tests cover the file boundary and use a Python MCP client to launch the server, discover the tools, and call them over stdio.

## Try the tools

The command an MCP client uses to start the server is `.venv/bin/python server.py`. Running it directly in a terminal waits for MCP messages on standard input. For the browser walkthrough, launch [MCP Inspector](https://github.com/modelcontextprotocol/inspector) from this folder with Node.js and `npx` available.

```sh
npx @modelcontextprotocol/inspector .venv/bin/python server.py
```

If Node.js is installed in this project's `.node/` folder, run the same command with its bin directory on your PATH.

```sh
PATH="$PWD/.node/bin:$PATH" npx @modelcontextprotocol/inspector .venv/bin/python server.py
```

Click **Connect**, then **List Tools**. Select a tool, enter the sample `path`, and click **Run Tool**.

| Tool | Sample `path` | Expected result |
| --- | --- | --- |
| `count_lines` | `notes.txt` | `{"line_count": 3}`. Blank lines count. |
| `analyze_json` | `example.json` | `{"type": "object", "keys": ["project", "tools"]}`. Arrays report an item count and scalars report their JSON type. |
| `search_todos` | `notes.txt` | Two matches, on lines 2 and 3. Each match includes the line text. |

Try `../notes.txt` in any tool to see a rejected request. The shared reader also rejects absolute paths and symbolic links.

## How a call works

Inspector is the **host** you interact with. Its MCP **client** launches the Python **server** and exchanges JSON-RPC messages over the server's standard input and output. The connection starts with an `initialize` request and a `notifications/initialized` notification. Then `tools/list` fetches the available tools and their inputs, and `tools/call` runs the tool you choose.
