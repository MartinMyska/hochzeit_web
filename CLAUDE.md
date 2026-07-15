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

# Verify Django can locate a static file
python manage.py findstatic core/<filename>
```

## Architecture

Django 6.0.6 wedding website (`hochzeit` = German for "wedding"). Single app: `core`.

- `hochzeit/` — project config: `settings.py`, root `urls.py`
- `core/` — the only app; `views.py` renders templates, `urls.py` wires routes
- `templates/core/` — HTML templates; all CSS is inline in each template file
- `core/static/core/` — static assets (images); served via `{% load static %}` / `{% static '...' %}`
- `static/css/` — directory exists but unused

URL routing: `hochzeit/urls.py` → `core/urls.py`:
- `/` → `views.index` (`index.html`)
- `/prijdeme/` → `views.rsvp` (`rsvp.html`)

## Page: index.html

### Gate layer
`#gate` — `position: fixed; z-index: 100`; two dark navy panels (`.gate-left`, `.gate-right`) covering the full screen. Click swings them open via CSS `rotateY`. A wax seal PNG (`.wax-seal`) is inside `.gate-left` at `right: 0`, straddling the center seam. JS state machine: `idle → opening → done`. Second click or Enter/Esc/Space skips to `done`.

The `#top-nav` (sticky nav bar) starts at `opacity: 0; pointer-events: none` and transitions to visible only when the gate finishes opening (`onGateOpened()` adds `.visible`). Similarly, Leaflet is loaded eagerly but the map is only initialized after the gate opens — two boolean flags (`leafletReady`, `gateOpened`) coordinate this to avoid a race condition.

### Scroll-model info page (`#main-page`)
Full-page scroll layout revealed once the gate is gone. Sections in order:

1. `.hero` — full-viewport (`min-height: 100vh`) with names, date, venue, countdown timer
2. `#o-nas` — split layout (image left, text right)
3. `#nas-mlyn` (Místo činu) — reversed split layout (text left, image right), venue address + date, `.section-alt` background
4. `.map-wrap` — Leaflet.js map (OpenStreetMap tiles), constrained to `.section-inner` width, shares `.section-alt` background with the section above plus `padding-bottom`
5. `#harmonogram` — vertical dot-and-line timeline
6. `#dress-code` — color swatch circles with labels
7. `#ubytovani` — hotel card grid (`.hotel-cards`)
8. `#prakticke-info` — 4-column info grid (Svědci, Parkování, Dary, Kontakt)
9. `.cta-section` — bottom "Přijdeme!" button

### Section layout system
- `.page-section` — base `padding: 5rem 0` + `scroll-margin-top: 52px` (offsets sticky nav)
- `.page-section.section-alt` — `background: rgba(193, 215, 238, 0.25)` (slightly darker tint for alternating sections)
- `.section-inner` — `max-width: 1100px; margin: 0 auto; padding: 0 2rem` (constrains content width)
- `.split-grid` — two-column CSS grid; `.split-grid.reverse` moves `.split-img` to `order: 2` so it visually appears on the right
- `.img-placeholder` — `background: #bdd0e4; aspect-ratio: 4/3` placeholder until real photos are added

### Map
Leaflet.js + OpenStreetMap (no API key). Loaded from `https://unpkg.com/leaflet@1.9.4/`. Venue pin: `49.59996165335355, 16.932577732762` (Ochoz 18, 798 52 Ochoz).

## Page: rsvp.html

RSVP form at `/prijdeme/`. POST handling not yet implemented — view only renders.

- **Per-person cards** — cloned from `<template id="person-tpl">` via JS. Each card has: name, optional child age, dietary pills, alcohol pills. "Dítě" toggle hides alcohol section and shows age field. First card's remove button is hidden; `renumber()` keeps indices and visibility correct after removals.
- **Accommodation** — radio toggle (`accom_want`: `sleep` / `help`). Selecting "help" reveals `#accom-options-wrap` with two checkbox options (`chaticky`, `penzion`).
- **Song request** and **message** — family-level free-text fields.
- Form uses `{% csrf_token %}`.

## Design

- **Language:** Czech throughout
- **Colour palette:** background `#e1eefc`, main text `#1a2e4f` (navy), secondary `#3d5a80`, accent/hover `#577C97`
- **Gate panels:** `#1a2e4f` (dark navy), initials "V" / "M" at `rgba(225, 238, 252, 0.55)`
- **Wax seal:** `core/static/core/wax_seal_lilly_2.png`
- **Section alt background:** `rgba(193, 215, 238, 0.25)` — used on Místo činu, Dress code, Praktické info, and the map wrap

## Database

SQLite for local development. No models defined yet. Plan to migrate to PostgreSQL for production.

## Content

- **Couple:** Viola & Martin
- **Wedding date:** 31. 10. 2026, ceremony 12:30 CET
- **Venue:** Náš Mlýn, Ochoz 18, 798 52 Ochoz

## Planned scope (not yet built)

- **RSVP backend** — Django model(s) to persist submissions; one submission covers a whole family group
- **Real photos** — replace `.img-placeholder` divs in O nás, Místo činu, hotel cards
- **Harmonogram** — replace placeholder timeline with graphical design
- **Dress code** — replace placeholder swatches with actual wedding colour palette
- **Ubytování** — replace placeholder hotel cards with real hotel names, photos, links
