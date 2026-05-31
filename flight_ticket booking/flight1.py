import streamlit as st
import pandas as pd
import smtplib
import secrets
import time
import random
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Air Journey",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:          #F3EFE6;
  --card:        #FFFDF8;
  --muted:       #6B5E50;
  --text:        #2B2218;
  --accent:      #C4622D;
  --accent-dark: #9D4D22;
  --line:        #D6C9B8;
  --success:     #3A7D44;
  --error:       #B53B3B;
}

.stApp { background: var(--bg) !important; }
[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden; }

.nav-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0 10px; border-bottom: 1.5px solid var(--line); margin-bottom: 28px;
}
.nav-logo {
  font-family: 'Cormorant Garamond', serif; font-size: 26px; font-weight: 700;
  color: var(--text); letter-spacing: 1px;
}
.nav-logo span { color: var(--accent); }
.nav-user {
  font-family: 'DM Sans', sans-serif; font-size: 13px; color: var(--muted);
  background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 5px 14px;
}

.aj-card {
  background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 32px 36px; margin-bottom: 20px; box-shadow: 0 2px 18px rgba(43,34,24,.06);
}
.aj-title {
  font-family: 'Cormorant Garamond', serif; font-size: 28px; font-weight: 700;
  color: var(--text); margin: 0 0 4px;
}
.aj-sub { font-family: 'DM Sans', sans-serif; font-size: 13px; color: var(--muted); margin: 0 0 22px; }

.stTextInput input, .stSelectbox select, .stNumberInput input {
  background: #fff !important; border: 1.5px solid var(--line) !important;
  border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
  font-size: 14px !important; color: var(--text) !important;
  padding: 10px 14px !important; transition: border-color .2s;
}
.stTextInput input:focus, .stSelectbox select:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(196,98,45,.12) !important;
}
label[data-baseweb] {
  font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
  font-weight: 600 !important; color: var(--text) !important;
}

.stButton > button {
  background: var(--accent) !important; color: #fff !important; border: none !important;
  border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important; font-size: 14px !important; padding: 10px 24px !important;
  transition: background .2s, transform .1s; cursor: pointer;
}
.stButton > button:hover { background: var(--accent-dark) !important; transform: translateY(-1px); }
.stButton > button:active { transform: translateY(0); }

.ghost .stButton > button {
  background: transparent !important; color: var(--accent-dark) !important;
  border: 1.5px solid var(--line) !important;
}
.ghost .stButton > button:hover { background: var(--bg) !important; border-color: var(--accent) !important; }

