def build_project_status_prompt(project_name, issues_json, completion_stats_json=None):
    return f"""
You are a senior project manager preparing a leadership update.

Rules:
- Use only provided data
- Do not assume timelines
- Be concise and structured
- Call out risks and blockers clearly

Project: {project_name}

Completion snapshot (based only on the provided Jira issues sample):
{completion_stats_json or "Not provided"}

Jira Issues:
{issues_json}

Provide:
1. Overall project health (Green / Yellow / Red)
2. Key progress highlights
3. Risks & blockers
4. Team workload observations
5. Completion status (what’s done vs remaining, based on the provided data)
6. Recommended next actions
"""
