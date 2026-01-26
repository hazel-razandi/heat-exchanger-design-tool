import streamlit as st

def check_login(username, password):
    """
    Simple mock authentication. 
    In a real SaaS, this would check a Supabase or Firebase database.
    """
    # For demo, allow any non-empty username
    if username and len(username) > 2:
        return True
    return False

def render_login():
    """Renders the Login Screen"""
    st.markdown("## 🔒 ExchangerAI Secure Login")
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("login_form"):
            user = st.text_input("Username")
            passw = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", type="primary")
            
            if submitted:
                if check_login(user, passw):
                    st.session_state['user'] = user
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Username must be > 2 chars.")

