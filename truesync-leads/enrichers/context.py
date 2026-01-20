"""
Catalog Context Enrichment
==========================

Adds catalog context to leads for personalized outreach.
Pulls from TMDb and stored company data.
"""

from typing import Optional, Dict
from scrapers.catalog import TMDbClient
from data.companies import COMPANIES


class CatalogContextEnricher:
    """
    Enriches leads with catalog context for their company.
    
    This helps sales reps personalize outreach by mentioning
    specific titles that could benefit from TrueSync.
    """
    
    def __init__(self):
        self.tmdb_client = TMDbClient()
        
        # Build company lookup
        self.company_data = {c['name']: c for c in COMPANIES}
    
    def get_context_for_lead(
        self,
        company_name: str,
        market: str
    ) -> str:
        """
        Get catalog context string for a lead.
        
        Args:
            company_name: Name of the lead's company
            market: Market (spain/korea/france)
            
        Returns:
            Context string for the lead
        """
        # First, get stored catalog notes
        company_info = self.company_data.get(company_name, {})
        catalog_notes = company_info.get('catalog_notes', '')
        catalog_size = company_info.get('catalog_size', '')
        
        # Try to get TMDb data for specific titles
        tmdb_context = self.tmdb_client.get_catalog_context_for_lead(
            company_name, market
        )
        
        # Combine into a useful context string
        parts = []
        
        if catalog_size:
            parts.append(catalog_size)
        
        if tmdb_context and 'not available' not in tmdb_context.lower():
            parts.append(tmdb_context)
        elif catalog_notes:
            # Use stored notes if TMDb doesn't have data
            parts.append(catalog_notes[:200])
        
        return ' | '.join(parts) if parts else 'Catalog data not available'
    
    def get_full_catalog_data(
        self,
        company_name: str,
        market: str
    ) -> Dict:
        """
        Get full catalog data for a company.
        
        Used for the Catalog Intelligence sheet in Excel output.
        
        Args:
            company_name: Name of the company
            market: Market (spain/korea/france)
            
        Returns:
            Dictionary with full catalog information
        """
        company_info = self.company_data.get(company_name, {})
        tmdb_catalog = self.tmdb_client.get_catalog_for_company(company_name, market)
        
        return {
            'company': company_name,
            'market': market,
            'type': company_info.get('type', 'Unknown'),
            'catalog_size': company_info.get('catalog_size', 'Unknown'),
            'catalog_notes': company_info.get('catalog_notes', ''),
            'linkedin_url': company_info.get('linkedin_url', ''),
            'tmdb_movies': tmdb_catalog.get('movies', []),
            'tmdb_tv_shows': tmdb_catalog.get('tv_shows', []),
            'non_english_count': tmdb_catalog.get('non_english_count', 0),
            'tmdb_summary': tmdb_catalog.get('summary', '')
        }
    
    def get_outreach_talking_points(
        self,
        company_name: str,
        market: str
    ) -> list:
        """
        Generate talking points for outreach.
        
        Args:
            company_name: Name of the company
            market: Market (spain/korea/france)
            
        Returns:
            List of talking points
        """
        catalog = self.get_full_catalog_data(company_name, market)
        points = []
        
        # Market-specific talking point
        market_messages = {
            'uk': 'British content has proven global appeal - from Doctor Who to Fleabag. TrueSync can help unlock non-English markets.',
            'usa': 'US studios lead global content distribution. TrueSync can help your international content reach English-speaking audiences.',
            'spain': 'Spanish content has massive global appeal - La Casa de Papel proved it. TrueSync unlocks English-speaking markets.',
            'germany': 'German content is underleveraged in English markets. High production values + TrueSync = global opportunity.',
            'france': 'French prestige content travels well when properly localized. Lupin proved it. TrueSync can help scale this.',
            'korea': 'K-drama is the hottest content category globally. Squid Game showed the potential. TrueSync can accelerate localization.'
        }
        
        if market in market_messages:
            points.append(market_messages[market])
        
        # Catalog size talking point
        if catalog.get('catalog_size'):
            points.append(f"Your catalog of {catalog['catalog_size']} represents significant dubbing opportunity.")
        
        # Specific titles talking point
        movies = catalog.get('tmdb_movies', [])
        shows = catalog.get('tmdb_tv_shows', [])
        
        if movies or shows:
            titles = [m['title'] for m in movies[:2]] + [s['title'] for s in shows[:2]]
            if titles:
                points.append(f"Titles like {', '.join(titles)} could reach English-speaking audiences with TrueSync.")
        
        # ROI talking point
        if catalog.get('non_english_count', 0) > 5:
            points.append(
                f"With {catalog['non_english_count']}+ non-English titles, "
                "TrueSync could significantly expand your addressable market."
            )
        
        return points


# Example usage
if __name__ == '__main__':
    enricher = CatalogContextEnricher()
    
    # Test with Gaumont
    context = enricher.get_context_for_lead('Gaumont', 'france')
    print(f"\nGaumont context: {context}")
    
    points = enricher.get_outreach_talking_points('Gaumont', 'france')
    print("\nTalking points:")
    for p in points:
        print(f"  - {p}")
