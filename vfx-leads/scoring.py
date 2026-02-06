"""
VFX Lead Scoring Engine
========================

Scores leads based on persona tier, seniority, and company factors.

Scoring dimensions:
  1. Persona Tier (40%) - Economic Buyer > Technical Champion > User > Procurement
  2. Seniority (25%) - Head/Director/VP > Supervisor > Lead > Senior > Junior
  3. Company Relevance (20%) - Notable projects, parent company
  4. Market Priority (15%) - USA/UK > Canada > France > India

Score range: 1-100
"""

import re
from typing import Optional

from data.roles import classify_title, TIER_DEFINITIONS
from data.markets import get_market_multiplier


class VFXLeadScorer:
    """
    Calculates priority scores for VFX leads.
    """
    
    # ============================================================
    # WEIGHTS
    # ============================================================
    WEIGHTS = {
        'persona_tier': 0.40,
        'seniority': 0.25,
        'company_relevance': 0.20,
        'market_priority': 0.15,
    }
    
    # ============================================================
    # PERSONA TIER SCORES
    # ============================================================
    TIER_SCORES = {
        'economic_buyer': 100,
        'technical_champion': 85,
        'day_to_day_user': 55,
        'procurement': 40,
        'unclassified': 25,
    }
    
    # ============================================================
    # SENIORITY SCORES
    # ============================================================
    SENIORITY_KEYWORDS = {
        # C-suite / top leadership
        'chief': 100,
        'ceo': 100,
        'coo': 100,
        'cto': 100,
        'cfo': 95,
        'president': 100,
        
        # VP / Director level
        'evp': 95,
        'svp': 92,
        'vp': 88,
        'vice president': 88,
        'managing director': 95,
        'director': 80,
        'head of': 85,
        'global head': 95,
        
        # Supervisor level
        'supervisor': 75,
        'lead': 65,
        'senior': 60,
        
        # Individual contributor
        'artist': 40,
        'td': 55,
        'junior': 30,
        'assistant': 30,
        'coordinator': 35,
        'intern': 20,
    }
    
    # ============================================================
    # COMPANY RELEVANCE (notable projects = higher relevance)
    # ============================================================
    # Companies with blockbuster credits are higher priority targets
    HIGH_PROFILE_COMPANIES = {
        'Industrial Light & Magic (ILM)': 100,
        'DNEG': 100,
        'Framestore': 100,
        'Digital Domain': 100,
        'Moving Picture Company (MPC)': 100,
        'Sony Pictures Imageworks': 95,
        'Cinesite': 90,
        'Rodeo FX': 90,
        'Image Engine': 90,
        'FuseFX': 85,
        'BOT VFX': 85,
        'Zoic Studios': 85,
        'Crafty Apes': 85,
        'DreamWorks Animation': 95,
        'Pixar Animation Studios': 95,
        'The Mill': 90,
        'Union VFX': 85,
        'Spin VFX': 80,
        'MR. X': 80,
        'Tippett Studio': 80,
        'Cosa VFX': 80,
        'Whiskytree': 80,
        'Atomic Arts': 80,
        'One of Us': 80,
        'Milk VFX': 80,
        'Alchemy24': 85,
        'WeFX': 80,
        'VFX Legion': 80,
        'VisualCreatures': 80,
        'ZERO VFX': 80,
        'Territory Studio': 80,
        'Jellyfish Pictures': 75,
    }
    
    def calculate_score(self, lead: dict) -> int:
        """
        Calculate priority score for a lead.
        
        Args:
            lead: Dict with 'title', 'company', 'market', 'persona_tier' fields
            
        Returns:
            Integer score 1-100
        """
        title = lead.get('title', '')
        company = lead.get('company', '')
        market = lead.get('market', 'unknown')
        persona_tier = lead.get('persona_tier') or classify_title(title)
        
        # Component scores
        tier_score = self._score_tier(persona_tier)
        seniority_score = self._score_seniority(title)
        company_score = self._score_company(company, lead)
        market_score = self._score_market(market)
        
        # Weighted combination
        weighted = (
            tier_score * self.WEIGHTS['persona_tier'] +
            seniority_score * self.WEIGHTS['seniority'] +
            company_score * self.WEIGHTS['company_relevance'] +
            market_score * self.WEIGHTS['market_priority']
        )
        
        return max(1, min(100, int(weighted)))
    
    def _score_tier(self, tier: str) -> int:
        """Score based on persona tier."""
        return self.TIER_SCORES.get(tier, 25)
    
    def _score_seniority(self, title: Optional[str]) -> int:
        """Score based on seniority level from title."""
        if not title:
            return 30
        
        title_lower = title.lower()
        best_score = 30
        
        for keyword, score in self.SENIORITY_KEYWORDS.items():
            if keyword in title_lower:
                best_score = max(best_score, score)
        
        return best_score
    
    def _score_company(self, company: str, lead: dict) -> int:
        """Score based on company profile."""
        if not company:
            return 50
        
        # Check high-profile list
        score = self.HIGH_PROFILE_COMPANIES.get(company, 0)
        if score > 0:
            return score
        
        # Has notable projects -> higher score
        notable = lead.get('notable_projects', '')
        if notable:
            return 70
        
        # Has parent company -> usually bigger
        parent = lead.get('parent')
        if parent:
            return 65
        
        return 55  # Default for target companies
    
    def _score_market(self, market: str) -> int:
        """Score based on market priority."""
        multiplier = get_market_multiplier(market)
        return int(100 * multiplier)
    
    def get_score_breakdown(self, lead: dict) -> dict:
        """Get detailed breakdown of score components."""
        title = lead.get('title', '')
        company = lead.get('company', '')
        market = lead.get('market', 'unknown')
        persona_tier = lead.get('persona_tier') or classify_title(title)
        
        return {
            'persona_tier': persona_tier,
            'tier_score': self._score_tier(persona_tier),
            'seniority_score': self._score_seniority(title),
            'company_score': self._score_company(company, lead),
            'market_score': self._score_market(market),
            'final_score': self.calculate_score(lead),
        }


if __name__ == '__main__':
    scorer = VFXLeadScorer()
    
    test_leads = [
        {'title': 'Managing Director', 'company': 'DNEG', 'market': 'uk'},
        {'title': 'Head of Post Production', 'company': 'Framestore', 'market': 'uk'},
        {'title': 'VFX Supervisor', 'company': 'Industrial Light & Magic (ILM)', 'market': 'usa'},
        {'title': 'CG Supervisor', 'company': 'Rodeo FX', 'market': 'canada'},
        {'title': 'Head of Pipeline', 'company': 'DNEG', 'market': 'uk'},
        {'title': 'Senior Compositor', 'company': 'Cinesite', 'market': 'uk'},
        {'title': 'Lead Roto Artist', 'company': 'MR. X', 'market': 'canada'},
        {'title': 'Procurement Manager', 'company': 'Framestore', 'market': 'uk'},
        {'title': 'Junior Artist', 'company': 'BlueBolt', 'market': 'uk'},
    ]
    
    print("VFX Lead Scoring Test:")
    print("-" * 80)
    for lead in test_leads:
        breakdown = scorer.get_score_breakdown(lead)
        print(f"  {lead['title']:<30} @ {lead['company']:<20} -> "
              f"Score: {breakdown['final_score']:>3} "
              f"({breakdown['persona_tier']})")
