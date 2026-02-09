# Project flow – Jira GenAI

This document describes the runtime flow, data transformations, and module responsibilities for the **Jira GenAI Project Status** app.

## What the app does (one sentence)

Given a Jira project key, it fetches recent issues, converts them to a compact JSON, asks an LLM to produce a structured leadership update, and renders that summary in Streamlit.

## End-to-end runtime flow

### 1) User interaction (UI)

- File: `app.py`
- UI element: a text input (`project_key`) and a button (**Generate Project Status**).

When the button is clicked:

- Inputs are validated:
  - `project_key` must be non-empty
  - Jira credentials must be present (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`)

### 2) Build JQL query

- File: `app.py`
- JQL used:
  - `project = {project_key} ORDER BY updated DESC`

This is intentionally simple: it fetches the most recently updated issues (including Done) so the app can estimate completion based on the fetched sample.

### 3) Fetch issues from Jira (REST API)

- File: `services/jira_service.py`
- Function: `fetch_jira_issues(base_url, email, token, jql, max_results=20)`

Steps:

- Sanitizes the Jira base URL (`rstrip("/")`) to prevent `//rest/...` URLs.
- Uses **Basic Auth** with email + API token.
- Calls the Jira Cloud API endpoint:
  - **`GET /rest/api/3/search/jql`**
- Passes these query params:
  - `jql`
  - `maxResults`
  - `fields`: `summary`, `status`, `assignee`, `priority`, `updated`, `issuetype`

On failures, it raises an HTTP error with a preview of Jira’s response body, which typically contains a useful message (e.g., permissions, invalid JQL).

### 4) Normalize Jira payload → compact JSON

- File: `utils/data_formatter.py`
- Function: `normalize_issues(issues)`

Input (from Jira): list of issues with large nested `fields` objects.

Output (used for prompting): a small array of objects like:

- `key`
- `summary`
- `status`
- `assignee` (display name or `"Unassigned"`)
- `priority` (name or `"None"`)
- `type`
- `last_updated`

### 5) Build the LLM prompt

- File: `prompts/prompt.py`
- Function: `build_project_status_prompt(project_name, issues_json)`

The prompt:

- Injects the project key
- Embeds the normalized issues JSON
- Requests a structured response:
  1. Overall health (Green/Yellow/Red)
  2. Highlights
  3. Risks & blockers
  4. Workload observations
  5. Next actions

### 6) Generate the summary via Groq

- File: `services/llm_service.py`
- Function: `generate_summary(prompt)`

Steps:

- Creates a Groq client using `GROQ_API_KEY`.
- Calls `client.chat.completions.create(...)` with:
  - model: `llama-3.3-70b-versatile`
  - temperature: `0.3`
  - a small system instruction and the user prompt

Returns:

- `response.choices[0].message.content`

### 7) Render results

- File: `app.py`

Streamlit renders:

- “Project Status Summary” as markdown
- An expander containing the normalized Jira issues JSON used as context

## Configuration / environment variables

- File: `config/settings.py` loads `.env` via `python-dotenv`.

Required:

- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `GROQ_API_KEY`

## Sequence diagram (conceptual)

```text
User
  |
  | enters project key + clicks button
  v
Streamlit (app.py)
  |
  | build JQL
  v
Jira Service (services/jira_service.py)
  |
  | GET {JIRA_BASE_URL}/rest/api/3/search/jql?jql=...&fields=...
  v
Jira Cloud REST API
  |
  | issues JSON
  v
Formatter (utils/data_formatter.py)
  |
  | normalized JSON
  v
Prompt builder (prompts/prompt.py)
  |
  | prompt string
  v
LLM Service (services/llm_service.py)
  |
  | Groq chat completion
  v
Groq API
  |
  | summary text
  v
Streamlit renders output (app.py)
```

## Common failure points

- **410 Gone from Jira search**: Jira Cloud removed `GET /rest/api/3/search`; use `/rest/api/3/search/jql` (already implemented).
- **401/403**: invalid API token or missing Jira permissions for the project.
- **JQL errors**: invalid project key or incorrect JQL syntax.
- **LLM errors**: missing/invalid `GROQ_API_KEY` or model/network issues.


