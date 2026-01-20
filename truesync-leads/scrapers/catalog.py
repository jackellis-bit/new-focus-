"""
TMDb Catalog Integration
========================

Fetches non-English catalog information for companies using TMDb API.
This data helps personalize outreach by showing what content
each company has that could benefit from TrueSync dubbing.
"""

import os
from typing import List, Dict, Optional
import requests


class TMDbClient:
    """
    Client for TMDb (The Movie Database) API.
    
    Used to lookup:
    - Production company catalogs
    - Non-English content by company
    - Popular titles that need English dubbing
    
    Supports two authentication methods:
    - TMDB_API_KEY: API key as query parameter (v3)
    - TMDB_ACCESS_TOKEN: Bearer token in header (more secure)
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    # Mapping of our company names to TMDb company IDs
    # (These need to be looked up manually or via search)
    COMPANY_IDS = {
        # UK - Tier 1
        'BBC Studios': 3324,
        'ITV Studios': 9168,
        'All3Media': 14080,
        'Fremantle UK': 2806,
        'Sky Studios': 16614,
        
        # USA - Tier 1
        'Lionsgate': 1632,
        'Sony Pictures Entertainment': 34,
        'Paramount Global': 4,
        'Warner Bros. Discovery': 174,
        'Netflix US': 213,
        
        # Spain - Tier 1
        'Atresmedia Studios': 36404,
        'Mediapro': 11573,
        'Beta Film': None,  # Distributor, not in TMDb
        'Latido Films': 1444,
        'Netflix Spain': 213,
        
        # Germany - Tier 2
        'UFA': 595,
        'Constantin Film': 238,
        'Beta Film DE': None,
        'ZDF Studios': 7036,
        'RTL+ Germany': None,
        
        # France - Tier 2
        'Gaumont': 9,
        'StudioCanal': 694,
        'StudioCanal Sales': 694,
        'Newen Distribution': None,
        'Canal+': 285,
        
        # Korea - Tier 2
        'Studio Dragon': 84430,
        'CJ ENM': 4399,
        'CJ ENM International': 4399,
        'SBS Contents Hub': 27436,
        'Netflix Korea': 213,
        
        # AVOD/FAST Platforms - USA
        'Tubi': None,  # AVOD platform, not in TMDb as producer
        'Pluto TV': None,  # AVOD platform
        'Roku Channel': None,  # AVOD platform
        'Freevee': None,  # Amazon AVOD
    }
    
    # Language codes for our target markets
    LANGUAGE_CODES = {
        'uk': 'en',
        'usa': 'en',
        'spain': 'es',
        'germany': 'de',
        'france': 'fr',
        'korea': 'ko'
    }
    
    def __init__(self):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.access_token = os.getenv('TMDB_ACCESS_TOKEN')
        
        if not self.api_key and not self.access_token:
            print("Warning: TMDB_API_KEY or TMDB_ACCESS_TOKEN not set. Catalog lookup will be limited.")
    
    def _make_request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make a request to TMDb API."""
        if not self.api_key and not self.access_token:
            return None
        
        params = params or {}
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {}
        
        # Use Bearer token if available (more secure), otherwise use API key
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            headers['accept'] = 'application/json'
        else:
            params['api_key'] = self.api_key
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"  TMDb API error: {e}")
            return None
    
    def search_company(self, company_name: str) -> Optional[int]:
        """
        Search for a company and return its TMDb ID.
        
        Args:
            company_name: Name of the production company
            
        Returns:
            TMDb company ID or None
        """
        # First check our mapping
        if company_name in self.COMPANY_IDS:
            return self.COMPANY_IDS[company_name]
        
        # Otherwise search
        data = self._make_request('search/company', {'query': company_name})
        
        if data and data.get('results'):
            return data['results'][0].get('id')
        
        return None
    
    def get_company_movies(
        self,
        company_id: int,
        language: str = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Get movies produced by a company.
        
        Args:
            company_id: TMDb company ID
            language: Filter by original language (e.g., 'es', 'ko', 'fr')
            max_results: Maximum number of results
            
        Returns:
            List of movie dictionaries
        """
        data = self._make_request(
            f'discover/movie',
            {
                'with_companies': company_id,
                'sort_by': 'popularity.desc',
                'with_original_language': language
            }
        )
        
        if not data:
            return []
        
        movies = []
        for movie in data.get('results', [])[:max_results]:
            movies.append({
                'title': movie.get('title'),
                'original_title': movie.get('original_title'),
                'original_language': movie.get('original_language'),
                'release_date': movie.get('release_date'),
                'popularity': movie.get('popularity'),
                'overview': movie.get('overview', '')[:200]
            })
        
        return movies
    
    def get_company_tv_shows(
        self,
        company_id: int,
        language: str = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Get TV shows produced by a company.
        
        Args:
            company_id: TMDb company ID
            language: Filter by original language
            max_results: Maximum number of results
            
        Returns:
            List of TV show dictionaries
        """
        data = self._make_request(
            f'discover/tv',
            {
                'with_companies': company_id,
                'sort_by': 'popularity.desc',
                'with_original_language': language
            }
        )
        
        if not data:
            return []
        
        shows = []
        for show in data.get('results', [])[:max_results]:
            shows.append({
                'title': show.get('name'),
                'original_title': show.get('original_name'),
                'original_language': show.get('original_language'),
                'first_air_date': show.get('first_air_date'),
                'popularity': show.get('popularity'),
                'overview': show.get('overview', '')[:200]
            })
        
        return shows
    
    def get_catalog_for_company(
        self,
        company_name: str,
        market: str
    ) -> Dict:
        """
        Get full catalog information for a company.
        
        Args:
            company_name: Name of the company
            market: Market (spain/korea/france)
            
        Returns:
            Dictionary with movies, TV shows, and summary
        """
        company_id = self.search_company(company_name)
        
        if not company_id:
            return {
                'company': company_name,
                'market': market,
                'movies': [],
                'tv_shows': [],
                'summary': f'No TMDb data found for {company_name}'
            }
        
        language = self.LANGUAGE_CODES.get(market)
        
        movies = self.get_company_movies(company_id, language, max_results=10)
        tv_shows = self.get_company_tv_shows(company_id, language, max_results=10)
        
        # Count non-English content
        non_english_movies = [m for m in movies if m.get('original_language') != 'en']
        non_english_shows = [s for s in tv_shows if s.get('original_language') != 'en']
        
        summary = (
            f"{len(non_english_movies)} non-English films, "
            f"{len(non_english_shows)} non-English TV shows. "
            f"Top titles: {', '.join([m['title'] for m in movies[:3]])}"
        )
        
        return {
            'company': company_name,
            'company_id': company_id,
            'market': market,
            'movies': movies,
            'tv_shows': tv_shows,
            'non_english_count': len(non_english_movies) + len(non_english_shows),
            'summary': summary
        }
    
    def get_catalog_context_for_lead(
        self,
        company_name: str,
        market: str
    ) -> str:
        """
        Get a concise catalog context string for a lead.
        
        This is used in the Excel output to help personalize outreach.
        
        Args:
            company_name: Name of the company
            market: Market (spain/korea/france)
            
        Returns:
            String summarizing the company's non-English catalog
        """
        catalog = self.get_catalog_for_company(company_name, market)
        
        if not catalog.get('movies') and not catalog.get('tv_shows'):
            return f"{company_name}: Catalog data not available"
        
        # Get top 3 titles
        all_titles = catalog.get('movies', []) + catalog.get('tv_shows', [])
        top_titles = sorted(all_titles, key=lambda x: x.get('popularity', 0), reverse=True)[:3]
        
        title_str = ', '.join([t['title'] for t in top_titles])
        
        return (
            f"{catalog.get('non_english_count', 0)} non-English titles. "
            f"Notable: {title_str}"
        )
    
    def get_top_shows_formatted(
        self,
        company_name: str,
        market: str,
        max_titles: int = 5
    ) -> Dict:
        """
        Get top shows with formatted data for Excel output.
        
        Returns:
            Dictionary with:
            - top_shows: Comma-separated list of show names
            - show_details: List of dicts with name, rating, year, language
            - total_catalog: Total titles found
        """
        catalog = self.get_catalog_for_company(company_name, market)
        
        all_titles = catalog.get('movies', []) + catalog.get('tv_shows', [])
        
        if not all_titles:
            return {
                'top_shows': '',
                'show_details': [],
                'total_catalog': 0
            }
        
        # Sort by popularity
        top_titles = sorted(all_titles, key=lambda x: x.get('popularity', 0), reverse=True)[:max_titles]
        
        show_details = []
        for title in top_titles:
            # Get year from date
            date_str = title.get('release_date') or title.get('first_air_date') or ''
            year = date_str[:4] if date_str else ''
            
            show_details.append({
                'name': title.get('title', ''),
                'popularity': round(title.get('popularity', 0), 1),
                'year': year,
                'language': title.get('original_language', '').upper()
            })
        
        # Format as comma-separated string
        top_shows_str = ', '.join([
            f"{s['name']} ({s['year']}, {s['language']})" 
            for s in show_details if s['name']
        ])
        
        return {
            'top_shows': top_shows_str,
            'show_details': show_details,
            'total_catalog': len(all_titles),
            'non_english_count': catalog.get('non_english_count', 0)
        }


# Example usage
if __name__ == '__main__':
    client = TMDbClient()
    
    # Test with Gaumont
    catalog = client.get_catalog_for_company('Gaumont', 'france')
    print(f"\nGaumont Catalog:")
    print(f"  Movies: {len(catalog.get('movies', []))}")
    print(f"  TV Shows: {len(catalog.get('tv_shows', []))}")
    print(f"  Summary: {catalog.get('summary')}")
