---
name: project_state
description: Current state of the Venuzle project — what's been implemented, what's pending
type: project
---

As of 2026-03-17, the following was implemented in one session:

**Scraper (venue_scraper_ajax.py):**
- Added `REGIONS` dict and `ACTIVE_REGIONS` list at the top of the file as the easy-to-find config
- `get_week_availability()` now loops over all `ACTIVE_REGIONS` per day, merging data
- `_extract_venues_from_ajax()` accepts `region_name` and tags each venue with it
- `_process_week_data()` handles multiple region entries per date (merges into same date key)
- Each venue entry in the JSON now has a `region` field (e.g. "Nord")
- `main()` passes `ACTIVE_REGIONS` to `get_week_availability()`
- `total_days` fixed to use `len(sorted_dates)` not `len(all_days_data)`

**Viewer (calendar_viewer.html):**
- Replaced table-based layout with CSS Gantt grid: `120px day label + 60 × 15-min columns (07:00–22:00)`
- Venue chips placed directly in grid with `grid-column: startCol / endCol` — duration is now visual
- `grid-auto-flow: dense` packs chips to top-left, no empty rows above
- Header shows fixed hour labels (7:00–21:00), sticky at top
- Day label column sticky left
- Rows start collapsed (46px), click day label to expand/collapse individual rows
- Header "Day" cell = "Expand All ▼" / "Collapse All ▲" toggle; updates reactively
- Region filter checkboxes (Nord/Ost/Süd/West), only shows regions present in data, default Nord
- Name filters: include regex + exclude regex (default exclude: "Gymnastik"), live on input, invalid regex turns input red
- `data-region` and `data-venue-name` attributes on each chip for filtering

**Pending (Todo.md):**
- Rating system (localStorage or venue_ratings.json)
- Calendar column layout: quickfix (round time_from to hour) or proper Gantt already done ✓
- Region filter + name filter: done ✓
