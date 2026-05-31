# Luna MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

MCP server for debugging [Luna](https://lunalabs.io) (Unity-to-JS transpiler) builds running in Chrome via CDP.

> **Disclaimer:** This is an unofficial community tool. Luna is a product of [Luna Labs](https://lunalabs.io). This project is not affiliated with, endorsed by, or sponsored by Luna Labs.

## What it does

Connects an AI coding assistant to a Luna build running in Chrome via the Chrome DevTools Protocol. 75 exposed tools covering:

- **Scene inspection** — traverse hierarchy, read component properties, query objects by name/type
- **Property editing** — set component fields at runtime, toggle flags, modify transforms
- **Screenshots & visual analysis** — capture the current view, compare before/after, detect regressions
- **Build diffing** — compare two Luna builds, surface added/removed/changed symbols
- **Flag exploration** — enumerate feature flags and experiment configs exposed by the build
- **Physics diagnostics** — inspect colliders, rigidbody state, velocity, contact points
- **Console & error monitoring** — stream JS console output, capture exceptions with stack traces
- **Performance metrics** — frame time, draw calls, memory usage

```
AI Assistant <--stdio--> Luna MCP (Python) <--CDP WebSocket--> Chrome (Luna build)
```

Works with any MCP-compatible client: **Claude Code**, **OpenAI Codex CLI**, Cursor, Windsurf, and others.

## Requirements

- Python >= 3.10
- Google Chrome (or Chromium) launched with `--remote-debugging-port=9222`
- A Luna build served locally or remotely and opened in that Chrome instance
- **Luna Debugger** Chrome extension (optional but recommended — see below)

### Luna Debugger Extension

The [Luna Debugger](https://lunalabs.io) is a Chrome extension that ships with the Luna SDK. It exposes `pc.Debugger.*` APIs inside the browser, giving Luna MCP access to deep runtime introspection.

**Without the extension** (~50 tools work): scene hierarchy, screenshots, console, performance metrics, property editing, transforms, animations, build analysis, physics probes — everything that runs via standard CDP and injected JS helpers.

**With the extension** (~75 tools work): adds component field introspection, type info, enum values, custom component registration, animator state details, collider visualization, and the raw debugger message API.

To install: open a Luna build in Chrome, then follow the [Luna Debugger setup guide](https://docs.lunalabs.io/docs/playable/code/plugin-in-browser/debug-js/). The extension activates automatically when a Luna build is detected.

> **Tip:** If you don't have the extension, Luna MCP still works — tools that require it return a clear error message and the rest function normally.

## Installation

```bash
git clone https://github.com/german-krasnikov/luna-kiss-mcp.git
cd luna-kiss-mcp/server
pip install -e ".[dev]"
```

## Launch Chrome

Chrome must be running with remote debugging enabled **before** the MCP server connects.

**macOS:**

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/luna-debug-profile
```

**Linux:**

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/luna-debug-profile
```

**Windows (PowerShell):**

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:TEMP\luna-debug-profile"
```

> **Important:** The `--user-data-dir` flag is required when Chrome is already running — without it, the debugging port flag is silently ignored.

Open your Luna build URL in that Chrome window before proceeding.

---

## Setup: Claude Code

Claude Code supports MCP servers via JSON config. Two scopes:

| Scope | File | Use case |
|-------|------|----------|
| **Project** | `.mcp.json` in project root | Shared with team, checked into git |
| **User** | `~/.claude.json` | Personal, all projects |

### Option A: Project config (recommended)

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "luna-mcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "luna_mcp.server"],
      "cwd": "/absolute/path/to/luna-kiss-mcp/server",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Option B: Using a virtualenv

If you installed into a virtualenv, point `command` directly at it:

```json
{
  "mcpServers": {
    "luna-mcp": {
      "type": "stdio",
      "command": "/absolute/path/to/luna-kiss-mcp/server/.venv/bin/python3",
      "args": ["-m", "luna_mcp.server"],
      "cwd": "/absolute/path/to/luna-kiss-mcp/server",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Option C: With environment variables

```json
{
  "mcpServers": {
    "luna-mcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "luna_mcp.server"],
      "cwd": "/absolute/path/to/luna-kiss-mcp/server",
      "env": {
        "PYTHONPATH": "src",
        "LUNA_CDP_PORT": "9222",
        "LUNA_PAGE_FILTER": "my-build",
        "LUNA_PLUGIN_PATH": "/path/to/Playworks/7.1.0",
        "LUNA_BUDGET_MODE": "deep_debug"
      }
    }
  }
}
```

### Verify

Restart Claude Code (or run `/mcp` to check status), then ask:

```
Inspect the Luna scene hierarchy
```

or

```
Take a screenshot of the current build
```

---

## Setup: OpenAI Codex CLI

Codex CLI uses TOML config. Two scopes:

| Scope | File | Use case |
|-------|------|----------|
| **Project** | `.codex/config.toml` in project root | Shared with team |
| **User** | `~/.codex/config.toml` | Personal, all projects |

### Option A: Project config (recommended)

Create `.codex/config.toml` in your project root:

```toml
[mcp_servers.luna-mcp]
command = "python3"
args = ["-m", "luna_mcp.server"]
cwd = "/absolute/path/to/luna-kiss-mcp/server"

[mcp_servers.luna-mcp.env]
PYTHONPATH = "src"
```

### Option B: Using a virtualenv

```toml
[mcp_servers.luna-mcp]
command = "/absolute/path/to/luna-kiss-mcp/server/.venv/bin/python3"
args = ["-m", "luna_mcp.server"]
cwd = "/absolute/path/to/luna-kiss-mcp/server"

[mcp_servers.luna-mcp.env]
PYTHONPATH = "src"
```

### Option C: With environment variables

```toml
[mcp_servers.luna-mcp]
command = "python3"
args = ["-m", "luna_mcp.server"]
cwd = "/absolute/path/to/luna-kiss-mcp/server"

[mcp_servers.luna-mcp.env]
PYTHONPATH = "src"
LUNA_CDP_PORT = "9222"
LUNA_PAGE_FILTER = "my-build"
LUNA_BUDGET_MODE = "deep_debug"
```

### Verify

Restart Codex CLI, then ask:

```
Use luna-mcp to get the scene hierarchy
```

---

## Setup: Other MCP Clients

Any MCP client that supports stdio transport can connect. The server command is always:

```bash
cd /path/to/luna-kiss-mcp/server && PYTHONPATH=src python3 -m luna_mcp.server
```

The server communicates via stdin/stdout using the MCP protocol. No HTTP server, no ports — just stdio.

**Cursor / Windsurf / Continue:** These editors use the same JSON format as Claude Code. Add the `luna-mcp` entry to their respective MCP config files.

---

## Environment Variables

| Var | Default | Description |
|-----|---------|-------------|
| `LUNA_CDP_PORT` | `9222` | Chrome remote debugging port |
| `LUNA_PAGE_FILTER` | — | Substring to filter Luna page URL (useful when multiple tabs are open) |
| `LUNA_PLUGIN_PATH` | — | Path to Playworks plugin for typemap resolution (enables C#→JS mapping) |
| `LUNA_VISUAL_LLM` | `0` | Enable server-side LLM analysis on screenshots (`1` to enable) |
| `LUNA_BUDGET_MODE` | `work` | Token budget: `warmup` (5k) / `work` (30k) / `deep_debug` (100k) / `auto` |
| `LUNA_BUDGET_DISABLED` | `0` | Disable cost budget router entirely (`1` to disable) |
| `LUNA_RECORD` | `0` | Record MCP sessions to JSONL (`1` to enable) |
| `LUNA_MCP_DATA_DIR` | `~/.luna_mcp` | Data directory for lessons DB, baselines, templates |
| `LUNA_COMPANY_HINT` | `AcmeCorp` | Company name for federation privacy scrub |

## Troubleshooting

**"No Luna page found" / connection refused**

- Confirm Chrome launched with `--remote-debugging-port=9222` (check `lsof -i :9222` on macOS/Linux).
- The `--user-data-dir` flag is required on macOS when Chrome is already running — without it, the flag is silently ignored.
- If multiple tabs are open, set `LUNA_PAGE_FILTER` to a substring of your build's URL so the server targets the right tab.

**MCP server doesn't appear in your client**

- Restart the client after editing the MCP config.
- Verify `cwd` points to the `server/` subdirectory of this repo, not the repo root.
- Run manually to surface errors: `cd server && PYTHONPATH=src python3 -m luna_mcp.server`
- Check that Python >= 3.10 is being used: `python3 --version`

**"Module not found" errors**

- Ensure you ran `pip install -e ".[dev]"` from the `server/` directory.
- If using a virtualenv, make sure `command` in the config points to the venv Python, not the system one.

**Screenshots are blank / all black**

- The Luna page must be visible (not minimized or in a background tab) when the screenshot tool fires.
- Try adding `--disable-gpu` to Chrome launch flags.

**Server connects but tools return errors**

- Check `get_console level=E count=20` for JS errors in the Luna build itself.
- Ensure the Luna build has finished loading before calling tools.
- Try `ping` first — it verifies the CDP connection without touching the scene.

## Tool Highlights

The server exposes 77 tools. Here are the most useful starting points:

| Tool | Description |
|------|-------------|
| `get_hierarchy` | Scene tree overview (depth, root params) |
| `screenshot` | Capture current view as PNG |
| `diagnose_object path=X` | Why is this object invisible? (checks active, transform, renderer, material) |
| `get_console level=E` | Recent error logs |
| `get_performance_metrics` | FPS, frame time, heap, load time |
| `set_property` | Change component field at runtime |
| `batch commands="cmd1\ncmd2"` | Run multiple tools in one round-trip (80%+ token savings) |
| `do intent="..."` | AI-planned multi-step workflow |
| `diagnose_physics symptom="..."` | Physics backend detection + symptom diagnosis |
| `diff_builds` | Compare two Luna builds (4-tier: file/semantic/visual/auto) |

Use `batch` for multi-tool workflows — it saves 80%+ tokens compared to calling tools individually.

## Development

```bash
cd server && pytest tests/ -v          # 1700+ tests
cd server && python3 -m luna_mcp.server  # run server manually
```

## License

MIT — see [LICENSE](LICENSE) for details.
