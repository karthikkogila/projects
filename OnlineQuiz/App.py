# App.py — Main Streamlit application. Single entry point.
# Run with: streamlit run App.py

import streamlit as st
from Config import SPECIAL_CHARS
from Style import QUIZ_CSS
import Quiz
from Database import (
    find_user_by_email,
    find_user_by_username,
    find_email_by_identifier,
    authenticate_user,
    create_user,
    update_password,
)
from Emailsender import (
    generate_and_send_otp,
    verify_otp,
    send_welcome_email,
    send_password_reset_mail,
)

# ── Page config — MUST be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="Online Quiz",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Inject global CSS
st.markdown(QUIZ_CSS, unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "page":               "login",   # login | register | forgot | quiz
    "mail_verified":      False,
    "current_mail":       "",
    "otp_store":          {},
    "reset_otp_verified": False,
    "logged_in_user":     None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helpers ───────────────────────────────────────────────────────────────────

def go(page: str):
    """Navigate to a page and reset transient auth state."""
    st.session_state.page               = page
    st.session_state.mail_verified      = False
    st.session_state.current_mail       = ""
    st.session_state.reset_otp_verified = False


def validate_password(pw: str):
    """Return error string if password fails policy, else None."""
    if len(pw) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in pw):
        return "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in pw):
        return "Password must contain at least one digit."
    if not any(c in SPECIAL_CHARS for c in pw):
        return "Password must contain at least one special character (!@#$… etc.)."
    return None


# ── Page: Login ───────────────────────────────────────────────────────────────

def page_login():
    st.markdown(
        "<h1 style='text-align:center'>🔐 Login</h1>",
        unsafe_allow_html=True,
    )

    identifier = st.text_input("Username or Email", key="login_id")
    password   = st.text_input("Password", type="password", key="login_pw")

    col1, col2, col3 = st.columns(3)

    if col1.button("Login", use_container_width=True):
        if not identifier or not password:
            st.warning("Please fill in both fields.")
        elif authenticate_user(identifier, password):
            row = find_user_by_username(identifier)
            if row:
                st.session_state.logged_in_user = row[1]
            else:
                row2 = find_user_by_email(identifier)
                st.session_state.logged_in_user = row2[1] if row2 else identifier
            go("quiz")
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

    if col2.button("Sign Up", use_container_width=True):
        go("register")
        st.rerun()

    if col3.button("Forgot Password", use_container_width=True):
        go("forgot")
        st.rerun()


# ── Page: Register ────────────────────────────────────────────────────────────

def page_register():
    st.markdown(
        "<h1 style='text-align:center'>📝 Create Account</h1>",
        unsafe_allow_html=True,
    )

    username = st.text_input("Username", key="reg_user")

    st.subheader("Email Verification")
    email_col, send_col = st.columns([3, 1])
    email = email_col.text_input("Email address", key="reg_email")

    if send_col.button("Send OTP", key="send_otp_reg"):
        if not email:
            st.warning("Enter an email address first.")
        elif find_user_by_email(email):
            st.info("An account with this email already exists — please log in.")
        else:
            if generate_and_send_otp(email):
                st.session_state.current_mail  = email
                st.session_state.mail_verified = False
                st.success(f"OTP sent to {email}")

    otp_col, verify_col = st.columns([3, 1])
    otp_input = otp_col.text_input("Enter OTP", max_chars=6, key="reg_otp")

    if verify_col.button("Verify", key="verify_otp_reg"):
        mail = st.session_state.current_mail
        if not mail:
            st.warning("Send an OTP first.")
        elif verify_otp(mail, otp_input):
            st.session_state.mail_verified = True
            st.success("✅ Email verified!")
        else:
            st.error("Invalid OTP. Try again or request a new one.")

    if st.session_state.mail_verified:
        st.caption("✅ Email verified")

    st.subheader("Set Password")
    password = st.text_input("Create password", type="password", key="reg_pw")
    confirm  = st.text_input("Confirm password", type="password", key="reg_pw2")

    if st.button("Create Account", use_container_width=True, key="reg_submit"):
        mail  = st.session_state.current_mail
        error = None
        if not username or not mail or not password or not confirm:
            error = "All fields are required."
        elif not st.session_state.mail_verified:
            error = "Please verify your email first."
        elif find_user_by_username(username):
            error = "Username already taken — choose another."
        else:
            error = validate_password(password)
        if not error and password != confirm:
            error = "Passwords do not match."

        if error:
            st.error(error)
        else:
            create_user(username, mail, password)
            send_welcome_email(username, mail)
            st.success("🎉 Account created! You can now log in.")
            st.session_state.mail_verified = False
            st.session_state.current_mail  = ""

    st.divider()
    if st.button("← Back to Login", key="reg_back"):
        go("login")
        st.rerun()


# ── Page: Forgot Password ─────────────────────────────────────────────────────

def page_forgot():
    st.markdown(
        "<h1 style='text-align:center'>🔑 Reset Password</h1>",
        unsafe_allow_html=True,
    )

    identifier = st.text_input("Enter your username or email", key="forgot_id")

    if st.button("Send OTP", key="forgot_send"):
        if not identifier:
            st.warning("Enter your username or email first.")
        else:
            reset_mail = find_email_by_identifier(identifier)
            if not reset_mail:
                st.error("No account found. Please sign up first.")
            elif generate_and_send_otp(reset_mail):
                st.session_state.current_mail       = reset_mail
                st.session_state.reset_otp_verified = False
                st.success(f"OTP sent to {reset_mail}")

    otp_col, verify_col = st.columns([3, 1])
    otp_input = otp_col.text_input("Enter OTP", max_chars=6, key="forgot_otp")

    if verify_col.button("Verify OTP", key="forgot_verify"):
        mail = st.session_state.current_mail
        if not mail:
            st.warning("Request an OTP first.")
        elif verify_otp(mail, otp_input):
            st.session_state.reset_otp_verified = True
            st.success("✅ OTP verified!")
        else:
            st.error("Invalid OTP.")

    if st.session_state.reset_otp_verified:
        st.subheader("Set New Password")
        new_pw  = st.text_input("New password",     type="password", key="new_pw")
        conf_pw = st.text_input("Confirm password", type="password", key="conf_pw")

        if st.button("Reset Password", use_container_width=True, key="forgot_reset"):
            error = validate_password(new_pw)
            if error:
                st.error(error)
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                update_password(st.session_state.current_mail, new_pw)
                send_password_reset_mail(st.session_state.current_mail)
                st.success("Password updated! Please log in.")
                go("login")
                st.rerun()

    st.divider()
    if st.button("← Back to Login", key="forgot_back"):
        go("login")
        st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────

page = st.session_state.page

if page == "login":
    page_login()
elif page == "register":
    page_register()
elif page == "forgot":
    page_forgot()
elif page == "quiz":
    if not st.session_state.get("logged_in_user"):
        # Guard: must be logged in to reach quiz
        st.warning("Please log in first.")
        go("login")
        st.rerun()
    else:
        Quiz.page_quiz()
else:
    go("login")
    st.rerun()