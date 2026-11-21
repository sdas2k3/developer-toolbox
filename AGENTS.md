# Developer Toolbox project guidance

- Keep this project a small, local MCP example. Register tools in `server.py` with the official MCP Python SDK and serve them over stdio.
- Read tool inputs through `read_sandbox_text` in `sandbox_reader.py`. Keep tool access read-only and confined to the local `sandbox/` directory. Keep the sandbox root out of the tools' public arguments.
- Reserve stdout for MCP messages. Send diagnostics to stderr.
- Keep sample files in `sandbox/` and use the project environment to run `.venv/bin/python -B -m unittest -v` from this directory.
