"""
VFX Buyer Persona Definitions
===============================

4-tier persona structure for VFX house sales targeting.

Every serious opportunity should have:
  1. One economic buyer
  2. One technical champion
  3. One active user group

If any are missing, it's not a qualified deal.

Shortcut:
  - Sell value to Post/Production leadership
  - Prove capability with Supervisors
  - Drive adoption through Artists
"""

# ============================================================================
# TIER 1: ECONOMIC BUYERS (sign budget / approve vendors)
# ============================================================================
# These are your primary commercial targets.
# They care about: cost per shot, schedule risk, capacity constraints,
# competitive differentiation.
# If you don't reach one of these, you're usually stuck in pilot land.

ECONOMIC_BUYER_TITLES = [
    # Core titles
    'Head of Post',
    'Head of Post Production',
    'Head of Production',
    'Managing Director',
    'Executive Producer',
    'Head of VFX',
    'COO',
    'Chief Operating Officer',
    'Operations Director',
    'Head of Operations',
    'Director of Operations',
    'VP Operations',
    'Head of Innovation',
    'Head of Emerging Technology',
    'Head of Technology',
    'Chief Technology Officer',
    'CTO',
    'CEO',
    'Chief Executive Officer',
    'President',
    'General Manager',
    'Studio Director',
    'Facility Director',
    'VP of Production',
    'SVP Production',
    'Director of Production',
    'Global Head of Production',
    'Chief Creative Officer',
]

# Keywords that identify economic buyers in title strings
ECONOMIC_BUYER_KEYWORDS = [
    'managing director',
    'executive producer',
    'head of post',
    'head of production',
    'head of vfx',
    'chief operating',
    'operations director',
    'head of operations',
    'head of innovation',
    'head of emerging tech',
    'head of technology',
    'chief technology',
    'chief executive',
    'chief creative',
    'president',
    'general manager',
    'studio director',
    'facility director',
    'vp of production',
    'vp production',
    'svp production',
    'director of production',
    'global head',
    'coo',
    'cto',
    'ceo',
]

# ============================================================================
# TIER 2: TECHNICAL CHAMPIONS (make it real internally)
# ============================================================================
# These are your critical enablers.
# They validate: quality, workflow fit, failure modes, artist acceptance.
# Without one of these on side, production adoption won't happen.

TECHNICAL_CHAMPION_TITLES = [
    'VFX Supervisor',
    'CG Supervisor',
    'Compositing Supervisor',
    'Head of 2D',
    'Head of Comp',
    'Head of Compositing',
    'Pipeline TD',
    'Head of Pipeline',
    'Pipeline Supervisor',
    'Pipeline Developer',
    'Senior Pipeline TD',
    'Lead Pipeline TD',
    'Technical Director',
    'Head of R&D',
    'R&D Lead',
    'Software Development Lead',
    'Head of Software',
    'DFX Supervisor',
    'Digital Effects Supervisor',
    'Senior VFX Supervisor',
    'Associate VFX Supervisor',
    'Head of CG',
    'CG Lead',
    'Head of 3D',
    'Lighting Supervisor',
    'Animation Supervisor',
    'FX Supervisor',
    'Effects Supervisor',
    'Look Development Supervisor',
    'Asset Supervisor',
]

TECHNICAL_CHAMPION_KEYWORDS = [
    'vfx supervisor',
    'cg supervisor',
    'compositing supervisor',
    'comp supervisor',
    'head of 2d',
    'head of comp',
    'head of compositing',
    'pipeline td',
    'head of pipeline',
    'pipeline supervisor',
    'pipeline developer',
    'technical director',
    'head of r&d',
    'r&d lead',
    'head of software',
    'dfx supervisor',
    'digital effects supervisor',
    'head of cg',
    'head of 3d',
    'lighting supervisor',
    'animation supervisor',
    'fx supervisor',
    'effects supervisor',
    'look dev supervisor',
    'asset supervisor',
]

# ============================================================================
# TIER 3: DAY-TO-DAY USERS (drive organic pull)
# ============================================================================
# These create bottom-up momentum.
# They feel the pain directly: cleanup volume, shot iteration fatigue,
# late-stage change pressure.
# They won't sign contracts - but they create internal demand.

DAY_TO_DAY_USER_TITLES = [
    'Senior Compositor',
    'Lead Compositor',
    'Compositor',
    'Lead Roto Artist',
    'Lead Paint Artist',
    'Roto/Paint Lead',
    'Prep Supervisor',
    'Prep Lead',
    'Sequence Lead',
    'Shot Lead',
    'Senior Roto Artist',
    'Senior Paint Artist',
    'Lead Matchmove Artist',
    'Matchmove Lead',
    'Senior Matchmove Artist',
    'Rotoscope Supervisor',
    'Paint Supervisor',
    'Cleanup Lead',
    'Senior Prep Artist',
    '2D Lead',
    '2D Artist Lead',
]

