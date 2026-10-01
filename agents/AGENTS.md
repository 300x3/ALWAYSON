# Workspace Rules / AGENTS.md

## Perplexity: Read a Link You Paste

When the user gives you a **perplexity.ai search link** (URL matching `https://www.perplexity.ai/search/<hash>` or any path under `https://www.perplexity.ai/search/`):

### Do this:
- Treat it as a live web page to be read through the browser MCP tools, NOT as a file path and NOT as something to fetch with a raw HTTP tool.
- Use the configured browser MCP server (Playwright) to:
  1. `browser_navigate` to the URL.
  2. Wait briefly for the page to load.
  3. `browser_snapshot` to capture the full rendered content.
  4. Return the visible text content of the page (search query, all results, snippets, answers, and follow-ups) to the user so they can confirm you read it.
- If the user wants a summary or action based on the content, do that AFTER the full content is captured and shown.

### Do NOT do this:
- Do not treat the link as a local file path.
- Do not try to `cat`/read it with FileRead tools.
- Do not paste only a short excerpt unless the user explicitly asks for that — capture and show the whole page content first.
- Do not assume the page is static HTML; Perplexity pages are rendered client-side, so the snapshot is the authoritative read.

## Perplexity: Run a Search on My Behalf ("look it up on perplexity", "use perplexity", etc.)

When the user asks you to **"look it up on perplexity"**, **"use perplexity"**, **"search perplexity for X"**, **"ask perplexity"**, **"find on perplexity"**, or otherwise instructs you to run a search on their authenticated Perplexity account:

### Trigger phrases
- "look it up on perplexity"
- "use perplexity"
- "search perplexity for ..."
- "ask perplexity"
- "find on perplexity"
- "perplexity search"
- "search on perplexity"
- anything else that means "go use perplexity and bring back what it says"

### Do this:
1. If the Playwright MCP server is not already running, start it pointing at the authenticated Firefox profile:
   ```
   npx -y @playwright/mcp@latest --port=9877 --browser=firefox --user-data-dir=/tmp/pw-ff-profile
   ```
2. Connect to the Playwright MCP SSE endpoint at `http://localhost:9877/sse` and initialize the session.
3. Open the authenticated Perplexity session:
   - navigate to `https://www.perplexity.ai/` or `https://www.perplexity.ai/search` (whichever loads the search box most directly).
4. Wait for the page to render, then `browser_snapshot` to locate:
   - the search input field,
   - any session/sign-in state (confirm the user is signed in; if not signed in, stop and tell the user),
   - the search submit control.
5. Type or paste the user's exact query into the search field.
6. Submit the search:
   - press Enter in the search box, or click the submit/search button, whichever is visible.
7. Wait for the results/answer to render, then `browser_snapshot` to confirm the query ran.
   - If the user only wanted the shareable link, you can stop after the search is confirmed.
   - If the user also wanted the answer/snippet, capture the visible answer and key results from the snapshot.
8. Click the **Share** button (typically in the session actions / top-right area).
9. If a sharing option appears, click **"Anyone with the link can view"** to make the session publicly shareable.
   - If that option is already selected/enabled, skip it and go straight to Copy Link.
10. Click **Copy Link** to copy the shareable `perplexity.ai/search/...` URL to the clipboard.
11. Read back the copied link:
    - If the browser MCP exposes clipboard access, read the clipboard contents.
    - Otherwise, take a snapshot after the copy action and extract the URL from the page/clipboard UI.
12. Return to the user:
    - the shareable perplexity link,
    - a short note on what was searched,
    - and, if requested, the key findings/snippet from the results snapshot.

### Important rules for the search flow
- Always run searches under the user's authenticated Firefox profile at `/tmp/pw-ff-profile`. Do not open an incognito or unauthenticated session for a search the user asked you to run on their account.
- Do not fabricate or guess the shareable link. It must come from the actual browser session after the Share → Anyone with the link can view → Copy Link flow completes.
- If the share UI differs slightly from the description, adapt to the visible controls (snapshot first, then interact with the most relevant Share / Anyone with the link / Copy Link controls).
- If the share flow cannot be completed (e.g., UI blocked, auth expired, "Anyone with the link can view" not available), stop and tell the user exactly what happened rather than guessing.
- If the user's query is ambiguous, ask for the exact search string before running it, unless the intent is obvious from context.

### Scope and precedence
- This rule covers both:
  - reading a perplexity link the user pastes, and
  - initiating a perplexity search when the user tells you to "use perplexity" / "look it up" / etc.
- For both, prefer the browser MCP snapshot as the authoritative read for perplexity pages, because they are JS-rendered.
- This rule does not change how you handle non-perplexity websites.

### Verification
- After navigating and snapping, always confirm to the user that you read the whole page and surface the key content.
- After a search-and-share flow, always return the actual shareable link you copied from the browser, and confirm whether the user also wanted the results content.

