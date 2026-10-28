#!/usr/bin/env python3
"""Mockup validator (standard library only, Python 3.8+).

Usage:
  validate.py --all     validate the whole mockup and print the result (exit 1 on any error)
  validate.py --hook    PostToolUse hook: read the JSON from stdin and validate only the edited file
  validate.py --stop    Stop hook: if the mockup changed in the turn, validate everything and block ONCE on error

What it guarantees (see docs/conventions.md):
  - CSS/JS/HTML kept separate (no <style>, style=, onclick=, inline <script>, fetch outside app.js)
  - colors only in tokens.css; var(--x) only with variables that exist
  - tables in data/*.json match data/schema.json (columns, types, unique ids, foreign keys)
  - screens registered in screens.json, files exist, links and <link>/<script> resolve
  - Mock.tables('x') only asks for tables that exist
"""
import datetime
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
MOCKUP = PROJECT / "docs" / "mockup"
MARKER = PROJECT / ".claude" / ".mockup-changed"
TYPES = {"integer", "number", "text", "date", "boolean"}
LAYOUTS = {"app", "center"}
REQUIRED_CSS = ("tokens.css", "base.css", "components.css")


def rel(path):
    try:
        return Path(path).resolve().relative_to(PROJECT).as_posix()
    except ValueError:
        return str(path)


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def read_json(path, errors):
    try:
        return json.loads(read_text(path))
    except FileNotFoundError:
        errors.append(f"{rel(path)}: file not found")
    except json.JSONDecodeError as e:
        errors.append(f"{rel(path)}: invalid JSON (line {e.lineno}): {e.msg}")
    return None


# ---------------------------------------------------------------- data
def type_ok(value, type_):
    optional = type_.endswith("?")
    base = type_.rstrip("?")
    if value is None:
        return optional
    if base == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if base == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if base == "text":
        return isinstance(value, str)
    if base == "boolean":
        return isinstance(value, bool)
    if base == "date":
        try:
            return isinstance(value, str) and bool(datetime.date.fromisoformat(value))
        except ValueError:
            return False
    return False


def check_schema(errors):
    """Validate data/schema.json. Return the dict of tables, or None if it is broken."""
    before = len(errors)
    schema = read_json(MOCKUP / "data" / "schema.json", errors)
    if schema is None:
        return None
    tables = schema.get("tables")
    if not isinstance(tables, dict) or not tables:
        errors.append('docs/mockup/data/schema.json: missing the "tables" object')
        return None
    for name, definition in tables.items():
        where = f"docs/mockup/data/schema.json (table {name})"
        columns = definition.get("columns") if isinstance(definition, dict) else None
        if not isinstance(columns, dict) or columns.get("id") != "integer":
            errors.append(f'{where}: "columns" must be an object and have "id": "integer"')
            continue
        for column, type_ in columns.items():
            if str(type_).rstrip("?") not in TYPES:
                errors.append(f'{where}: column "{column}" has type "{type_}" (use {", ".join(sorted(TYPES))}; "?" = optional)')
        for column, target in (definition.get("fk") or {}).items():
            if column not in columns:
                errors.append(f'{where}: fk "{column}" is not a column')
            elif target not in tables:
                errors.append(f'{where}: fk "{column}" points to table "{target}" which does not exist')
            elif str(columns[column]).rstrip("?") != "integer":
                errors.append(f'{where}: fk "{column}" must be of type integer')
    return tables if len(errors) == before else None


def check_rows(name, definition, rows, errors):
    file = f"docs/mockup/data/{name}.json"
    if not isinstance(rows, list):
        errors.append(f"{file}: must be a list of objects (one row per record)")
        return
    columns = definition["columns"]
    seen = set()
    for i, row in enumerate(rows, 1):
        where = f"{file}: row {i}"
        if not isinstance(row, dict):
            errors.append(f"{where}: must be an object")
            continue
        missing, extra = set(columns) - set(row), set(row) - set(columns)
        if missing:
            errors.append(f"{where}: missing columns {sorted(missing)} (use null on optional ones)")
        if extra:
            errors.append(f"{where}: columns outside the schema {sorted(extra)} (declare them in schema.json)")
        for column, type_ in columns.items():
            if column in row and not type_ok(row[column], type_):
                errors.append(f'{where}: "{column}" = {row[column]!r} is not of type {type_}')
        id_ = row.get("id")
        if id_ in seen:
            errors.append(f"{where}: id {id_} repeated")
        seen.add(id_)


