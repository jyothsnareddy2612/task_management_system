import requests
import streamlit as st

st.set_page_config(page_title="Task Management", layout="wide")

API_BASE = st.sidebar.text_input("API URL", "http://localhost:8000/api/v1")
STATUSES = ["TODO", "IN_PROGRESS", "DONE"]
PRIORITIES = ["LOW", "MEDIUM", "HIGH", "URGENT"]


def show_api_error(error: requests.RequestException) -> None:
    st.error(f"API request failed: {error}")


def api_request(method: str, path: str, **kwargs: object) -> requests.Response | None:
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    request_headers = kwargs.pop("headers", {})
    if isinstance(request_headers, dict):
        headers.update(request_headers)
    try:
        return requests.request(
            method,
            f"{API_BASE}{path}",
            headers=headers,
            timeout=10,
            **kwargs,
        )
    except requests.RequestException as exc:
        show_api_error(exc)
        return None


def load_me() -> None:
    response = api_request("GET", "/auth/me")
    if response and response.ok:
        st.session_state.user = response.json()
    else:
        st.session_state.token = ""
        st.session_state.refresh_token = ""
        st.session_state.user = None


def load_users() -> list[dict[str, object]]:
    response = api_request("GET", "/admin/users")
    if response and response.ok:
        return list(response.json())
    return []


def render_history(task_id: str) -> None:
    response = api_request("GET", f"/tasks/{task_id}/history")
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


def render_comments(task_id: str) -> None:
    response = api_request("GET", f"/tasks/{task_id}/comments")
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
        created = api_request("POST", f"/tasks/{task_id}/comments", json={"content": comment})
        if created and created.ok:
            st.success("Comment added")
            st.rerun()
        elif created:
            st.error(created.text)


def render_task(task: dict[str, object], is_admin: bool, user_options: dict[str, str]) -> None:
    task_id = str(task["id"])
    with st.expander(f"{task['title']} - {task['status']}"):
        st.write(task.get("description") or "")
        st.caption(f"Priority: {task['priority']} | Assigned to: {task.get('assigned_to') or 'Unassigned'}")

        tab_details, tab_comments, tab_history = st.tabs(["Details", "Comments", "History"])

        with tab_details:
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
                current_assignee = task.get("assigned_to")
                reverse_options = {value: label for label, value in user_options.items()}
                current_label = reverse_options.get(str(current_assignee), "Unassigned")
                assignee = st.selectbox(
                    "Assign to",
                    ["Unassigned", *user_options.keys()],
                    index=["Unassigned", *user_options.keys()].index(current_label),
                    key=f"assignee-{task_id}",
                )
                status = st.selectbox(
                    "Status",
                    STATUSES,
                    index=STATUSES.index(str(task["status"])),
                    key=f"status-admin-{task_id}",
                )
                col_save, col_delete = st.columns(2)
                with col_save:
                    if st.button("Save changes", key=f"save-{task_id}", use_container_width=True):
                        response = api_request(
                            "PATCH",
                            f"/tasks/{task_id}",
                            json={
                                "title": title,
                                "description": description,
                                "priority": priority,
                                "status": status,
                                "assigned_to": None if assignee == "Unassigned" else user_options[assignee],
                            },
                        )
                        if response and response.ok:
                            st.success("Task updated")
                            st.rerun()
                        elif response:
                            st.error(response.text)
                with col_delete:
                    if st.button("Remove task", key=f"delete-{task_id}", use_container_width=True):
                        response = api_request("DELETE", f"/tasks/{task_id}")
                        if response and response.status_code == 204:
                            st.success("Task removed")
                            st.rerun()
                        elif response:
                            st.error(response.text)
            else:
                status = st.selectbox(
                    "Change status",
                    STATUSES,
                    index=STATUSES.index(str(task["status"])),
                    key=f"status-worker-{task_id}",
                )
                if st.button("Update status", key=f"worker-status-{task_id}"):
                    response = api_request("PATCH", f"/tasks/{task_id}", json={"status": status})
                    if response and response.ok:
                        st.success("Status updated")
                        st.rerun()
                    elif response:
                        st.error(response.text)

        with tab_comments:
            render_comments(task_id)

        with tab_history:
            render_history(task_id)


st.title("Task Management")

if "token" not in st.session_state:
    st.session_state.token = ""
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = ""
if "user" not in st.session_state:
    st.session_state.user = None

if "access_token" in st.query_params:
    st.session_state.token = st.query_params["access_token"]
    st.session_state.refresh_token = st.query_params.get("refresh_token", "")
    st.query_params.clear()

if st.session_state.token and st.session_state.user is None:
    load_me()

with st.sidebar:
    st.subheader("Session")
    if st.session_state.user:
        st.success(f"Signed in as {st.session_state.user['name']}")
        st.caption(st.session_state.user["email"])
        st.caption(f"Role: {st.session_state.user['role']}")
        if st.button("Logout", use_container_width=True):
            st.session_state.token = ""
            st.session_state.refresh_token = ""
            st.session_state.user = None
            st.rerun()
    else:
        st.link_button("Login with Google", f"{API_BASE}/auth/google/login", use_container_width=True)

if st.session_state.user:
    st.success(
        f"Welcome, {st.session_state.user['name']} "
        f"({st.session_state.user['email']}) - {st.session_state.user['role']}"
    )
else:
    st.info("Workers and admins sign in using Google.")
    st.link_button("Sign in with Google", f"{API_BASE}/auth/google/login")
    st.stop()

is_admin = st.session_state.user["role"] == "ADMIN"
users = load_users() if is_admin else []
worker_options = {
    f"{user['name']} ({user['email']})": str(user["id"])
    for user in users
    if user["role"] == "WORKER"
}

left, right = st.columns([2, 1])

with left:
    st.subheader("Tasks")
    status_filter = st.selectbox("Status filter", ["ALL", *STATUSES])
    params = {} if status_filter == "ALL" else {"status": status_filter}
    if st.button("Refresh tasks", use_container_width=True):
        st.rerun()
    response = api_request("GET", "/tasks", params=params)
    if response and response.ok:
        for task_item in response.json()["items"]:
            render_task(task_item, is_admin, worker_options)
    elif response:
        st.error(response.text)

with right:
    if is_admin:
        st.subheader("Create Task")
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", PRIORITIES, index=1)
        selected_user = st.selectbox("Assign to", ["Unassigned", *worker_options.keys()])
        if st.button("Create", use_container_width=True):
            assigned_to = None if selected_user == "Unassigned" else worker_options[selected_user]
            response = api_request(
                "POST",
                "/tasks",
                json={
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "assigned_to": assigned_to,
                },
            )
            if response and response.ok:
                st.success("Created")
                st.rerun()
            elif response:
                st.error(response.text)
    else:
        st.subheader("Task Status Flow")
        st.write("TODO -> IN_PROGRESS -> DONE")
        st.info("Workers can comment on assigned tasks and update only their task status.")
