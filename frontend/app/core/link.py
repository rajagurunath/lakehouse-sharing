import json
from datetime import datetime

import jwt
import streamlit as st
from app.core.api.rest import RestClient

client = RestClient(token=st.session_state["token"])

days_to_seconds = lambda days: days * 24 * 60 * 60


def create_link_in_db(linkDetails):
    client.set_token(st.session_state["token"])
    response = client.post("/admin/link", data=None, json=linkDetails)
    print(response.content)
    if response.status_code == 200:
        st.markdown(response.text)
        st.balloons()
    else:
        st.error(response.text)


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
    client.set_token(st.session_state["token"])
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
    client.set_token(st.session_state["token"])
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


def get_token(user_id):
    response = client.get(f"/admin/token/{user_id}")
    if response.status_code == 200:
        print(response.content)
        return response.json()["access_token"]


def get_expiry_from_token(token):
    expiry_timestamp = jwt.decode(
        token, algorithms="HS256", options={"verify_signature": False}
    )["exp"]
    return datetime.fromtimestamp(expiry_timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")


def download_creds_layout(user_id, container):
    button = container.button("Download Credentials")
    if button:
        token = get_token(user_id=user_id)
        sharing_profile = {
            "shareCredentialsVersion": 1,
            "endpoint": f"{client.baseurl}{client.prefix}",
            "bearerToken": token,
            "expirationTime": get_expiry_from_token(token),
        }
        container.write(sharing_profile)
        download_button = container.download_button(
            "Download Credentials",
            data=json.dumps(sharing_profile),
            file_name="profile.json",
        )
        if download_button:
            st.write(user_id)

        else:
            st.error("Error generating token")


def list_users():
    client.set_token(st.session_state["token"])
    response = client.get("/auth/users")
    if response.status_code == 200:
        print(response.content)
        items = response.json()
        _list_users = []
        for r in items:
            _list_users.append(f"{r['name']} ({r['id']})")
        print(_list_users)
    else:
        _list_users = []
    return _list_users


def update_token_lifetime(username, seconds):
    data = {"username": username, "expiry": seconds}
    response = client.post("/admin/lifetime", data=None, json=data)
    if response.status_code == 200:
        st.success(f"User {username} Token lifetime updated")
    else:
        st.write(response.text)
        st.error(f"Error updating lifetime of the token for User {username}")


def create_link_form_layout():
    st.header("Give Required Permissions to the User")
    create_link_form = st.container()
    user_id = create_link_form.selectbox("users", list_users())
    col1, col2, col3 = create_link_form.columns(3)
    share = col1.selectbox("shares", list_shares())
    print(share)
    schema = col2.selectbox("schema", list_schema(share))
    table = col3.selectbox("table", list_tables(share, schema=schema))

    submit = create_link_form.button("Give permission")
    linkDetails = {}
    linkDetails["user_id"] = user_id.split(" ")[1].split("(")[-1].replace(")", "")
    linkDetails["share_id"] = share.split(" ")[1].split("(")[-1].replace(")", "")
    linkDetails["schema_name"] = schema
    linkDetails["table_id"] = table.split(" ")[1].split("(")[-1].replace(")", "")
    if submit:
        create_link_in_db(linkDetails)
    create_link_form.header("Define Token/Credential Lifetime for the User Token")
    col1, col3, _ = create_link_form.columns(3, gap="medium")
    expiry = col1.slider("Expiry in days", min_value=1, max_value=7)
    update_lifetime = col3.button("Update Token Lifetime")
    if update_lifetime:
        seconds = days_to_seconds(expiry)
        create_link_form.write(seconds)
        update_token_lifetime(username=user_id.split(" ")[0], seconds=seconds)
    create_link_form.header("Download Sharing Profile")
    download_creds_layout(linkDetails["user_id"], create_link_form)
    return create_link_form
