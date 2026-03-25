"""
scorer.py — All scoring criteria from the benchmarking criteria sheet.
Scores each factor, writes a reason, and generates both CSV outputs.
"""

# ──────────────────────────────────────────────
# CONFIG: WEIGHTS & STRUCTURE
# ──────────────────────────────────────────────

FACTORS = [
    {'key': 'location',    'label': 'Location',               'bucket': 'Location', 'weight': 5},
    {'key': 'amenities',   'label': 'Amenities',              'bucket': 'Service',  'weight': 4},
    {'key': 'restaurant',  'label': 'On Site Restaurant & Food', 'bucket': 'Product','weight': 3},
    {'key': 'meeting',     'label': 'Meeting Space',          'bucket': 'Product',  'weight': 3},
    {'key': 'brand',       'label': 'Type of Brand',          'bucket': 'Brand',    'weight': 5},
    {'key': 'parking',     'label': 'Parking Space',          'bucket': 'Product',  'weight': 4},
    {'key': 'ratings',     'label': 'Ratings & Reviews',      'bucket': 'Service',  'weight': 5},
    {'key': 'pool',        'label': 'Swimming Pool',          'bucket': 'Product',  'weight': 4},
]

BRAND_SCORES = {
    'Economy':       1.5,
    'MidScale':      2.5,
    'UpperMidScale': 3.0,
    'UpperScale':    3.5,
    'UpperUpscale':  4.0,
    'Luxury':        5.0,
}

AMENITIES_LIST = [
    'Daily housekeeping',
    'Laundry',
    '24-hour front desk',
    'Lift',
    'Suite Rooms',
    'Bathtub in Room',
    'Pet-Friendly Rooms',
    'Room service',
    'Fitness center',
    'Bar',
]

AMENITIES_KEYWORDS = {
    'Daily housekeeping': ['daily housekeeping', 'housekeeping daily', 'daily cleaning', 'turndown'],
    'Laundry':            ['laundry service', 'laundry', 'dry cleaning', 'washing service'],
    '24-hour front desk': ['24-hour front desk', '24/7 front desk', '24-hour reception',
                           'front desk 24', 'hour front desk'],
    'Lift':               ['lift', 'elevator'],
    'Suite Rooms':        ['suite rooms', 'junior suite', 'suites available', 'suite'],
    'Bathtub in Room':    ['bathtub in room', 'bathtub', 'bath tub', 'soaking tub'],
    'Pet-Friendly Rooms': ['pet-friendly', 'pets allowed', 'pet friendly', 'pets welcome'],
    'Room service':       ['room service', '24-hour room service'],
    'Fitness center':     ['fitness center', 'fitness centre', 'gym', 'workout room',
                           'exercise room', 'health club'],
    'Bar':                ['hotel bar', 'bar/lounge', 'cocktail bar', 'lounge bar', ' bar '],
}


# ──────────────────────────────────────────────
# INDIVIDUAL SCORING FUNCTIONS
# ──────────────────────────────────────────────

def score_amenities(combined_text):
    text = combined_text.lower()
    details = {}
    for amenity, keywords in AMENITIES_KEYWORDS.items():
        details[amenity] = any(kw in text for kw in keywords)

    count = sum(1 for v in details.values() if v)
    score = round(count * 0.5, 1)   # Max = 10 × 0.5 = 5
    found = [a for a, v in details.items() if v]
    not_found = [a for a, v in details.items() if not v]
    reason = f"{count}/10 amenities detected."
    if found:
        reason += f" Found: {', '.join(found)}."
    if not_found:
        reason += f" Not found: {', '.join(not_found)}."
    return score, reason, details


def score_restaurant(combined_text):
    t = combined_text.lower()
    has_restaurant = any(k in t for k in
        ['on-site restaurant', 'onsite restaurant', 'full-service restaurant',
         'restaurant on site', 'dining room', 'hotel restaurant'])
    has_buffet = any(k in t for k in
        ['buffet breakfast', 'continental breakfast', 'full breakfast',
         'breakfast buffet', 'complimentary breakfast', 'free breakfast'])
    has_vending = any(k in t for k in
        ['vending machine', 'coffee machine', 'microwave', 'snack bar', 'coffee maker'])

    if has_restaurant:
        return 5.0, "On-site restaurant found on listing → Score: 5"
    if has_buffet and has_vending:
        return 3.5, "Buffet/Breakfast + Vending/Coffee/Microwave found → Score: 3.5"
    if has_buffet:
        return 3.0, "Buffet/Breakfast found → Score: 3"
    if has_vending:
        return 1.5, "Vending/Coffee Machine/Microwave only → Score: 1.5"
    return 0.0, "No dining facilities detected → Score: 0"


