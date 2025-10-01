import json
from typing import Any, Dict, Optional, List, Mapping, cast

import streamlit as st
import requests


# # ---------- App Configuration ----------
st.set_page_config(page_title="Booklynn Frontend", page_icon="📚", layout="wide")


# ---------- Helpers ----------
def get_base_url() -> str:
    base_url: str = st.session_state.get("base_url") or "http://localhost:8000/v2"
    return base_url.rstrip("/")


def get_auth_headers(token: Optional[str]) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_request(
    method: str,
    path: str,
    token: Optional[str] = None,
    json_body: Optional[Dict[str, Any]] = None,
) -> requests.Response:
    url = f"{get_base_url()}{path}"
    headers = {"Content-Type": "application/json", **get_auth_headers(token)}
    try:
        resp = requests.request(method=method.upper(), url=url, headers=headers, json=json_body, timeout=15)
        return resp
    except requests.RequestException as exc:
        st.error(f"Request error: {exc}")
        raise


def get_query_params() -> Dict[str, List[str]]:
    # Streamlit newer API
    qp: Dict[str, List[str]] = {}
    try:
        # type: ignore[attr-defined]
        raw_qp = cast(Mapping[str, str] | Mapping[str, List[str]], st.query_params)  # available in recent Streamlit
        # Ensure list values
        qp = {k: (v if isinstance(v, list) else [v]) for k, v in raw_qp.items()}
        if qp:
            return qp
    except Exception:
        pass
    # Fallback to experimental API
    try:
        qp = st.experimental_get_query_params()  # type: ignore[attr-defined]
    except Exception:
        qp = {}
    return qp


def show_response(resp: requests.Response) -> None:
    st.write(f"Status: {resp.status_code}")
    try:
        st.json(resp.json())
    except Exception:
        st.code(resp.text)


# ---------- Session State ----------
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "refresh_token" not in st.session_state:
    st.session_state["refresh_token"] = None
if "base_url" not in st.session_state:
    st.session_state["base_url"] = "http://localhost:8000/v2"
if "login_prompt" not in st.session_state:
    st.session_state["login_prompt"] = False

# Handle any pending clear flags BEFORE widgets render
if st.session_state.get("pending_clear_access"):
    st.session_state.pop("access_token", None)
    st.session_state.pop("access_token_input", None)
    st.session_state["login_prompt"] = True
    st.session_state.pop("pending_clear_access", None)
    st.rerun()

if st.session_state.get("pending_clear_refresh"):
    st.session_state.pop("refresh_token", None)
    st.session_state.pop("refresh_token_input", None)
    st.session_state["login_prompt"] = True
    st.session_state.pop("pending_clear_refresh", None)
    st.rerun()


# ---------- Sidebar (Settings) ----------
with st.sidebar:
    st.header("Settings")
    st.session_state["base_url"] = st.text_input("Base API URL", value=st.session_state["base_url"]) or st.session_state["base_url"]
    st.caption("Docs usually at /v2/docs")
    st.divider()
    st.write("Tokens")

    # Access token controls
    st.text_input("Access Token", value=st.session_state.get("access_token") or "", key="access_token_input")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("Apply Access"):
            st.session_state["access_token"] = st.session_state.get("access_token_input") or None
    with col_a2:
        if st.button("Clear Access"):
            st.session_state["pending_clear_access"] = True
            st.rerun()

    # Refresh token controls
    st.text_input("Refresh Token", value=st.session_state.get("refresh_token") or "", key="refresh_token_input")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("Apply Refresh"):
            st.session_state["refresh_token"] = st.session_state.get("refresh_token_input") or None
    with col_r2:
        if st.button("Clear Refresh"):
            st.session_state["pending_clear_refresh"] = True
            st.rerun()


st.title("📚 Booklynn")
st.caption("Interact with the FastAPI backend endpoints.")


tab_auth, tab_books, tab_reviews = st.tabs(["Auth", "Books", "Reviews"])


