import streamlit as st


def render_admin_dashboard(counts: dict[str, int]) -> None:
    todo, progress, done = st.columns(3)
    todo.metric("Todo", counts.get("TODO", 0))
    progress.metric("In Progress", counts.get("IN_PROGRESS", 0))
    done.metric("Done", counts.get("DONE", 0))
