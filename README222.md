# OrbitFeed

A photo-sharing social media web application built with **Flask**, **SQLAlchemy** and **Bootstrap 5**.
Users register, publish image posts, follow each other, like / save / comment on posts, and find people through a live search popup.

Developed individually for **COMP2011 – Web Application Development** (BSc Computer Science, University of Leeds).
The accompanying design and testing report is included in this repository: `COMP2011_Report.pdf`.

---

## Features

| Area | What is implemented |
|---|---|
| **Authentication** | Registration with unique-username validation and password confirmation; login with optional "remember me"; logout; `@login_required` protection with safe `next` redirect; passwords hashed with Werkzeug |
| **Posts** | Create a post with text and a JPG/PNG image (extension whitelist, 16 MB request limit, `secure_filename`); home feed ordered newest-first |
| **Social graph** | Follow / unfollow through a many-to-many `Follow` association table (composite primary key, indexed); follower and following counts returned as JSON |
| **Engagement** | Like / unlike and save / unsave toggles (JSON endpoints, composite-key tables with indexes); comment creation through a JSON endpoint; saved-posts list |
| **Profiles** | Public profile page with avatar, description and the user's posts; edit-profile endpoint (username, description, password, avatar upload) |
| **Search** | Live search popup (`fetch` to `/search?q=`) returning users by username (case-insensitive partial match) or hashtags when the query starts with `#`; closes on Escape or outside click |
| **Security** | CSRF protection on all forms and AJAX calls (`Flask-WTF` + `X-CSRFToken` header), HTTP-only / SameSite session cookies, secret key and database URL read from environment variables |
| **UI** | Responsive Bootstrap 5 layout, off-canvas navigation menu, comment modal, media-query breakpoints for small screens |

## Tech Stack

- **Backend:** Python, Flask 3, Flask-SQLAlchemy / SQLAlchemy 2, Flask-Login, Flask-WTF / WTForms, Flask-Migrate, Pillow
- **Database:** SQLite (default) – any SQLAlchemy URL via `DATABASE_URL`
- **Frontend:** Jinja2 templates, Bootstrap 5.3, Font Awesome 5, vanilla JavaScript + jQuery (AJAX)

## Data Model

```
User ──< Post ──< Comment
 │         ├──< Like   (post_id, user_id)  composite PK
 │         └──< Save   (post_id, user_id)  composite PK
 └──< Follow (follower_id, followed_id)    self-referential many-to-many
```

## Project Structure

```
OrbitFeed/
├── run.py                  # Entry point
├── config.py               # Security, database and upload settings
├── db_create.py            # Table-creation helper (see Setup)
├── requirements.txt
├── COMP2011_Report.pdf     # Design, implementation and testing report
└── app/
    ├── __init__.py         # App factory-style setup, CSRF, Login, Migrate
    ├── models.py           # User, Post, Comment, Like, Save, Follow
    ├── forms.py            # WTForms: register, login, post, profile, comment
    ├── views.py            # Routes and JSON endpoints
    ├── static/
    │   ├── css/            # sidebar, search, popup and post styles
    │   └── js/             # search, follow, like, save, comment, lazy-load
    └── templates/          # base, index, profile, post, create_post, login, register, ...
```

## Getting Started

```bash
git clone https://github.com/yeeheng12/WebApp2.git
cd WebApp2
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install Flask==3.0.3 Flask-SQLAlchemy==3.1.1 Flask-Login==0.6.3 Flask-WTF==1.2.2 \
            Flask-Migrate==4.0.7 Pillow
# (requirements.txt also lists optional packages that the current code does not import)

# create the database tables (SQLite file app.db)
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# optional but recommended
export SECRET_KEY="change-me"

python run.py          # http://127.0.0.1:5000
```

Place a `default_profile.png` in `app/static/images/default/` for the default avatar.

### Main Routes

| Route | Method | Purpose |
|---|---|---|
| `/register`, `/login`, `/logout` | GET/POST | Authentication |
| `/` | GET | Home feed |
| `/create_post` | GET/POST | New image post |
| `/profile/<username>` | GET | Profile page |
| `/edit_profile` | POST | Update profile |
| `/like/<id>`, `/save_toggle/<id>` | POST | JSON toggles |
| `/add_comment/<id>` | POST (JSON) | Add comment |
| `/follow_toggle/<user_id>` | POST | Follow / unfollow, returns counts |
| `/search?q=` | GET | User / hashtag search (JSON) |

## Testing

Testing for the coursework was **manual** (functional walkthroughs, input/validation checks and responsiveness checks across screen sizes); methodology and results are documented in the report. There is no automated test suite in this repository yet.

## Known Limitations & Future Work

This repository is the as-submitted coursework version. Known gaps I identified when reviewing it afterwards:

- **Profile page, saved-posts page, single-post view and "load more comments"** raise server errors with the pinned library versions (a list-vs-dynamic relationship mismatch, a missing `User.saves` relationship, removed `request.is_xhr`, and the pre-3.0 `paginate()` signature).
- **Front-end scripts are not loaded:** `base.html` has no `scripts` block, so the like, save, comment and follow JavaScript in `app/static/js/` is never included on pages. The `like.js` / `save.js` response keys also differ from the endpoints (`is_liked` vs `liked`).
- The home feed currently lists **all** posts rather than only followed users; hashtags are never extracted (`Post.set_tags()` is not called), so hashtag search returns no results.
- Registration enforces no minimum password length; no delete-post / delete-account routes; a custom 404 handler is not registered.
- Uploaded files keep their original filename (collisions possible); missing default image assets and `base.css`.
- `db_create.py` needs an application context (use the command above).

**Planned improvements:** fix the routes above, add followers/following list pages, hashtag extraction, unique upload names, pytest-based tests, and a production WSGI deployment.

## Author

**Loke Yee Heng** – BSc Computer Science, University of Leeds · [github.com/yeeheng12](https://github.com/yeeheng12)
