"""
scraper.py — Human-like Playwright scraper for Booking.com and Expedia.
Extracts facilities text and guest rating from each hotel page.
"""

from playwright.sync_api import sync_playwright
import time
import random
import re


def human_delay(min_s=1.5, max_s=3.5):
    time.sleep(random.uniform(min_s, max_s))


def click_if_exists(page, selector, timeout=3000):
    try:
        el = page.wait_for_selector(selector, timeout=timeout)
        if el and el.is_visible():
            el.click()
            human_delay(0.8, 1.8)
            return True
    except Exception:
        pass
    return False


def extract_rating_from_text(text, max_scale=10):
    """Extract a numeric rating from arbitrary text, return as 0–5 scale."""
    numbers = re.findall(r'\b(\d+[.,]\d+|\d+)\b', text)
    for n in numbers:
        val = float(n.replace(',', '.'))
        if 5 < val <= 10:
            return round(val / 2, 2)
        if 0 < val <= 5:
            return round(val, 2)
    return None


# ──────────────────────────────────────────────
# BOOKING.COM SCRAPER
# ──────────────────────────────────────────────

def scrape_booking(url, page):
    result = {'facilities_text': '', 'rating': None, 'error': None, 'source': 'Booking.com'}
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=45000)
        human_delay(2, 4)

        # Dismiss cookie banners
        for sel in ['#onetrust-accept-btn-handler', 'button[aria-label*="accept" i]',
                    '[id*="accept-cookies"]', '.bui-button--accept']:
            click_if_exists(page, sel, 2000)

        # Scroll to load lazy content
        page.evaluate("window.scrollBy(0, 600)")
        human_delay(1, 2)

        # Try to expand full facilities list
        for sel in [
            'button[data-testid="show-all-facilities-button"]',
            'a[href*="#facilities"]',
            'button:text("Show all facilities")',
            'button:text("See all facilities")',
        ]:
            click_if_exists(page, sel, 2500)

        human_delay(1, 2)

        facilities_text = ''

        # Priority selectors for BDC facilities section
        for selector in [
            '[data-testid="property-section--facilities"]',
            '[data-testid="amenities-wrapper"]',
            '.hprt-table',
            '#facilities',
            '.facilitiesChecklist',
            '[class*="facilities"]',
            '[class*="amenities"]',
            '.hp_desc_main_block',
        ]:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    for el in elements:
                        t = el.inner_text()
                        if t:
                            facilities_text += ' ' + t
                    if len(facilities_text.strip()) > 150:
                        break
            except Exception:
                continue

        # Fallback: full page text (still useful for keyword matching)
        if len(facilities_text.strip()) < 150:
            try:
                facilities_text = page.inner_text('body')
            except Exception:
                pass

        # Extract rating — BDC scores out of 10
        rating = None
        for sel in [
            '[data-testid="review-score-right-component"]',
            '.bui-review-score__badge',
            '[class*="review-score__badge"]',
            '[class*="fcd9eec8fb"]',   # BDC dynamic class (common)
            '.b5a328e8df',
            '[data-testid="rating-and-reviews"]',
        ]:
            try:
                el = page.query_selector(sel)
                if el:
                    t = el.inner_text().strip()
                    rating = extract_rating_from_text(t)
                    if rating:
                        break
            except Exception:
                continue

        result['facilities_text'] = facilities_text
        result['rating'] = rating

    except Exception as e:
        result['error'] = str(e)

    return result


# ──────────────────────────────────────────────
# EXPEDIA SCRAPER
# ──────────────────────────────────────────────

def scrape_expedia(url, page):
    result = {'facilities_text': '', 'rating': None, 'error': None, 'source': 'Expedia'}
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=45000)
        human_delay(2, 4)

        # Dismiss overlays / cookie banners
        for sel in ['[data-testid="accept-button"]', 'button[id*="accept"]',
                    '[class*="cookie"] button', '.onetrust-accept-btn-handler']:
            click_if_exists(page, sel, 2000)

        page.evaluate("window.scrollBy(0, 500)")
        human_delay(1, 2)

        # Try to expand amenities
        for sel in [
            'button[data-stid="button-see-all-amenities"]',
            'button:text("See all amenities")',
            'button:text("Show all amenities")',
            'a:text("See all amenities")',
            '[data-testid="amenities-link"]',
        ]:
            click_if_exists(page, sel, 2500)

        human_delay(1, 2)

        facilities_text = ''

        for selector in [
            '[data-stid="content-hotel-amenities"]',
            '[data-stid="summary-amenities"]',
            '[data-testid="amenities-section"]',
            '[class*="amenity" i]',
            '[class*="property-amenities" i]',
            '[data-stid="hotel-overview"]',
            '.uitk-layout-grid',
        ]:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    for el in elements:
                        t = el.inner_text()
                        if t:
                            facilities_text += ' ' + t
                    if len(facilities_text.strip()) > 150:
                        break
            except Exception:
                continue

        if len(facilities_text.strip()) < 150:
            try:
                facilities_text = page.inner_text('body')
            except Exception:
                pass

        # Rating — Expedia uses out of 5 or 10
        rating = None
        for sel in [
            '[data-stid="reviews-summary-rating"]',
            '[data-testid="rating-badge"]',
            '[class*="guest-rating" i]',
            '[class*="GuestRating"]',
            '.uitk-badge-base',
            '[data-stid="score-section"]',
        ]:
            try:
                el = page.query_selector(sel)
                if el:
                    t = el.inner_text().strip()
                    rating = extract_rating_from_text(t)
                    if rating:
                        break
            except Exception:
                continue

        result['facilities_text'] = facilities_text
        result['rating'] = rating

    except Exception as e:
        result['error'] = str(e)

    return result


# ──────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────

def scrape_hotel_data(hotel_input):
    """Scrape one hotel from BDC and/or Expedia."""

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-extensions',
            ]
        )
        context = browser.new_context(
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/122.0.0.0 Safari/537.36'
            ),
            viewport={'width': 1366, 'height': 768},
            locale='en-US',
            timezone_id='America/New_York',
        )
        context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        page = context.new_page()

        # Block images/media to speed up loading
        page.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,woff,woff2}", lambda r: r.abort())

        result = {'booking': None, 'expedia': None}

        try:
            if hotel_input.get('booking_url'):
                result['booking'] = scrape_booking(hotel_input['booking_url'], page)
            if hotel_input.get('expedia_url'):
                result['expedia'] = scrape_expedia(hotel_input['expedia_url'], page)
        finally:
            browser.close()

    return result
