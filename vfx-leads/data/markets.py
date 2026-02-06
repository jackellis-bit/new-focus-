"""
Market Definitions for VFX Pipeline
=====================================

VFX houses are primarily in: USA, UK, Canada, India, France.
"""

MARKETS = {
    'usa': {
        'name': 'United States',
        'priority': 1,
        'priority_multiplier': 1.0,
    },
    'uk': {
        'name': 'United Kingdom',
        'priority': 2,
        'priority_multiplier': 1.0,
    },
    'canada': {
        'name': 'Canada',
        'priority': 3,
        'priority_multiplier': 0.95,
    },
    'india': {
        'name': 'India',
        'priority': 4,
        'priority_multiplier': 0.85,
    },
    'france': {
        'name': 'France',
        'priority': 5,
        'priority_multiplier': 0.90,
    },
}


# Location patterns mapped to market keys
LOCATION_PATTERNS = {
    # USA
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
    'san rafael': 'usa',
    'miami': 'usa',
    'santa monica': 'usa',
    'culver city': 'usa',
    'burbank': 'usa',
    'glendale': 'usa',
    'hollywood': 'usa',
    'emeryville': 'usa',
    'marina del rey': 'usa',
    'venice, ca': 'usa',
    'berkeley': 'usa',
    'el segundo': 'usa',
    'boulder': 'usa',
    'alpharetta': 'usa',
    ', ca,': 'usa',
    ', ny,': 'usa',
    ', ny': 'usa',
    ', ca': 'usa',
    ', ma': 'usa',
    ', co': 'usa',
    ', ga': 'usa',

    # UK
    'united kingdom': 'uk',
    'london': 'uk',
    'england': 'uk',
    'scotland': 'uk',
    'wales': 'uk',
    'manchester': 'uk',
    'bournemouth': 'uk',
    'bristol': 'uk',
    'lincoln, eng': 'uk',
    ', uk': 'uk',

    # Canada
    'canada': 'canada',
    'montreal': 'canada',
    'vancouver': 'canada',
    'toronto': 'canada',
    'quebec': 'canada',
    'kelowna': 'canada',
    'abbotsford': 'canada',
    'piedmont, qc': 'canada',
    ', bc,': 'canada',
    ', on,': 'canada',
    ', qc,': 'canada',
    ', bc': 'canada',
    ', on': 'canada',
    ', qc': 'canada',

    # India
    'india': 'india',
    'mumbai': 'india',
    'bengaluru': 'india',
    'bangalore': 'india',
    'hyderabad': 'india',
    'chennai': 'india',

    # France
    'france': 'france',
    'paris': 'france',
    'lyon': 'france',
    'marseille': 'france',
}


def detect_market(location: str) -> str:
    """
    Detect market from a location string.
    
    Args:
        location: Location string (e.g., "Los Angeles, CA, USA")
        
    Returns:
        Market key or 'unknown'
    """
    if not location:
        return 'unknown'
    
    loc_lower = location.lower()
    
    for pattern, market in LOCATION_PATTERNS.items():
        if pattern in loc_lower:
            return market
    
    return 'unknown'


def detect_markets_from_leads(leads: list) -> set:
    """Detect unique markets from a list of leads."""
    markets = set()
    for lead in leads:
        location = lead.get('location', '')
        market = detect_market(location)
        if market != 'unknown':
            markets.add(market)
    return markets


def get_market_multiplier(market_key: str) -> float:
    """Get scoring multiplier for a market."""
    return MARKETS.get(market_key, {}).get('priority_multiplier', 0.7)
