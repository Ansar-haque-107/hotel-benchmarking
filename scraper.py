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

        for sel in ['#onetrust-accept-btn-handler', 'button[aria-label*="accept" i]',
                    '[id*="accept-cookies"]', '.bui-button--accept']:
            click_if_exists(page, sel, 2000)

        page.evaluate("window.scrollBy(0, 600)")
        human_delay(1, 2)

        for sel in [
            'button[data-testid="show-all-facilities-button"]',
            'a[href*="#facilities"]',
            'button:has-text("Show all facilities")',
            'button:has-text("See all facilities")',
        ]:
            click_if_exists(page, sel, 2500)

        human_delay(2, 3)

        # AGGRESSIVE SCRAPE: Grab all text visible on the page/modal
        result['facilities_text'] = page.evaluate("document.body.innerText")

        rating = None
        for sel in [
            '[data-testid="review-score-right-component"]',
            '.bui-review-score__badge',
            '[class*="review-score__badge"]',
            '[class*="fcd9eec8fb"]',   
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

        for sel in ['[data-testid="accept-button"]', 'button[id*="accept"]',
                    '[class*="cookie"] button', '.onetrust-accept-btn-handler']:
            click_if_exists(page, sel, 2000)

        page.evaluate("window.scrollBy(0, 500)")
        human_delay(1, 2)

        for sel in [
            'button[data-stid="button-see-all-amenities"]',
            'button:has-text("See all amenities")',
            'button:has-text("See all property amenities")',
            'button:has-text("Show all amenities")',
            '[data-testid="amenities-link"]',
        ]:
            click_if_exists(page, sel, 2500)

        human_delay(2, 3)

        # AGGRESSIVE SCRAPE: Grab all text visible on the page/modal
        result['facilities_text'] = page.evaluate("document.body.innerText")

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

        result['rating'] = rating

    except Exception as e:
        result['error'] = str(e)

    return result

# ──────────────────────────────────────────────
# MAIN ENTRY POINT
# ──────────────────────────────────────────────

def scrape_hotel_data(hotel_input):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas', '--no-first-run', '--no-zygote',
                '--disable-gpu', '--disable-extensions',
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1366, 'height': 768},
            locale='en-US', timezone_id='America/New_York',
        )
        page = context.new_page()
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