def check_data(tables, errors):
    folder = MOCKUP / "data"
    content = {}
    for name, definition in tables.items():
        file = folder / f"{name}.json"
        if not file.exists():
            errors.append(f"docs/mockup/data/{name}.json: table is in the schema but the file does not exist")
            continue
        rows = read_json(file, errors)
        if rows is None:
            continue
        check_rows(name, definition, rows, errors)
        content[name] = rows
    for file in sorted(folder.glob("*.json")):
        if file.stem != "schema" and file.stem not in tables:
            errors.append(f"{rel(file)}: table outside the schema (declare it in schema.json or delete the file)")
    # foreign keys
    for name, definition in tables.items():
        for column, target in (definition.get("fk") or {}).items():
            if name not in content or target not in content:
                continue
            target_ids = {r.get("id") for r in content[target] if isinstance(r, dict)}
            for i, row in enumerate(content[name], 1):
                if isinstance(row, dict) and row.get(column) is not None and row[column] not in target_ids:
                    errors.append(f"docs/mockup/data/{name}.json: row {i}: {column}={row[column]} does not exist in {target}")


# ---------------------------------------------------------------- html
RE_REF = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)


def check_html(path, errors):
    text = read_text(path)
    where = rel(path)
    if re.search(r"<style\b", text, re.I):
        errors.append(f"{where}: CSS inside the HTML (<style>): move it to docs/mockup/css/")
    if re.search(r"\sstyle\s*=", text, re.I):
        errors.append(f"{where}: style= attribute: use the classes in components.css (or create one there)")
    if re.search(r"\son(click|change|submit|input|load|keyup|keydown|focus|blur|mouse\w+)\s*=", text, re.I):
        errors.append(f'{where}: inline handler (onclick=...): use data-action="toast" or docs/mockup/js/screens/')
    for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", text, re.I | re.S):
        if "src=" not in m.group(1).lower() or m.group(2).strip():
            errors.append(f"{where}: <script> with code inside the HTML: move it to docs/mockup/js/screens/")
    for css in REQUIRED_CSS:
        if f"css/{css}" not in text:
            errors.append(f"{where}: missing <link> to css/{css}")
    if "js/app.js" not in text:
        errors.append(f"{where}: missing <script> for js/app.js")
    layout = re.search(r'data-layout\s*=\s*["\']([^"\']*)["\']', text)
    if layout and layout.group(1) not in LAYOUTS:
        errors.append(f'{where}: data-layout="{layout.group(1)}" is invalid (use {", ".join(sorted(LAYOUTS))} or omit it)')
    for ref in RE_REF.findall(text):
        if re.match(r"^(https?:|mailto:|tel:|#|data:|javascript:)", ref, re.I):
            continue
        if ref.startswith("/"):
            errors.append(f"{where}: absolute path {ref!r}: use a relative path")
            continue
        target = ref.split("#")[0].split("?")[0]
        if target and not (Path(path).parent / target).exists():
            errors.append(f"{where}: link/file does not exist: {ref}")


# ---------------------------------------------------------------- css
def strip_css_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def defined_variables():
    tokens = MOCKUP / "css" / "tokens.css"
    if not tokens.exists():
        return set()
    return set(re.findall(r"(--[\w-]+)\s*:", strip_css_comments(read_text(tokens))))


