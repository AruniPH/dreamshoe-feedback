import streamlit as st
try:
    from database import verify_user
except ImportError:
    raise ImportError("The 'database' module could not be found. Ensure 'database.py' exists in the same directory or adjust the import path.")

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.username = None
    return st.session_state.authenticated

def login_page():
    st.title("Welcome to DreamShoe")

    tab_customer, tab_management = st.tabs(["Customer Access", "Management Login"])

    with tab_customer:
        st.markdown("Enter your name and email to continue.")
        name  = st.text_input("Full Name",  placeholder="Enter your full name",  key="login_customer_name")
        email = st.text_input("Email",      placeholder="Enter your email address", key="login_customer_email")
        if st.button("Continue as Customer", use_container_width=True):
            if name.strip() and email.strip():
                st.session_state.authenticated  = True
                st.session_state.user_role      = "customer"
                st.session_state.username       = name.strip()
                st.session_state.customer_name  = name.strip()
                st.session_state.customer_email = email.strip()
                st.rerun()
            else:
                st.error("Please enter both your name and email.")

    with tab_management:
        st.markdown("Management staff login with credentials.")
        username = st.text_input("Username", key="login_mgmt_username")
        password = st.text_input("Password", type="password", key="login_mgmt_password")
        if st.button("Login", use_container_width=True):
            user = verify_user(username, password)
            if user:
                st.session_state.authenticated  = True
                st.session_state.user_role      = user["role"]
                st.session_state.username       = user["username"]
                st.rerun()
            else:
                st.error("Invalid credentials")

def logout():
    st.session_state.authenticated  = False
    st.session_state.user_role      = None
    st.session_state.username       = None
    st.session_state.customer_name  = None
    st.session_state.customer_email = None
    st.rerun()

