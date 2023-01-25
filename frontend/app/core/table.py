import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])


def create_table_in_db(tableDetails):
    client.set_token(st.session_state["token"])
    response = client.post("/admin/table", data=None, json=tableDetails)
    print(response.content)
    if response.status_code == 200:
        st.markdown(f"## Table {tableDetails['table_name']} created in the lakehouse")
        st.balloons()


def create_table_form_layout():
    create_table_form = st.form("create_table")
    tablename = create_table_form.text_input("tablename")
    tablelocation = create_table_form.text_input("table_location")
    submit = create_table_form.form_submit_button("create")
    tableDetails = {}
    tableDetails["table_name"] = tablename
    tableDetails["table_location"] = tablelocation
    if submit:
        create_table_in_db(tableDetails)
    return create_table_form
