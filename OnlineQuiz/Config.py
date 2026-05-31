# Config.py — Reads all secrets from .streamlit/secrets.toml (never committed).
# Safe to push to GitHub — zero credentials here.

import streamlit as st

# ── Database ───────────────────────────────────────────────────────────────────
DB_HOST     = st.secrets["database"]["host"]
DB_USER     = st.secrets["database"]["user"]
DB_PASSWORD = st.secrets["database"]["password"]
DB_NAME     = st.secrets["database"]["name"]

# ── Email ──────────────────────────────────────────────────────────────────────
SENDER_EMAIL        = st.secrets["email"]["sender_email"]
SENDER_APP_PASSWORD = st.secrets["email"]["app_password"]

# ── Password policy (not secret — safe here) ──────────────────────────────────
SPECIAL_CHARS = set("!@#$%^&*()_+?><:}{][")

# ── Quiz settings (not secret — safe here) ────────────────────────────────────
QUIZ_DURATION   = 5 * 60   # seconds
TOTAL_QUESTIONS = 15