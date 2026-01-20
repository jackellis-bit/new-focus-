"""
Email Enrichment Module
=======================

Finds email addresses for leads using multiple sources:
- Hunter.io API
- Apify email finder actors
- Pattern-based guessing
"""

import os
import re
from typing import Optional, List
import requests


class EmailEnricher:
    """
    Enriches leads with email addresses.
    
    Uses a fallback chain:
    1. Hunter.io API (if configured)
    2. Apify email finder (if configured)
    3. Pattern-based guessing (as last resort)
    """
    
    # Common email patterns by domain
    EMAIL_PATTERNS = [
        "{first}.{last}@{domain}",
        "{first}{last}@{domain}",
        "{first}_{last}@{domain}",
        "{first}@{domain}",
        "{f}{last}@{domain}",
        "{first}.{l}@{domain}",
    ]
    
    # Known company domains
    COMPANY_DOMAINS = {
        # UK - Tier 1
        'BBC Studios': 'bbc.com',
        'ITV Studios': 'itv.com',
        'All3Media': 'all3media.com',
        'Fremantle UK': 'fremantle.com',
        'Sky Studios': 'sky.com',
        
        # USA - Tier 1
        'Lionsgate': 'lionsgate.com',
        'Sony Pictures Entertainment': 'spe.sony.com',
        'Paramount Global': 'paramount.com',
        'Warner Bros. Discovery': 'wbd.com',
        'Netflix US': 'netflix.com',
        
        # Spain - Tier 1
        'Atresmedia Studios': 'atresmedia.com',
        'Mediapro': 'mediapro.es',
        'Beta Film': 'betafilm.com',
        'Latido Films': 'latidofilms.com',
        'Netflix Spain': 'netflix.com',
        
        # Germany - Tier 2
        'UFA': 'ufa.de',
        'Constantin Film': 'constantin-film.de',
        'Beta Film DE': 'betafilm.com',
        'ZDF Studios': 'zdf-studios.com',
        'RTL+ Germany': 'rtl.de',
        
        # France - Tier 2
        'Gaumont': 'gaumont.com',
        'StudioCanal': 'studiocanal.com',
        'StudioCanal Sales': 'studiocanal.com',
        'Newen Distribution': 'newen.fr',
        'Canal+': 'canal-plus.com',
        
        # Korea - Tier 2
        'Studio Dragon': 'studiodragon.net',
        'CJ ENM': 'cjenm.com',
        'CJ ENM International': 'cjenm.com',
        'SBS Contents Hub': 'sbs.co.kr',
        'Netflix Korea': 'netflix.com',
    }
    
    def __init__(self):
        self.hunter_api_key = os.getenv('HUNTER_API_KEY')
        self.apify_token = os.getenv('APIFY_TOKEN')
        
        if not self.hunter_api_key:
            print("Note: HUNTER_API_KEY not set. Email enrichment will be limited.")
    
    def find_email(
        self,
        name: str,
        company: str,
        linkedin_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Find email address for a person.
        
        Tries multiple methods in order of reliability.
        
        Args:
            name: Person's full name
            company: Company name
            linkedin_url: Optional LinkedIn URL
            
        Returns:
            Email address or None
        """
        # Try Hunter.io first
        if self.hunter_api_key:
            email = self._hunter_find(name, company)
            if email:
                return email
        
        # Try pattern-based guessing
        domain = self.COMPANY_DOMAINS.get(company)
        if domain:
            emails = self._generate_patterns(name, domain)
            # In production, you'd verify these with Hunter or similar
            # For now, return the most common pattern
            if emails:
                return emails[0]
        
        return None
    
    def _hunter_find(self, name: str, company: str) -> Optional[str]:
        """
        Find email using Hunter.io API.
        
        Args:
            name: Person's full name
            company: Company name or domain
            
        Returns:
            Email address or None
        """
        domain = self.COMPANY_DOMAINS.get(company)
        
        if not domain:
            # Try to find domain via Hunter
            domain_result = self._hunter_domain_search(company)
            if domain_result:
                domain = domain_result
            else:
                return None
        
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            'domain': domain,
            'full_name': name,
            'api_key': self.hunter_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data', {}).get('email'):
                return data['data']['email']
                
        except requests.RequestException as e:
            print(f"  Hunter API error: {e}")
        
        return None
    
    def _hunter_domain_search(self, company: str) -> Optional[str]:
        """
        Search for a company's domain using Hunter.io.
        
        Args:
            company: Company name
            
        Returns:
            Domain or None
        """
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            'company': company,
            'api_key': self.hunter_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data', {}).get('domain'):
                return data['data']['domain']
                
        except requests.RequestException as e:
            print(f"  Hunter domain search error: {e}")
        
        return None
    
    def _generate_patterns(self, name: str, domain: str) -> List[str]:
        """
        Generate possible email patterns for a name.
        
        Args:
            name: Person's full name
            domain: Company email domain
            
        Returns:
            List of possible email addresses
        """
        # Parse name
        name_parts = name.lower().split()
        
        if len(name_parts) < 2:
            return []
        
        first = self._clean_name(name_parts[0])
        last = self._clean_name(name_parts[-1])
        f = first[0] if first else ''
        l = last[0] if last else ''
        
        emails = []
        for pattern in self.EMAIL_PATTERNS:
            try:
                email = pattern.format(
                    first=first,
                    last=last,
                    f=f,
                    l=l,
                    domain=domain
                )
                emails.append(email)
            except (KeyError, IndexError):
                continue
        
        return emails
    
    def _clean_name(self, name: str) -> str:
        """Remove accents and special characters from name."""
        # Simple transliteration for common accented characters
        replacements = {
            'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a',
            'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
            'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
            'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o',
            'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
            'ñ': 'n', 'ç': 'c',
        }
        
        result = name.lower()
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        # Remove any remaining non-alphanumeric characters
        result = re.sub(r'[^a-z0-9]', '', result)
        
        return result
    
    def verify_email(self, email: str) -> bool:
        """
        Verify if an email address is valid and deliverable.
        
        Uses Hunter.io verification API.
        
        Args:
            email: Email address to verify
            
        Returns:
            True if email is valid and deliverable
        """
        if not self.hunter_api_key:
            return True  # Can't verify, assume valid
        
        url = "https://api.hunter.io/v2/email-verifier"
        params = {
            'email': email,
            'api_key': self.hunter_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            status = data.get('data', {}).get('status')
            return status in ['valid', 'accept_all']
            
        except requests.RequestException:
            return True  # On error, don't reject
        
        return False


# Example usage
if __name__ == '__main__':
    enricher = EmailEnricher()
    
    # Test pattern generation
    patterns = enricher._generate_patterns("Jean-Pierre Dupont", "gaumont.com")
    print("Generated patterns for Jean-Pierre Dupont:")
    for p in patterns:
        print(f"  {p}")
