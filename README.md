# The Daily Edit

A small, responsive Flask website with a home page, a news page, and a login
page.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/ in your browser. The main pages are:

- `/` — home page
- `/news` — latest stories
- `/login` — sign-in page UI

The login form is intentionally a front-end demo; user accounts and
authentication are not configured.