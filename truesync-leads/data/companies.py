"""
Target Companies
================

Priority companies across Tier 1 (UK, USA, Spain) and Tier 2 (Germany, France, Korea) markets.

Updated strategy: 2 Producers + 1 Distributor + Platforms per market.
This reflects feedback that distributors are often regional sales agents rather than 
having actual ability to distribute themselves.

Company Types:
- Producer: Creates content (greenlight power, catalog owners)
- Distributor: Sells/licenses content internationally  
- Platform: Streaming/broadcast platforms (buyers with commissioning power)
- AVOD Platform: Ad-supported streaming (minutes watched = revenue)
"""

COMPANIES = [
    # ==========================================
    # TIER 1 - PRIMARY MARKETS (1.0x priority)
    # ==========================================
    
    # ==================
    # UK (Gateway to US buyers)
    # ==================
    # 2 Producers
    {
        'name': 'BBC Studios',
        'type': 'Producer',
        'market': 'uk',
        'linkedin_url': 'https://www.linkedin.com/company/bbc-studios/',
        'catalog_size': '2500+ hours annually, 40,000+ hours archive',
        'catalog_notes': 'Global content powerhouse. Doctor Who, Top Gear, Planet Earth. Strong international distribution arm. Key decision maker for dubbing investments into non-English markets.'
    },
    {
        'name': 'ITV Studios',
        'type': 'Producer',
        'market': 'uk',
        'linkedin_url': 'https://www.linkedin.com/company/itv-studios/',
        'catalog_size': '8,000+ hours production annually',
        'catalog_notes': 'Major UK producer. Love Island, Hell\'s Kitchen formats. Strong scripted and unscripted slate. ITV Studios Global handles international distribution.'
    },
    # 1 Distributor
    {
        'name': 'All3Media',
        'type': 'Distributor',
        'market': 'uk',
        'linkedin_url': 'https://www.linkedin.com/company/all3media/',
        'catalog_size': '27,000+ hours TV content',
        'catalog_notes': 'PE-backed super-indie. Fleabag, Skins, Midsomer Murders. All3Media International handles global sales. Heavy international sales focus.'
    },
    # Platforms
    {
        'name': 'Sky Studios',
        'type': 'Platform',
        'market': 'uk',
        'linkedin_url': 'https://www.linkedin.com/company/sky/',
        'catalog_size': '100+ Sky Originals',
        'catalog_notes': 'Comcast-owned. Chernobyl, Gangs of London. Major original content investment. Pan-European platform presence.'
    },
    {
        'name': 'Channel 4',
        'type': 'Platform',
        'market': 'uk',
        'linkedin_url': 'https://www.linkedin.com/company/channel-4/',
        'catalog_size': '1,000+ hours originals',
        'catalog_notes': 'Public service broadcaster with commercial model. Strong in comedy, drama, documentaries. Channel 4 Studios produces originals. International distribution via All3Media.'
    },
    
    # ==================
    # USA (Greenlight Power)
    # ==================
    # 2 Producers
    {
        'name': 'Universal Pictures Content Group',
        'type': 'Producer',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/nbcuniversal/',
        'catalog_size': '5000+ films, major franchises',
        'catalog_notes': 'Jurassic World, Fast & Furious, Minions. Major studio with global distribution. Key targets: CFO/SVP Commercial Strategy (joint role), SVP Production/Programming/Operations (handles localization on all slate titles).'
    },
    {
        'name': 'Lionsgate',
        'type': 'Producer',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/lionsgate/',
        'catalog_size': '20,000+ film & TV titles',
        'catalog_notes': 'Hunger Games, John Wick, Mad Men. Catalog-first economics. Heavy FAST/AVOD exposure. Many active or re-licensed titles with engagement upside.'
    },
    {
        'name': 'Sony Pictures Entertainment',
        'type': 'Producer',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/sony-pictures-entertainment/',
        'catalog_size': '3,500+ films, 150,000+ TV episodes',
        'catalog_notes': 'Spider-Man, Breaking Bad, The Crown. Licensing-first model. Rational, data-driven buyers. Strong fit for live and semi-active assets.'
    },
    # 1 Distributor
    {
        'name': 'Warner Bros. Discovery',
        'type': 'Distributor',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/warnerbros/',
        'catalog_size': '10,000+ films, 200,000+ TV episodes',
        'catalog_notes': 'HBO, Max, DC, Harry Potter, Friends. Enormous upside on live franchises and resurgent catalog. Big payoff where urgency exists.'
    },
    # Platform
    {
        'name': 'Netflix US',
        'type': 'Platform',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/netflix/',
        'catalog_size': '15,000+ titles globally',
        'catalog_notes': 'Streaming leader. Massive original content investment. Data-driven localization decisions. Key validation partner for dubbing ROI.'
    },
    
    # ==================
    # SPAIN (Highest ROI for Dubbing)
    # ==================
    # 2 Producers
    {
        'name': 'Atresmedia Studios',
        'type': 'Producer',
        'market': 'spain',
        'linkedin_url': 'https://www.linkedin.com/company/atresmedia/',
        'catalog_size': '500+ hours of premium Spanish content',
        'catalog_notes': 'Major Spanish broadcaster production arm. Key titles: La Casa de Papel spin-offs, El Internado. Strong slate of Spanish-language originals with global distribution deals.'
    },
    {
        'name': 'Mediapro',
        'type': 'Producer',
        'market': 'spain',
        'linkedin_url': 'https://www.linkedin.com/company/mediapro/',
        'catalog_size': '1000+ hours across film and TV',
        'catalog_notes': 'Largest independent Spanish producer. Behind major Netflix Spain originals. Strong sports content and drama slate. The Mediapro Studio is their premium scripted arm.'
    },
    # 1 Distributor
    {
        'name': 'Beta Film',
        'type': 'Distributor',
        'market': 'spain',
        'linkedin_url': 'https://www.linkedin.com/company/beta-film/',
        'catalog_size': '6000+ hours international catalog',
        'catalog_notes': 'Pan-European distribution powerhouse with strong Spanish arm. Handles major Spanish dramas for international markets. Key partner for dubbing to English for US/UK buyers.'
    },
    # Platform
    {
        'name': 'Netflix Spain',
        'type': 'Platform',
        'market': 'spain',
        'linkedin_url': 'https://www.linkedin.com/company/netflix/',
        'catalog_size': '100+ Spanish originals',
        'catalog_notes': 'Platform anchor for Spain market. Greenlight power for local originals. Key validation partner - their Spanish content travels globally when properly localized.'
    },
    
    # ==========================================
    # TIER 2 - EXPANSION MARKETS (0.85x priority)
    # ==========================================
    
    # ==================
    # GERMANY
    # ==================
    # 2 Producers
    {
        'name': 'UFA',
        'type': 'Producer',
        'market': 'germany',
        'linkedin_url': 'https://www.linkedin.com/company/ufa-gmbh/',
        'catalog_size': '1000+ hours annually',
        'catalog_notes': 'RTL Group subsidiary. Germany\'s largest fiction producer. Strong scripted and format production. Bertelsmann backing.'
    },
    {
        'name': 'Constantin Film',
        'type': 'Producer',
        'market': 'germany',
        'linkedin_url': 'https://www.linkedin.com/company/constantin-film/',
        'catalog_size': '300+ films',
        'catalog_notes': 'Resident Evil, Fantastic Four (German rights). Major German film producer. Strong theatrical and streaming presence.'
    },
    # 1 Distributor
    {
        'name': 'Beta Film DE',
        'type': 'Distributor',
        'market': 'germany',
        'linkedin_url': 'https://www.linkedin.com/company/beta-film/',
        'catalog_size': '6000+ hours international',
        'catalog_notes': 'Major pan-European distributor headquartered in Munich. Handles premium European drama for global markets.'
    },
    # Platform
    {
        'name': 'RTL+ Germany',
        'type': 'Platform',
        'market': 'germany',
        'linkedin_url': 'https://www.linkedin.com/company/rtl-deutschland/',
        'catalog_size': '500+ originals and exclusives',
        'catalog_notes': 'RTL Group streaming platform. Growing original content investment. Key player in German streaming market.'
    },
    
    # ==================
    # FRANCE
    # ==================
    # 2 Producers
    {
        'name': 'Gaumont',
        'type': 'Producer',
        'market': 'france',
        'linkedin_url': 'https://www.linkedin.com/company/gaumont/',
        'catalog_size': '1500+ films, 100+ TV series',
        'catalog_notes': 'Historic French studio (founded 1895). Behind Lupin, Narcos. Large catalog of prestige French content requiring English localization for global markets.'
    },
    {
        'name': 'StudioCanal',
        'type': 'Producer',
        'market': 'france',
        'linkedin_url': 'https://www.linkedin.com/company/studiocanal/',
        'catalog_size': '7000+ films',
        'catalog_notes': 'Major European studio (Canal+ Group). One of Europe\'s largest film libraries. Active in production and distribution. Strategic priority for catalog monetization through dubbing.'
    },
    # 1 Distributor
    {
        'name': 'Newen Distribution',
        'type': 'Distributor',
        'market': 'france',
        'linkedin_url': 'https://www.linkedin.com/company/newen/',
        'catalog_size': '4000+ hours across 400+ titles',
        'catalog_notes': 'TF1 Group international arm. Handles French and international content sales. Strong drama and format catalog. Active buyer at international markets.'
    },
    # Platform
    {
        'name': 'Canal+',
        'type': 'Platform',
        'market': 'france',
        'linkedin_url': 'https://www.linkedin.com/company/canal-plus/',
        'catalog_size': '200+ original productions',
        'catalog_notes': 'Major French platform with international expansion ambitions. Strong original content slate. Key partner for French content requiring English localization.'
    },
    
    # ==================
    # SOUTH KOREA
    # ==================
    # 2 Producers
    {
        'name': 'Studio Dragon',
        'type': 'Producer',
        'market': 'korea',
        'linkedin_url': 'https://www.linkedin.com/company/studiodragon/',
        'catalog_size': '100+ premium K-drama series',
        'catalog_notes': '#1 K-drama factory. Behind Squid Game, Crash Landing on You, Vincenzo. CJ ENM subsidiary. Massive global appetite for their content - prime candidate for English dubbing.'
    },
    {
        'name': 'CJ ENM',
        'type': 'Producer',
        'market': 'korea',
        'linkedin_url': 'https://www.linkedin.com/company/cj-enm/',
        'catalog_size': '500+ hours film and TV',
        'catalog_notes': 'Parasite producer. Massive content engine spanning film, TV, music. Owns Studio Dragon, TVING. Strategic priority for English localization of premium content.'
    },
    # 1 Distributor
    {
        'name': 'SBS Contents Hub',
        'type': 'Distributor',
        'market': 'korea',
        'linkedin_url': 'https://www.linkedin.com/company/sbs-contents-hub/',
        'catalog_size': '10000+ hours TV content',
        'catalog_notes': 'Major broadcaster SBS international sales arm. Vast catalog of K-dramas and variety shows. Active in format sales and finished content distribution.'
    },
    # Platform
    {
        'name': 'Netflix Korea',
        'type': 'Platform',
        'market': 'korea',
        'linkedin_url': 'https://www.linkedin.com/company/netflix/',
        'catalog_size': '50+ Korean originals',
        'catalog_notes': 'Platform anchor for Korea. Co-production deals with major studios. Their Korean content has proven massive global appeal - key partner for dubbing investments.'
    },
    
    # ==========================================
    # AVOD/FAST PLATFORMS (USA)
    # ==========================================
    # Secondary ICP #5 - Head of Programming
    # Minutes watched = revenue, localization quality affects RPMs
    
    {
        'name': 'Tubi',
        'type': 'AVOD Platform',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/tubi-tv/',
        'catalog_size': '50,000+ titles',
        'catalog_notes': 'Fox-owned AVOD leader. Minutes watched = revenue. Major buyer of international content for English-speaking audiences. Localization quality directly affects engagement and RPMs.'
    },
    {
        'name': 'Pluto TV',
        'type': 'AVOD Platform',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/pluto-tv/',
        'catalog_size': '250+ channels, 100,000+ hours',
        'catalog_notes': 'Paramount-owned FAST leader. Linear and on-demand programming. Strong international content slate. Ad-supported model means engagement drives revenue directly.'
    },
    {
        'name': 'Roku Channel',
        'type': 'AVOD Platform',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/roku/',
        'catalog_size': '80,000+ titles',
        'catalog_notes': 'Hardware + content play. Massive US reach through Roku devices. Growing original content and licensed international programming. Engagement metrics tied to ad revenue.'
    },
    {
        'name': 'Freevee',
        'type': 'AVOD Platform',
        'market': 'usa',
        'linkedin_url': 'https://www.linkedin.com/company/amazon/',
        'catalog_size': '20,000+ titles',
        'catalog_notes': 'Amazon-owned AVOD (formerly IMDb TV). Integrated with Prime Video ecosystem. Strong focus on licensed content and originals. Key player in ad-supported streaming.'
    }
]


