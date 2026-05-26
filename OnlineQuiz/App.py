# Main Streamlit application — UI only.
import streamlit as st
from Config import SPECIAL_CHARS
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
#Page config 

st.set_page_config(page_title="Online Quiz", page_icon="🧠", layout="centered")

# Session state defaults 

for key, default in {
    "page": "login",        # login | register | forgot
    "mail_verified": False,
    "current_mail": "",
    "otp_store": {},        # {email: otp_code}  — managed by email_sender.py
    "reset_otp_verified": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

#  Helpers 

def go(page: str):
    """Navigate to a page and reset transient auth state."""
    st.session_state.page = page
    st.session_state.mail_verified = False
    st.session_state.current_mail = ""
    st.session_state.reset_otp_verified = False


def validate_password(pw: str) -> str | None:
    """Return an error string if the password fails policy, else None."""
    if not any(c.isupper() for c in pw):
        return "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in pw):
        return "Password must contain at least one digit."
    if not any(c in SPECIAL_CHARS for c in pw):
        return "Password must contain at least one special character (!@#$… etc.)."
    return None

# Page: Login

def page_login():
    st.title("🔐 Login")

    identifier = st.text_input("Username or Email")
    password   = st.text_input("Password", type="password")

    col1, col2, col3 = st.columns(3)

    if col1.button("Login", use_container_width=True):
        if not identifier or not password:
            st.warning("Please fill in both fields.")
        elif authenticate_user(identifier, password):
            go("quiz")
            st.rerun()
            
        else:
            st.error("Invalid credentials.")

    if col2.button("Sign Up", use_container_width=True):
        go("register")
        st.rerun()

    if col3.button("Forgot Password", use_container_width=True):
        go("forgot")
        st.rerun()


# Page: Register

def page_register():
    st.title("📝 Sign Up")

    username = st.text_input("Username")

    # Email + OTP section 
    st.subheader("Email Verification")

    email_col, send_col = st.columns([3, 1])
    email = email_col.text_input("Email address")

    if send_col.button("Send OTP"):
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
    otp_input = otp_col.text_input("Enter OTP", max_chars=6)

    if verify_col.button("Verify"):
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

    # Password section 
    st.subheader("Set Password")
    password = st.text_input("Create password", type="password")
    confirm  = st.text_input("Confirm password", type="password")

    # Submit 
    if st.button("Submit", use_container_width=True):
        mail = st.session_state.current_mail
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
            st.success("🎉 Registered successfully! You can now log in.")
            st.session_state.mail_verified = False
            st.session_state.current_mail  = ""

    st.divider()
    if st.button("← Back to Login"):
        go("login")
        st.rerun()

# Page: Forgot Password

def page_forgot():
    st.title("🔑 Reset Password")

    identifier = st.text_input("Enter your username or email")

    if st.button("Send OTP"):
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
    otp_input = otp_col.text_input("Enter OTP", max_chars=6, key="reset_otp_input")

    if verify_col.button("Verify OTP"):
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

        if st.button("Reset Password", use_container_width=True):
            error = validate_password(new_pw)
            if error:
                st.error(error)
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                update_password(st.session_state.current_mail, new_pw)
                st.success("Password updated! Please log in.")
                send_password_reset_mail(st.session_state.current_mail)
                go("login")
                st.rerun()

    st.divider()
    if st.button("← Back to Login"):
        go("login")
        st.rerun()

# Router

{
    "login":    page_login,
    "register": page_register,
    "forgot":   page_forgot,
    "quiz":     Quiz.page_quiz, 
    "playing":   Quiz._phase_playing,
}[st.session_state.page]()