---
name: new-screen
description: Creates a new mockup screen (HTML, JS, data and entry in screens.json) already wired to the others and following the project pattern. Use when asked to "create the X screen" or "add a Y screen".
argument-hint: '[screen name and what it shows or lets the user do]'
allowed-tools: Bash(python3 .claude/hooks/validate.py *)
---

Create a new mockup screen. Request: $ARGUMENTS

The user should not need to explain patterns: they are in `docs/conventions.md`, the product context is in `docs/context.md` and the existing screens show the rest.

Names, identifiers and code comments are in English. UI text and sample data values are in Brazilian Portuguese (pt-BR), and so is your reply to the user.

## 1. Understand what already exists

Read `docs/context.md`, `docs/mockup/data/schema.json`, `docs/mockup/screens.json` and the most similar existing screen (list, detail, form or dashboard) with its JS. With no screen of that type in `docs/mockup/screens/`, use `docs/templates/`.

## 2. Define (in a few lines, without asking what the pattern already settles)

- `id` in kebab-case and the title.
- Screen type and **which tables it uses**. If a table or column is missing, adjust the schema first.
- **Entry**: which screen/menu leads here and which parameter it receives (`?id=`).
- **Exit**: where it leads (back, detail, form).
- Empty state and "not found", when applicable.

Only ask the user if the doubt changes the structure (which data appears, what the flow is) and the context does not answer it. Otherwise pick the simplest option and record the assumption.

## 3. Create, in this order

1. **Data**: new tables or columns in `docs/mockup/data/*.json` and `schema.json`, with ids and foreign keys consistent with the other screens.
2. **CSS**: only if a component is missing, in `components.css`, using tokens. No fixed colors and no styles inside the screen.
3. **JS**: `docs/mockup/js/screens/<id>.js`, using `Mock.ready`, `Mock.tables` and the helpers in `app.js`. No `fetch`, no hardcoded data, no styles.
4. **HTML**: `docs/mockup/screens/<id>.html`, copying the `<head>` and structure of an existing screen, `data-screen="<id>"` and the right `data-layout`.
5. **Registry**: a line in `docs/mockup/screens.json` (`id`, `title`, `file`, `menu`, `description`). `menu: true` only for main navigation.
6. **Flow**: add the entry link in the related screens (button in the list, menu item, etc.) and the exit on this screen. No orphan screens, no dead links.

## 4. Check

Run `python3 .claude/hooks/validate.py --all` and fix until it passes. If a hook reports an error during creation, fix it at the source.

## 5. Reply (short, in pt-BR)

Files created or changed, how it connects to the rest (where it comes from, where it goes) and the assumptions made. Remind the user that to view it they run `python3 docs/mockup/serve.py`.