def get_companies_by_market(market: str) -> list:
    """Get all companies for a specific market."""
    return [c for c in COMPANIES if c['market'] == market]


def get_companies_by_type(company_type: str) -> list:
    """Get all companies of a specific type."""
    return [c for c in COMPANIES if c['type'] == company_type]


def get_tier1_companies() -> list:
    """Get companies from Tier 1 markets (UK, USA, Spain)."""
    tier1_markets = ['uk', 'usa', 'spain']
    return [c for c in COMPANIES if c['market'] in tier1_markets]


def get_tier2_companies() -> list:
    """Get companies from Tier 2 markets (Germany, France, Korea)."""
    tier2_markets = ['germany', 'france', 'korea']
    return [c for c in COMPANIES if c['market'] in tier2_markets]


def get_avod_companies() -> list:
    """Get AVOD/FAST platform companies."""
    return [c for c in COMPANIES if c['type'] == 'AVOD Platform']


def get_producers() -> list:
    """Get all producer companies."""
    return [c for c in COMPANIES if c['type'] == 'Producer']


def get_distributors() -> list:
    """Get all distributor companies."""
    return [c for c in COMPANIES if c['type'] == 'Distributor']


def get_platforms() -> list:
    """Get all platform companies (including AVOD)."""
    return [c for c in COMPANIES if 'Platform' in c['type']]


