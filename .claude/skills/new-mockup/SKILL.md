---
name: new-mockup
description: Starts a new mockup from scratch. Asks a few questions about the product, saves the context, proposes tables and screens for approval and then creates everything following the conventions.
argument-hint: '[product name and one sentence about it]'
disable-model-invocation: true
allowed-tools: Bash(python3 .claude/hooks/validate.py *) Bash(mkdir *) Bash(mv *)
---

You are going to start a new mockup. Goal: get the context right **before** any screen, to avoid redoing work. User input: $ARGUMENTS

Names, identifiers and code comments are in English. Everything the user reads (questions, UI text, sample data values, `docs/context.md`, your replies) is in Brazilian Portuguese (pt-BR).

## 1. Check the state

Read `docs/context.md` and `docs/mockup/screens.json`.

- If the context is already filled in (no `NOT-FILLED` in the file) or `project` is not "Projeto Exemplo", **a project already exists here**. Warn the user and ask whether to start over (this deletes the current screens and tables) or use `/new-screen`. Continue only with explicit confirmation.

## 2. Interview (one question at a time, plain language, in pt-BR)

Ask at most 6 questions, one per message, skipping the ones `$ARGUMENTS` or earlier answers already cover:

1. Product name and, in one sentence, what it is.
2. Who uses it (profiles) and in what situation/device (phone in the field, computer in the office...).
3. The 3 things the person needs to do quickly.
4. Which "things" exist in the business (e.g. order, customer, animal) and how they relate.
5. Which screens they imagine and where the person starts (is there a login?).
6. Visual tone and accent color (or "doesn't matter").

Vague or missing answer: record "não informado". Do not fill it in with assumptions.

## 3. Save the context

Fill `docs/context.md` with what was said (keep the sections of the file) and **delete the `NOT-FILLED` line**.

## 4. Propose and wait for approval

Show, as a short list:

- **Tables**: name, columns with type, foreign keys and domain tables (status, types). At most ~6 tables.
- **Screens**: id, type (list/detail/form/dashboard), where it comes from and where it goes.

Ask whether it looks good. **Do not create anything before the go-ahead.** Apply the requested adjustments.

## 5. Prepare the mockup

1. Keep the molds (do not delete them): `mkdir -p docs/templates/screens docs/templates/js`, move `docs/mockup/screens/*.html` to `docs/templates/screens/` and `docs/mockup/js/screens/*.js` to `docs/templates/js/`. Create `docs/templates/README.md` (2 lines, in pt-BR): they are mold screens (login, list, detail, form, list with count); copy them to `docs/mockup/screens` and `docs/mockup/js/screens`, the relative paths already work there.
2. Data: delete `docs/mockup/data/*.json` except `schema.json`; rewrite `schema.json` and create one JSON per approved table (realistic and small data, 3 to 10 rows, in Portuguese, consistent ids and keys).
3. Reset `docs/mockup/screens.json` to `{ "project": "<name>", "screens": [] }`.
4. Visual: adjust **only** `docs/mockup/css/tokens.css` (accent color and its variations) according to answer 6.
5. Create the approved screens following the `new-screen` skill procedure, using the molds in `docs/templates/`. Login (or the start screen) first: the first screen registered in `screens.json` is the flow entry. For 3 or more independent screens, you may delegate to the `mockup-builder` agent.

## 6. Wrap up

Run `python3 .claude/hooks/validate.py --all` and fix whatever it reports. Reply briefly in pt-BR: what was created, how to open it (`python3 docs/mockup/serve.py`, then http://localhost:5173) and the open questions left in `docs/context.md`.
