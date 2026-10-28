#!/usr/bin/env python3
"""SessionStart hook: prints a short summary of the mockup state (stdout goes into Claude's context)."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
MOCKUP = PROJECT / "mockup"


def read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def main():
    context = PROJECT / "docs" / "context.md"
    filled = context.exists() and "NOT-FILLED" not in context.read_text(encoding="utf-8")
    registry = read(MOCKUP / "screens.json") or {}
    schema = (read(MOCKUP / "data" / "schema.json") or {}).get("tables", {})

    print(f"[mockup] Project: {registry.get('project', '(unnamed)')}")
    if filled:
        print("[mockup] Product context: docs/context.md is filled in.")
    else:
        print("[mockup] Product context NOT filled in yet: if the user wants to start a new project, suggest /new-mockup.")

    screens = registry.get("screens", [])
    print(f"[mockup] Screens ({len(screens)}): " + (", ".join(s["id"] for s in screens if "id" in s) or "none"))
    if schema:
        parts = []
        for name, definition in schema.items():
            fks = ", ".join(f"{c}->{t}" for c, t in (definition.get("fk") or {}).items())
            parts.append(f"{name}({len(definition.get('columns', {}))} cols{'; ' + fks if fks else ''})")
        print("[mockup] Tables: " + ", ".join(parts))
    print("[mockup] Before creating/changing screens: read docs/conventions.md (imported in CLAUDE.md) and use /new-screen.")
    print("[mockup] View in the browser: python3 mockup/serve.py -> http://localhost:5173")
    print("[mockup] Reply to the user in Brazilian Portuguese (pt-BR).")


if __name__ == "__main__":
    main()
