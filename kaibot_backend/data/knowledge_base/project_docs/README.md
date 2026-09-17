# Project help docs

This folder holds "how do I use this app" content for OTHER intern
projects that call Mit Chomkar's `/chat` API with a `project_id`. It's
isolated by design: a request that supplies `project_id=X` can only ever
retrieve docs where `product` equals `X`, never another project's docs.
A request with no `project_id` (the farming web UI, the Telegram bot)
never sees anything in this folder at all. See
`../../../docs/PROJECT_INTEGRATION.md` for the full integration guide.

## Adding your project's docs

1. Pick a short, unique slug for your project (e.g. `pos_system`,
   `harvest_tracker`) -- this is your `project_id`.
2. Create a folder here named after that slug:
   `project_docs/<your_project_id>/`.
3. Add one or more `.json` files in it, each shaped like:

```json
{
  "source": "Your project's README or docs page",
  "category": "project_help",
  "product": "<your_project_id>",
  "lifecycle_stage": "general",
  "province": "national",
  "topic": "short_topic_slug",
  "text": "The actual content, in whatever language your users ask in. One idea per file/chunk works best -- if you have a long doc, split it into several files by topic (login, main features, troubleshooting, etc.) rather than one giant file."
}
```

`category` and `product` are the two fields that matter for isolation --
`category` must be exactly `"project_help"`, and `product` must exactly
match the `project_id` you'll send in API requests. The other fields
follow the same schema as the farming knowledge base but aren't used for
project docs; keep them as shown above.

4. Ask whoever runs the Mit Chomkar server to run `python -m rag.ingest`
   to index your new docs (or do it yourself if you have server access).
5. Start passing `project_id: "<your_project_id>"` in your `/chat`
   requests.
