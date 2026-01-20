"""
Apify Integration Module
========================

Handles lead discovery using Apify actors for LinkedIn scraping.

Available actors:
- LinkedIn Company Employees Scraper: Find employees at a company
- LinkedIn Profile Scraper: Get detailed profile information
- Contact Info Scraper: Find email addresses
"""

import os
import time
from typing import List, Dict, Optional
import yaml

try:
    from apify_client import ApifyClient as ApifyAPIClient
except ImportError:
    ApifyAPIClient = None


class ApifyClient:
    """
    Client for Apify actor interactions.
    
    Handles:
    - Company employee discovery
    - Profile scraping
    - Email/contact finding
    """
    
    def __init__(self):
        self.api_token = os.getenv('APIFY_TOKEN')
        
        if not self.api_token:
            print("Warning: APIFY_TOKEN not set. Apify features will be limited.")
            self.client = None
        elif ApifyAPIClient is None:
            print("Warning: apify-client not installed. Run: pip install apify-client")
            self.client = None
        else:
            self.client = ApifyAPIClient(self.api_token)
        
        # Load config for actor IDs and settings
        self.config = self._load_config()
        
        # Default target roles from config
        self.target_roles = self._get_target_roles()
    
    def _load_config(self) -> dict:
        """Load configuration from config.yaml."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config.yaml'
        )
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _get_target_roles(self) -> List[str]:
        """Get target roles from config."""
        discovery = self.config.get('discovery', {})
        target_roles = discovery.get('target_roles', {})
        
        # Collect all roles from all categories
        all_roles = []
        for category in ['distribution', 'licensing_sales', 'ma_acquisitions', 'executive', 'production_programming']:
            roles = target_roles.get(category, [])
            if isinstance(roles, list):
                all_roles.extend(roles)
        
        # Fallback to old structure if new structure not found
        if not all_roles:
            high = target_roles.get('high_priority', [])
            medium = target_roles.get('medium_priority', [])
            all_roles = high + medium
        
        # Fallback to hardcoded roles if config is empty
        if not all_roles:
            all_roles = [
                "Head of Distribution", "VP Distribution", "SVP Distribution",
                "Head of Licensing", "VP Licensing", "Head of Sales",
                "Head of M&A", "VP Acquisitions", "CFO", "SVP Commercial Strategy",
                "SVP Production", "VP Programming", "Head of Operations"
            ]
        
        return all_roles
    
    def discover_company_employees(
        self,
        company_name: str,
        company_linkedin_url: Optional[str] = None,
        target_roles: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Discover employees at a company matching target roles.
        
        Uses the LinkedIn Company Employees Scraper actor.
        
        Args:
            company_name: Name of the company
            company_linkedin_url: LinkedIn company page URL
            target_roles: List of job titles to filter for
            max_results: Maximum number of results to return
            
        Returns:
            List of lead dictionaries with name, title, linkedin_url
        """
        # For now, always use mock data since free Apify plan doesn't support API
        # To enable real Apify: upgrade to paid plan and set USE_MOCK_DATA=false
        use_mock = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'
        
        if not self.client or use_mock:
            print(f"  Using mock data for {company_name}")
            return self._get_mock_employees(company_name, target_roles, max_results)
        
        roles = target_roles or self.target_roles
        
        # Actor input configuration
        actor_input = {
            "companyUrl": company_linkedin_url,
            "companyName": company_name,
            "roles": roles[:5],  # Limit roles per query for efficiency
            "maxResults": max_results,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            }
        }
        
        # Get actor ID from config - using leads_finder as primary
        actors = self.config.get('apify', {}).get('actors', {})
        actor_id = actors.get(
            'leads_finder',
            'code_crafter/leads-finder'
        )
        
        try:
            print(f"  Running Apify actor: {actor_id}")
            
            # Run the actor
            run = self.client.actor(actor_id).call(run_input=actor_input)
            
            # Fetch results from the dataset
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append({
                    'name': item.get('fullName', item.get('name', '')),
                    'title': item.get('title', item.get('headline', '')),
                    'linkedin_url': item.get('profileUrl', item.get('url', '')),
                    'location': item.get('location', ''),
                    'company': company_name
                })
            
            print(f"  Found {len(results)} employees")
            return results[:max_results]
            
        except Exception as e:
            print(f"  Error running Apify actor: {e}")
            print(f"  Falling back to mock data...")
            return self._get_mock_employees(company_name, target_roles, max_results)
    
    def scrape_profile(self, linkedin_url: str) -> Optional[Dict]:
        """
        Scrape detailed information from a LinkedIn profile.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Dictionary with profile details or None
        """
        if not self.client:
            return None
        
        actors = self.config.get('apify', {}).get('actors', {})
        actor_id = actors.get(
            'linkedin_profile',
            'anchor/linkedin-profile-scraper'
        )
        
        actor_input = {
            "urls": [linkedin_url],
            "proxy": {
                "useApifyProxy": True
            }
        }
        
        try:
            run = self.client.actor(actor_id).call(run_input=actor_input)
            
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                return {
                    'name': item.get('fullName'),
                    'title': item.get('headline'),
                    'summary': item.get('summary'),
                    'experience': item.get('experience', []),
                    'education': item.get('education', []),
                    'location': item.get('location'),
                    'connections': item.get('connections')
                }
            
        except Exception as e:
            print(f"  Error scraping profile: {e}")
        
        return None
    
    def find_email(
        self,
        name: str,
        company: str,
        linkedin_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Find email address for a person.
        
        Args:
            name: Person's full name
            company: Company name
            linkedin_url: Optional LinkedIn URL for better matching
            
        Returns:
            Email address or None
        """
        if not self.client:
            return None
        
        actors = self.config.get('apify', {}).get('actors', {})
        actor_id = actors.get(
            'email_finder',
            'alexey/contact-info-scraper'
        )
        
        actor_input = {
            "name": name,
            "company": company,
            "linkedinUrl": linkedin_url
        }
        
        try:
            run = self.client.actor(actor_id).call(run_input=actor_input)
            
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                return item.get('email')
            
        except Exception as e:
            print(f"  Error finding email: {e}")
        
        return None
    
    def _get_mock_employees(
        self,
        company_name: str,
        target_roles: Optional[List[str]],
        max_results: int
    ) -> List[Dict]:
        """
        Return mock employee data for testing without Apify.
        
        This allows the system to be tested end-to-end without
        actually making API calls.
        """
        import hashlib
        
        roles = target_roles or self.target_roles
        
        # Create a company-specific slug for unique URLs
        company_slug = company_name.lower().replace(' ', '-').replace('+', 'plus')
        
        # Generate mock employees based on company
        mock_data = []
        role_subset = roles[:max_results] if len(roles) >= max_results else roles
        
        # Mock names by market (for more realistic data)
        mock_names_uk = ["James Thompson", "Sarah Williams", "David Anderson", "Emma Watson",
                        "Michael Brown", "Charlotte Davies", "William Taylor", "Olivia Johnson",
                        "Thomas Wilson", "Jessica Moore", "Daniel Harris", "Sophie Clark",
                        "Christopher Lewis", "Emily Robinson", "Matthew Walker", "Hannah White"]
        mock_names_usa = ["John Smith", "Jennifer Davis", "Robert Miller", "Michelle Johnson",
                        "Christopher Wilson", "Amanda Martinez", "Michael Anderson", "Stephanie Brown",
                        "David Taylor", "Nicole Thomas", "James Garcia", "Ashley Jackson",
                        "Kevin Rodriguez", "Lauren White", "Brian Harris", "Megan Lewis"]
        mock_names_spain = ["Carlos García", "María López", "Juan Martínez", "Ana Fernández", 
                           "Pedro Sánchez", "Laura Rodríguez", "Miguel Torres", "Carmen Ruiz",
                           "Javier Moreno", "Isabel Jiménez", "Antonio Díaz", "Elena Muñoz",
                           "Francisco Romero", "Lucía Álvarez", "Pablo Navarro", "Marta Serrano"]
        mock_names_germany = ["Hans Müller", "Anna Schmidt", "Thomas Fischer", "Claudia Weber",
                             "Michael Schneider", "Sabine Meyer", "Stefan Wagner", "Petra Becker",
                             "Andreas Hoffmann", "Monika Schäfer", "Markus Koch", "Karin Bauer",
                             "Jürgen Richter", "Birgit Klein", "Wolfgang Wolf", "Susanne Neumann"]
        mock_names_france = ["Jean-Pierre Dupont", "Marie Laurent", "François Martin", "Sophie Bernard",
                            "Pierre Dubois", "Isabelle Moreau", "Olivier Petit", "Catherine Richard",
                            "Philippe Thomas", "Christine Robert", "Alain Michel", "Nathalie Simon",
                            "Laurent Garcia", "Sylvie Leroy", "Bruno Roux", "Valérie Fournier"]
        mock_names_korea = ["Kim Min-jun", "Park Seo-yeon", "Lee Ji-ho", "Choi Yu-na",
                           "Jung Hyun-woo", "Kang Ha-eun", "Yoon Do-yun", "Song Ji-min",
                           "Cho Eun-ji", "Han Sung-ho", "Lim Da-eun", "Shin Jae-won",
                           "Oh Mi-rae", "Hwang Tae-min", "Bae Soo-jin", "Jang Hye-rim"]
        
        # Select names based on company
        company_lower = company_name.lower()
        if any(x in company_lower for x in ['bbc', 'itv', 'all3media', 'fremantle uk', 'sky']):
            names = mock_names_uk
        elif any(x in company_lower for x in ['lionsgate', 'sony', 'paramount', 'warner', 'netflix us']):
            names = mock_names_usa
        elif any(x in company_lower for x in ['atresmedia', 'mediapro', 'latido', 'netflix spain']) or 'spain' in company_lower:
            names = mock_names_spain
        elif any(x in company_lower for x in ['ufa', 'constantin', 'zdf', 'rtl']) or 'germany' in company_lower:
            names = mock_names_germany
        elif any(x in company_lower for x in ['gaumont', 'studiocanal', 'newen', 'canal+']) or 'france' in company_lower:
            names = mock_names_france
        elif any(x in company_lower for x in ['dragon', 'cj', 'sbs', 'korea']):
            names = mock_names_korea
        else:
            names = mock_names_usa  # Default to USA names
        
        for i, role in enumerate(role_subset):
            name = names[i % len(names)]
            # Create unique URL with company and name hash
            url_hash = hashlib.md5(f"{company_name}-{name}-{i}".encode()).hexdigest()[:8]
            
            mock_data.append({
                'name': name,
                'title': role,
                'linkedin_url': f'https://www.linkedin.com/in/{company_slug}-{url_hash}',
                'location': 'Location TBD',
                'company': company_name
            })
        
        print(f"  [MOCK] Generated {len(mock_data)} test employees for {company_name}")
        return mock_data


# Example usage
if __name__ == '__main__':
    client = ApifyClient()
    
    # Test with a sample company
    employees = client.discover_company_employees(
        company_name="Gaumont",
        company_linkedin_url="https://www.linkedin.com/company/gaumont/",
        max_results=5
    )
    
    for emp in employees:
        print(f"  {emp['name']} - {emp['title']}")
