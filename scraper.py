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
            'text=/See all \\d+ facilities/i',
            'text=/See all facilities/i',
            'text=/Show all facilities/i',
        ]:
            if click_if_exists(page, sel, 2500):
                break

        human_delay(2, 3)
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
                    rating = extract_rating_from_text(el.inner_text().strip())
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
            'text="See all about this property"',
            'text="See all amenities"',
            'button:has-text("See all amenities")',
            'button:has-text("Show all amenities")',
            '[data-stid="button-see-all-amenities"]',
            '[data-testid="amenities-link"]',
        ]:
            if click_if_exists(page, sel, 2500):
                break

        human_delay(2, 3)
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
                    rating = extract_rating_from_text(el.inner_text().strip())
                    if rating:
                        break
            except Exception:
                continue
        result['rating'] = rating

    except Exception as e:
        result['error'] = str(e)
    return result


# ──────────────────────────────────────────────
# AGODA SCRAPER
# ──────────────────────────────────────────────

def scrape_agoda(url, page):
    result = {'facilities_text': '', 'rating': None, 'error': None, 'source': 'Agoda'}
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=45000)
        human_delay(2, 4)

        for sel in [
            '[data-element-name="accept-cookie"]',
            'button[aria-label*="accept" i]',
            'button:has-text("Accept")',
            '[data-testid="close-button"]',
            'button[aria-label="Close"]',
        ]:
            click_if_exists(page, sel, 2000)

        page.evaluate("window.scrollBy(0, 400)")
        human_delay(1, 2)

        for sel in [
            'a[data-tab-name="Facilities"]',
            'button:has-text("Facilities")',
            'a:has-text("Facilities")',
            '[data-element-name="tab-facilities"]',
            'li:has-text("Facilities")',
            'span:has-text("Facilities")',
        ]:
            if click_if_exists(page, sel, 3000):
                break

        human_delay(2, 3)

        for sel in [
            'button:has-text("See all")',
            'a:has-text("See all facilities")',
            'span:has-text("See all facilities")',
        ]:
            if click_if_exists(page, sel, 2000):
                break

        human_delay(1, 2)
        result['facilities_text'] = page.evaluate("document.body.innerText")

        rating = None
        for sel in [
            '[data-element-name="hotel-score"]',
            '[class*="ReviewScore"]',
            '[class*="review-score"]',
            '[data-testid="review-score"]',
            'span[class*="Score"]',
        ]:
            try:
                el = page.query_selector(sel)
                if el:
                    rating = extract_rating_from_text(el.inner_text().strip())
                    if rating:
                        break
            except Exception:
                continue
        result['rating'] = rating

    except Exception as e:
        result['error'] = str(e)
    return result


# ──────────────────────────────────────────────
# GOOGLE HOTELS SCRAPER
# ──────────────────────────────────────────────

def scrape_google(url, page):
    result = {'facilities_text': '', 'rating': None, 'error': None, 'source': 'Google Hotels'}
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=45000)
        human_delay(2, 4)

        for sel in [
            'button:has-text("Accept all")',
            'button:has-text("I agree")',
            'button:has-text("Accept")',
            '[aria-label*="Accept" i]',
        ]:
            if click_if_exists(page, sel, 2000):
                break

        human_delay(1, 2)

        for sel in [
            'button:has-text("About")',
            'a:has-text("About")',
            '[aria-label="About"]',
            'li:has-text("About")',
        ]:
            if click_if_exists(page, sel, 3000):
                break

        human_delay(2, 3)
        page.evaluate("window.scrollBy(0, 400)")
        human_delay(1, 2)

        for sel in [
            'button:has-text("See more amenities")',
            'a:has-text("See more amenities")',
            'span:has-text("See more")',
        ]:
            if click_if_exists(page, sel, 2000):
                break

        human_delay(1, 2)
        result['facilities_text'] = page.evaluate("document.body.innerText")

        rating = None
        for sel in [
            '[aria-label*="out of 5" i]',
            '[aria-label*="stars" i]',
            'span[class*="rating"]',
            'div[class*="rating"]',
        ]:
            try:
                el = page.query_selector(sel)
                if el:
                    aria = el.get_attribute('aria-label') or el.inner_text()
                    rating = extract_rating_from_text(aria)
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
            locale='en-US',
            timezone_id='America/New_York',
        )
        context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,woff,woff2}", lambda r: r.abort())

        result = {'booking': None, 'expedia': None, 'agoda': None, 'google': None}

        try:
            if hotel_input.get('booking_url'):
                result['booking'] = scrape_booking(hotel_input['booking_url'], page)
            if hotel_input.get('expedia_url'):
                result['expedia'] = scrape_expedia(hotel_input['expedia_url'], page)
            if hotel_input.get('agoda_url'):
                result['agoda'] = scrape_agoda(hotel_input['agoda_url'], page)
            if hotel_input.get('google_url'):
                result['google'] = scrape_google(hotel_input['google_url'], page)
        finally:
            browser.close()

    return result
