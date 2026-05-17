import requests
import streamlit as st

from src.frontend.api_client import ApiClient


def render_admin_dashboard(client: ApiClient) -> None:
    try:
        response = client.task_analytics()
    except requests.RequestException as exc:
        st.warning(f"Could not load analytics: {exc}")
        return
    if not response.ok:
        st.warning("Could not load analytics.")
        return
    counts = response.json()
    todo, progress, done = st.columns(3)
    todo.metric("Todo", counts.get("TODO", 0))
    progress.metric("In Progress", counts.get("IN_PROGRESS", 0))
    done.metric("Done", counts.get("DONE", 0))

