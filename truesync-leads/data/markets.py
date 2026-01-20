"""
Market Definitions
==================

Priority markets for TrueSync lead generation.

Tier 1 (Primary): UK, USA, Spain
Tier 2 (Expansion): Germany, France, Korea
"""

MARKETS = {
    # TIER 1 - PRIMARY MARKETS
    'uk': {
        'name': 'United Kingdom',
        'priority': 1,
        'tier': 1,
        'priority_multiplier': 1.0,
        'languages': ['English'],
        'why': 'Gateway to US buyers, strong rights control, many foreign hits are English-adjacent, major studios with global distribution',
        'key_platforms': ['BBC iPlayer', 'ITV Hub', 'Channel 4', 'Sky']
    },
    'usa': {
        'name': 'United States',
        'priority': 2,
        'tier': 1,
        'priority_multiplier': 1.0,
        'languages': ['English'],
        'why': 'Greenlight power, platform influence, benchmarking vs domestic content, largest English-speaking market',
        'key_platforms': ['Netflix', 'Amazon Prime Video', 'HBO Max', 'Peacock', 'Pluto TV', 'Tubi']
    },
    'spain': {
        'name': 'Spain',
        'priority': 3,
        'tier': 1,
        'priority_multiplier': 0.95,
        'languages': ['Spanish', 'Catalan', 'Basque'],
        'why': 'Massive global Spanish-speaking base, subtitles underperform in English markets, strong track record of global breakouts',
        'key_platforms': ['Netflix Spain', 'Amazon Prime Video Spain', 'Movistar Plus+']
    },
    
    # TIER 2 - EXPANSION MARKETS
    'germany': {
        'name': 'Germany',
        'priority': 4,
        'tier': 2,
        'priority_multiplier': 0.85,
        'languages': ['German'],
        'why': 'High budgets, historically weak English penetration, strong upside for dubbing, DACH region coverage',
        'key_platforms': ['Netflix Germany', 'Amazon Prime Video Germany', 'RTL+']
    },
    'france': {
        'name': 'France',
        'priority': 5,
        'tier': 2,
        'priority_multiplier': 0.85,
        'languages': ['French'],
        'why': 'Strong state-supported production, internationally exportable formats, large catalog depth',
        'key_platforms': ['Netflix France', 'Canal+', 'Amazon Prime Video France']
    },
    'korea': {
        'name': 'South Korea',
        'priority': 6,
        'tier': 2,
        'priority_multiplier': 0.85,
        'languages': ['Korean'],
        'why': 'Proven global appetite (Squid Game, Parasite), high production quality, strong genre portability',
        'key_platforms': ['Netflix Korea', 'TVING', 'Wavve']
    }
}


def get_market_priority(market_key: str) -> int:
    """Get priority ranking for a market (1 = highest)."""
    return MARKETS.get(market_key, {}).get('priority', 99)


def get_market_multiplier(market_key: str) -> float:
    """Get scoring multiplier for a market."""
    return MARKETS.get(market_key, {}).get('priority_multiplier', 0.5)


def get_tier1_markets() -> list:
    """Get list of Tier 1 (primary) market keys."""
    return [k for k, v in MARKETS.items() if v.get('tier') == 1]


def get_tier2_markets() -> list:
    """Get list of Tier 2 (expansion) market keys."""
    return [k for k, v in MARKETS.items() if v.get('tier') == 2]


# ============================================================================
# MARKET DETECTION FROM LOCATION STRINGS
# ============================================================================

# Location patterns mapped to market keys
# More specific patterns should come before general ones
LOCATION_PATTERNS = {
    # USA - Cities and states
    'united states': 'usa',
    'california': 'usa',
    'new york': 'usa',
    'los angeles': 'usa',
    'texas': 'usa',
    'florida': 'usa',
    'chicago': 'usa',
    'seattle': 'usa',
    'boston': 'usa',
    'atlanta': 'usa',
    'denver': 'usa',
    'san francisco': 'usa',
    'miami': 'usa',
    'washington': 'usa',
    'arizona': 'usa',
    'colorado': 'usa',
    'georgia': 'usa',
    'massachusetts': 'usa',
    'new jersey': 'usa',
    'pennsylvania': 'usa',
    'illinois': 'usa',
    'ohio': 'usa',
    'michigan': 'usa',
    'north carolina': 'usa',
    'virginia': 'usa',
    'maryland': 'usa',
    'connecticut': 'usa',
    'santa monica': 'usa',
    'culver city': 'usa',
    'burbank': 'usa',
    'hollywood': 'usa',
    'brooklyn': 'usa',
    'manhattan': 'usa',
    
    # UK - Cities and regions
    'united kingdom': 'uk',
    'london': 'uk',
    'england': 'uk',
    'scotland': 'uk',
    'wales': 'uk',
    'manchester': 'uk',
    'birmingham': 'uk',
    'bristol': 'uk',
    'leeds': 'uk',
    'glasgow': 'uk',
    'edinburgh': 'uk',
    'greater london': 'uk',
    'london area': 'uk',
    
    # Spain - Cities and regions
    'spain': 'spain',
    'madrid': 'spain',
    'barcelona': 'spain',
    'valencia': 'spain',
    'seville': 'spain',
    'malaga': 'spain',
    'españa': 'spain',
    'catalonia': 'spain',
    'andalusia': 'spain',
    
    # Germany - Cities and regions
    'germany': 'germany',
    'berlin': 'germany',
    'munich': 'germany',
    'frankfurt': 'germany',
    'hamburg': 'germany',
    'cologne': 'germany',
    'düsseldorf': 'germany',
    'deutschland': 'germany',
    'bavaria': 'germany',
    'münchen': 'germany',
    'köln': 'germany',
    
    # France - Cities and regions
    'france': 'france',
    'paris': 'france',
    'lyon': 'france',
    'marseille': 'france',
    'toulouse': 'france',
    'nice': 'france',
    'greater paris': 'france',
    'ile-de-france': 'france',
    
    # South Korea - Cities and regions
    'south korea': 'korea',
    'korea': 'korea',
    'seoul': 'korea',
    'busan': 'korea',
    'incheon': 'korea',
    'daegu': 'korea',
    'gangnam': 'korea',
    '한국': 'korea',
    '서울': 'korea',
}


def detect_market(location: str) -> str:
    """
    Detect market from a location string.
    
    Args:
        location: Location string (e.g., "Los Angeles, California, United States")
        
    Returns:
        Market key (e.g., 'usa', 'uk', 'spain') or 'other' if not detected
    """
    if not location:
        return 'other'
    
    loc_lower = location.lower()
    
    # Check each pattern
    for pattern, market in LOCATION_PATTERNS.items():
        if pattern in loc_lower:
            return market
    
    return 'other'


def detect_markets_from_leads(leads: list) -> set:
    """
    Detect unique markets from a list of leads.
    
    Args:
        leads: List of lead dictionaries with 'location' field
        
    Returns:
        Set of detected market keys
    """
    markets = set()
    for lead in leads:
        location = lead.get('location', '')
        market = detect_market(location)
        if market != 'other':
            markets.add(market)
    return markets


def get_location_filter_for_market(market: str) -> list:
    """
    Get location strings to use for Apify filtering for a given market.
    
    Args:
        market: Market key (e.g., 'usa', 'uk')
        
    Returns:
        List of location strings for API filtering
    """
    market_locations = {
        'usa': ['united states'],
        'uk': ['united kingdom'],
        'spain': ['spain'],
        'germany': ['germany'],
        'france': ['france'],
        'korea': ['south korea'],
    }
    return market_locations.get(market, [])
