# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
python manage.py runserver

# Run all tests
python manage.py test core

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Create admin superuser (needed once per fresh DB)
python manage.py createsuperuser

# Wipe all data (keeps table structure, clears admin user too)
python manage.py flush

# Verify Django can locate a static file
python manage.py findstatic core/<filename>
```

## Architecture

Django 6.0.6 wedding website (`hochzeit` = German for "wedding"). Single app: `core`.

- `hochzeit/` — project config: `settings.py`, root `urls.py`
- `core/` — the only app; `views.py`, `models.py`, `admin.py`, `urls.py`
- `templates/core/` — HTML templates; all CSS is inline in each template file
- `core/static/core/` — static assets; served via `{% load static %}` / `{% static '...' %}`
  - `wax_seal_lilly_2.png` — wax seal used on gate and as favicon
  - `photos/o-nas/` — carousel photos for O nás section (JPG/PNG only; HEIC ignored)
  - `photos/misto-cinu/` — venue photos
- `static/css/` — directory exists but unused

URL routing: `hochzeit/urls.py` → `core/urls.py`:
- `/` → `views.index` (`index.html`)
- `/prijdeme/` → `views.rsvp` (`rsvp.html`)
- `/admin/` → Django admin (browse RSVP submissions)

## Page: index.html

### Gate layer
`#gate` — `position: fixed; z-index: 100`; two dark navy panels covering the full screen. Click swings them open via CSS `rotateY`. JS state machine: `idle → opening → done`. Second click or Enter/Esc/Space skips to `done`.

`#top-nav` and the Leaflet map both start hidden/uninitialised. `onGateOpened()` reveals the nav and triggers map init. Two flags (`leafletReady`, `gateOpened`) coordinate the map init to avoid a race condition between script load and gate open.

### Hero section
`.hero` — full-viewport (`min-height: 100vh`), background photo set via inline `style="background-image: url(...)"` (required for Django `{% static %}` to work). A `::before` overlay (`rgba(225, 238, 252, 0.55)`) keeps text readable. On wide landscape viewports (`min-width: 721px` + `min-aspect-ratio: 4/3`) the text shifts to the lower portion (`align-items: flex-end; padding-bottom: 20vh`) to avoid covering faces in the portrait photo.

### Scroll-model info page (`#main-page`)
Sections in order:

1. `.hero` — names, date, venue, countdown timer + background photo
2. `#o-nas` — split layout (carousel left, text right)
3. `#nas-mlyn` (Místo činu) — reversed split (text left, single photo right), `.section-alt` background
4. `.map-wrap` — Leaflet map, constrained to `.section-inner` width, shares `.section-alt` background + `padding-bottom`
5. `#harmonogram` — vertical dot-and-line timeline (placeholder times)
6. `#dress-code` — colour swatch circles with labels
7. `#ubytovani` — hotel card grid (placeholder cards)
8. `#prakticke-info` — info grid (Svědci, Parkování, Dary, Kontakt, Dogs friendly)
9. `.cta-section` — bottom "Přijdeme!" button

### Section layout system
- `.page-section` — `padding: 5rem 0` + `scroll-margin-top: 52px` (offsets sticky nav height)
- `.page-section.section-alt` — `background: rgba(193, 215, 238, 0.25)`
- `.section-inner` — `max-width: 1100px; margin: 0 auto; padding: 0 2rem`
- `.split-grid` / `.split-grid.reverse` — two-column CSS grid; `.reverse` sets `.split-img { order: 2 }`
- `.img-placeholder` — `background: #bdd0e4; aspect-ratio: 4/3` for sections still awaiting real photos

### O nás carousel
`views.index` reads `core/static/core/photos/o-nas/` at request time, filters to web-compatible extensions (JPG/PNG/GIF/WebP — HEIC silently skipped), passes sorted list as `o_nas_photos` to the template. The carousel auto-advances every 4.5 seconds; clicking the image advances manually. Portrait images (detected via `naturalHeight > naturalWidth` after load) switch to `object-fit: contain` to avoid cropping heads. Falls back to `.img-placeholder` if the folder is empty.

### Map
Leaflet.js + OpenStreetMap (no API key). CDN: `https://unpkg.com/leaflet@1.9.4/`. Venue pin: `49.598830, 16.929680` (Náš Mlýn / Ochozský Mlýn, Ochoz 18, 798 52 Ochoz). No popup — pin only.

## Page: rsvp.html

RSVP form at `/prijdeme/`. Submits via `fetch()` as JSON (not a standard form POST) because person cards are dynamically added/removed by JS, making indexed POST field names impractical.

- **Already-submitted guard** — on GET, if `request.session['rsvp_submitted']` is set, renders a "Přihláška odeslána" message instead of the form. Same session flag is checked on POST to silently no-op duplicate submissions.
- **Honeypot** — hidden `<input name="hp_name">` positioned off-screen. If the field has any value in the JSON payload, the view returns `{'ok': True}` without saving anything.
- **Per-person cards** — cloned from `<template id="person-tpl">`. "Dítě" toggle hides alcohol and shows age field. `renumber()` keeps indices correct after removals.
- **Accommodation** — radio (`accom_want`: `sleep`/`help`). "Help" reveals checkboxes (`chaticky`, `penzion`).
- **On success** — form hidden, `#rsvp-success` shown in its place. Session flag set server-side.

## Database models (`core/models.py`)

`RSVPSubmission` — one row per family:
- `accom_want` (CharField), `accom_pref` (comma-separated string), `song_request`, `message`, `submitted_at`

`Person` — multiple rows per submission (FK → `RSVPSubmission`):
- `name`, `is_child`, `age` (nullable), `diet` (comma-separated), `other_diet`, `alcohol` (comma-separated)

Admin registered in `core/admin.py`. `RSVPSubmissionAdmin` shows persons inline. Browse at `/admin/`.

## Design

- **Language:** Czech throughout
- **Colour palette:** background `#e1eefc`, main text `#1a2e4f` (navy), secondary `#3d5a80`, accent/hover `#577C97`
- **Section alt background:** `rgba(193, 215, 238, 0.25)`
- **Gate panels:** `#1a2e4f`, initials "V" / "M" at `rgba(225, 238, 252, 0.55)`
- **Dress code swatches:** Námořní `#1a2e4f`, Ocelová `#3d5a80`, Nebeská `#8ea9c1`, Retrorůžová `#d4aea8`, Krémová `#d4c5b0`

## Content

- **Couple:** Viola & Martin
- **Wedding date:** 31. 10. 2026, ceremony 12:30 CET
- **Venue:** Náš Mlýn (Ochozský Mlýn), Ochoz 18, 798 52 Ochoz

## Still to do

- **Content** — replace lorem ipsum in O nás + Místo činu; real Harmonogram times; real hotel cards in Ubytování
- **Photos** — convert HEIC files to JPG; add venue photos carousel to Místo činu; hotel photos
- **Email notification** — alert Martin when a new RSVP is submitted (without having to check admin)
- **Deployment** — server, domain, switch SQLite → PostgreSQL
