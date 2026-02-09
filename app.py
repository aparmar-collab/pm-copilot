import streamlit as st
import json

from config.settings import (
    JIRA_BASE_URL,
    JIRA_EMAIL,
    JIRA_API_TOKEN
)
from services.jira_service import fetch_jira_issues
from services.llm_service import generate_summary
from utils.data_formatter import normalize_issues, compute_completion_stats, compute_dashboard_stats
from utils.validators import validate_inputs
from prompts.prompt import build_project_status_prompt

st.set_page_config("Jira GenAI Project Status", layout="wide")
st.title("📊 Jira Project Status – GenAI")

project_key = st.text_input("Jira Project Key (e.g. ABC)")


if st.button("Generate Project Status"):
    if not validate_inputs(project_key):
        st.error("Project key is required")
    elif not validate_inputs(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN):
        st.error("Missing Jira configuration. Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN in your environment/.env.")
    else:
        with st.spinner("Fetching Jira data..."):
            # Include Done issues too so we can estimate completion from the fetched sample.
            jql = f"project = {project_key} ORDER BY updated DESC"
            try:
                issues = fetch_jira_issues(
                    JIRA_BASE_URL,
                    JIRA_EMAIL,
                    JIRA_API_TOKEN,
                    jql,
                    max_results=100
                )
            except Exception as e:
                st.error(f"Failed to fetch Jira issues: {e}")
                st.stop()

        completion_stats = compute_completion_stats(issues)
        dashboard_stats = compute_dashboard_stats(issues)
        formatted = normalize_issues(issues)
        prompt = build_project_status_prompt(
            project_key,
            json.dumps(formatted, indent=2),
            json.dumps(completion_stats, indent=2)
        )

        tab_dashboard, tab_summary = st.tabs(["📊 Dashboard", "✅ Project Summary"])

        with tab_dashboard:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total issues (sample)", completion_stats["total_issues_in_sample"])
            c2.metric("Done", completion_stats["done_issues"])
            c3.metric("Remaining", completion_stats["not_done_issues"])
            c4.metric("Done %", f"{completion_stats['done_percent']}%")
            st.progress(min(max(completion_stats["done_percent"] / 100.0, 0.0), 1.0))

            col_left, col_right = st.columns(2)

            # Status distribution
            status_values = [{"status": k, "count": v} for k, v in completion_stats["count_by_status"].items()]
            col_left.vega_lite_chart(
                {
                    "data": {"values": status_values},
                    "mark": {"type": "bar"},
                    "encoding": {
                        "x": {"field": "count", "type": "quantitative", "title": "Issues"},
                        "y": {"field": "status", "type": "nominal", "sort": "-x", "title": "Status"},
                        "tooltip": [{"field": "status"}, {"field": "count"}],
                        "color": {"field": "status", "type": "nominal", "legend": None},
                    },
                    "title": "Issues by status",
                },
                use_container_width=True,
            )

            # Done vs not-done (based on statusCategory)
            category_map = {
                "new": "Block / To Do",
                "indeterminate": "In Progress (indeterminate)",
                "done": "Done",
                "unknown": "Unknown",
            }
            cat_counts = completion_stats.get("count_by_status_category", {}) or {}
            cat_values = [{"category": category_map.get(k, k), "count": v} for k, v in cat_counts.items()]
            col_right.vega_lite_chart(
                {
                    "data": {"values": cat_values},
                    "mark": {"type": "arc", "innerRadius": 50},
                    "encoding": {
                        "theta": {"field": "count", "type": "quantitative"},
                        "color": {"field": "category", "type": "nominal"},
                        "tooltip": [{"field": "category"}, {"field": "count"}],
                    },
                    "title": "Progress by status category",
                },
                use_container_width=True,
            )

            col_a, col_b = st.columns(2)

            # Workload by assignee (top N)
            assignee_values = [{"assignee": k, "count": v} for k, v in dashboard_stats["count_by_assignee_top"].items()]
            col_a.vega_lite_chart(
                {
                    "data": {"values": assignee_values},
                    "mark": {"type": "bar"},
                    "encoding": {
                        "x": {"field": "count", "type": "quantitative", "title": "Issues"},
                        "y": {"field": "assignee", "type": "nominal", "sort": "-x", "title": "Assignee"},
                        "tooltip": [{"field": "assignee"}, {"field": "count"}],
                    },
                    "title": "Workload by assignee (top 10)",
                },
                use_container_width=True,
            )

            # Activity by day (based on 'updated' timestamp)
            day_values = [{"day": k, "count": v} for k, v in dashboard_stats["updated_by_day"].items()]
            col_b.vega_lite_chart(
                {
                    "data": {"values": day_values},
                    "mark": {"type": "line", "point": True},
                    "encoding": {
                        "x": {"field": "day", "type": "temporal", "title": "Day"},
                        "y": {"field": "count", "type": "quantitative", "title": "Issues updated"},
                        "tooltip": [{"field": "day"}, {"field": "count"}],
                    },
                    "title": "Issue update activity (sample)",
                },
                use_container_width=True,
            )

            with st.expander("📌 Completion details (sample)"):
                st.write(completion_stats)

        with tab_summary:
            with st.spinner("Generating AI summary..."):
                summary = generate_summary(prompt)

            st.subheader("✅ Project Status Summary")
            st.markdown(summary)

            with st.expander("📄 Jira Issues Used"):
                st.json(formatted)
