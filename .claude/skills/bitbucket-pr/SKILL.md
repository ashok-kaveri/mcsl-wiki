---
name: bitbucket-pr
description: Fetch Bitbucket PR details — status, files changed, diff, reviewers, and comments. Use when an agent or user needs to review a PR, check if it's open/merged, get the list of changed files, or fetch a diff.
argument-hint: <PR URL or "workspace/repo PR-number"> [files|diff|status|comments]
allowed-tools: Bash
disable-model-invocation: false
---

# Bitbucket PR Skill

Fetch Bitbucket pull request data using the REST API v2.0.

Credentials come from environment variables set in `~/.claude/settings.json`:
- `$BITBUCKET_USERNAME` — your Bitbucket account username
- `$BITBUCKET_TOKEN` — a Bitbucket App Password with `pullrequest` and `repository` read scopes
- `$BITBUCKET_WORKSPACE` — default workspace slug (optional; can be inferred from a URL)

## Setup (one-time)

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "BITBUCKET_USERNAME": "your-bitbucket-username",
    "BITBUCKET_TOKEN": "your-app-password",
    "BITBUCKET_WORKSPACE": "your-workspace-slug"
  }
}
```

Generate an App Password at: Bitbucket Settings > Personal settings > App passwords → grant **Repositories: Read** and **Pull requests: Read**.

---

## Parsing the arguments: `$ARGUMENTS`

`$ARGUMENTS` may be:
- A full URL: `https://bitbucket.org/myworkspace/myrepo/pull-requests/42`
- A short form: `myworkspace/myrepo 42` or `myrepo 42` (use `$BITBUCKET_WORKSPACE`)
- Optionally followed by a subcommand: `files`, `diff`, `status`, `comments`

Parse workspace, repo slug, and PR number from whichever format is given. If no subcommand is present, fetch **full PR details** (default).

Base URL for all calls: `https://api.bitbucket.org/2.0`
Auth for all calls: `-u "$BITBUCKET_USERNAME:$BITBUCKET_TOKEN"` (Basic Auth — App Passwords require this, not Bearer)

---

## Operations

### Default — full PR details

```bash
curl -s "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_number}" \
  -u "$BITBUCKET_USERNAME:$BITBUCKET_TOKEN"
```

Present as:

**PR #{number} — `<title>`**
- **State**: OPEN / MERGED / DECLINED / SUPERSEDED
- **Author**: display name
- **Source**: `source_branch` → `destination_branch`
- **Created**: date | **Updated**: date
- **Reviewers**: list (name — approved/unapproved)
- **Description**: (truncated to ~300 chars if long)
- **Links**: web URL

---

### `status` — just the PR state

Same endpoint as above, extract only: state, title, author, source→destination, created/updated. One-paragraph summary.

---

### `files` — list of changed files

```bash
curl -s "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_number}/diffstat" \
  -u "$BITBUCKET_USERNAME:$BITBUCKET_TOKEN"
```

Each item in `values[]` has `old.path` / `new.path` and `lines_added` / `lines_removed` / `status` (added, removed, modified, renamed).

Present as a table:

| Status | File | +Lines | -Lines |
|--------|------|--------|--------|
| modified | src/foo/bar.py | 12 | 4 |

If `next` is present in the response, paginate: append `?page=2` etc. until all files are fetched.

---

### `diff` — unified diff

```bash
curl -s "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_number}/diff" \
  -u "$BITBUCKET_USERNAME:$BITBUCKET_TOKEN"
```

Returns raw unified diff text. Present it in a fenced code block with `diff` syntax highlighting. If the diff is very large (>300 lines), summarize by file and offer to show individual file diffs on request.

---

### `comments` — PR comments and review threads

```bash
curl -s "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_number}/comments" \
  -u "$BITBUCKET_USERNAME:$BITBUCKET_TOKEN"
```

Each item in `values[]` has `author.display_name`, `content.raw`, `created_on`, and optionally `inline.path` + `inline.from`/`to` (for inline comments).

Present as:

**Comments on PR #{number}**

> **@author** — 2026-04-09
> File: `src/foo.py` line 42 *(inline)*
> Comment text here

Group inline comments by file, then general comments at the end.

---

## Error handling

- **401**: Token missing or invalid — show setup instructions above.
- **404**: PR or repo not found — confirm workspace/repo/PR number are correct.
- **Missing env vars**: If `$BITBUCKET_TOKEN` is unset, stop and show setup instructions.

---

## Usage examples

- `/bitbucket-pr https://bitbucket.org/acme/backend/pull-requests/99` → full PR details
- `/bitbucket-pr acme/backend 99 files` → changed files table
- `/bitbucket-pr acme/backend 99 diff` → unified diff
- `/bitbucket-pr acme/backend 99 status` → is it open?
- `/bitbucket-pr acme/backend 99 comments` → review comments
