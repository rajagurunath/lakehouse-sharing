import streamlit as st
from app.core.api.rest import RestClient


class Authenticator(object):
    def __init__(self) -> None:
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = None
        if "username" not in st.session_state:
            st.session_state["username"] = None
        if "logout" not in st.session_state:
            st.session_state["logout"] = None
        if "token" not in st.session_state:
            st.session_state["token"] = None

    def verify_user(self, username, password):
        user_details = {"username": username, "password": password}
        client = RestClient(user_details=user_details)
        token = client.jauth.get_token()
        return token

    def login_screen(self):
        print("logged_in", st.session_state["logged_in"])
        if not st.session_state["logged_in"]:
            st.header("Lakehouse-Sharing")
            st.text("( A table format agnostic sharing app )")
            login_form = st.form("Lakehouse-Sharing")
            username = login_form.text_input("username")
            password = login_form.text_input("password", type="password")
            login_form.form_submit_button("login")
            try:
                token = self.verify_user(username=username, password=password)
                st.session_state["username"] = username
                st.session_state["password"] = password
                st.session_state["token"] = token
                st.session_state["logged_in"] = True
                st.experimental_rerun()
                return True
            except Exception as e:
                st.session_state["logged_in"] = False
                st.warning("Logging failed")
                st.error(e)

    def logout(self):
        logout = st.sidebar.button("logout")
        if logout:
            st.session_state["username"] = None
            st.session_state["password"] = None
            st.session_state["token"] = None
            st.session_state["logged_in"] = False
            st.experimental_rerun()
