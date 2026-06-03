# Database.py — All database connection and query logic.

import streamlit as st
import mysql.connector
from Config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


# ── Connection ─────────────────────────────────────────────────────────────────

'''@st.cache_resource
def get_db():
    """Return a single cached DB connection for the lifetime of the server."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )'''
@st.cache_resource
def get_db():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
    except Exception as e:
        st.error(f"MySQL Error: {e}")
        raise


def get_cursor():
    """Return a fresh cursor, reconnecting if the connection dropped."""
    db = get_db()
    db.ping(reconnect=True)
    return db.cursor()


# ── Schema bootstrap ───────────────────────────────────────────────────────────

def ensure_scores_table():
    db  = get_db()
    cur = get_cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            username      VARCHAR(150) NOT NULL,
            topic         VARCHAR(60)  NOT NULL,
            difficulty    ENUM('Easy','Medium','Hard') NOT NULL,
            score         TINYINT      NOT NULL,
            total         TINYINT      NOT NULL DEFAULT 15,
            time_taken_s  SMALLINT     NOT NULL,
            completed_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


# ── User queries ───────────────────────────────────────────────────────────────

def find_user_by_email(email: str):
    cur = get_cursor()
    cur.execute("SELECT * FROM signup WHERE mail = %s", (email,))
    return cur.fetchone()


def find_user_by_username(username: str):
    cur = get_cursor()
    cur.execute("SELECT * FROM signup WHERE user_deatails = %s", (username,))
    return cur.fetchone()


def find_email_by_identifier(identifier: str):
    cur = get_cursor()
    cur.execute("SELECT mail FROM signup WHERE mail = %s", (identifier,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("SELECT mail FROM signup WHERE user_deatails = %s", (identifier,))
    row = cur.fetchone()
    return row[0] if row else None


def authenticate_user(identifier: str, password: str) -> bool:
    cur = get_cursor()
    cur.execute(
        """SELECT 1 FROM signup
           WHERE (user_deatails = %s OR mail = %s)
             AND password_details = %s""",
        (identifier, identifier, password),
    )
    return cur.fetchone() is not None


def create_user(username: str, email: str, password: str):
    db  = get_db()
    cur = get_cursor()
    cur.execute(
        "INSERT INTO signup(user_deatails, mail, password_details) VALUES (%s, %s, %s)",
        (username, email, password),
    )
    db.commit()


def update_password(email: str, new_password: str):
    db  = get_db()
    cur = get_cursor()
    cur.execute(
        "UPDATE signup SET password_details = %s WHERE mail = %s",
        (new_password, email),
    )
    db.commit()


# ── Quiz question queries ──────────────────────────────────────────────────────

VALID_TOPICS = {"ai", "python", "java", "web_development", "cpp", "ethical_hacking"}


def fetch_random_questions(topic: str, difficulty: str, n: int = 15) -> list:
    if topic not in VALID_TOPICS:
        raise ValueError(f"Unknown topic: {topic}")
    cur = get_cursor()
    cur.execute(
        f"""SELECT id, difficulty, question,
                   option_a, option_b, option_c, option_d,
                   correct_answer, explanation
            FROM `{topic}`
            WHERE difficulty = %s
            ORDER BY RAND()
            LIMIT %s""",
        (difficulty, n),
    )
    cols = ["id","difficulty","question",
            "option_a","option_b","option_c","option_d",
            "correct_answer","explanation"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


# ── Score queries ──────────────────────────────────────────────────────────────

def save_score(username: str, topic: str, difficulty: str,
               score: int, total: int, time_taken_s: int):
    ensure_scores_table()
    db  = get_db()
    cur = get_cursor()
    cur.execute(
        """INSERT INTO quiz_scores
               (username, topic, difficulty, score, total, time_taken_s)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (username, topic, difficulty, score, total, time_taken_s),
    )
    db.commit()


def get_user_history(username: str) -> list:
    ensure_scores_table()
    cur = get_cursor()
    cur.execute(
        """SELECT topic, difficulty, score, total, time_taken_s, completed_at
           FROM quiz_scores
           WHERE username = %s
           ORDER BY completed_at DESC""",
        (username,),
    )
    cols = ["topic","difficulty","score","total","time_taken_s","completed_at"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def get_leaderboard(limit: int = 200) -> list:
    ensure_scores_table()
    cur = get_cursor()
    cur.execute(
        """SELECT username, topic, difficulty, score, total,
                  time_taken_s, completed_at
           FROM quiz_scores
           ORDER BY score DESC, time_taken_s ASC
           LIMIT %s""",
        (limit,),
    )
    cols = ["username","topic","difficulty","score","total","time_taken_s","completed_at"]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    return rows