def get_all_companies() -> list:
    """Get all companies."""
    return COMPANIES


def get_company_domains() -> dict:
    """
    Get company domains for Apify filtering.
    Returns dict mapping company name to likely domain.
    
    This is the SINGLE SOURCE OF TRUTH for company→domain mappings.
    All other modules should import from here.
    """
    domains = {
        # UK Companies
        'BBC Studios': 'bbcstudios.com',
        'BBC': 'bbc.com',
        'ITV Studios': 'itvstudios.com',
        'ITV': 'itv.com',
        'All3Media': 'all3media.com',
        'Sky Studios': 'sky.com',
        'Sky': 'sky.com',
        'Channel 4': 'channel4.com',
        
        # USA - Major Studios
        'Lionsgate': 'lionsgate.com',
        'Sony Pictures Entertainment': 'sonypictures.com',
        'Sony Pictures': 'sonypictures.com',
        'Sony': 'sonypictures.com',
        'Warner Bros. Discovery': 'wbd.com',
        'Warner Bros': 'wbd.com',
        'WBD': 'wbd.com',
        'HBO': 'wbd.com',
        'Discovery': 'wbd.com',
        'Paramount': 'paramount.com',
        'Paramount Global': 'paramount.com',
        'Disney': 'disney.com',
        'Universal': 'nbcuniversal.com',
        'NBCUniversal': 'nbcuniversal.com',
        'Universal Pictures Content Group': 'nbcuniversal.com',
        'UPCG': 'nbcuniversal.com',
        'MGM': 'amazon.com',
        
        # USA - Streaming/AVOD
        'Netflix': 'netflix.com',
        'Netflix US': 'netflix.com',
        'Amazon': 'amazon.com',
        'Prime Video': 'amazon.com',
        'Tubi': 'tubi.tv',
        'Pluto TV': 'pluto.tv',
        'Roku': 'roku.com',
        'Roku Channel': 'roku.com',
        'Freevee': 'amazon.com',
        'Peacock': 'nbcuniversal.com',
        'Audible': 'audible.com',
        
        # Spain
        'Atresmedia Studios': 'atresmedia.com',
        'Atresmedia': 'atresmedia.com',
        'Mediapro': 'mediapro.tv',
        'Beta Film': 'betafilm.com',
        'Netflix Spain': 'netflix.com',
        
        # Germany
        'UFA': 'ufa.de',
        'Constantin Film': 'constantin-film.de',
        'Beta Film DE': 'betafilm.com',
        'RTL+ Germany': 'rtl.de',
        'RTL': 'rtl.de',
        'ZDF Studios': 'zdf-studios.com',
        
        # France
        'Gaumont': 'gaumont.com',
        'StudioCanal': 'studiocanal.com',
        'STUDIOCANAL': 'studiocanal.com',
        'Studiocanal': 'studiocanal.com',
        'Newen Distribution': 'newen.com',
        'Newen': 'newen.com',
        'Canal+': 'canalplus.com',
        'Canal+ Group': 'canalplus.com',
        
        # Korea
        'Studio Dragon': 'studiodragon.net',
        'CJ ENM': 'cjenm.com',
        'CJ ENM International': 'cjenm.com',
        'SBS Contents Hub': 'sbs.co.kr',
        'SBS': 'sbs.co.kr',
        'Netflix Korea': 'netflix.com',
        'TVING': 'tving.com',
    }
    return domains


