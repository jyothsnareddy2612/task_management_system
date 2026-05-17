import sys
from pathlib import Path

import streamlit as st

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
from src.frontend.tasks_ui import load_worker_options, render_create_task, render_task_list

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

if is_admin:
    render_admin_dashboard(client)
    worker_options = load_worker_options(client)
else:
    worker_options = {}

left, right = st.columns([2, 1])
with left:
    render_task_list(client, is_admin, worker_options)
with right:
    if is_admin:
        render_create_task(client, worker_options)
    else:
        st.subheader("Task Status Flow")
        st.write("TODO -> IN_PROGRESS -> DONE")
        st.info("Workers can comment on assigned tasks and update only their task status.")
