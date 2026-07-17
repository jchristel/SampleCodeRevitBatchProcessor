# Wiring the roommate MCP server into a host

`bin/mcp.rs` is an [MCP](https://modelcontextprotocol.io) server over **stdio**:
the host launches it as a child process, speaks JSON-RPC on stdin/stdout, and it
exposes roommate's read side (`list_projects`, `get_rooms`, `get_validation`,
`get_hierarchy_areas`, …) as tools. See [STRATEGY-MCP.md](STRATEGY-MCP.md) for
what it is and why; this file is the concrete "how do I plug it into a client".

## 0. Build it

```sh
cd .../VS/duHastApplications/roommate
cargo build --release --bin mcp        # -> target/release/mcp.exe  (drop .exe on Linux/macOS)
```

Invocation (the host runs this for you):

```
mcp.exe --server-settings <server.toml> --project-settings <projects-dir> [--server-url http://127.0.0.1:5151]
```

- `--server-settings` / `--project-settings` — the **same** files the HTTP server
  reads, so the two front doors see identical data. Their own relative paths
  (storage root, seed) resolve against the settings file's directory, so absolute
  paths here work regardless of the host's working directory.
- `--server-url` — only used by the one mutating tool (`upload_drofus`), which
  forwards to the running HTTP server (the single writer). Read-only tools need no
  HTTP server at all.
- **stdout is the JSON-RPC transport; logs go to stderr.** Don't wrap the command
  in anything that prints to stdout.

## 1. Claude Desktop

Edit `claude_desktop_config.json` (Windows: `%APPDATA%\Claude\`, macOS:
`~/Library/Application Support/Claude/`) and add an `mcpServers` entry with
**absolute** paths (Desktop launches it with an arbitrary working directory):

```json
{
  "mcpServers": {
    "roommate": {
      "command": "C:\\Users\\janchristel\\Documents\\GitHub\\SampleCodeRevitBatchProcessor-NET8\\VS\\duHastApplications\\roommate\\target\\release\\mcp.exe",
      "args": [
        "--server-settings", "C:\\Users\\janchristel\\Documents\\GitHub\\SampleCodeRevitBatchProcessor-NET8\\VS\\duHastApplications\\roommate\\settings\\server.toml",
        "--project-settings", "C:\\Users\\janchristel\\Documents\\GitHub\\SampleCodeRevitBatchProcessor-NET8\\VS\\duHastApplications\\roommate\\settings\\projects"
      ]
    }
  }
}
```

Restart Claude Desktop; "roommate" appears in the tools list. (For `upload_drofus`
to work, also start the HTTP server and add `"--server-url", "http://127.0.0.1:5151"`.)

## 2. Claude Code

A project-scoped [`.mcp.json`](../.mcp.json) is committed at the roommate crate
root, so opening Claude Code **in the roommate directory** picks it up
automatically. It uses `cargo run` so there's nothing to pre-build and no
machine-specific path — at the cost of a one-time compile on first launch:

```json
{ "mcpServers": { "roommate": { "command": "cargo",
  "args": ["run", "-q", "--bin", "mcp", "--",
           "--server-settings", "settings/server.toml",
           "--project-settings", "settings/projects"] } } }
```

`-q` keeps cargo's status lines off stdout so they can't corrupt the JSON-RPC
stream. Relative settings paths resolve against the working directory, so launch
Claude Code from `.../roommate` (or replace them with absolute paths to launch
from anywhere). Equivalent one-liner without editing a file:

```sh
claude mcp add roommate -- cargo run -q --bin mcp -- \
  --server-settings settings/server.toml --project-settings settings/projects
```

## 3. Verify

Any host: after wiring, the tool list should show `get_rooms`,
`get_hierarchy_areas`, etc. A transport-level smoke test without a host:

```sh
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_hierarchy_areas","arguments":{"project_id":"sample-project"}}}' \
 | target/release/mcp.exe --server-settings settings/server.toml --project-settings settings/projects
```

The `id:2` response carries the areas JSON — the same shape `GET /projects/{id}/areas` returns.
