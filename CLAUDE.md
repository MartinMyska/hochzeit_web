# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
python manage.py runserver

# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test core

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations
```

## Architecture

This is a Django 6 wedding website (`hochzeit` = German for "wedding"). The project has a single Django app, `core`, which currently serves a coming-soon landing page.

- `hochzeit/` — project config: `settings.py`, root `urls.py`
- `core/` — the only app; `views.py` renders templates, `urls.py` wires routes
- `templates/core/` — HTML templates (global `templates/` dir, configured in `settings.py` `DIRS`)
- `db.sqlite3` — local SQLite database (no models defined yet)

URL routing: `hochzeit/urls.py` delegates everything except `/admin/` to `core/urls.py`, which currently only has the index route (`/`).

Templates are inline-styled (no separate CSS files or static assets yet). The color palette is warm cream/brown (`#fdf8f0`, `#4a3728`, `#8a6d5e`), and the font is Georgia serif.