# ---------- Auth Tab ----------
with tab_auth:
    if st.session_state.get("login_prompt"):
        st.warning("Credentials cleared. Please log in again.")
        # Reset flag once shown
        st.session_state["login_prompt"] = False
    st.subheader("Sign Up")
    with st.form("signup_form", clear_on_submit=False):
        su_first = st.text_input("First name", value="aditya")
        su_username = st.text_input("Username (<=8 chars)", value="adi")
        su_email = st.text_input("Email", value="aditya59ranjan@gmail.com")
        su_password = st.text_input("Password", type="password", value="adi123")
        su_role = st.selectbox("Role", ["user", "admin"], index=0)
        submitted = st.form_submit_button("Create Account")
        if submitted:
            payload = {
                "first_name": su_first,
                "username": su_username,
                "email": su_email,
                "password": su_password,
                "role": su_role,
            }
            resp = api_request("POST", "/auth/signup", json_body=payload)
            show_response(resp)

    st.divider()
    st.subheader("Login")
    with st.form("login_form"):
        li_email = st.text_input("Email", value="aditya59ranjan@gmail.com")
        li_password = st.text_input("Password", type="password", value="adi123")
        login_sub = st.form_submit_button("Login")
        if login_sub:
            body = {"email": li_email, "password": li_password}
            resp = api_request("POST", "/auth/login", json_body=body)
            show_response(resp)
            if resp.ok:
                try:
                    data = resp.json()
                    st.session_state["access_token"] = data.get("access_token") or data.get("access")
                    st.session_state["refresh_token"] = data.get("refresh_token") or data.get("refresh")
                except Exception:
                    pass

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Me (requires access token)")
        if st.button("GET /auth/me"):
            resp = api_request("GET", "/auth/me", token=st.session_state.get("access_token"))
            show_response(resp)
    with col2:
        st.write("Refresh (requires refresh token)")
        if st.button("POST /auth/refresh"):
            resp = api_request("POST", "/auth/refresh", token=st.session_state.get("refresh_token"))
            show_response(resp)
            if resp.ok:
                try:
                    data = resp.json()
                    st.session_state["access_token"] = data.get("access_token") or data.get("access")
                except Exception:
                    pass
    with col3:
        st.write("Logout (revokes access token)")
        if st.button("GET /auth/logout"):
            resp = api_request("GET", "/auth/logout", token=st.session_state.get("access_token"))
            show_response(resp)

    st.divider()
    st.subheader("Password Reset")
    with st.form("pw_reset_form"):
        pr_email = st.text_input("Email for reset", value="jane@example.com")
        pr_submit = st.form_submit_button("POST /auth/password-reset")
        if pr_submit:
            resp = api_request("POST", "/auth/password-reset", json_body={"email": pr_email})
            show_response(resp)

    st.divider()
    st.subheader("Password Reset Confirm")
    qp = get_query_params()
    token_prefill = ""
    # Auto-pick token from URL like ...?token=XYZ or .../password-reset-confirm/XYZ routed through FE
    if "token" in qp and isinstance(qp["token"], list) and qp["token"]:
        token_prefill = qp["token"][0]
    with st.form("pw_reset_confirm_form"):
        pr_token = st.text_input("Token", value=token_prefill)
        new_pw = st.text_input("New Password", type="password")
        conf_pw = st.text_input("Confirm New Password", type="password")
        prc_submit = st.form_submit_button("POST /auth/password-reset-confirm/{token}")
        if prc_submit:
            if not pr_token:
                st.warning("Provide the reset token (from email link).")
            else:
                body = {"new_password": new_pw, "confirm_new_password": conf_pw}
                resp = api_request("POST", f"/auth/password-reset-confirm/{pr_token}", json_body=body)
                show_response(resp)

    st.divider()
    st.subheader("Admin: Delete User")
    with st.form("delete_user_form"):
        del_user_uid = st.text_input("User UID to delete", value="")
        del_submit = st.form_submit_button("DELETE /auth/users/{user_uid}")
        if del_submit:
            if del_user_uid:
                resp = api_request("DELETE", f"/auth/users/{del_user_uid}", token=st.session_state.get("access_token"))
                show_response(resp)
            else:
                st.warning("Provide a valid user UID.")