def get_domain_for_company(company_name: str) -> str:
    """
    Get domain for a company name (fuzzy matching).
    
    Args:
        company_name: Company name to look up
        
    Returns:
        Domain string or None if not found
    """
    if not company_name:
        return None
    
    domains = get_company_domains()
    company_lower = company_name.lower()
    
    # Try exact match first
    for name, domain in domains.items():
        if name.lower() == company_lower:
            return domain
    
    # Try partial match
    for name, domain in domains.items():
        if name.lower() in company_lower or company_lower in name.lower():
            return domain
    
    return None


# ============================================================================
# COMPANY-SPECIFIC EMAIL PATTERNS
# ============================================================================

# Some companies use different email patterns than first.last@domain
# Key is domain, value is pattern template
COMPANY_EMAIL_PATTERNS = {
    # Netflix uses firstlast (no dot)
    'netflix.com': '{first}{last}@{domain}',
    
    # Most companies use first.last (default)
    'default': '{first}.{last}@{domain}',
}


def get_email_pattern_for_domain(domain: str) -> str:
    """
    Get the email pattern template for a domain.
    
    Args:
        domain: Company email domain
        
    Returns:
        Email pattern template string
    """
    return COMPANY_EMAIL_PATTERNS.get(domain, COMPANY_EMAIL_PATTERNS['default'])


