"""
Lead Scoring Engine
===================

Scores leads based on multiple factors to prioritize outreach.

Scoring Factors (from plan):
- Role Relevance: 25%
- Catalog Volume: 25%
- Market Priority: 20%
- Decision Authority: 15%
- Company Type: 15%
"""

import os
import re
from typing import Optional
import yaml


class LeadScorer:
    """
    Calculates priority scores for leads.
    
    Score range: 1-100
    Higher scores = higher priority for outreach
    """
    
    # Default weights (can be overridden by config)
    DEFAULT_WEIGHTS = {
        'role_relevance': 0.25,
        'catalog_volume': 0.25,
        'market_priority': 0.20,
        'decision_authority': 0.15,
        'company_type': 0.15
    }
    
    # Role keywords and their scores (0-100)
    ROLE_SCORES = {
        # DISTRIBUTION - Highest priority
        'head of distribution': 100,
        'vp distribution': 98,
        'svp distribution': 100,
        'evp distribution': 100,
        'president of distribution': 100,
        'head of international distribution': 100,
        'vp international distribution': 98,
        'director of distribution': 90,
        
        # LICENSING AND SALES - Highest priority
        'head of licensing': 100,
        'vp licensing': 98,
        'svp licensing': 100,
        'head of sales': 98,
        'vp sales': 95,
        'head of international sales': 100,
        'vp international sales': 98,
        'director of content sales': 90,
        'head of content licensing': 98,
        
        # M&A AND ACQUISITIONS - High priority
        'head of m&a': 100,
        'vp m&a': 98,
        'svp m&a': 100,
        'head of acquisitions': 98,
        'vp acquisitions': 95,
        'director of acquisitions': 88,
        'head of business development': 95,
        'vp business development': 92,
        'svp business development': 95,
        
        # C-SUITE AND COMMERCIAL STRATEGY - Very high priority
        'cfo': 100,
        'chief financial officer': 100,
        'svp commercial strategy': 100,
        'vp commercial strategy': 98,
        'head of commercial strategy': 98,
        'chief commercial officer': 100,
        'cco': 100,
        'chief strategy officer': 98,
        'cso': 98,
        
        # PRODUCTION, PROGRAMMING & OPERATIONS - High priority
        'svp production': 95,
        'vp production': 90,
        'head of production': 92,
        'svp programming': 95,
        'vp programming': 90,
        'head of programming': 92,
        'svp operations': 90,
        'vp operations': 85,
        'head of operations': 88,
        'chief content officer': 100,
        'chief operating officer': 95,
        'coo': 95,
        
        # Other relevant roles
        'head of international': 95,
        'head of global': 95,
        'vp international': 92,
        'svp international': 95,
        'evp': 95,
        'head of fast': 88,
        'head of avod': 88,
        
        # Consumer Insights / Data Science (Validation Partners)
        'head of consumer insights': 85,
        'vp data science': 82,
        'head of content analytics': 85,
        'vp consumer research': 80,
        'director of audience insights': 78,
        'head of research': 80,
        'svp consumer insights': 88,
        
        # Studio Business Owners (Label/Franchise)
        'president of studio': 100,
        'studio head': 98,
        'head of label': 95,
        'evp franchise development': 92,
        'svp franchise strategy': 90,
        'general manager': 85,
        
        # International Originals Leadership
        'head of international originals': 95,
        'vp local originals': 90,
        'head of local content': 88,
        'svp international originals': 95,
        'director of originals': 85,
        
        # Lower priority but still relevant
        'director': 75,
        'senior director': 80,
        'manager': 50,
        'senior manager': 55,
        'coordinator': 40,
        'associate': 35,
        'assistant': 30,
    }
    
    # Authority level scores based on title prefix
    AUTHORITY_SCORES = {
        'chief': 100,
        'ceo': 100,
        'coo': 95,
        'cco': 95,
        'president': 95,
        'evp': 90,
        'executive vice president': 90,
        'svp': 85,
        'senior vice president': 85,
        'vp': 80,
        'vice president': 80,
        'head of': 80,
        'director': 70,
        'senior director': 75,
        'manager': 50,
        'senior manager': 55,
        'coordinator': 40,
        'associate': 35,
        'assistant': 30,
    }
    
    # Market priority multipliers
    # Tier 1 (Primary): UK, USA, Spain
    # Tier 2 (Expansion): Germany, France, Korea
    MARKET_MULTIPLIERS = {
        # Tier 1 - Primary
        'uk': 1.0,       # Gateway to US, highest priority
        'usa': 1.0,      # Greenlight power
        'spain': 0.95,   # Highest ROI for dubbing
        # Tier 2 - Expansion
        'germany': 0.85,  # High budgets, weak English penetration
        'france': 0.85,   # Prestige + volume
        'korea': 0.85     # Premium scripted, proven global appeal
    }
    
    # Company type multipliers
    COMPANY_TYPE_MULTIPLIERS = {
        'Distributor': 1.0,   # Direct sales path
        'Producer': 0.90,     # Content creators
        'Platform': 0.85      # Validation anchors
    }
    
    def __init__(self):
        self.weights = self._load_weights()
    
    def _load_weights(self) -> dict:
        """Load scoring weights from config."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            'config.yaml'
        )
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('scoring', self.DEFAULT_WEIGHTS)
        
        return self.DEFAULT_WEIGHTS
    
    def calculate_score(self, lead) -> int:
        """
        Calculate priority score for a lead.
        
        Args:
            lead: Lead object with title, market, company
            
        Returns:
            Integer score 1-100
        """
        # Get component scores
        role_score = self._score_role(lead.title)
        authority_score = self._score_authority(lead.title)
        market_score = self._score_market(lead.market)
        company_score = self._score_company_type(lead.company)
        catalog_score = self._score_catalog(lead.company)
        
        # Apply weights
        weights = self.weights
        
        weighted_score = (
            role_score * weights.get('role_relevance', 0.25) +
            catalog_score * weights.get('catalog_volume', 0.25) +
            market_score * weights.get('market_priority', 0.20) +
            authority_score * weights.get('decision_authority', 0.15) +
            company_score * weights.get('company_type', 0.15)
        )
        
        # Ensure score is in range 1-100
        final_score = max(1, min(100, int(weighted_score)))
        
        return final_score
    
    def _score_role(self, title: Optional[str]) -> int:
        """Score based on role relevance."""
        if not title:
            return 30
        
        title_lower = title.lower()
        
        # Check for matching role keywords
        best_score = 30  # Default for unknown roles
        
        for keyword, score in self.ROLE_SCORES.items():
            if keyword in title_lower:
                best_score = max(best_score, score)
        
        return best_score
    
    def _score_authority(self, title: Optional[str]) -> int:
        """Score based on decision-making authority level."""
        if not title:
            return 30
        
        title_lower = title.lower()
        
        # Check for authority indicators
        for keyword, score in self.AUTHORITY_SCORES.items():
            if keyword in title_lower:
                return score
        
        return 40  # Default for unknown authority
    
    def _score_market(self, market: Optional[str]) -> int:
        """Score based on market priority."""
        if not market:
            return 50
        
        market_lower = market.lower()
        multiplier = self.MARKET_MULTIPLIERS.get(market_lower, 0.7)
        
        return int(100 * multiplier)
    
    def _score_company_type(self, company) -> int:
        """Score based on company type."""
        if not company:
            return 50
        
        company_type = getattr(company, 'type', None)
        if not company_type:
            return 50
        
        multiplier = self.COMPANY_TYPE_MULTIPLIERS.get(company_type, 0.8)
        
        return int(100 * multiplier)
    
    def _score_catalog(self, company) -> int:
        """Score based on catalog size/volume."""
        if not company:
            return 50
        
        catalog_size = getattr(company, 'catalog_size', '')
        
        if not catalog_size:
            return 50
        
        # Parse catalog size string for rough volume estimate
        catalog_lower = catalog_size.lower()
        
        # Look for numbers
        numbers = re.findall(r'(\d+)', catalog_size)
        if numbers:
            # Get the largest number mentioned
            max_num = max(int(n) for n in numbers)
            
            # Score based on volume
            if max_num >= 5000:
                return 100
            elif max_num >= 1000:
                return 90
            elif max_num >= 500:
                return 80
            elif max_num >= 100:
                return 70
            else:
                return 60
        
        # Keyword-based scoring
        if 'large' in catalog_lower or 'major' in catalog_lower:
            return 80
        elif 'premium' in catalog_lower:
            return 75
        
        return 60  # Default
    
    def get_score_breakdown(self, lead) -> dict:
        """
        Get detailed breakdown of score components.
        
        Useful for debugging and explaining scores.
        
        Args:
            lead: Lead object
            
        Returns:
            Dictionary with component scores
        """
        return {
            'role_relevance': self._score_role(lead.title),
            'decision_authority': self._score_authority(lead.title),
            'market_priority': self._score_market(lead.market),
            'company_type': self._score_company_type(lead.company),
            'catalog_volume': self._score_catalog(lead.company),
            'final_score': self.calculate_score(lead)
        }


# Example usage and testing
if __name__ == '__main__':
    scorer = LeadScorer()
    
    # Test role scoring
    test_titles = [
        "VP International Distribution",
        "Head of Global Sales",
        "Director of Content Acquisitions",
        "Senior Manager, Partnerships",
        "Content Coordinator",
        "Chief Content Officer"
    ]
    
    print("Role Scoring Test:")
    print("-" * 60)
    for title in test_titles:
        role_score = scorer._score_role(title)
        authority_score = scorer._score_authority(title)
        print(f"{title}")
        print(f"  Role Score: {role_score}, Authority Score: {authority_score}")
    
    print("\nMarket Scoring:")
    for market in ['spain', 'korea', 'france']:
        print(f"  {market}: {scorer._score_market(market)}")
