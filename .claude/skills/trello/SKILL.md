---
name: trello
description: Interact with Trello — get board lanes, cards in a lane, card details, create cards, update cards, or check cards for missing Bitbucket PRs. Use when the user mentions Trello, a trello.com URL, board/lane/card lookups, creating cards, or asks about missing PRs on Trello cards.
argument-hint: <command> [board/lane/card URL or ID]
allowed-tools: WebFetch, Bash
disable-model-invocation: false
---

# Trello Skill

Use the Trello REST API with credentials from environment variables:
- `$TRELLO_API_KEY`
- `$TRELLO_TOKEN`

Base URL: `https://api.trello.com/1`
Always append `?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN` (plus extra params) to every request.

---

## Resolving IDs

- **Board ID / short link**: from `trello.com/b/{shortLink}/board-name` — use the shortLink as the board ID.
- **Card short ID**: from `trello.com/c/{shortId}` — use shortId directly.
- **List ID**: fetch the board's lists first to resolve by name.

---

## Operations

### Get card details
`GET /cards/{cardId}?key=...&token=...&attachments=true&fields=name,desc,idList&list=true`

Returns card name, description, lane (list) name, and attachments.

### Get lanes (lists) on a board
`GET /boards/{boardId}/lists?key=...&token=...&fields=name,id`

### Get cards in a lane
`GET /lists/{listId}/cards?key=...&token=...&attachments=true&fields=name,desc,idList`

### Get all cards on a board
Fetch cards: `GET /boards/{boardId}/cards?key=...&token=...&attachments=true&fields=name,desc,idList`
Fetch lists: `GET /boards/{boardId}/lists?key=...&token=...&fields=name,id`
Join cards to their list names for display.

### Create a card
Use `curl` via Bash (WebFetch is GET-only):

```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "idList": "<listId>",
    "name": "<card title>",
    "desc": "<card description in markdown>",
    "pos": "top"
  }'
```

**Workflow for creating a card:**
1. If user provides a board URL/ID but no lane, first fetch lanes: `GET /boards/{boardId}/lists`
2. Ask the user which lane to create the card in (or use the lane they specified)
3. Resolve the lane name to a list ID
4. POST the card with `idList`, `name`, `desc`
5. Report back the created card URL from the response (`shortUrl` field)

**Optional fields** (add to the JSON body as needed):
- `idLabels`: comma-separated label IDs (fetch available labels: `GET /boards/{boardId}/labels`)
- `idMembers`: comma-separated member IDs (fetch members: `GET /boards/{boardId}/members`)
- `due`: due date in ISO 8601 format (e.g., `"2026-04-20T17:00:00.000Z"`)
- `pos`: position — `"top"`, `"bottom"`, or a positive number

### Update a card
```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<new title>",
    "desc": "<new description>"
  }'
```

Only include fields that need updating. Supports same fields as create.

### Move a card to a different lane
```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"idList": "<targetListId>"}'
```

### Add a comment to a card
```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "<comment text>"}'
```

### Add an attachment to a card

**Upload a file:**
```bash
curl -s -X POST \
  "https://api.trello.com/1/cards/{cardId}/attachments?key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}" \
  -F "file=@/path/to/file.md"
```

**Attach from URL:**
```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/attachments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "<attachment URL>", "name": "<display name>"}'
```

### Get board labels
`GET /boards/{boardId}/labels?key=...&token=...&fields=name,color,id`

### Get board members
`GET /boards/{boardId}/members?key=...&token=...&fields=fullName,username,id`

---

## Bitbucket PR check

Whenever cards are fetched, automatically check each card's **description** for Bitbucket PR links matching `bitbucket.org/.*/pull-requests/`.

Report two groups:
- **Missing PR** — card name, lane name, Trello URL
- **Has PR** — card name, PR link(s) found

Fetch all cards in parallel for speed.

---

## Usage examples

- "get card https://trello.com/c/aKsZL2jZ" → card details + PR check
- "list lanes on board https://trello.com/b/abc123/board-name" → board lists
- "show cards in lane {name or ID}" → cards in lane + PR check
- "check all cards on board https://trello.com/b/abc123/board-name" → all cards + PR check
- "which cards are missing PRs?" (with a list of URLs) → PR check, report missing ones
- "create a card on board https://trello.com/b/abc123" → fetch lanes, ask which lane, create card
- "add a card 'Fix bug' to the In Progress lane on board abc123" → resolve lane, create card
- "move card https://trello.com/c/xyz to Done" → resolve lane ID, update card
- "add a comment to card xyz: 'Deployed to staging'" → post comment
- "upload file /tmp/analysis.md to card xyz" → file upload attachment
