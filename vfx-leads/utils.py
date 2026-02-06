"""
Utilities Module
================

Common utilities for the VFX Lead Generation Pipeline.

Includes:
- Retry logic with exponential backoff
- API result caching
- Input validation
- Structured logging
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Optional, List, Dict, Any, Callable


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(
    output_dir: str = 'output',
    log_level: int = logging.INFO,
    log_to_file: bool = True
) -> logging.Logger:
    """
    Set up structured logging for pipeline runs.
    
    Args:
        output_dir: Directory for log files
        log_level: Logging level (default INFO)
        log_to_file: Whether to also log to file
        
    Returns:
        Configured logger instance
    """
    # Create output directory if needed
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('vfx_leads')
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Console handler with color formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = Path(output_dir) / f'pipeline_run_{timestamp}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        logger.info(f"Logging to: {log_file}")
    
    return logger


def get_logger() -> logging.Logger:
    """Get the truesync logger instance."""
    logger = logging.getLogger('vfx_leads')
    if not logger.handlers:
        # Set up default logging if not configured
        setup_logging(log_to_file=False)
    return logger


# ============================================================================
# RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exceptions: Tuple of exceptions to catch and retry
        logger: Optional logger for retry messages
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        log.error(f"❌ {func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    log.warning(
                        f"⚠ {func.__name__} attempt {attempt + 1}/{max_retries + 1} failed: {str(e)[:50]}"
                    )
                    log.info(f"   Retrying in {delay:.1f}s...")
                    time.sleep(delay)
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


# ============================================================================
# API RESULT CACHING
# ============================================================================

class APICache:
    """
    Simple file-based cache for API results.
    
    Caches API responses to avoid redundant calls during development
    and when re-running pipelines.
    """
    
    def __init__(self, cache_dir: str = '.cache', ttl_hours: int = 24):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live in hours (0 = no expiry)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_hours * 3600
        self.logger = get_logger()
    
    def _get_cache_key(self, data: Any) -> str:
        """Generate a unique cache key from data."""
        if isinstance(data, dict):
            serialized = json.dumps(data, sort_keys=True)
        else:
            serialized = str(data)
        return hashlib.md5(serialized.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check TTL
            if self.ttl_seconds > 0:
                cached_time = cached.get('_cached_at', 0)
                if time.time() - cached_time > self.ttl_seconds:
                    self.logger.debug(f"Cache expired for key: {key[:8]}...")
                    return None
            
            self.logger.debug(f"Cache hit for key: {key[:8]}...")
            return cached.get('data')
            
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, data: Any) -> None:
        """
        Set cached value.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(key)
        
        try:
            cached = {
                'data': data,
                '_cached_at': time.time()
            }
            with open(cache_path, 'w') as f:
                json.dump(cached, f)
            self.logger.debug(f"Cached data for key: {key[:8]}...")
        except IOError as e:
            self.logger.warning(f"Cache write error: {e}")
    
    def get_or_fetch(
        self,
        cache_key: str,
        fetch_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Get from cache or fetch and cache.
        
        Args:
            cache_key: Cache key to use
            fetch_func: Function to call if not cached
            *args, **kwargs: Arguments for fetch_func
            
        Returns:
            Cached or fetched data
        """
        cached = self.get(cache_key)
        if cached is not None:
            return cached
        
        # Fetch fresh data
        data = fetch_func(*args, **kwargs)
        
        # Cache the result
        if data is not None:
            self.set(cache_key, data)
        
        return data
    
    def clear(self) -> int:
        """
        Clear all cached data.
        
        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
            count += 1
        self.logger.info(f"Cleared {count} cache files")
        return count
    
    def clear_expired(self) -> int:
        """
        Clear only expired cache entries.
        
        Returns:
            Number of cache files deleted
        """
        if self.ttl_seconds <= 0:
            return 0
        
        count = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                cached_time = cached.get('_cached_at', 0)
                if current_time - cached_time > self.ttl_seconds:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, IOError):
                # Remove corrupted cache files
                cache_file.unlink()
                count += 1
        
        if count > 0:
            self.logger.info(f"Cleared {count} expired cache files")
        return count


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_leads(leads: List[Dict], strict: bool = False) -> List[Dict]:
    """
    Validate and clean lead data.
    
    Args:
        leads: List of lead dictionaries
        strict: If True, reject leads with any missing fields
        
    Returns:
        List of validated leads
    """
    logger = get_logger()
    valid_leads = []
    skipped = 0
    
    required_fields = ['name']
    recommended_fields = ['company', 'title']
    
    for i, lead in enumerate(leads):
        # Check required fields
        missing_required = [f for f in required_fields if not lead.get(f)]
        if missing_required:
            logger.warning(f"Lead {i+1}: Missing required fields {missing_required}, skipping")
            skipped += 1
            continue
        
        # Check recommended fields
        missing_recommended = [f for f in recommended_fields if not lead.get(f)]
        if strict and missing_recommended:
            logger.warning(f"Lead {i+1} ({lead.get('name')}): Missing {missing_recommended}, skipping")
            skipped += 1
            continue
        elif missing_recommended:
            logger.debug(f"Lead {i+1} ({lead.get('name')}): Missing {missing_recommended}")
        
        # Clean the lead data
        cleaned = {
            'name': lead.get('name', '').strip(),
            'title': lead.get('title', '').strip(),
            'company': lead.get('company', '').strip(),
            'location': lead.get('location', '').strip(),
            'linkedin_url': lead.get('linkedin_url', '').strip() or None,
            'email': lead.get('email', '').strip() or None,
        }
        
        # Preserve any additional fields
        for key, value in lead.items():
            if key not in cleaned:
                cleaned[key] = value
        
        valid_leads.append(cleaned)
    
    if skipped > 0:
        logger.info(f"Validation: {len(valid_leads)} valid, {skipped} skipped")
    
    return valid_leads