def check_css(path, errors):
    text = strip_css_comments(read_text(path))
    where = rel(path)
    if Path(path).name != "tokens.css":
        for m in re.finditer(r"([a-zA-Z-]+)\s*:\s*([^;{}]+)", text):
            if re.search(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla)\(", m.group(2)):
                errors.append(f"{where}: fixed color in '{m.group(1)}: {m.group(2).strip()}': use var(--color-...) from tokens.css")
        if re.search(r"(^|[}\s,>+~])#[a-zA-Z_][\w-]*\s*[{,:.>+~\[ ]", text):
            errors.append(f"{where}: id selector (#...): use classes")
    defined = defined_variables()
    for var in sorted(set(re.findall(r"var\(\s*(--[\w-]+)", text))):
        if var not in defined:
            errors.append(f"{where}: variable {var} does not exist in tokens.css (create it there or use an existing one)")


# ---------------------------------------------------------------- js
def check_js(path, tables, errors):
    text = read_text(path)
    where = rel(path)
    code = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    code = re.sub(r"(?m)^\s*//.*$", "", code)
    if Path(path).name != "app.js":
        if re.search(r"\bfetch\s*\(", code):
            errors.append(f"{where}: direct fetch: read tables with Mock.tables('table')")
        if re.search(r"\.style\.|\bstyle\s*=|setAttribute\(\s*['\"]style", code):
            errors.append(f"{where}: style in JS: use classes from components.css")
        if re.search(r"\b(localStorage|sessionStorage)\b", code):
            errors.append(f"{where}: use Mock.userId()/Mock.signIn() instead of accessing storage directly")
        if re.search(r"\[\s*\{\s*['\"]?id['\"]?\s*:", code):
            errors.append(f"{where}: hardcoded data inside JS: move it to docs/mockup/data/ and declare it in schema.json")
    if tables is not None:
        for m in re.finditer(r"Mock\.tables\(([^)]*)\)", code):
            for name in re.findall(r"""["']([^"']+)["']""", m.group(1)):
                if name not in tables:
                    errors.append(f'{where}: Mock.tables("{name}"): table does not exist in schema.json')


# ---------------------------------------------------------------- screens
def check_registry(errors):
    registry = read_json(MOCKUP / "screens.json", errors)
    if registry is None:
        return
    screens = registry.get("screens") if isinstance(registry, dict) else None
    if not isinstance(screens, list) or not registry.get("project"):
        errors.append('docs/mockup/screens.json: needs "project" (text) and "screens" (list)')
        return
    ids, files = set(), set()
    for s in screens:
        missing = [c for c in ("id", "title", "file") if not isinstance(s, dict) or c not in s]
        if missing:
            errors.append(f"docs/mockup/screens.json: screen without {missing}: {s}")
            continue
        if s["id"] in ids:
            errors.append(f'docs/mockup/screens.json: id "{s["id"]}" repeated')
        ids.add(s["id"])
        files.add(s["file"])
        file = MOCKUP / s["file"]
        if not file.exists():
            errors.append(f'docs/mockup/screens.json: screen "{s["id"]}" points to {s["file"]}, which does not exist')
            continue
        m = re.search(r'data-screen\s*=\s*["\']([^"\']*)["\']', read_text(file))
        if not m or m.group(1) != s["id"]:
            errors.append(f'{rel(file)}: expected <body data-screen="{s["id"]}"> (same as the id in screens.json)')
    for file in sorted((MOCKUP / "screens").glob("*.html")):
        if f"screens/{file.name}" not in files:
            errors.append(f"{rel(file)}: screen not registered in docs/mockup/screens.json")


# ---------------------------------------------------------------- orchestration
def validate_all():
    errors = []
    tables = check_schema(errors)
    if tables:
        check_data(tables, errors)
    check_registry(errors)
    pages = sorted(MOCKUP.glob("*.html")) + sorted((MOCKUP / "screens").glob("*.html"))
    for page in pages:
        check_html(page, errors)
    for css in sorted((MOCKUP / "css").glob("*.css")):
        check_css(css, errors)
    for js in sorted((MOCKUP / "js").rglob("*.js")):
        check_js(js, tables, errors)
    summary = f"{len(pages)} pages, {len(tables or {})} tables"
    return errors, summary


def validate_file(path):
    """Local checks for ONE file (cross-file ones are left to --all at the end of the turn)."""
    errors = []
    path = Path(path).resolve()
    suffix = path.suffix.lower()
    if suffix == ".html":
        check_html(path, errors)
    elif suffix == ".css":
        check_css(path, errors)
    elif suffix == ".js":
        shadow = []
        tables = check_schema(shadow)  # if the schema is still incomplete, just skip the table check
        check_js(path, tables, errors)
    elif suffix == ".json" and path.parent == MOCKUP / "data":
        if path.name == "schema.json":
            check_schema(errors)
        else:
            tables = check_schema([])
            if tables and path.stem in tables:
                rows = read_json(path, errors)
                if rows is not None:
                    check_rows(path.stem, tables[path.stem], rows, errors)
            else:
                read_json(path, errors)
    return errors


def format_errors(errors, limit=15):
    lines = [f"- {e}" for e in errors[:limit]]
    if len(errors) > limit:
        lines.append(f"- ... and {len(errors) - limit} more")
    return "\n".join(lines)


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def read_input():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def hook_mode():
    data = read_input()
    file = (data.get("tool_input") or {}).get("file_path")
    if not file:
        return 0
    path = Path(file)
    if not path.is_absolute():
        path = Path(data.get("cwd") or PROJECT) / path
    try:
        path.resolve().relative_to(MOCKUP)
    except ValueError:
        return 0
    MARKER.write_text("", encoding="utf-8")
    errors = validate_file(path)
    if errors:
        block(f"Fix before continuing (rules in docs/conventions.md):\n{format_errors(errors)}")
    return 0


def stop_mode():
    data = read_input()
    if not MARKER.exists():
        return 0
    errors, _ = validate_all()
    if not errors:
        MARKER.unlink(missing_ok=True)
        return 0
    if data.get("stop_hook_active"):
        MARKER.unlink(missing_ok=True)  # already tried to fix once: let it finish and warn
        print(json.dumps({"systemMessage": f"Mockup still has {len(errors)} problem(s):\n{format_errors(errors)}"}, ensure_ascii=False))
        return 0
    block(f"The mockup has {len(errors)} consistency problem(s). Fix them before finishing:\n{format_errors(errors)}\n"
          "Then run: python3 .claude/hooks/validate.py --all")
    return 0


def all_mode():
    errors, summary = validate_all()
    if errors:
        print(f"{len(errors)} problem(s):\n{format_errors(errors, limit=60)}")
        return 1
    print(f"OK — {summary}, everything consistent.")
    MARKER.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--all"
    sys.exit({"--hook": hook_mode, "--stop": stop_mode, "--all": all_mode}.get(mode, all_mode)())