DAY_TO_DAY_USER_KEYWORDS = [
    'senior compositor',
    'lead compositor',
    'lead roto',
    'lead paint',
    'roto/paint lead',
    'roto paint lead',
    'prep supervisor',
    'prep lead',
    'sequence lead',
    'shot lead',
    'senior roto',
    'senior paint',
    'lead matchmove',
    'matchmove lead',
    'rotoscope supervisor',
    'paint supervisor',
    'cleanup lead',
    'senior prep',
    '2d lead',
    '2d artist lead',
]

# ============================================================================
# TIER 4: PROCUREMENT / COMMERCIAL (later-stage only)
# ============================================================================
# Engage once value is proven.
# They care about: pricing model, contract terms, risk.
# NEVER lead with these.

PROCUREMENT_TITLES = [
    'Procurement Manager',
    'Commercial Manager',
    'Vendor Management',
    'Vendor Manager',
    'Head of Procurement',
    'Purchasing Manager',
    'Commercial Director',
    'Head of Commercial',
    'Finance Director',
    'CFO',
    'Chief Financial Officer',
    'Finance Manager',
    'Business Affairs',
    'Head of Business Affairs',
    'Contract Manager',
    'Sourcing Manager',
]

PROCUREMENT_KEYWORDS = [
    'procurement',
    'vendor management',
    'vendor manager',
    'purchasing',
    'commercial manager',
    'commercial director',
    'head of commercial',
    'business affairs',
    'contract manager',
    'sourcing manager',
    'finance director',
    'finance manager',
]


# ============================================================================
# TIER CLASSIFICATION
# ============================================================================

TIER_DEFINITIONS = {
    'economic_buyer': {
        'label': 'Economic Buyer',
        'short': 'EB',
        'description': 'Signs budget, approves vendors',
        'priority': 1,
        'keywords': ECONOMIC_BUYER_KEYWORDS,
        'titles': ECONOMIC_BUYER_TITLES,
        'cares_about': [
            'Cost per shot',
            'Schedule risk',
            'Capacity constraints',
            'Competitive differentiation',
        ],
        'approach': 'Sell value to Post/Production leadership',
    },
    'technical_champion': {
        'label': 'Technical Champion',
        'short': 'TC',
        'description': 'Makes it real internally',
        'priority': 2,
        'keywords': TECHNICAL_CHAMPION_KEYWORDS,
        'titles': TECHNICAL_CHAMPION_TITLES,
        'cares_about': [
            'Quality',
            'Workflow fit',
            'Failure modes',
            'Artist acceptance',
        ],
        'approach': 'Prove capability with Supervisors',
    },
    'day_to_day_user': {
        'label': 'Day-to-Day User',
        'short': 'USER',
        'description': 'Drives organic pull',
        'priority': 3,
        'keywords': DAY_TO_DAY_USER_KEYWORDS,
        'titles': DAY_TO_DAY_USER_TITLES,
        'cares_about': [
            'Cleanup volume',
            'Shot iteration fatigue',
            'Late-stage change pressure',
        ],
        'approach': 'Drive adoption through Artists',
    },
    'procurement': {
        'label': 'Procurement',
        'short': 'PROC',
        'description': 'Later-stage only',
        'priority': 4,
        'keywords': PROCUREMENT_KEYWORDS,
        'titles': PROCUREMENT_TITLES,
        'cares_about': [
            'Pricing model',
            'Contract terms',
            'Risk',
        ],
        'approach': 'Engage once value is proven. Never lead with these.',
    },
}


def classify_title(title: str) -> str:
    """
    Classify a job title into a persona tier.
    
    Args:
        title: Job title string
        
    Returns:
        Tier key: 'economic_buyer', 'technical_champion', 
        'day_to_day_user', 'procurement', or 'unclassified'
    """
    if not title:
        return 'unclassified'
    
    title_lower = title.lower().strip()
    
    import re
    
    # Exclude low-level roles that might match substrings
    exclude_indicators = ['coordinator', 'intern', 'runner', 'receptionist', 'assistant']
    if any(ind in title_lower for ind in exclude_indicators):
        # Only exclude if there's no strong tier keyword present (word-boundary match)
        strong_keywords = [r'\bhead of\b', r'\bdirector\b', r'\bsupervisor\b', r'\bmanager\b',
                          r'\bvp\b', r'\bchief\b', r'\bcoo\b', r'\bcto\b', r'\bceo\b']
        if not any(re.search(sk, title_lower) for sk in strong_keywords):
            return 'unclassified'
    
    # Check each tier in priority order
    # Use word-boundary matching for short keywords (coo, cto, ceo) to avoid
    # false positives like "coordinator" matching "coo"
    SHORT_KEYWORDS = {'coo', 'cto', 'ceo'}
    
    for tier_key in ['economic_buyer', 'technical_champion', 'day_to_day_user', 'procurement']:
        tier = TIER_DEFINITIONS[tier_key]
        for keyword in tier['keywords']:
            if keyword in SHORT_KEYWORDS:
                # Use word boundary for short acronyms
                if re.search(r'\b' + keyword + r'\b', title_lower):
                    return tier_key
            else:
                if keyword in title_lower:
                    return tier_key
    
    return 'unclassified'


