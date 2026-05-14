## Rating
I want a system with which I can input ratings / certain parameters for the halls we already used - is it too small, does it have windows, etc.

**Approach:** Store ratings in a separate `venue_ratings.json` file (keyed by `venue_id`) that lives alongside `venue_calendar.json`. This file is hand-edited / written by the viewer and never touched by the scraper.

**Schema:**
```json
{
  "86": {
    "name": "Robinsonschule - Turnsaal",
    "rating": 4,
    "size": "ok",
    "windows": true,
    "notes": "Good floor, bit loud"
  }
}
```

**Viewer changes:**
- On load, also `fetch('./venue_ratings.json')` (silently ignore 404 — file may not exist yet).
- In the tooltip, show the rating/notes if a record exists for that `venue_id`.
- Add an "Edit rating" button in the tooltip that opens a small inline form (rating 1–5, size dropdown: too small / ok / large, windows checkbox, free-text notes).
- On save, update the in-memory ratings object and offer a "Download ratings JSON" button (since GitHub Pages can't write files). User then replaces the file in the repo manually or via a commit.

**Alternative (simpler):** Skip the download step — just use `localStorage` so ratings persist in the browser across visits without needing a file at all. Downside: ratings are browser-local, not shared.

## Fix Viewer:
- pin the whole date column when scrolling horizontally (currently only expand/collapse all is pinned)
- reduce size of date column to minimum possible fitting text
    - when scrolling on mobile, maybe move text so the weekday abbreviation disappears and the column can shrink to gain some extra space (if gracefully possible)
- make the genaral column width wider so that the first ~12 letters of the venue name are displayed always (on Mobile theres only the first letter now, is seems to fit the whole width of the day tothe screen in landscape mode wich is not necessary)
    - maybe make width adjustable by zooming/dragging 2 fingers on the time axis

## Load Data automatically
execute the load data button automatically when loading the site

## filter display on mobile
now it is breaking lines wich is messy in portrait mode
either collapse the filters or make them scrollable/zoomable in one line
