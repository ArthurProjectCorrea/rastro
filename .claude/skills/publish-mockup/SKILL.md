---
name: publish-mockup
description: Publishes the mockup folder (docs/mockup) as a static site on Cloudflare Workers through a GitHub Actions workflow, sets up the repository variable and secret safely, optionally protects it with Cloudflare Access, and tests the result. Use when asked to publish, deploy or put the mockup online, or to fix its deploy pipeline.
argument-hint: '[worker name, branch and who may view it (optional)]'
allowed-tools: Bash(python3 .claude/hooks/validate.py *) Bash(gh run *) Bash(gh api *) Bash(gh secret list *) Bash(gh variable *) Bash(gh workflow run *) Bash(curl *) Bash(npx --yes wrangler@4 deploy --dry-run*)
---

Publish the mockup. Request: $ARGUMENTS

Names, identifiers and code comments are in English. Everything the user reads (your replies) is in Brazilian Portuguese (pt-BR).

Defaults, unless the request says otherwise: Worker name `<repository>-mockup`, deploy branch `develop`, mockup folder `docs/mockup`, GitHub variable `CLOUDFLARE_ACCOUNT_ID`, GitHub secret `CLOUDFLARE_API_TOKEN`.

## Hard rules (these came from real mistakes)

1. **Never handle the API token.** Do not put it in a GitHub secret, a command, a file or a reply, even if the user pastes it or asks. Tell the user to run `gh secret set CLOUDFLARE_API_TOKEN -R <owner>/<repo>` themselves (it prompts for the value, so it stays out of history). The account id is not a credential: set it with `gh variable set`.
2. **Never read `.env` values.** Check only that the file exists, its size and the variable names (`sed -E 's/=.*/=<hidden>/'`). An empty `.env` (0 bytes) means the user did not save it. Remind them the CI cannot read local files: only repository secrets and variables count.
3. **Never trust an empty listing as success.** `gh secret list` exits 0 even with no secrets. Confirm with `gh api repos/<owner>/<repo>/actions/secrets --jq '[.secrets[].name]'` and require the name to be in the list **before** any push that triggers the deploy.
4. **Ask before pushing.** A push to the deploy branch runs the deploy and makes things public. Push only after the secret is confirmed and the user agreed.
5. **Never publish anything outside the mockup folder.** No repo root, no `.claude`, no `node_modules`, no `.env`.
6. **Do not make the site public by accident.** Keep `workers_dev: false` until Cloudflare Access is on, unless the user explicitly says it may be public. When they do, say once that anyone with the URL can open it, then proceed.

## 1. Check the mockup is self-contained

- `python3 .claude/hooks/validate.py --all` must print `OK`.
- Search the mockup folder for paths that leave it (`../..`, absolute `/` paths, `http` URLs). Only relative paths inside the folder are allowed; everything must work when only that folder is served.
- Files that must not be published (`serve.py`, `.assetsignore`, `__pycache__`) go in `<mockup>/.assetsignore`.

## 2. Create the files (once)

`wrangler.jsonc` at the repository root (static assets only, so nothing else is uploaded):

```jsonc
{
  "$schema": "https://developers.cloudflare.com/workers/wrangler/config-schema.json",
  "name": "<worker-name>",
  "compatibility_date": "<today, YYYY-MM-DD>",
  "assets": {
    "directory": "./docs/mockup",
    "html_handling": "auto-trailing-slash",
    "not_found_handling": "none",
  },
  "workers_dev": false,
  "preview_urls": false,
}
```

`<mockup>/.assetsignore`:

```
.assetsignore
serve.py
__pycache__
```

`.github/workflows/deploy-mockup.yml`: triggers on push to the deploy branch with `paths` limited to the mockup folder, `wrangler.jsonc` and the workflow itself, plus `workflow_dispatch`; `permissions: contents: read`; a `concurrency` group; steps `actions/checkout@v4`, the validator, then `cloudflare/wrangler-action@v3` with `apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}`, `accountId: ${{ vars.CLOUDFLARE_ACCOUNT_ID }}`, `wranglerVersion: '4'`, `command: deploy`.

Prove the upload scope before pushing: `npx --yes wrangler@4 deploy --dry-run` with `WRANGLER_LOG=debug` lists the files read; only mockup files may appear and `serve.py` must show as ignored.

## 3. Credentials

1. Set the variable: `gh variable set CLOUDFLARE_ACCOUNT_ID --body <id> -R <owner>/<repo>` (the user gives the id; it is not secret).
2. Tell the user how to create the secret (rule 1) and the token permissions they need: Account > **Workers Scripts: Edit**, plus **Access: Apps and Policies: Edit** if Access will be used, with this account in "Account Resources".
3. Verify the secret with the API (rule 3). If it is missing, do not push or run the deploy. Ask the user to paste the output of `gh auth status` and of their `gh secret set` command (without the token); likely causes are another repository or account, a wrong name, or an environment/organization secret.

## 4. Deploy and read the result

- Trigger with the push, or `gh workflow run deploy-mockup.yml -R <owner>/<repo> --ref <branch>`.
- Wait with an until-loop on `gh run view <id> --json status`, never with chained `sleep` calls.
- On failure read `gh run view <id> --log-failed` (strip ANSI codes) and map the message:
  - `CLOUDFLARE_API_TOKEN environment variable` : the secret is missing or misspelled.
  - `No access to the specified resource` : the token lacks **Workers Scripts: Edit** or is limited to another account. The user must fix it in Cloudflare; do not retry blindly.
  - validation errors : fix the mockup at the source.
- The public URL is printed in the logs: `grep -oE 'https://[a-z0-9.-]+\.workers\.dev'`.

## 5. Protect it with Cloudflare Access (when requested)

The Worker must exist first, so deploy once with `workers_dev: false`. Then the user turns Access on in the Cloudflare dashboard: Workers & Pages > the Worker > Access > "Protect this Worker behind Access" > All traffic > policy allowing only their e-mail. Only after they confirm, set `workers_dev: true`, commit and push, then test that the page asks for sign-in.

## 6. Test the published site

- `curl -s -o /dev/null -w '%{http_code}'` on `/`, a data file and a stylesheet (expect 200), and on `serve.py`, `.assetsignore` and `../package.json` (expect 404).
- A 307 on `*.html` is normal (`auto-trailing-slash`); relative links keep working.
- In the browser: sign in, open the list and a detail page. Wait about two seconds before reading text, because data loads asynchronously (an empty table right after load is not a bug). Check the console for errors.

## Working habits

- Use absolute paths. A `cd` in the Bash tool persists between calls and silently changes the working directory.
- A `git push` in PowerShell may print a `NativeCommandError` for normal progress output; check the `old..new branch -> branch` line to know it worked.
- Commit on `develop` with a semantic message in English whose body lines are at most 100 characters.
- Remind the user, once, that a token pasted in chat should be rotated.

## Reply (short, in pt-BR)

What was published and where (URL), what was tested, what is public or protected, and what the user still has to do (secret, token permissions, Access).