def validate_json_file(file_path: str) -> List[Dict]:
    """
    Validate and load a JSON file containing leads.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of validated leads
        
    Raises:
        ValueError: If file is invalid or empty
    """
    logger = get_logger()
    path = Path(file_path)
    
    if not path.exists():
        raise ValueError(f"Input file not found: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    
    if not isinstance(data, list):
        raise ValueError(f"Expected list of leads, got {type(data).__name__}")
    
    if len(data) == 0:
        raise ValueError(f"Empty leads list in {file_path}")
    
    logger.info(f"Loaded {len(data)} leads from {file_path}")
    
    return validate_leads(data)


# ============================================================================
# PROGRESS DISPLAY
# ============================================================================

class ProgressTracker:
    """Simple progress tracker for long operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.logger = get_logger()
    
    def update(self, n: int = 1, message: str = None):
        """Update progress by n items."""
        self.current += n
        
        # Calculate progress
        pct = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        # Estimate remaining time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"{eta:.0f}s remaining"
        else:
            eta_str = "calculating..."
        
        # Log progress
        status = f"{self.description}: {self.current}/{self.total} ({pct:.1f}%) - {eta_str}"
        if message:
            status += f" | {message}"
        
        self.logger.info(status)
    
    def finish(self):
        """Mark progress as complete."""
        elapsed = time.time() - self.start_time
        self.logger.info(f"✅ {self.description} complete: {self.current} items in {elapsed:.1f}s")


# ============================================================================
# STRING UTILITIES
# ============================================================================

def name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two names.
    
    Args:
        name1: First name
        name2: Second name
        
    Returns:
        Similarity score 0.0 to 1.0
    """
    from difflib import SequenceMatcher
    
    if not name1 or not name2:
        return 0.0
    
    # Normalize names
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()
    
    return SequenceMatcher(None, n1, n2).ratio()


def normalize_company_name(company: str) -> str:
    """
    Normalize company name for matching.
    
    Args:
        company: Company name
        
    Returns:
        Normalized company name
    """
    if not company:
        return ''
    
    # Lowercase and strip
    result = company.lower().strip()
    
    # Remove common suffixes
    suffixes = [
        ' inc', ' inc.', ' llc', ' ltd', ' ltd.', ' limited',
        ' corp', ' corp.', ' corporation', ' co', ' co.',
        ' gmbh', ' ag', ' s.a.', ' sa', ' plc'
    ]
    for suffix in suffixes:
        if result.endswith(suffix):
            result = result[:-len(suffix)]
    
    return result.strip()
