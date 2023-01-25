import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])


def create_user_in_db(userDetails):
    client.set_token(st.session_state["token"])
    response = client.post("/auth/add_user", data=None, json=userDetails)
    if response.status_code == 200:
        st.markdown(f"## User {userDetails['name']} added to the lakehouse")
        st.balloons()


def create_user_form_layout():
    create_user_form = st.form("create_user")
    username = create_user_form.text_input("username")
    password = create_user_form.text_input("password", type="password")
    email = create_user_form.text_input("email")
    team = create_user_form.text_input("team")
    submit = create_user_form.form_submit_button("create")
    userDetails = {}
    userDetails["name"] = username
    userDetails["password"] = password
    userDetails["email"] = email
    userDetails["namespace"] = team
    if submit:
        create_user_in_db(userDetails)

    return create_user_form
