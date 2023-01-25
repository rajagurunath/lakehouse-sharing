import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])


def create_schema_in_db(schemaDetails):
    response = client.post("/admin/schema", data=None, json=schemaDetails)
    print(response.content)
    if response.status_code == 200:
        st.markdown(f"## schema {schemaDetails['name']} created in the lakehouse")
        st.balloons()


def list_shares():
    client.set_token(st.session_state["token"])
    response = client.get("/delta-sharing/shares")
    if response.status_code == 200:
        print(response.content)
        items = response.json()["items"]
        _list_shares = []
        for r in items:
            _list_shares.append(f"{r['name']} ({r['id']})")
        print(_list_shares)
    return _list_shares


def list_tables(share):
    client.set_token(st.session_state["token"])
    st.write(share)
    sharename, id = share.split(" ")
    response = client.get(f"/delta-sharing/shares/{sharename}/schemas/all-tables")
    if response.status_code == 200:
        print(response.content)
        items = response.json()["items"]
        _list_tables = []
        for r in items:
            _list_tables.append(f"{r['name']} ({r['id']})")
    else:
        raise Exception(response.content)
    return _list_tables


def create_schema_form_layout():
    create_schema_form = st.container()
    schemaname = create_schema_form.text_input("name")
    col1, col2 = create_schema_form.columns(2)
    share = col1.selectbox("shares", list_shares())
    print(share)
    table = col2.selectbox("table", list_tables(share))
    submit = create_schema_form.button("create")
    schemaDetails = {}
    schemaDetails["name"] = schemaname
    schemaDetails["share_id"] = share.split(" ")[1].rstrip("(").lstrip(")")
    schemaDetails["table_id"] = table.split(" ")[1].rstrip("(").lstrip(")")
    if submit:
        create_schema_in_db(schemaDetails)
    return create_schema_form
