import json

import pandas as pd
import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])

days_to_seconds = lambda days: days * 24 * 60 * 60


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


def list_schema(share):
    sharename, id = share.split(" ")
    response = client.get(f"/delta-sharing/shares/{sharename}/schemas")
    if response.status_code == 200:
        print(response.content)
        items = response.json()["items"]
        _list_tables = []
        for r in items:
            _list_tables.append(f"{r['name']}")
    else:
        raise Exception(response.content)
    return _list_tables


def list_tables(share, schema):
    sharename, id = share.split(" ")
    response = client.get(f"/delta-sharing/shares/{sharename}/schemas/{schema}/tables")
    if response.status_code == 200:
        print(response.content)
        items = response.json()["items"]
        _list_tables = []
        for r in items:
            _list_tables.append(f"{r['name']} ({r['id']})")
    else:
        raise Exception(response.content)
    return _list_tables


def get_metadata(share, schema, table):
    response = client.get(
        f"/delta-sharing/shares/{share}/schemas/{schema}/tables/{table}/metadata"
    )
    if response.status_code == 200:
        lines = response.iter_lines()
        header = json.loads(next(lines))
        metadata = json.loads(next(lines))
    else:
        raise Exception(response.content)
    return header, metadata


def get_table_data(share, schema, table, version, limitHint):
    response = client.post(
        f"/delta-sharing/shares/{share}/schemas/{schema}/tables/{table}/query",
        data=None,
        json={"predicateHints": [], "limitHint": limitHint, "version": version},
    )
    if response.status_code == 200:
        lines = response.iter_lines()
        header = json.loads(next(lines))
        metadata = json.loads(next(lines))
    else:
        raise Exception(response.content)
    return header, metadata, lines


def table_format_exploration():
    st.header("Explore Table formats")
    create_link_form = st.container()
    col1, col2, col3 = create_link_form.columns(3)
    share = col1.selectbox("shares", list_shares())
    print(share)
    schema = col2.selectbox("schema", list_schema(share))
    table = col3.selectbox("table", list_tables(share, schema=schema))
    col1, col2 = create_link_form.columns(2)
    # metadata_bt = col1.button("get Metadata")
    # table_bt = col2.button("get Table Files")
    with st.expander("Metadata"):
        get_meta = st.button("Get Metadata")
        if get_meta:
            st.header("Metadata")
            share = share.split(" ")[0].split("(")[-1].replace(")", "")
            table = table.split(" ")[0].split("(")[-1].replace(")", "")
            header, metadata = get_metadata(share, schema, table)
            st.markdown("### Header")
            st.write(header)
            st.markdown("### Metadata")
            st.write(metadata)

    with st.expander("Table Details"):
        get_table_meta = st.button("Get Table Details")
        version = st.text_input("version")
        limitHint = st.text_input("limit hint")
        if get_table_meta:
            st.header("Table Details")
            share = share.split(" ")[0].split("(")[-1].replace(")", "")
            table = table.split(" ")[0].split("(")[-1].replace(")", "")
            header, metadata, table_iter = get_table_data(
                share, schema, table, version, limitHint
            )
            st.markdown("### Header")
            st.write(header)
            st.markdown("### Metadata")
            st.write(metadata)
            st.markdown("### Table")
            file_details = next(table_iter)
            df = pd.DataFrame(json.loads(file_details)["file"])
            st.write(df)
