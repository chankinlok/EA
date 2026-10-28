# Commonroom

A responsive Flask discussion forum demo with category feeds, search, sorting,
topic creation, and replies. The forum content is stored in memory and resets
when the app restarts. The original news and login demo pages are still
available.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/ in your browser. The main pages are:

- `/` — home page with a discussion feed
- `/forum` — full discussion forum, with category, search, and sort filters
- `/discussion/new` — create a discussion
- `/discussion/<id>` — discussion and replies
- `/news` — original news page
- `/login` — sign-in page UI

The login form is intentionally a front-end demo; user accounts and
authentication are not configured. Upvotes and saved posts are also browser
demo interactions and are not persisted.