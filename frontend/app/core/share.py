import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])


def create_share_in_db(shareDetails):
    client.set_token(st.session_state["token"])
    response = client.post("/admin/share", data=None, json=shareDetails)
    print(response.content)
    if response.status_code == 200:
        st.markdown(f"## Share {shareDetails['name']} created in the lakehouse")
        st.balloons()


def create_share_form_layout():
    create_share_form = st.form("create_share")
    sharename = create_share_form.text_input("sharename")
    submit = create_share_form.form_submit_button("create")
    shareDetails = {}
    shareDetails["name"] = sharename
    if submit:
        create_share_in_db(shareDetails)
    return create_share_form
