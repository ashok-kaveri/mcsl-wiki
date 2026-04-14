---
name: trello
description: Interact with Trello — get board lanes, cards in a lane, card details, or check cards for missing Bitbucket PRs. Use when the user mentions Trello, a trello.com URL, board/lane/card lookups, or asks about missing PRs on Trello cards.
argument-hint: <command> [board/lane/card URL or ID]
allowed-tools: WebFetch
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
