<img width="2560" height="1600" alt="Image" src="https://github.com/user-attachments/assets/bf4fe0f6-a536-4b2b-85a6-5e236b950e0e" />

# BenchMark — Hotel Competitive Analysis Tool

An automated competitive benchmarking tool for the hotel industry. It scrapes publicly visible OTA listings for competitor properties and scores each one across eight weighted criteria, giving revenue teams a fast, consistent way to see where they stand against the competition.

Built to replace a manual process — checking competitor amenities, ratings, and pricing signals by hand across multiple OTA sites — with a one-click benchmarking run.

## How it works

**1. Add Properties** — Enter your own hotel first, then add competitors. Paste a Booking.com and/or Expedia URL for each, and manually set Location Score (1–5) and Brand Tier.

**2. Scraping Data** — The tool opens each hotel's page in the background (Playwright), pulls the amenities/facilities text and guest rating, and shows live progress.

**3. Results & Export** — Every hotel is scored across 8 weighted factors and ranked. Scores and reasoning are editable inline before export. Download both an Amenities Checklist CSV and a full Scoring Matrix CSV.

## Scoring criteria

| Factor | Weight | How it's scored |
|---|---|---|
| Location | 5 | Manual entry (1–5) |
| Amenities | 4 | Auto-detected from scraped text — 0.5 pts per amenity found (max 5) |
| Ratings & Reviews | 5 | Average of Booking.com + Expedia guest ratings, auto-scraped |
| Brand Tier | 5 | Economy → Luxury, manually selected |
| Restaurant & Food | 3 | On-site restaurant / buffet / vending, auto-detected |
| Meeting Space | 3 | Business centre / meeting rooms / banquet, auto-detected |
| Parking | 4 | Free / charged / EV / street, auto-detected |
| Swimming Pool | 4 | Indoor / outdoor / heated / seasonal, auto-detected |

Each hotel's total is the sum of (score × weight) across all eight factors, and hotels are automatically ranked highest to lowest.

## Tech stack

**Backend:** Python, Flask, Playwright (headless Chromium)
**Frontend:** Vanilla HTML/CSS/JS (no framework — kept intentionally lightweight)
**Deployment:** Render

## Why these design choices

- **No framework on the frontend** — the tool is a 3-step wizard with editable tables; a build step wasn't worth the overhead for this scope.
- **In-memory job store** — scraping runs as a background job with a polling endpoint (`/api/status/<job_id>`) instead of blocking the request, since scraping 4-8 hotels can take a couple minutes.
- **Text-based amenity detection** — rather than fragile per-site CSS selectors for every amenity, the tool scrapes the full visible page text and keyword-matches against known amenity phrasing, which holds up better when OTA sites change their layout.

## Roadmap

- [ ] Agoda and Google Hotels as additional data sources (scraper functions exist, disabled pending reliability testing on OTA anti-bot behavior)
- [ ] Persistent storage for benchmarking history over time
- [ ] Configurable scoring weights per user

## Local setup

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for step-by-step local installation instructions.
