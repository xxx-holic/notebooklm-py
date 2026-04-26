# NotebookLM for Codex

Use this guide when Codex is asked to automate NotebookLM through `notebooklm-py`.
It is the Codex-facing counterpart to the Hermes skill layout in `skills/notebooklm/`.

## One-time install

From a released or forked GitHub checkout:

```bash
python -m pip install "notebooklm-py[browser,cookies] @ git+https://github.com/xxx-holic/notebooklm-py@main"
python -m playwright install chromium
notebooklm skill install --target codex
```

From this source checkout while developing:

```bash
python -m pip install -e ".[browser,cookies]"
python -m playwright install chromium
notebooklm skill install --target codex
```

The Codex target writes the skill to:

- user scope: `~/.codex/skills/notebooklm/SKILL.md`
- project scope: `<project>/.codex/skills/notebooklm/SKILL.md`

## Authentication

Prefer browser-cookie import for Codex sessions so automation does not trigger repeated
new-device login flows:

```bash
notebooklm login --browser-cookies chrome
notebooklm auth check --test
notebooklm list --json
```

If Google rotates cookies during a long Codex run, configure one-shot refresh:

```bash
export NOTEBOOKLM_REFRESH_CMD="notebooklm login --browser-cookies chrome"
```

PowerShell:

```powershell
$env:NOTEBOOKLM_REFRESH_CMD = "notebooklm login --browser-cookies chrome"
```

## Codex operating rules

1. Start with `notebooklm auth check --test` and one low-cost `notebooklm list --json`.
2. Prefer `--json` output and parse IDs from JSON instead of terminal tables.
3. Pass full notebook UUIDs with `--notebook` or `-n`; do not rely on `notebooklm use`
   in parallel Codex tasks.
4. Isolate concurrent Codex runs with either:
   - `NOTEBOOKLM_HOME=<workspace>/.codex/notebooklm/<run-id>`; or
   - `NOTEBOOKLM_PROFILE=codex-<run-id>`.
5. Never print or commit `storage_state.json`, cookies, exported browser JSON, or `.env`.
6. Treat `accepted` NotebookLM calls separately from durable automation: capture the
   command, JSON output, IDs, and rerun command before reporting success.

## Useful Codex command patterns

```bash
# Discover notebooks as machine-readable JSON
notebooklm list --json

# Create a notebook and capture the UUID
notebooklm create "Research" --json

# Add sources without changing global context
notebooklm source add "https://example.com" --notebook <notebook_uuid> --json

# Ask using explicit notebook and JSON output
notebooklm ask "Summarize the key evidence" --notebook <notebook_uuid> --json

# Wait/download by explicit notebook and artifact IDs
notebooklm artifact wait <artifact_id> -n <notebook_uuid> --json
notebooklm download audio ./podcast.mp3 -n <notebook_uuid> -a <artifact_id>
```

## Failure handling

- Auth expired: run `$NOTEBOOKLM_REFRESH_CMD` once if configured, then retry the exact command.
- Ambiguous or rejected IDs: re-run `notebooklm list --json` and use the full UUID.
- Parallel context drift: stop using `notebooklm use`; set a unique `NOTEBOOKLM_HOME` or profile.
- Browser-cookie import blocked: fall back to `notebooklm login` only when interactive browser
  login is acceptable for the current Codex task.
