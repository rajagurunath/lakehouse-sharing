import streamlit as st
from core.login import Authenticator

app_auth = Authenticator()
from core.link import create_link_form_layout
from core.schema import create_complete_share_layout
from core.share import create_share_form_layout
from core.table import create_table_form_layout
from core.table_format import table_format_exploration
from core.user import create_user_form_layout

st.set_page_config(
    page_title="LakeHouse Sharing",
    layout="wide",
    page_icon="https://uxwing.com/wp-content/themes/uxwing/download/web-app-development/data-lake-icon.png",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "# LakeHouse Sharing",
        "Report a bug": "https://github.com/rajagurunath/Lakehouse-Sharing",
    },
)


def create_user_layout():
    st.header("Create a New User")
    create_user_form_layout()


def create_components_layout():
    """
    share form
    schema form
    table form
    """
    st.title("Lakehouse Share Components")
    # st.header("create a share")
    # # create_share_form_layout()
    # st.header("create a table")
    # # create_table_form_layout()
    # st.header("create a schema")
    create_complete_share_layout()


def user_link_layout():
    """
    user-> share - > schema -> table
    """
    # download creds
    create_link_form_layout()


def main_layout():
    st.sidebar.title(f"Hi {st.session_state['username']}")
    tab = st.sidebar.radio(
        "Pages",
        ["Add User", "Create a Share", "Define Permissions", "Explore Table format"],
    )
    if tab == "Add User":
        create_user_layout()
    elif tab == "Create a Share":
        create_components_layout()
    elif tab == "Define Permissions":
        user_link_layout()
    elif tab == "Explore Table format":
        table_format_exploration()


if __name__ == "__main__":
    app_auth.login_screen()
    if st.session_state["logged_in"]:

        main_layout()
        app_auth.logout()
    else:
        st.write("Please Enter correct username and Password")
