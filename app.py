from collections import defaultdict
from datetime import date, timedelta

from flask import Flask, render_template

app = Flask(__name__)


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
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    all_sessions = []
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
            max(8, round((item["minutes"] / max_minutes) * 100))
            if max_minutes > 0
            else 0
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


if __name__ == "__main__":
    app.run(debug=True)