def get_tier_label(tier_key: str) -> str:
    """Get human-readable label for a tier."""
    tier = TIER_DEFINITIONS.get(tier_key)
    if tier:
        return tier['label']
    return 'Unclassified'


def get_tier_short(tier_key: str) -> str:
    """Get short code for a tier (for Excel columns)."""
    tier = TIER_DEFINITIONS.get(tier_key)
    if tier:
        return tier['short']
    return '?'


def get_all_target_titles() -> list:
    """Get flat list of all target titles across all tiers."""
    all_titles = []
    for tier in TIER_DEFINITIONS.values():
        all_titles.extend(tier['titles'])
    return all_titles


def get_titles_for_tier(tier_key: str) -> list:
    """Get title list for a specific tier."""
    tier = TIER_DEFINITIONS.get(tier_key)
    if tier:
        return tier['titles']
    return []


def check_deal_qualification(leads_by_tier: dict) -> dict:
    """
    Check if a company has qualified deal coverage.
    
    A qualified deal requires:
      1. At least one Economic Buyer
      2. At least one Technical Champion
      3. At least one Day-to-Day User group member
    
    Args:
        leads_by_tier: Dict mapping tier_key -> count of leads
        
    Returns:
        Dict with qualification status and missing tiers
    """
    required = ['economic_buyer', 'technical_champion', 'day_to_day_user']
    present = [t for t in required if leads_by_tier.get(t, 0) > 0]
    missing = [t for t in required if leads_by_tier.get(t, 0) == 0]
    
    return {
        'qualified': len(missing) == 0,
        'present_tiers': present,
        'missing_tiers': missing,
        'coverage': f"{len(present)}/3",
        'summary': 'QUALIFIED' if len(missing) == 0 else f"Missing: {', '.join(get_tier_label(t) for t in missing)}",
    }


# ============================================================================
# SALES NAVIGATOR SEARCH TITLES
# ============================================================================
# These are the exact title strings to use in LinkedIn Sales Navigator filters.

SALES_NAV_SEARCH_TITLES = {
    'economic_buyer': [
        'Head of Post Production',
        'Head of Production',
        'Managing Director',
        'Executive Producer',
        'Head of VFX',
        'COO',
        'Chief Operating Officer',
        'Operations Director',
        'Head of Operations',
        'Head of Innovation',
        'Head of Technology',
        'Chief Technology Officer',
        'CTO',
        'CEO',
        'President',
        'General Manager',
        'Studio Director',
        'Chief Creative Officer',
    ],
    'technical_champion': [
        'VFX Supervisor',
        'CG Supervisor',
        'Compositing Supervisor',
        'Head of 2D',
        'Head of Comp',
        'Pipeline TD',
        'Head of Pipeline',
        'Pipeline Supervisor',
        'Technical Director',
        'Head of R&D',
        'Head of CG',
        'Head of 3D',
        'DFX Supervisor',
        'Lighting Supervisor',
        'Animation Supervisor',
        'FX Supervisor',
        'Look Development Supervisor',
    ],
    'day_to_day_user': [
        'Senior Compositor',
        'Lead Compositor',
        'Lead Roto Artist',
        'Lead Paint Artist',
        'Prep Supervisor',
        'Sequence Lead',
        'Senior Roto Artist',
        'Lead Matchmove Artist',
        'Rotoscope Supervisor',
        'Paint Supervisor',
        '2D Lead',
    ],
    'procurement': [
        'Procurement Manager',
        'Commercial Manager',
        'Vendor Manager',
        'Head of Procurement',
        'Commercial Director',
        'Head of Commercial',
        'Finance Director',
    ],
}


if __name__ == '__main__':
    # Test classification
    test_titles = [
        "Managing Director",
        "Head of Post Production",
        "VFX Supervisor",
        "CG Supervisor",
        "Head of Pipeline",
        "Senior Compositor",
        "Lead Roto Artist",
        "Procurement Manager",
        "Junior Artist",
        "Production Coordinator",
    ]
    
    print("Title Classification Test:")
    print("-" * 60)
    for title in test_titles:
        tier = classify_title(title)
        label = get_tier_label(tier)
        print(f"  {title:<35} -> {label}")
