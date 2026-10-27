# Study Streak Coach

## Video Demo

<https://youtu.be/4XZ35gatrFI>

## Description

Study Streak Coach is a small Flask web application that helps a student turn regular study into a visible habit. The user records a study session by entering a subject, the number of minutes studied, a date, and an optional note. The dashboard then turns those records into simple, useful feedback: how much was studied today, during the current week, and in total; how many sessions have been logged; and the current consecutive-day study streak. The project is intended to be a lightweight personal tool rather than a large productivity system. It runs locally, stores its information in SQLite, and does not require an account, an internet service, or an API key.

The main dashboard is designed around the idea that a study habit is built from small wins. The log form makes recording a session quick, while the summary cards and seven-day bar chart provide an immediate sense of progress. A study streak counts consecutive dates with at least one session. If the user has not yet studied today, a streak that includes yesterday is still shown, so it can be continued during the current day. This avoids ending a streak at midnight before the user has a realistic chance to study.

The activity calendar is a conventional month view rather than a rolling list of dates. It starts weeks on Monday and includes the previous or next month’s days needed to complete the first and final rows. Those adjacent-month dates are faded so the selected month remains easy to read. Dates with a logged session are green, and the current date has a coral outline. Previous and next buttons change the displayed month, allowing the user to look back at earlier study patterns or ahead to future months. Viewing a different month does not change the dashboard statistics; those continue to describe the present day and week.

The History page provides a complete record of sessions, ordered from newest to oldest. Its note column wraps long descriptions rather than shortening them, which makes it suitable for reviewing what was learned. A session can also be removed from this page if it was entered by mistake. By contrast, the smaller “Recent sessions” component on the dashboard intentionally shortens long subjects and notes with an ellipsis. This keeps a single unusually long note from pushing the study duration outside the panel; the full text is still available by hovering over it.

## Files

`app.py` is the application’s Python entry point. It creates the Flask application, configures the SQLite database location, and creates the `sessions` table when the project first runs. It also contains the routes for the dashboard, adding a session, viewing history, and deleting a session. The helper functions calculate a study streak, generate full calendar weeks for a selected month, safely parse the `month` query parameter, and move between months. SQLite connections are stored per Flask request and closed automatically when the request finishes.

`templates/base.html` contains the shared page shell. It imports Bootstrap and the project stylesheet, defines the navigation bar, and shows temporary success or validation messages. `templates/index.html` is the dashboard template. It receives the statistics, bar-chart values, calendar data, recent sessions, and selected-month navigation from Flask and renders the study form and dashboard panels. `templates/history.html` renders the table of all saved sessions and provides the delete button for each record.

`static/styles.css` provides the visual design on top of Bootstrap’s responsive grid and form controls. It defines the color palette, typography, panels, dashboard cards, bar chart, responsive calendar, history table, and mobile adjustments. Bootstrap was used for dependable responsive layout, accessible controls, and alert behavior, while custom CSS gives the application its own quiet green-and-cream appearance.

`requirements.txt` lists Flask as the only required third-party Python package. `test_app.py` contains automated tests using Python’s built-in `unittest` module and Flask’s test client. The tests verify that the dashboard loads, a calendar month contains appropriate adjacent-month days and navigation links, a session can be added and deleted, and a long note is fully returned on the History page. The SQLite database file, `study_streak.db`, is generated automatically at runtime and is deliberately not source code that needs to be created by hand.

## Design choices

I chose SQLite because the app has one local user and a small, structured set of records. It keeps installation simple and demonstrates database operations without adding a separate database server. The data model is intentionally one table: each row represents one study session with its date, duration, subject, note, and creation time. Multiple sessions on the same date are supported, while streak and calendar calculations work with the distinct set of study dates. This means the user can log separate subjects in a day without artificially increasing the streak.

I also chose not to implement registration, login, notifications, or external calendar integrations. Those features would add complexity but would not improve the core learning goal of this project: practicing Flask routing, templates, forms, validation, SQLite queries, and responsive presentation in a project that can be completed and understood independently. Validation rejects empty subjects, durations outside one to 1,440 minutes, invalid dates, and future study dates. The resulting scope is small enough to be reliable while still providing a complete, interactive study-tracking experience.

## Running the project

From the project directory, create and activate a virtual environment, install the requirements, and start Flask:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

Open the local address shown by Flask in a browser. On the first run, the app creates `study_streak.db` automatically. To run the automated checks, use `python3 -m unittest -v test_app.py` while the virtual environment is active.

## Creator

- GitHub username: [stillnurs](https://github.com/stillnurs)
- edX username: [stillnurs](https://profile.edx.org/u/stillnurs)