.stWarning { border-left: 4px solid #C8921A !important; border-radius: 8px !important; }
.stError   { border-left: 4px solid var(--error) !important; border-radius: 8px !important; }

.fare-row {
  display: flex; justify-content: space-between; font-family: 'DM Sans', sans-serif;
  font-size: 14px; color: var(--text); padding: 6px 0; border-bottom: 1px solid var(--line);
}
.fare-row:last-child { border-bottom: none; }
.fare-total { font-weight: 700; font-size: 16px; color: var(--accent); }

.ticket-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.pnr-badge {
  background: var(--accent); color: #fff; font-family: 'DM Sans', sans-serif;
  font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 20px; letter-spacing: 1px;
}
.route-display {
  font-family: 'Cormorant Garamond', serif; font-size: 24px; font-weight: 600;
  color: var(--text); text-align: center; padding: 16px 0; letter-spacing: 1px;
}
.route-arrow { color: var(--accent); margin: 0 10px; }
.pax-item {
  font-family: 'DM Sans', sans-serif; font-size: 13px; color: var(--text);
  padding: 8px 12px; background: var(--bg); border-radius: 6px; margin-bottom: 6px;
}
.step-indicator { display: flex; gap: 8px; margin-bottom: 24px; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--line); }
.step-dot.active { background: var(--accent); }
.step-dot.done   { background: var(--success); }
.divider { border: none; border-top: 1px solid var(--line); margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  EXCEL FILE PATHS  (same as original tkinter)
# ─────────────────────────────────────────────
DETAILS_PATH = Path("details.xlsx")
BOOKING_PATH = Path("booking.xlsx")
TICKETS_PATH = Path("tickets.xlsx")

DETAILS_COLS = ["user", "mobile", "mail", "password"]
BOOKING_COLS = ["From Airport", "To Airport", "Flight1", "Business1", "Economy1", "Flight2", "Business2", "Economy2"]
TICKET_COLS  = ["Mobile", "From", "To", "Passenger", "Aadhaar", "SeatType",
                "TicketPrice", "WindowPrice", "MealPrice", "DrinkPrice", "Total", "Date", "PaymentMode"]

# ─────────────────────────────────────────────
#  EXCEL HELPERS
# ─────────────────────────────────────────────
def load_sheet(path: Path, columns: list) -> pd.DataFrame:
    if path.exists():
        try:
            df = pd.read_excel(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]
        except Exception:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_sheet(df: pd.DataFrame, path: Path):
    df.to_excel(path, index=False)

# ─────────────────────────────────────────────
#  CACHED LOADERS  (reload on every rerun)
# ─────────────────────────────────────────────
def get_details() -> pd.DataFrame:
    return load_sheet(DETAILS_PATH, DETAILS_COLS)

def get_booking() -> pd.DataFrame:
    return load_sheet(BOOKING_PATH, BOOKING_COLS)

def get_tickets() -> pd.DataFrame:
    return load_sheet(TICKETS_PATH, TICKET_COLS)

# ─────────────────────────────────────────────
#  E-MAIL / OTP
# ─────────────────────────────────────────────
SENDER_EMAIL = "onlinequizcompition@gmail.com"
SENDER_PASS  = "vonbjkvtreecktva"

def send_mail(to_addr: str, subject: str, body: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = to_addr
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.sendmail(SENDER_EMAIL, to_addr, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Mail error: {e}")
        return False

def generate_and_send_otp(email: str) -> bool:
    otp = str(secrets.randbelow(900000) + 100000)
    st.session_state["otp_value"]   = otp
    st.session_state["otp_email"]   = email
    st.session_state["otp_expires"] = time.time() + 60
    body = f"""Dear Customer,

Greetings from Air Journey.

Your One-Time Password (OTP) for verification is:

OTP: {otp}

This OTP is valid for the next 60 seconds.
Please do not share this OTP with anyone.

Thank you,
Air Journey
"""
    return send_mail(email, "Your OTP Verification Code", body)

def otp_still_valid() -> bool:
    return time.time() < st.session_state.get("otp_expires", 0)

def verify_otp(entered: str) -> str:
    """Returns 'verified' | 'expired' | 'invalid'"""
    if not otp_still_valid():
        return "expired"
    if entered == st.session_state.get("otp_value"):
        st.session_state["email_verified"] = True
        st.session_state["otp_value"]      = None
        return "verified"
    return "invalid"

# ─────────────────────────────────────────────
#  VALIDATION
# ─────────────────────────────────────────────
def validate_password(pwd: str):
    if not any(c.isupper() for c in pwd):
        return "Password must contain at least one UPPERCASE letter."
    if not any(c.isdigit() for c in pwd):
        return "Password must contain at least one digit."
    if not any(c in "!@#$%^&*()_+?><:}{][" for c in pwd):
        return "Password must contain at least one special character."
    return None

def validate_mobile(mob: str) -> bool:
    return mob.isdigit() and len(mob) == 10 and mob[0] in "6789"

def validate_email(mail: str) -> bool:
    return "@" in mail and " " not in mail and mail.lower().endswith(".com")

# ─────────────────────────────────────────────
#  USER DATA HELPERS  (Excel-backed)
# ─────────────────────────────────────────────
def email_exists(email: str) -> bool:
    df = get_details()
    return email.lower() in df["mail"].astype(str).str.lower().tolist()

def mobile_exists(mobile: str) -> bool:
    df = get_details()
    return mobile in df["mobile"].astype(str).tolist()

def username_exists(username: str) -> bool:
    df = get_details()
    return username in df["user"].astype(str).tolist()

def get_user_by_login(identifier: str):
    """Returns matching row Series or None — checks username, mobile, email."""
    df = get_details()
    identifier = identifier.strip()
    mask = (
        (df["mail"].astype(str).str.lower() == identifier.lower()) |
        (df["mobile"].astype(str) == identifier) |
        (df["user"].astype(str) == identifier)
    )
    match = df[mask]
    return match.iloc[0] if not match.empty else None

def insert_user(username: str, mobile: str, email: str, password: str):
    df = get_details()
    df.loc[len(df)] = [username, int(mobile), email.lower(), password]
    save_sheet(df, DETAILS_PATH)

def update_password(email: str, new_password: str):
    df = get_details()
    df.loc[df["mail"].astype(str).str.lower() == email.lower(), "password"] = new_password
    save_sheet(df, DETAILS_PATH)

def append_ticket(row: dict):
    df = get_tickets()
    df.loc[len(df)] = [
        row["Mobile"], row["From"], row["To"], row["Passenger"], row["Aadhaar"],
        row["SeatType"], row["TicketPrice"], row["WindowPrice"],
        row["MealPrice"], row["DrinkPrice"], row["Total"], row["Date"], row["PaymentMode"],
    ]
    save_sheet(df, TICKETS_PATH)

def get_user_tickets(mobile: str) -> pd.DataFrame:
    df = get_tickets()
    return df[df["Mobile"].astype(str) == str(mobile)]

# ─────────────────────────────────────────────
#  SESSION DEFAULTS
# ─────────────────────────────────────────────
defaults = {
    "page": "login",
    "email_verified": False,
    "otp_value": None,
    "otp_email": None,
    "otp_expires": 0,
    "otp_sent": False,
    "logged_in_user": None,
    "logged_in_mobile": None,
    "fp_otp_sent": False,
    "fp_email_verified": False,
    # booking flow
    "booking_step": 1,
    "selected_from": None,
    "selected_to": None,
    "selected_flight": None,
    "selected_class": "Economy",
    "num_passengers": 1,
    "flight_row": None,
    "passengers": [],
    "meal": False,
    "drink": False,
    "base_fare": 0,
    "total": 0,
    "pay_mode": "UPI",
    "pnr": None,
    "issued_on": None,
    "view_tickets": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def nav(page: str):
    st.session_state["page"] = page
    st.rerun()

def logo_bar(show_user=False):
    user_html = (
        f'<span class="nav-user">✈ {st.session_state["logged_in_user"]}</span>'
        if show_user else ""
    )
    st.markdown(f"""
    <div class="nav-bar">
      <div class="nav-logo">AIR<span>JOURNEY</span></div>
      {user_html}
    </div>""", unsafe_allow_html=True)

def step_dots(active: int, total_steps: int = 5):
    dots = "".join(
        f'<div class="step-dot {"active" if i == active else "done" if i < active else ""}"></div>'
        for i in range(1, total_steps + 1)
    )
    st.markdown(f'<div class="step-indicator">{dots}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: LOGIN
# ─────────────────────────────────────────────
def page_login():
    logo_bar()
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Welcome Back</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">Sign in with your username, mobile or email</p>', unsafe_allow_html=True)

    identifier = st.text_input("Username / Mobile / Email", key="login_id")
    password   = st.text_input("Password", type="password", key="login_pw")

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        login_btn = st.button("Login", use_container_width=True)
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        signup_btn = st.button("Sign Up", use_container_width=True, key="go_signup")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        forgot_btn = st.button("Forgot Password?", use_container_width=True, key="go_forgot")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if login_btn:
        if not identifier or not password:
            st.warning("Please fill all fields.")
        else:
            row = get_user_by_login(identifier.strip())
            if row is None:
                st.error("No account found. Please sign up first.")
            elif row["password"] != password:
                st.error("Incorrect password.")
            else:
                st.session_state["logged_in_user"]   = row["user"]
                st.session_state["logged_in_mobile"] = str(row["mobile"])
                st.session_state["page"] = "booking"
                st.rerun()
    if signup_btn:
        nav("register")
    if forgot_btn:
        nav("forgot")

# ─────────────────────────────────────────────
#  PAGE: REGISTER
# ─────────────────────────────────────────────
def page_register():
    logo_bar()
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Create Account</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">Start booking your next air journey</p>', unsafe_allow_html=True)

    username = st.text_input("Username", key="reg_user")
    mobile   = st.text_input("Mobile Number", key="reg_mob")
    email    = st.text_input("Email ID", key="reg_mail")

    # OTP block
    if not st.session_state["email_verified"]:
        c1, c2 = st.columns([3, 2])
        with c2:
            if st.button("Send OTP", key="send_otp_btn"):
                if not email or not validate_email(email):
                    st.warning("Enter a valid email first.")
                elif email_exists(email):
                    st.warning("This email is already registered.")
                else:
                    if generate_and_send_otp(email):
                        st.session_state["otp_sent"] = True
                        st.success("OTP sent! Check your inbox.")
                    else:
                        st.error("Failed to send OTP.")
        if st.session_state.get("otp_sent"):
            otp_input = st.text_input("Enter OTP", key="reg_otp", max_chars=6)
            if st.button("Verify OTP", key="verify_otp_btn"):
                result_v = verify_otp(otp_input.strip())
                if result_v == "verified":
                    st.success("Email verified ✓")
                    st.rerun()
                elif result_v == "expired":
                    st.error("OTP expired. Please resend.")
                else:
                    st.error("Incorrect OTP.")
    else:
        st.success("✓ Email verified")

    password = st.text_input("Create Password", type="password", key="reg_pw")
    confirm  = st.text_input("Confirm Password", type="password", key="reg_con")

    col1, col2 = st.columns([2, 2])
    with col1:
        submit = st.button("Register", use_container_width=True)
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True, key="back_login"):
            st.session_state["email_verified"] = False
            st.session_state["otp_sent"] = False
            nav("login")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        errs = []
        if not all([username, mobile, email, password, confirm]):
            errs.append("Please fill all fields.")
        if mobile and not validate_mobile(mobile):
            errs.append("Enter a valid 10-digit mobile number starting with 6–9.")
        if email and not validate_email(email):
            errs.append("Enter a valid email address (must contain @ and end with .com).")
        if not st.session_state["email_verified"]:
            errs.append("Please verify your email with OTP.")
        pw_err = validate_password(password) if password else "Password is required."
        if pw_err:
            errs.append(pw_err)
        if password and confirm and password != confirm:
            errs.append("Passwords do not match.")
        if username and username_exists(username):
            errs.append("Username already taken.")
        if mobile and mobile_exists(mobile):
            errs.append("Mobile number already registered.")
        if email and email_exists(email):
            errs.append("Email already registered.")

        if errs:
            for e in errs:
                st.warning(e)
        else:
            insert_user(username, mobile, email, password)
            st.session_state["email_verified"] = False
            st.session_state["otp_sent"] = False
            st.success("Account created successfully! Please login.")
            time.sleep(1.5)
            nav("login")

# ─────────────────────────────────────────────
#  PAGE: FORGOT PASSWORD
# ─────────────────────────────────────────────
def page_forgot():
    logo_bar()
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Reset Password</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">Verify your email to set a new password</p>', unsafe_allow_html=True)

    fp_email = st.text_input("Registered Email", key="fp_email")

    if not st.session_state["fp_email_verified"]:
        c1, c2 = st.columns([3, 2])
        with c2:
            if st.button("Send OTP", key="fp_send_otp"):
                if not fp_email or not validate_email(fp_email):
                    st.warning("Enter a valid email.")
                elif not email_exists(fp_email):
                    st.error("No account found with this email.")
                else:
                    if generate_and_send_otp(fp_email):
                        st.session_state["fp_otp_sent"] = True
                        st.success("OTP sent!")
        if st.session_state.get("fp_otp_sent"):
            otp_in = st.text_input("Enter OTP", key="fp_otp_in", max_chars=6)
            if st.button("Verify OTP", key="fp_verify_btn"):
                r = verify_otp(otp_in.strip())
                if r == "verified":
                    st.session_state["fp_email_verified"] = True
                    st.success("Identity verified ✓")
                    st.rerun()
                elif r == "expired":
                    st.error("OTP expired. Please resend.")
                else:
                    st.error("Incorrect OTP.")
    else:
        st.success("✓ Identity verified")
        new_pw  = st.text_input("New Password", type="password", key="fp_new")
        conf_pw = st.text_input("Confirm Password", type="password", key="fp_conf")
        if st.button("Update Password", use_container_width=True):
            err = validate_password(new_pw)
            if err:
                st.warning(err)
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                update_password(fp_email, new_pw)
                st.session_state["fp_otp_sent"]       = False
                st.session_state["fp_email_verified"] = False
                st.success("Password updated! Redirecting to login…")
                time.sleep(1.5)
                nav("login")

    st.markdown('<div class="ghost" style="margin-top:14px">', unsafe_allow_html=True)
    if st.button("← Back to Login", key="fp_back"):
        st.session_state["fp_otp_sent"]       = False
        st.session_state["fp_email_verified"] = False
        nav("login")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BOOKING FLOW ROUTER
# ─────────────────────────────────────────────
def page_booking():
    logo_bar(show_user=True)
    if st.session_state["view_tickets"]:
        show_my_tickets()
        return
    step = st.session_state["booking_step"]
    if   step == 1: booking_step1_route()
    elif step == 2: booking_step2_flight()
    elif step == 3: booking_step3_passengers()
    elif step == 4: booking_step4_payment()
    elif step == 5: booking_step5_ticket()

# ── Step 1: Route ────────────────────────────
def booking_step1_route():
    step_dots(1)
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Book a Flight</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">Choose your origin and destination</p>', unsafe_allow_html=True)

    booking = get_booking()
    if booking.empty:
        st.info("No flight routes found in booking.xlsx. Please add routes and rerun.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    airports = sorted(set(booking["From Airport"].tolist() + booking["To Airport"].tolist()))
    from_ap  = st.selectbox("From", airports, key="sel_from")
    to_ap    = st.selectbox("To",   airports, key="sel_to")

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        search = st.button("Show Flights", use_container_width=True)
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("My Tickets", use_container_width=True, key="btn_my_tickets"):
            st.session_state["view_tickets"] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True, key="btn_logout"):
            for k, v in defaults.items():
                st.session_state[k] = v
            nav("login")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if search:
        if from_ap == to_ap:
            st.warning("Source and destination cannot be the same.")
        else:
            result = booking[
                (booking["From Airport"] == from_ap) &
                (booking["To Airport"]   == to_ap)
            ]
            if result.empty:
                st.error("This route is not available.")
            else:
                st.session_state["selected_from"] = from_ap
                st.session_state["selected_to"]   = to_ap
                st.session_state["flight_row"]    = result.iloc[0].to_dict()
                st.session_state["booking_step"]  = 2
                st.rerun()

# ── Step 2: Choose Flight ────────────────────
def booking_step2_flight():
    step_dots(2)
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Available Flights</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="aj-sub">{st.session_state["selected_from"]} → {st.session_state["selected_to"]}</p>',
        unsafe_allow_html=True
    )

    row     = st.session_state["flight_row"]
    flights = [f for f in [row.get("Flight1"), row.get("Flight2")] if pd.notna(f) and str(f).strip()]
    flight  = st.selectbox("Choose Flight", flights, key="sel_flight")
    num_p   = st.selectbox("Number of Passengers", [1, 2, 3], key="sel_num_p")

    col1, col2 = st.columns([2, 2])
    with col1:
        nxt = st.button("Next →", use_container_width=True)
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="b2_back"):
            st.session_state["booking_step"] = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if nxt:
        st.session_state["selected_flight"] = flight
        st.session_state["num_passengers"]  = num_p
        st.session_state["passengers"]      = [
            {"name": "", "aadhaar": "", "window": False} for _ in range(num_p)
        ]
        st.session_state["booking_step"] = 3
        st.rerun()

# ── Step 3: Passengers ───────────────────────
def booking_step3_passengers():
    step_dots(3)
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Passenger Details</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">Enter details for all travellers</p>', unsafe_allow_html=True)

    seat_class = st.radio("Seat Type", ["Economy", "Business"], horizontal=True, key="sel_class")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    num_p = st.session_state["num_passengers"]
    names, aadhaars, windows = [], [], []

    for i in range(num_p):
        st.markdown(f"**Passenger {i + 1}**")
        n = st.text_input("Full Name",                    key=f"pax_name_{i}")
        a = st.text_input("Aadhaar Number (12 digits)",   key=f"pax_aad_{i}", max_chars=12)
        w = st.checkbox("Window Seat (+$7)",               key=f"pax_win_{i}")
        names.append(n); aadhaars.append(a); windows.append(w)
        if i < num_p - 1:
            st.markdown('<hr style="border-top:1px dashed #D6C9B8;margin:12px 0">', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**Dining Options**")
    meal  = st.checkbox("Meal (+$25 per person)",   key="sel_meal")
    drink = st.checkbox("Drinks (+$15 per person)", key="sel_drink")

    col1, col2 = st.columns([2, 2])
    with col1:
        confirm = st.button("Next →", use_container_width=True, key="b3_next")
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="b3_back"):
            st.session_state["booking_step"] = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if confirm:
        errs = []
        if any(n.strip() == "" for n in names):
            errs.append("Enter all passenger names.")
        if any(a.strip() == "" for a in aadhaars):
            errs.append("Enter all Aadhaar numbers.")
        elif any((not a.strip().isdigit()) or len(a.strip()) != 12 for a in aadhaars):
            errs.append("Aadhaar numbers must be exactly 12 digits.")
        elif len(set(a.strip() for a in aadhaars)) < num_p:
            errs.append("Aadhaar numbers must be unique across passengers.")
        if errs:
            for e in errs:
                st.warning(e)
        else:
            st.session_state["passengers"] = [
                {"name": names[i].strip(), "aadhaar": aadhaars[i].strip(), "window": windows[i]}
                for i in range(num_p)
            ]
            st.session_state["selected_class"] = seat_class
            st.session_state["meal"]           = meal
            st.session_state["drink"]          = drink
            st.session_state["booking_step"]   = 4
            st.rerun()

# ── Step 4: Payment ──────────────────────────
def booking_step4_payment():
    step_dots(4)
    row    = st.session_state["flight_row"]
    flight = st.session_state["selected_flight"]
    cls    = st.session_state["selected_class"]
    paxs   = st.session_state["passengers"]
    num_p  = len(paxs)
    meal   = st.session_state["meal"]
    drink  = st.session_state["drink"]

    # Fare calculation (mirrors original tkinter logic)
    if str(flight) == str(row.get("Flight1")):
        base = int(row.get(f"{cls}1", 0))
    else:
        base = int(row.get(f"{cls}2", 0))

    window_count = sum(1 for p in paxs if p["window"])
    meal_cost    = 25 * num_p if meal  else 0
    drink_cost   = 15 * num_p if drink else 0
    window_cost  = 7  * window_count
    total        = base * num_p + window_cost + meal_cost + drink_cost

    st.session_state["base_fare"] = base
    st.session_state["total"]     = total

    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">Payment</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">Review your fare before confirming</p>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:var(--bg);border-radius:10px;padding:18px 20px;margin-bottom:16px">
      <div class="fare-row"><span>Flight</span><span>{flight}</span></div>
      <div class="fare-row"><span>Route</span><span>{row['From Airport']} → {row['To Airport']}</span></div>
      <div class="fare-row"><span>Class</span><span>{cls}</span></div>
      <div class="fare-row"><span>Base Fare ({num_p} × ${base})</span><span>${base * num_p}</span></div>
      <div class="fare-row"><span>Window Seats ({window_count} × $7)</span><span>${window_cost}</span></div>
      <div class="fare-row"><span>Meals</span><span>${meal_cost}</span></div>
      <div class="fare-row"><span>Drinks</span><span>${drink_cost}</span></div>
      <div class="fare-row fare-total"><span>Total</span><span>${total}</span></div>
    </div>
    """, unsafe_allow_html=True)

    pay_mode   = st.radio("Payment Method", ["UPI", "Debit/Credit Card"], horizontal=True, key="sel_pay")
    pay_detail = st.text_input(
        "UPI ID" if pay_mode == "UPI" else "Card Number",
        key="pay_detail_input"
    )

    col1, col2 = st.columns([2, 2])
    with col1:
        confirm = st.button("Confirm Payment", use_container_width=True)
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True, key="b4_back"):
            st.session_state["booking_step"] = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if confirm:
        if not pay_detail.strip():
            st.warning("Please enter your payment details.")
        else:
            pnr    = f"AJ{random.randint(100000, 999999)}"
            issued = datetime.now().strftime("%d-%b-%Y %I:%M %p")
            st.session_state["pnr"]      = pnr
            st.session_state["issued_on"] = issued
            st.session_state["pay_mode"] = pay_mode

            # Save each passenger's ticket to tickets.xlsx
            mobile = st.session_state["logged_in_mobile"]
            for p in paxs:
                win_c = 7  if p["window"] else 0
                m_c   = 25 if meal        else 0
                d_c   = 15 if drink       else 0
                append_ticket({
                    "Mobile":      mobile,
                    "From":        row["From Airport"],
                    "To":          row["To Airport"],
                    "Passenger":   p["name"],
                    "Aadhaar":     p["aadhaar"],
                    "SeatType":    cls,
                    "TicketPrice": base,
                    "WindowPrice": win_c,
                    "MealPrice":   m_c,
                    "DrinkPrice":  d_c,
                    "Total":       base + win_c + m_c + d_c,
                    "Date":        issued,
                    "PaymentMode": pay_mode,
                })

            masked = (
                pay_detail.strip()
                if pay_mode == "UPI"
                else f"****{pay_detail.strip()[-4:]}"
            )
            st.success(f"Payment confirmed via {pay_mode}: {masked}")
            time.sleep(1)
            st.session_state["booking_step"] = 5
            st.rerun()

# ── Step 5: E-Ticket ─────────────────────────
def booking_step5_ticket():
    step_dots(5)
    paxs   = st.session_state["passengers"]
    row    = st.session_state["flight_row"]
    flight = st.session_state["selected_flight"]
    cls    = st.session_state["selected_class"]
    total  = st.session_state["total"]
    base   = st.session_state["base_fare"]
    pnr    = st.session_state["pnr"]
    issued = st.session_state["issued_on"]
    num_p  = len(paxs)
    meal   = st.session_state["meal"]
    drink  = st.session_state["drink"]
    window_count = sum(1 for p in paxs if p["window"])
    ml_cost = 25 * num_p if meal  else 0
    dk_cost = 15 * num_p if drink else 0

    st.markdown(f"""
    <div class="aj-card">
      <div class="ticket-header">
        <div>
          <p class="aj-title" style="margin-bottom:4px">E-Ticket</p>
          <p class="aj-sub" style="margin:0">Booking Confirmed ✓</p>
        </div>
        <span class="pnr-badge">PNR: {pnr}</span>
      </div>

      <div class="route-display">
        {row['From Airport']} <span class="route-arrow">✈</span> {row['To Airport']}
      </div>

      <div style="font-family:'DM Sans',sans-serif;font-size:13px;color:var(--muted);
                  text-align:center;margin-bottom:20px">
        {flight} &nbsp;|&nbsp; {cls} Class &nbsp;|&nbsp;
        {num_p} Passenger{'s' if num_p > 1 else ''}<br>
        Issued: {issued}
      </div>

      <hr class="divider">
      <p style="font-family:'DM Sans',sans-serif;font-weight:600;font-size:13px;
                color:var(--text);margin-bottom:10px">Passengers</p>
    """, unsafe_allow_html=True)

    for i, p in enumerate(paxs, 1):
        seat_label = "Window" if p["window"] else "Regular"
        masked_aad = "X" * 8 + p["aadhaar"][-4:]
        st.markdown(f"""
        <div class="pax-item">
          <strong>{i}. {p['name']}</strong>
          &nbsp;|&nbsp; Aadhaar: {masked_aad}
          &nbsp;|&nbsp; Seat: {seat_label}
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
      <hr class="divider">
      <p style="font-family:'DM Sans',sans-serif;font-weight:600;font-size:13px;
                color:var(--text);margin-bottom:10px">Fare Summary</p>
      <div class="fare-row"><span>Base Fare ({num_p} × ${base})</span><span>${base * num_p}</span></div>
      <div class="fare-row"><span>Window Seats ({window_count} × $7)</span><span>${window_count * 7}</span></div>
      <div class="fare-row"><span>Meals</span><span>${ml_cost}</span></div>
      <div class="fare-row"><span>Drinks</span><span>${dk_cost}</span></div>
      <div class="fare-row fare-total"><span>Total Paid</span><span>${total}</span></div>
      <div style="margin-top:12px;font-family:'DM Sans',sans-serif;font-size:13px;color:var(--muted)">
        Payment: {st.session_state['pay_mode']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        if st.button("✈ Book Another Ticket", use_container_width=True):
            for k in ["booking_step", "selected_from", "selected_to", "selected_flight",
                      "selected_class", "num_passengers", "flight_row", "passengers",
                      "meal", "drink", "base_fare", "total", "pnr", "issued_on"]:
                st.session_state[k] = defaults[k]
            st.session_state["booking_step"] = 1
            st.rerun()
    with col2:
        st.markdown('<div class="ghost">', unsafe_allow_html=True)
        if st.button("My Tickets", use_container_width=True, key="ticket5_my"):
            st.session_state["view_tickets"] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MY TICKETS
# ─────────────────────────────────────────────
def show_my_tickets():
    st.markdown('<div class="aj-card">', unsafe_allow_html=True)
    st.markdown('<p class="aj-title">My Tickets</p>', unsafe_allow_html=True)
    st.markdown('<p class="aj-sub">All your booked journeys</p>', unsafe_allow_html=True)

    mobile = st.session_state["logged_in_mobile"]
    df = get_user_tickets(mobile)

    if df.empty:
        st.info("You haven't booked any tickets yet.")
    else:
        st.dataframe(df.reset_index(drop=True), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="ghost">', unsafe_allow_html=True)
    if st.button("← Back to Booking", key="back_from_tickets"):
        st.session_state["view_tickets"] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
page = st.session_state["page"]
if   page == "login":    page_login()
elif page == "register": page_register()
elif page == "forgot":   page_forgot()
elif page == "booking":  page_booking()
else:                    nav("login")