def generate_email(first_name: str, last_name: str, domain: str) -> str:
    """
    Generate email address for a person at a company.
    Uses company-specific patterns when known.
    
    Args:
        first_name: First name
        last_name: Last name
        domain: Company email domain
        
    Returns:
        Generated email address
    """
    import re
    
    # Clean names (remove accents, special chars)
    def clean_name(name: str) -> str:
        if not name:
            return ''
        # Simple transliteration
        replacements = {
            'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ã': 'a',
            'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
            'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
            'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
            'ñ': 'n', 'ç': 'c', 'ß': 'ss',
        }
        result = name.lower()
        for old, new in replacements.items():
            result = result.replace(old, new)
        # Remove non-alphanumeric
        result = re.sub(r'[^a-z0-9]', '', result)
        return result
    
    first = clean_name(first_name)
    last = clean_name(last_name)
    
    if not first or not last:
        return None
    
    pattern = get_email_pattern_for_domain(domain)
    return pattern.format(first=first, last=last, domain=domain)


# Summary counts
def get_summary() -> dict:
    """Get summary counts of companies by type and market."""
    summary = {
        'total': len(COMPANIES),
        'by_type': {},
        'by_market': {},
        'by_tier': {
            'tier1': len(get_tier1_companies()),
            'tier2': len(get_tier2_companies()),
        }
    }
    
    for c in COMPANIES:
        # By type
        t = c['type']
        summary['by_type'][t] = summary['by_type'].get(t, 0) + 1
        
        # By market
        m = c['market']
        summary['by_market'][m] = summary['by_market'].get(m, 0) + 1
    
    return summary