# ---------- Books Tab ----------
with tab_books:
    st.subheader("Books – requires user role for most actions")

    def list_books() -> None:
        resp = api_request("GET", "/books/", token=st.session_state.get("access_token"))
        st.caption("GET /books/")
        show_response(resp)
        if resp.ok:
            try:
                st.session_state["books_cache"] = resp.json()
            except Exception:
                pass

    col_l, col_c = st.columns(2)
    with col_l:
        if st.button("List Books"):
            list_books()
    with col_c:
        st.caption("Create a book")
        with st.form("create_book_form"):
            b_title = st.text_input("Title", value="The Great Gatsby")
            b_author = st.text_input("Author", value="F. Scott Fitzgerald")
            b_year = st.text_input("Year", value="1925")
            b_language = st.selectbox("Language", ["English", "Other"], index=0)
            create_sub = st.form_submit_button("POST /books/")
            if create_sub:
                payload = {
                    "title": b_title,
                    "author": b_author,
                    "year": b_year,
                    "language": b_language,
                }
                resp = api_request("POST", "/books/", token=st.session_state.get("access_token"), json_body=payload)
                show_response(resp)

    st.divider()
    st.caption("Update/Delete a book")
    books_for_select = st.session_state.get("books_cache", [])
    selected_book_uid = None
    if isinstance(books_for_select, list) and books_for_select:
        labels = [f"{b.get('title')} ({b.get('uid')})" for b in books_for_select]
        idx = st.selectbox("Choose a book", options=list(range(len(labels))), format_func=lambda i: labels[i])
        selected_book_uid = books_for_select[idx].get("uid")
    else:
        st.info("Click 'List Books' to load books or create a new one.")

    col_u, col_d, col_r = st.columns(3)
    with col_u:
        with st.form("update_book_form"):
            up_title = st.text_input("New title", value="")
            up_author = st.text_input("New author", value="")
            up_year = st.text_input("New year", value="")
            up_language = st.selectbox("New language", ["", "English", "Other"], index=0)
            up_sub = st.form_submit_button("PATCH /books/{uid}")
            if up_sub and selected_book_uid:
                payload: Dict[str, Any] = {}
                if up_title:
                    payload["title"] = up_title
                if up_author:
                    payload["author"] = up_author
                if up_year:
                    payload["year"] = up_year
                if up_language:
                    payload["language"] = up_language
                resp = api_request("PATCH", f"/books/{selected_book_uid}", token=st.session_state.get("access_token"), json_body=payload)
                show_response(resp)
            elif up_sub:
                st.warning("Select a book first.")

    with col_d:
        if st.button("DELETE /books/{uid}"):
            if selected_book_uid:
                resp = api_request("DELETE", f"/books/{selected_book_uid}", token=st.session_state.get("access_token"))
                show_response(resp)
            else:
                st.warning("Select a book first.")

    with col_r:
        if st.button("GET /books/{uid}"):
            if selected_book_uid:
                resp = api_request("GET", f"/books/{selected_book_uid}", token=st.session_state.get("access_token"))
                show_response(resp)
            else:
                st.warning("Select a book first.")


# ---------- Reviews Tab ----------
with tab_reviews:
    st.subheader("Reviews")
    st.caption("Note: backend mounts reviews under '/review' prefix.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("GET /review/"):
            resp = api_request("GET", "/review/", token=st.session_state.get("access_token"))
            show_response(resp)

    with col_b:
        st.caption("POST /review/book/{book_uid}")
        with st.form("add_review_form"):
            books_for_select = st.session_state.get("books_cache", [])
            if isinstance(books_for_select, list) and books_for_select:
                labels = [f"{b.get('title')} ({b.get('uid')})" for b in books_for_select]
                idx = st.selectbox("Book", options=list(range(len(labels))), format_func=lambda i: labels[i], key="rev_book_selector")
                book_uid = books_for_select[idx].get("uid")
            else:
                book_uid = st.text_input("Book UID")
            rating = st.number_input("Rating (1-5)", min_value=1, max_value=5, value=5, step=1)
            review_text = st.text_input("Review text", value="one of the greatest reads")
            rev_sub = st.form_submit_button("Add Review")
            if rev_sub and book_uid:
                payload = {"rating": int(rating), "review_text": review_text}
                resp = api_request("POST", f"/review/book/{book_uid}", token=st.session_state.get("access_token"), json_body=payload)
                show_response(resp)
            elif rev_sub:
                st.warning("Provide a valid book UID.")

    st.divider()
    st.caption("GET /review/book/{book_uid}")
    book_uid_lookup = st.text_input("Book UID to fetch reviews for")
    if st.button("Fetch Reviews for Book"):
        if book_uid_lookup:
            resp = api_request("GET", f"/review/book/{book_uid_lookup}", token=st.session_state.get("access_token"))
            show_response(resp)
        else:
            st.warning("Provide a book UID.")

    st.divider()
    st.caption("DELETE /review/{review_uid} (admin role)")
    review_uid_del = st.text_input("Review UID to delete")
    if st.button("Delete Review"):
        if review_uid_del:
            resp = api_request("DELETE", f"/review/{review_uid_del}", token=st.session_state.get("access_token"))
            show_response(resp)
        else:
            st.warning("Provide a review UID.")


st.divider()
st.info("Run: streamlit run frontend/frontend.py")


