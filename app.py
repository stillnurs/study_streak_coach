import os
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta

from flask import Flask, flash, g, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get(
    "STUDY_DB", os.path.join(app.root_path, "study_streak.db")
)


def get_db():
    """Return one SQLite connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_date TEXT NOT NULL,
            minutes INTEGER NOT NULL CHECK (minutes > 0),
            subject TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


def day_streak(active_dates, today):
    """Count consecutive study days ending today or yesterday."""
    if not active_dates:
        return 0

    cursor = today if today in active_dates else today - timedelta(days=1)
    if cursor not in active_dates:
        return 0

    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def calendar_days(active_dates, today):
    """Build the last 35 days for a compact, Monday-first activity grid."""
    start = today - timedelta(days=34)
    start -= timedelta(days=start.weekday())
    return [
        {
            "date": start + timedelta(days=offset),
            "active": start + timedelta(days=offset) in active_dates,
        }
        for offset in range(35)
    ]


@app.route("/")
def index():
    db = get_db()
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    all_sessions = db.execute(
        "SELECT id, study_date, minutes, subject, note FROM sessions "
        "ORDER BY study_date DESC, id DESC"
    ).fetchall()
    active_dates = {date.fromisoformat(row["study_date"]) for row in all_sessions}
    today_minutes = sum(
        row["minutes"] for row in all_sessions if row["study_date"] == today.isoformat()
    )
    week_minutes = sum(
        row["minutes"]
        for row in all_sessions
        if week_start <= date.fromisoformat(row["study_date"]) <= today
    )

    weekly_totals = defaultdict(int)
    for row in all_sessions:
        session_day = date.fromisoformat(row["study_date"])
        if today - timedelta(days=6) <= session_day <= today:
            weekly_totals[session_day] += row["minutes"]

    week_chart = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        week_chart.append({"label": day.strftime("%a"), "minutes": weekly_totals[day]})
    max_minutes = max((item["minutes"] for item in week_chart), default=0)
    for item in week_chart:
        item["height"] = (
            max(8, round((item["minutes"] / max_minutes) * 100)) if max_minutes else 8
        )

    return render_template(
        "index.html",
        today=today,
        today_minutes=today_minutes,
        week_minutes=week_minutes,
        total_minutes=sum(row["minutes"] for row in all_sessions),
        total_sessions=len(all_sessions),
        streak=day_streak(active_dates, today),
        recent_sessions=all_sessions[:5],
        calendar=calendar_days(active_dates, today),
        week_chart=week_chart,
    )


@app.route("/add", methods=["POST"])
def add_session():
    try:
        study_date = datetime.strptime(
            request.form.get("study_date", ""), "%Y-%m-%d"
        ).date()
        minutes = int(request.form.get("minutes", ""))
    except (TypeError, ValueError):
        flash("Choose a valid date and number of minutes.", "danger")
        return redirect(url_for("index"))

    subject = request.form.get("subject", "").strip()
    note = request.form.get("note", "").strip()
    if not subject or not 1 <= minutes <= 1440:
        flash("Add a subject and enter between 1 and 1,440 minutes.", "danger")
    elif study_date > date.today():
        flash("A study session cannot be in the future.", "danger")
    else:
        get_db().execute(
            "INSERT INTO sessions (study_date, minutes, subject, note) VALUES (?, ?, ?, ?)",
            (study_date.isoformat(), minutes, subject, note or None),
        )
        get_db().commit()
        flash("Study session added — nice work!", "success")
    return redirect(url_for("index"))


@app.route("/history")
def history():
    sessions = (
        get_db()
        .execute(
            "SELECT id, study_date, minutes, subject, note FROM sessions "
            "ORDER BY study_date DESC, id DESC"
        )
        .fetchall()
    )
    return render_template("history.html", sessions=sessions)


@app.route("/delete/<int:session_id>", methods=["POST"])
def delete_session(session_id):
    db = get_db()
    db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    db.commit()
    flash("Session removed.", "secondary")
    return redirect(request.referrer or url_for("history"))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
