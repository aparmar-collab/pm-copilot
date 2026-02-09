def compute_completion_stats(issues):
    total = len(issues or [])
    done_count = 0
    by_status = {}
    by_status_category = {}

    for issue in issues or []:
        fields = issue.get("fields", {})
        status = fields.get("status") or {}
        status_name = status.get("name") or "Unknown"
        by_status[status_name] = by_status.get(status_name, 0) + 1

        status_category_key = (status.get("statusCategory") or {}).get("key")
        status_category_key = status_category_key or "unknown"
        by_status_category[status_category_key] = by_status_category.get(status_category_key, 0) + 1
        is_done = (status_category_key == "done") or (str(status_name).strip().lower() == "done")
        if is_done:
            done_count += 1

    not_done_count = total - done_count
    done_percent = round((done_count / total) * 100, 1) if total else 0.0

    return {
        "total_issues_in_sample": total,
        "done_issues": done_count,
        "not_done_issues": not_done_count,
        "done_percent": done_percent,
        "count_by_status": dict(sorted(by_status.items(), key=lambda kv: (-kv[1], kv[0]))),
        "count_by_status_category": dict(sorted(by_status_category.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def compute_dashboard_stats(issues, top_n_assignees=10):
    by_assignee = {}
    by_priority = {}
    by_type = {}
    updated_by_day = {}

    for issue in issues or []:
        fields = issue.get("fields", {})

        assignee = fields.get("assignee")
        assignee_name = assignee.get("displayName") if isinstance(assignee, dict) else None
        assignee_name = assignee_name or "Unassigned"
        by_assignee[assignee_name] = by_assignee.get(assignee_name, 0) + 1

        priority = fields.get("priority")
        priority_name = priority.get("name") if isinstance(priority, dict) else None
        priority_name = priority_name or "None"
        by_priority[priority_name] = by_priority.get(priority_name, 0) + 1

        issuetype = fields.get("issuetype")
        type_name = issuetype.get("name") if isinstance(issuetype, dict) else None
        type_name = type_name or "Unknown"
        by_type[type_name] = by_type.get(type_name, 0) + 1

        updated = fields.get("updated")
        # Jira returns ISO timestamps like 2026-02-08T12:34:56.000+0000
        if isinstance(updated, str) and len(updated) >= 10:
            day = updated[:10]
            updated_by_day[day] = updated_by_day.get(day, 0) + 1

    def _sorted_counts(d):
        return dict(sorted(d.items(), key=lambda kv: (-kv[1], kv[0])))

    by_assignee_sorted = _sorted_counts(by_assignee)
    by_assignee_top = dict(list(by_assignee_sorted.items())[: max(0, int(top_n_assignees))])

    return {
        "count_by_assignee_top": by_assignee_top,
        "count_by_assignee_all": by_assignee_sorted,
        "count_by_priority": _sorted_counts(by_priority),
        "count_by_type": _sorted_counts(by_type),
        "updated_by_day": dict(sorted(updated_by_day.items())),  # chronological by YYYY-MM-DD
    }


def normalize_issues(issues):
    formatted = []

    for issue in issues:
        fields = issue["fields"]
        formatted.append({
            "key": issue["key"],
            "summary": fields["summary"],
            "status": fields["status"]["name"],
            "assignee": fields["assignee"]["displayName"] if fields["assignee"] else "Unassigned",
            "priority": fields["priority"]["name"] if fields["priority"] else "None",
            "type": fields["issuetype"]["name"],
            "last_updated": fields["updated"]
        })

    return formatted
