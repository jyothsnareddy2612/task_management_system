import requests
import streamlit as st

from src.frontend.api_client import ApiClient


def initialize_session() -> None:
    if "token" not in st.session_state:
        st.session_state.token = ""
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = ""
    if "user" not in st.session_state:
        st.session_state.user = None


def consume_oauth_tokens() -> None:
    if "access_token" in st.query_params:
        st.session_state.token = st.query_params["access_token"]
        st.session_state.refresh_token = st.query_params.get("refresh_token", "")
        st.query_params.clear()


def load_current_user(client: ApiClient) -> None:
    if not st.session_state.token or st.session_state.user is not None:
        return
    try:
        response = client.me()
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return
    if response.ok:
        st.session_state.user = response.json()
    else:
        st.session_state.token = ""
        st.session_state.refresh_token = ""
        st.session_state.user = None


def render_sidebar_auth(api_base: str) -> None:
    st.sidebar.subheader("Session")
    if st.session_state.user:
        st.sidebar.success(f"Signed in as {st.session_state.user['name']}")
        st.sidebar.caption(st.session_state.user["email"])
        st.sidebar.caption(f"Role: {st.session_state.user['role']}")
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.token = ""
            st.session_state.refresh_token = ""
            st.session_state.user = None
            st.rerun()
        return
    st.sidebar.link_button("Login with Google", f"{api_base}/auth/google/login", use_container_width=True)


def require_login(api_base: str) -> None:
    if st.session_state.user:
        return
    st.info("Workers and admins sign in using Google.")
    st.link_button("Sign in with Google", f"{api_base}/auth/google/login")
    st.stop()