def score_pool(combined_text):
    t = combined_text.lower()
    has_pool = 'pool' in t or 'swimming' in t

    if not has_pool:
        return 0.0, "No pool mentioned → Score: 0"

    is_closed    = any(k in t for k in ['pool closed', 'pool is closed', 'pool renovation', 'pool under'])
    is_indoor    = any(k in t for k in ['indoor pool', 'indoor swimming', 'interior pool'])
    is_outdoor   = any(k in t for k in ['outdoor pool', 'outdoor swimming', 'outside pool'])
    is_heated    = 'heated' in t
    is_seasonal  = 'seasonal' in t
    is_multiple  = any(k in t for k in ['2 pool', 'two pool', 'multiple pool', '2pool'])

    if is_closed:
        return 1.0, "Pool listed as closed/under renovation → Score: 1"
    if is_indoor and (is_heated or is_multiple):
        return 5.0, "Indoor heated pool or 2 indoor pools found → Score: 5"
    if is_indoor:
        return 4.0, "Indoor pool found → Score: 4"
    if (is_outdoor or has_pool) and (is_heated or is_multiple) and not is_seasonal:
        return 3.5, "Outdoor heated pool / 2 pools found → Score: 3.5"
    if is_seasonal and is_heated:
        return 2.5, "Outdoor seasonal heated pool found → Score: 2.5"
    if is_seasonal:
        return 2.0, "Outdoor seasonal pool found → Score: 2"
    if is_outdoor or has_pool:
        return 3.0, "Outdoor pool found → Score: 3"
    return 0.0, "No usable pool found → Score: 0"


def score_meeting(combined_text):
    t = combined_text.lower()
    has_banquet  = 'banquet' in t
    has_bc       = 'business centre' in t or 'business center' in t
    has_meeting  = any(k in t for k in ['meeting room', 'conference room', 'boardroom', 'event room'])
    meeting_count = t.count('meeting room') + t.count('conference room')
    has_multi    = meeting_count > 1 or 'multiple meeting' in t

    if has_banquet:
        return 5.0, "Banquet facilities found → Score: 5"
    if has_multi and has_bc:
        return 5.0, "Multiple meeting rooms + Business centre found → Score: 5"
    if has_meeting and has_bc:
        return 4.0, "1 Meeting room + Business centre found → Score: 4"
    if has_multi:
        return 4.0, "Multiple meeting rooms found → Score: 4"
    if has_meeting:
        return 3.0, "Meeting room found → Score: 3"
    if has_bc:
        return 1.0, "Business centre found → Score: 1"
    return 0.0, "No meeting facilities found → Score: 0"


def score_parking(combined_text):
    t = combined_text.lower()
    if any(k in t for k in ['lorry', 'bus parking', 'truck parking', 'rv parking', 'coach parking']):
        return 5.0, "Lorry/bus/truck parking found → Score: 5"
    if any(k in t for k in ['ev charging', 'electric vehicle charging', 'ev parking', 'electric car charging']):
        return 4.0, "EV charging/parking found → Score: 4"
    if any(k in t for k in ['free parking', 'free private parking', 'complimentary parking',
                              'no charge parking', 'free self-parking']):
        return 3.0, "On-site free parking found → Score: 3"
    if any(k in t for k in ['paid parking', 'parking fee', 'parking surcharge',
                              'self-parking fee', 'valet parking fee', 'parking charges']):
        return 2.0, "On-site charged parking found → Score: 2"
    if any(k in t for k in ['street parking', 'public parking', 'nearby parking']):
        return 1.0, "Street/public parking found → Score: 1"
    if 'parking' in t:
        return 3.0, "Parking mentioned (assumed free on-site) → Score: 3"
    return 0.0, "No parking information found → Score: 0"


# ──────────────────────────────────────────────
# MAIN PROCESSOR
# ──────────────────────────────────────────────

