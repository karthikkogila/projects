# ── email_sender.py ───────────────────────────────────────────────────────────
# All email and OTP logic lives here.

import secrets
import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Config import SENDER_EMAIL, SENDER_APP_PASSWORD
from Database import find_user_by_email


# ── Core send function ─────────────────────────────────────────────────────────

def send_mail(recipient: str, subject: str, body: str) -> bool:
    """
    Send a plain-text email.
    Returns True on success, False on failure (error shown in Streamlit).
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = recipient
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Mail error: {e}")
        return False


# ── OTP helpers ────────────────────────────────────────────────────────────────

def generate_and_send_otp(recipient: str) -> bool:
    """
    Generate a 6-digit OTP, store it in session_state, and email it.
    Returns True if the email was sent successfully.
    """
    code = str(secrets.randbelow(900000) + 100000)
    st.session_state.otp_store[recipient] = code

    body = f"""Dear Customer,

Greetings from Online Quiz Competition.

Your One-Time Password (OTP) for verification is:

OTP: {code}

This OTP is valid for the next 5 minutes.
Please do not share this OTP with anyone.

Thank you,
Online Quiz Competition
"""
    return send_mail(recipient, "Your OTP Verification Code", body)


def verify_otp(recipient: str, entered: str) -> bool:
    """
    Check the entered OTP against the stored one.
    Clears the OTP from the store on a correct match.
    """
    stored = st.session_state.otp_store.get(recipient)
    if stored and stored == entered.strip():
        del st.session_state.otp_store[recipient]
        return True
    return False


# ── Notification emails ────────────────────────────────────────────────────────

def send_welcome_email(username: str, email: str):
    body = f"""Dear {username}, 

Welcome to Online Quiz Competition!

Your account has been successfully created.

Username : {username}
Email    : {email}

Please keep your credentials confidential and do not share them with anyone.

Best Regards,
Support Team — Online Quiz
"""
    send_mail(email, "Welcome to Online Quiz Competition", body)

def send_password_reset_mail(email: str):
    body=f"""Dear User,

We wanted to let you know that your account password was successfully changed.

If you made this change, no further action is required.

If you did not change your password, please reset your password immediately and contact our support team as soon as possible to secure your account.

For security reasons, we recommend:

* Using a strong and unique password
* Never sharing your login credentials
* Enabling two-factor authentication if available

Thank you,
Online Quiz Competition support team

    """
    send_mail(email, "Your Password Was Changed", body)