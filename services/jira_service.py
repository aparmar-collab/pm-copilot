import requests
from requests.auth import HTTPBasicAuth

def fetch_jira_issues(base_url, email, token, jql, max_results=20):
    if not base_url or not str(base_url).strip():
        raise ValueError("JIRA_BASE_URL is missing")
    if not email or not str(email).strip():
        raise ValueError("JIRA_EMAIL is missing")
    if not token or not str(token).strip():
        raise ValueError("JIRA_API_TOKEN is missing")

    # Avoid accidental double-slashes like https://site.atlassian.net//rest/api/3/search
    base_url = str(base_url).strip().rstrip("/")

    # Jira Cloud removed GET /rest/api/3/search (410 Gone). Use the replacement endpoint.
    url = f"{base_url}/rest/api/3/search/jql"

    auth = HTTPBasicAuth(email, token)
    headers = {"Accept": "application/json"}

    params = {
        "jql": jql,
        "maxResults": max_results,
        "fields": [
            "summary",
            "status",
            "assignee",
            "priority",
            "updated",
            "issuetype"
        ]
    }

    response = requests.get(
        url,
        headers=headers,
        auth=auth,
        params=params,
        timeout=(10, 30),
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        # Include response body (usually has a helpful Jira error message) without leaking secrets.
        body = (response.text or "").strip()
        body_preview = body[:1000] + ("..." if len(body) > 1000 else "")
        raise requests.HTTPError(
            f"{e} | Response body: {body_preview}",
            response=response,
        ) from None

    return response.json()["issues"]
