---
name: validate-mockup
description: Checks mockup consistency (separate CSS/JS/HTML, JSON tables vs schema, foreign keys, registered screens, links) and fixes whatever is broken. Use after big changes or when asked to validate, review or check the mockup.
allowed-tools: Bash(python3 .claude/hooks/validate.py *)
---

## Steps

1. Run `python3 .claude/hooks/validate.py --all`.
2. For each listed problem, **fix it at the source** (the file and rule indicated). Do not loosen or edit the validator to make the error disappear.
   - Table vs schema: adjust the JSON or `schema.json`, whichever is right for the product.
   - Fixed color or missing variable: use/create the token in `tokens.css`.
   - Unregistered screen or dead link: register it in `screens.json` or fix the link.
3. Run again until `OK` appears.

## Review the script does not do (check by reading the files)

- Does each screen have an entry and an exit, and use the same components as its neighbors?
- Does the same data appear identically on every screen (names, values, statuses)?
- Is there a screen that looks different from the others (spacing, buttons, hand-made tables)?

Reply briefly in Brazilian Portuguese (pt-BR): how many problems there were, what was fixed and what is left for the user to decide.
To look at it in the browser: `python3 docs/mockup/serve.py` and open http://localhost:5173.
