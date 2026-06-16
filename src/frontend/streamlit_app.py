import sys
from pathlib import Path

import streamlit as st
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.frontend.api_client import ApiClient
from src.frontend.auth_ui import (
    consume_oauth_tokens,
    initialize_session,
    load_current_user,
    render_sidebar_auth,
    require_login,
)
from src.frontend.dashboard_ui import render_admin_dashboard
from src.frontend.tasks_ui import STATUSES, load_worker_options, render_create_task, render_task_list

st.set_page_config(page_title="Task Management", layout="wide")

api_base = st.sidebar.text_input("API URL", "http://localhost:8000/api/v1")
initialize_session()
consume_oauth_tokens()

client = ApiClient(api_base, st.session_state.token)
load_current_user(client)
render_sidebar_auth(api_base)

st.title("Task Management")
require_login(api_base)

user = st.session_state.user
is_admin = user["role"] == "ADMIN"

st.success(f"Welcome, {user['name']} ({user['email']}) - {user['role']}")

if "dashboard_counts" not in st.session_state:
    st.session_state.dashboard_counts = {}
if "worker_options" not in st.session_state:
    st.session_state.worker_options = {}
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "force_data_refresh" not in st.session_state:
    st.session_state.force_data_refresh = True

status_filter = st.selectbox("Status filter", ["ALL", *STATUSES])
manual_refresh = st.button("Refresh data", use_container_width=True)

if manual_refresh or st.session_state.force_data_refresh:
    with st.spinner("Loading latest data..."):
        try:
            if is_admin:
                analytics_response = client.task_analytics()
                if analytics_response.ok:
                    st.session_state.dashboard_counts = analytics_response.json()
                st.session_state.worker_options = load_worker_options(client)

            task_response = client.list_tasks(status_filter)
            if task_response.ok:
                st.session_state.tasks = task_response.json()["items"]
            else:
                st.error(task_response.text)
            st.session_state.force_data_refresh = False
        except requests.RequestException as exc:
            st.error(f"Loading data failed: {exc}")

worker_options = st.session_state.worker_options if is_admin else {}

if is_admin:
    render_admin_dashboard(st.session_state.dashboard_counts)

left, right = st.columns([2, 1])
with left:
    render_task_list(client, st.session_state.tasks, is_admin, worker_options)
with right:
    if is_admin:
        render_create_task(client, worker_options)
    else:
        st.subheader("Task Status Flow")
        st.write("TODO -> IN_PROGRESS -> DONE")
        st.info("Workers can comment on assigned tasks and update only their task status.")