def process_hotel_data(hotel_input, scraped_data):
    """Score all factors for one hotel, return structured result."""

    # Merge text from both sources
    combined_text = ''
    bdc_rating, exp_rating = None, None

    if scraped_data.get('booking'):
        combined_text += ' ' + scraped_data['booking'].get('facilities_text', '')
        bdc_rating = scraped_data['booking'].get('rating')

    if scraped_data.get('expedia'):
        combined_text += ' ' + scraped_data['expedia'].get('facilities_text', '')
        exp_rating = scraped_data['expedia'].get('rating')

    # Score auto factors
    amenity_score, amenity_reason, amenity_details = score_amenities(combined_text)
    rest_score,   rest_reason    = score_restaurant(combined_text)
    pool_score,   pool_reason    = score_pool(combined_text)
    meet_score,   meet_reason    = score_meeting(combined_text)
    park_score,   park_reason    = score_parking(combined_text)

    # Ratings
    valid_ratings = [r for r in [bdc_rating, exp_rating] if r is not None]
    avg_rating = round(sum(valid_ratings) / len(valid_ratings), 2) if valid_ratings else 0.0
    rating_parts = []
    if bdc_rating is not None: rating_parts.append(f"BDC: {bdc_rating}")
    if exp_rating  is not None: rating_parts.append(f"Expedia: {exp_rating}")
    rating_reason = (', '.join(rating_parts) + f" → Average (out of 5): {avg_rating}") if rating_parts else "No ratings scraped"

    # Manual fields
    loc_score   = float(hotel_input.get('location_score', 0))
    brand_tier  = hotel_input.get('brand_tier', 'Economy')
    brand_score = BRAND_SCORES.get(brand_tier, 1.5)

    raw_scores = {
        'location':   (loc_score,    f"Manually entered → Score: {loc_score}"),
        'amenities':  (amenity_score, amenity_reason),
        'restaurant': (rest_score,   rest_reason),
        'meeting':    (meet_score,   meet_reason),
        'brand':      (brand_score,  f"Brand tier '{brand_tier}' → Score: {brand_score}"),
        'parking':    (park_score,   park_reason),
        'ratings':    (avg_rating,   rating_reason),
        'pool':       (pool_score,   pool_reason),
    }

    # Build per-factor results with weighted scores
    factor_results = {}
    total = 0.0
    for f in FACTORS:
        key = f['key']
        score, reason = raw_scores[key]
        weighted = round(score * f['weight'], 1)
        total += weighted
        factor_results[key] = {
            'label':          f['label'],
            'bucket':         f['bucket'],
            'weight':         f['weight'],
            'score':          score,
            'weighted_score': weighted,
            'reason':         reason,
        }

    return {
        'name':            hotel_input['name'],
        'factors':         factor_results,
        'total':           round(total, 1),
        'amenity_details': amenity_details,
        'scrape_errors': {
            'booking': scraped_data.get('booking', {}).get('error') if scraped_data.get('booking') else 'URL not provided',
            'expedia': scraped_data.get('expedia', {}).get('error') if scraped_data.get('expedia') else 'URL not provided',
        }
    }


# ──────────────────────────────────────────────
# CSV GENERATORS
# ──────────────────────────────────────────────

def generate_amenities_csv(results):
    rows = []
    header = ['Amenities'] + [r['name'] for r in results]
    rows.append(header)

    for amenity in AMENITIES_LIST:
        row = [amenity]
        for hotel in results:
            row.append('✓' if hotel.get('amenity_details', {}).get(amenity, False) else '')
        rows.append(row)

    # Count row
    count_row = ['Count']
    for hotel in results:
        count_row.append(sum(1 for v in hotel.get('amenity_details', {}).values() if v))
    rows.append(count_row)

    # Marking row
    marking_row = ['Marking']
    for hotel in results:
        marking_row.append(hotel['factors']['amenities']['score'])
    rows.append(marking_row)

    return rows


def generate_scoring_csv(results):
    rows = []

    # Header row — Score / Weighted Score / Reason per hotel
    header = ['Bucket', 'Factor', 'Weight']
    for hotel in results:
        n = hotel['name']
        header += [f"{n} — Score", f"{n} — Weighted Score", f"{n} — Reason"]
    rows.append(header)

    for f in FACTORS:
        key = f['key']
        row = [f['bucket'], f['label'], f['weight']]
        for hotel in results:
            fd = hotel['factors'].get(key, {})
            row += [fd.get('score', ''), fd.get('weighted_score', ''), fd.get('reason', '')]
        rows.append(row)

    # Blank separator
    rows.append([])

    # Total Score row
    total_row = ['', 'Total Score', '']
    for hotel in results:
        total_row += [hotel['total'], '', '']
    rows.append(total_row)

    # Rank row (sorted by total descending)
    ranked = sorted(results, key=lambda x: x['total'], reverse=True)
    rank_map = {r['name']: i + 1 for i, r in enumerate(ranked)}
    rank_row = ['', 'Rank', '']
    for hotel in results:
        rank_row += [rank_map[hotel['name']], '', '']
    rows.append(rank_row)

    return rows
