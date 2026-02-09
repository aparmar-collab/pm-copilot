# Jira GenAI – Project Status Summarizer

A small Streamlit app that:

- Fetches recent Jira issues for a project (via JQL)
- Normalizes the issue data into a compact JSON structure
- Builds a prompt for an LLM
- Generates a leadership-style project status summary using Groq

## Quick start

### 1) Create a virtual environment + install deps

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### 2) Configure environment variables

Create a `.env` file in the project root (or set these in your environment):

- `JIRA_BASE_URL` (example: `https://your-site.atlassian.net`)
- `JIRA_EMAIL` (your Atlassian account email)
- `JIRA_API_TOKEN` (Jira API token)
- `GROQ_API_KEY` (Groq API key)

You can copy `.env.example`.
If dotfiles are blocked in your environment, copy from `env.example` instead.

**Security note:** never commit `.env` (it contains secrets). This repo includes a `.gitignore` entry for `.env` to prevent accidental commits.

### 3) Run the app

```bash
venv\Scripts\streamlit run app.py
```

## Documentation

- `docs/PROJECT_FLOW.md`: detailed end-to-end flow and module responsibilities

## Repo structure (high level)

- `app.py`: Streamlit UI + orchestration
- `config/settings.py`: loads env vars via `python-dotenv`
- `services/jira_service.py`: Jira REST calls (search issues via JQL)
- `services/llm_service.py`: Groq chat completion call
- `utils/data_formatter.py`: transforms Jira issue payload → simplified JSON
- `utils/validators.py`: basic input validation
- `prompts/prompt.py`: prompt template builder

## Notes / troubleshooting

- Jira issue fetching uses **`/rest/api/3/search/jql`** (Jira Cloud removed `GET /rest/api/3/search` with 410 Gone).
- If the Jira call fails, the app displays a friendly error; the Jira service also includes a response-body preview in exceptions to help debugging.


