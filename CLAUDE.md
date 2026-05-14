# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper (generates/updates venue_calendar.json)
python venue_scraper_ajax.py
```

No test suite exists. Open `calendar_viewer.html` directly in a browser (or via a local HTTP server) to test viewer changes — loading `venue_calendar.json` via the "Load Data" button requires HTTP, not `file://`.

## Architecture

This project has two independent parts:

**Scraper (`venue_scraper_ajax.py`)** — fetches venue availability from `book.venuzle.at/stadt-linz/venues` and writes `venue_calendar.json`.
- Region configuration is at the top of the file: `REGIONS` dict and `ACTIVE_REGIONS` list (default `[6]` = Nord).
- `get_week_availability()` loops over `ACTIVE_REGIONS` and days, calling `get_day_availability()` per region per day.
- `_extract_venues_from_ajax()` parses the HTML table response; each `<tr>` is one venue, each `<td class="slot">` is a time block. colspan encodes duration in 5-minute units.
- `_process_week_data()` merges all per-region/per-day data into a single `calendar_grid` keyed by date, then by time.
- Each venue entry in the output carries a `region` field (e.g. `"Nord"`).

**Viewer (`calendar_viewer.html`)** — a self-contained single-page app with no build step.
- Loads `venue_calendar.json` via `fetch()` (requires HTTP) or a file picker.
- Renders a day × time grid where rows = days, columns = time slots, cells = venue chips.
- `renderCalendar()` builds the DOM; `createVenueSlot()` creates individual venue chips with `data-region` and status CSS classes.
- `applyFilters()` toggles `.filtered-out` on chips based on the status checkboxes and the region checkboxes (Nord/Ost/Süd/West).
- `initializeFilters()` hides region checkboxes for regions not present in the loaded data; defaults Nord checked.

**Data flow:** scraper → `venue_calendar.json` → viewer. The JSON structure is:
```
{
  calendar_grid: { "YYYYMMDD": { slots_by_time: { "HH:MM": [ {venue_id, venue_name, region, status, ...} ] } } },
  sorted_dates: [...],
  sorted_times: [...],
  all_days_data: [...]   // raw per-region-per-day responses
}
```

**Deployment:** GitHub Actions (`.github/workflows/scraper.yml`) runs the scraper at 6:00 and 18:00 UTC, commits `venue_calendar.json` to `main`, and GitHub Pages serves the viewer from the repo root.
