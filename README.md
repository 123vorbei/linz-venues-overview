# Venuzle Calendar Viewer

A venue calendar viewer for Stadt Linz booking system with automated daily scraping via GitHub Actions.

## GitHub Pages Setup

To publish this project on GitHub Pages:

1. **Go to your GitHub repository settings**
   - Navigate to: `Settings` → `Pages`

2. **Enable GitHub Pages**
   - Under "Build and deployment"
   - Select `Source`: `Deploy from a branch`
   - Select `Branch`: `main` with folder `/ (root)`
   - Click "Save"

3. **Your site will be live at**
   - `https://<YOUR_USERNAME>.github.io/<REPO_NAME>/`
   - Homepage: `https://<YOUR_USERNAME>.github.io/<REPO_NAME>/`
   - Direct viewer: `https://<YOUR_USERNAME>.github.io/<REPO_NAME>/calendar_viewer.html`

## GitHub Actions Scraper

The GitHub Actions workflow automatically runs the venue scraper and updates `venue_calendar.json` at:
- **7:00 UTC**
- **12:00 UTC**
- **18:00 UTC**
- **22:00 UTC**

### Workflow Features
- Automatically fetches latest venue availability
- Updates the calendar data
- Commits changes back to the repository
- Can be manually triggered via GitHub Actions UI

### Manual Trigger
To manually run the scraper:
1. Go to `Actions` tab in your GitHub repository
2. Select `Run Venue Scraper`
3. Click `Run workflow`

## Local Development

### Prerequisites
- Python 3.11+
- Dependencies: `requests`, `beautifulsoup4`

### Installation
```bash
pip install -r requirements.txt
```

### Running the Scraper
```bash
python venue_scraper_ajax.py
```

## Project Files

- `calendar_viewer.html` - Web-based calendar viewer
- `venue_scraper_ajax.py` - Scraper script to fetch venue availability
- `venue_calendar.json` - Scraped venue data (auto-updated)
- `.github/workflows/scraper.yml` - GitHub Actions configuration
