# Integrating with Mit Chomkar AI

Mit Chomkar is a real AI backend — it answers genuine agriculture
questions (crops, livestock, selling produce) grounded in ~2,160 sourced
Cambodian agricultural documents, not a canned FAQ bot. Any project can
call its API directly and get real answers, in Khmer or English, with
sources cited.

On top of that, your project can *also* get "how do I use this app"
answers about itself specifically, isolated from every other project
that does the same thing. This doc covers both.

Live API base URL: `https://mitchomkar.soksim-pos.me`

## Calling it for farming questions

```bash
curl -X POST https://mitchomkar.soksim-pos.me/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I control pests on tomatoes?", "language": "en"}'
```

Response:
```json
{
  "answer": "...",
  "low_confidence": false,
  "sources": ["..."],
  "transcript": null
}
```

- `language`: `"km"` (default) or `"en"`.
- `low_confidence: true` means it's giving you the honest "I don't have
  reliable information on this" message rather than guessing — treat
  this as a real signal, not noise, and show it to the user as-is.
- `sources`: which underlying documents the answer is grounded in.

There's also `POST /chat/voice` (multipart form: `audio` file + the same
fields as form fields instead of JSON) if you want voice input, and
`POST /tts` (`{"text": "...", "language": "km"}`, returns raw MP3 bytes)
for voice output.

## Getting your own "how to use this app" answers too

Pass a `project_id` and it will *also* draw on your project's own docs,
in addition to farming knowledge — while staying completely blind to
every other project's docs, and every other project stays blind to
yours.

```bash
curl -X POST https://mitchomkar.soksim-pos.me/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I log in?", "project_id": "pos_system", "language": "en"}'
```

Without `project_id`, none of this content exists as far as the API is
concerned — that's what makes multiple intern projects safe to share one
backend without leaking each other's internal docs.

### Adding your project's docs

See `kaibot_backend/data/knowledge_base/project_docs/README.md` for the
exact file format. Short version: pick a unique `project_id` slug, add
JSON files under `data/knowledge_base/project_docs/<your_project_id>/`
with `"category": "project_help"` and `"product": "<your_project_id>"`,
and ask whoever runs the server to re-run `python -m rag.ingest` (or do
it yourself if you have access).

### What this doesn't do

- It won't know about your project's *live data* (a specific user's
  order, a database record) — only whatever static usage docs you feed
  it. It's a docs/FAQ assistant for your app, not a live integration
  into your app's backend.
- If your question doesn't match anything in the farming knowledge base
  or your project's docs, you get the honest low-confidence message —
  by design, it never invents an answer.
