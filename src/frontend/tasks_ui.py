from datetime import date, datetime, time, timezone
from typing import Any

import requests
import streamlit as st

from src.frontend.api_client import ApiClient

STATUSES = ["TODO", "IN_PROGRESS", "DONE"]
PRIORITIES = ["LOW", "MEDIUM", "HIGH", "URGENT"]


def safe_request(label: str, fn: Any) -> requests.Response | None:
    try:
        return fn()
    except requests.RequestException as exc:
        st.error(f"{label} failed: {exc}")
        return None


def load_worker_options(client: ApiClient) -> dict[str, str]:
    response = safe_request("Loading users", client.list_users)
    if not response or not response.ok:
        return {}
    return {
        f"{user['name']} ({user['email']})": str(user["id"])
        for user in response.json()
        if user["role"] == "WORKER"
    }


def iso_due_date(selected_date: date | None) -> str | None:
    if selected_date is None:
        return None
    return datetime.combine(selected_date, time(hour=18), tzinfo=timezone.utc).isoformat()


def render_comments(client: ApiClient, task_id: str) -> None:
    response = safe_request("Loading comments", lambda: client.list_comments(task_id))
    if response and response.ok:
        comments = response.json()
        if comments:
            for comment in comments:
                st.write(comment["content"])
                st.caption(f"By {comment['user_id']} at {comment['created_at']}")
        else:
            st.caption("No comments yet.")
    comment = st.text_area("Add comment", key=f"comment-{task_id}", height=80)
    if st.button("Post comment", key=f"post-comment-{task_id}"):
        created = safe_request("Adding comment", lambda: client.add_comment(task_id, comment))
        if created and created.ok:
            st.success("Comment added")
            st.rerun()
        elif created:
            st.error(created.text)


def render_history(client: ApiClient, task_id: str) -> None:
    response = safe_request("Loading history", lambda: client.task_history(task_id))
    if not response:
        return
    if not response.ok:
        st.error(response.text)
        return
    history = response.json()
    if not history:
        st.caption("No status changes yet.")
        return
    for item in history:
        old_status = item["old_status"] or "CREATED"
        st.caption(f"{old_status} -> {item['new_status']} at {item['changed_at']}")


def render_task_details(
    client: ApiClient,
    task: dict[str, Any],
    is_admin: bool,
    worker_options: dict[str, str],
) -> None:
    task_id = str(task["id"])
    if is_admin:
        title = st.text_input("Title", value=str(task["title"]), key=f"title-{task_id}")
        description = st.text_area(
            "Description",
            value=str(task.get("description") or ""),
            key=f"description-{task_id}",
        )
        priority = st.selectbox(
            "Priority",
            PRIORITIES,
            index=PRIORITIES.index(str(task["priority"])),
            key=f"priority-{task_id}",
        )
        status = st.selectbox(
            "Status",
            STATUSES,
            index=STATUSES.index(str(task["status"])),
            key=f"status-admin-{task_id}",
        )
        reverse_options = {value: label for label, value in worker_options.items()}
        current_assignee = task.get("assigned_to")
        current_label = reverse_options.get(str(current_assignee), "Unassigned")
        assignee_options = ["Unassigned", *worker_options.keys()]
        assignee = st.selectbox(
            "Assign to",
            assignee_options,
            index=assignee_options.index(current_label),
            key=f"assignee-{task_id}",
        )
        due_date_value = None
        if task.get("due_date"):
            due_date_value = datetime.fromisoformat(str(task["due_date"]).replace("Z", "+00:00")).date()
        due_date = st.date_input("Due date", value=due_date_value, key=f"due-{task_id}")
        save, delete = st.columns(2)
        with save:
            if st.button("Save changes", key=f"save-{task_id}", use_container_width=True):
                response = safe_request(
                    "Updating task",
                    lambda: client.update_task(
                        task_id,
                        {
                            "title": title,
                            "description": description,
                            "priority": priority,
                            "status": status,
                            "assigned_to": None if assignee == "Unassigned" else worker_options[assignee],
                            "due_date": iso_due_date(due_date),
                        },
                    ),
                )
                if response and response.ok:
                    st.success("Task updated")
                    st.rerun()
                elif response:
                    st.error(response.text)
        with delete:
            if st.button("Remove task", key=f"delete-{task_id}", use_container_width=True):
                response = safe_request("Deleting task", lambda: client.delete_task(task_id))
                if response and response.status_code == 204:
                    st.success("Task removed")
                    st.rerun()
                elif response:
                    st.error(response.text)
        return

    status = st.selectbox(
        "Change status",
        STATUSES,
        index=STATUSES.index(str(task["status"])),
        key=f"status-worker-{task_id}",
    )
    if st.button("Update status", key=f"worker-status-{task_id}"):
        response = safe_request("Updating status", lambda: client.update_task(task_id, {"status": status}))
        if response and response.ok:
            st.success("Status updated")
            st.rerun()
        elif response:
            st.error(response.text)


def render_task(
    client: ApiClient,
    task: dict[str, Any],
    is_admin: bool,
    worker_options: dict[str, str],
) -> None:
    task_id = str(task["id"])
    with st.expander(f"{task['title']} - {task['status']}"):
        st.write(task.get("description") or "")
        st.caption(
            f"Priority: {task['priority']} | Due: {task.get('due_date') or 'No due date'} | "
            f"Assigned to: {task.get('assigned_to') or 'Unassigned'}"
        )
        details, comments, history = st.tabs(["Details", "Comments", "History"])
        with details:
            render_task_details(client, task, is_admin, worker_options)
        with comments:
            render_comments(client, task_id)
        with history:
            render_history(client, task_id)


def render_task_list(client: ApiClient, is_admin: bool, worker_options: dict[str, str]) -> None:
    st.subheader("Tasks")
    status_filter = st.selectbox("Status filter", ["ALL", *STATUSES])
    if st.button("Refresh tasks", use_container_width=True):
        st.rerun()
    response = safe_request("Loading tasks", lambda: client.list_tasks(status_filter))
    if response and response.ok:
        for task in response.json()["items"]:
            render_task(client, task, is_admin, worker_options)
    elif response:
        st.error(response.text)


def render_create_task(client: ApiClient, worker_options: dict[str, str]) -> None:
    st.subheader("Create Task")
    title = st.text_input("Title")
    description = st.text_area("Description")
    priority = st.selectbox("Priority", PRIORITIES, index=1)
    selected_user = st.selectbox("Assign to", ["Unassigned", *worker_options.keys()])
    due_date = st.date_input("Due date", value=None)
    if st.button("Create", use_container_width=True):
        response = safe_request(
            "Creating task",
            lambda: client.create_task(
                {
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "assigned_to": None if selected_user == "Unassigned" else worker_options[selected_user],
                    "due_date": iso_due_date(due_date),
                }
            ),
        )
        if response and response.ok:
            st.success("Created")
            st.rerun()
        elif response:
            st.error(response.text)

