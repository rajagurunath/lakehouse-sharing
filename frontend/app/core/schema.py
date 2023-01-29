import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])


def create_schema_in_db(completeDetails):
    client.set_token(st.session_state["token"])
    response = client.post("/admin/complete", data=None, json=completeDetails)
    print(response.content)
    if response.status_code == 200:
        st.markdown(f"## Share {completeDetails['share']['name']} created in the lakehouse")
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


def create_complete_share_layout():
    create_complete_share = st.container()
    create_complete_share.header("Create a Share")
    sharename = create_complete_share.text_input("sharename")
    create_complete_share.header("Create a Table")
    tablename = create_complete_share.text_input("tablename")
    table_location = create_complete_share.text_input("tablelocation")
    create_complete_share.header("Create a Schema")
    schemaname = create_complete_share.text_input("schemaname")
    submit = create_complete_share.button("create")
    completeDetails = {}
    completeDetails['share'] = {"name":sharename}
    completeDetails['schema_'] = {"name":schemaname}
    completeDetails['table'] ={
        "table_name":tablename,
        "table_location":table_location
    }
    if submit:
        create_schema_in_db(completeDetails)
    return create_complete_share
