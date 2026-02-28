import httpx
import hashlib
import random
import time
from datetime import datetime, timedelta
from urllib.parse import quote
from typing import Dict, Tuple, Optional

from app.config import get_settings

HIBP_BASE = "https://haveibeenpwned.com/api/v3"


class HIBPService:
    def __init__(self):
        self.settings = get_settings()
        # Rate limiting: 10 requests per minute = 1 request every 6 seconds
        self.rate_limit_interval = 6.0  # seconds
        self.last_request_time = 0.0
        
        # Cache to store results for 1 hour
        self.cache: Dict[str, Tuple[dict, datetime]] = {}
        self.cache_duration = timedelta(hours=1)
    
    def _can_make_request(self) -> bool:
        """Check if we can make a request without exceeding rate limits."""
        current_time = time.time()
        return current_time - self.last_request_time >= self.rate_limit_interval
    
    def _wait_for_rate_limit(self):
        """Wait until we can make the next request."""
        while not self._can_make_request():
            time.sleep(0.1)
        self.last_request_time = time.time()
    
    def _get_cache_key(self, account: str, endpoint: str) -> str:
        """Generate cache key for account and endpoint."""
        return f"{endpoint}:{account.lower()}"
    
    def _get_from_cache(self, account: str, endpoint: str) -> Optional[dict]:
        """Get data from cache if available and not expired."""
        cache_key = self._get_cache_key(account, endpoint)
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return data
            else:
                # Remove expired entry
                del self.cache[cache_key]
        return None
    
    def _store_in_cache(self, account: str, endpoint: str, data: dict):
        """Store data in cache."""
        cache_key = self._get_cache_key(account, endpoint)
        self.cache[cache_key] = (data, datetime.now())

    async def get_breaches_for_account(self, account: str) -> tuple[list[dict], bool]:
        """Fetch breaches from HIBP only. Returns (breaches, hibp_ok). Never returns mock data."""
        print(f"[HIBP] Getting breaches for {account}")
        if not self.settings.hibp_api_key:
            print("[HIBP] No API key configured")
            return [], False
        
        # Check cache first
        cached_data = self._get_from_cache(account, "breaches")
        if cached_data is not None:
            print(f"[HIBP] Using cached breaches for {account}")
            return cached_data["data"], cached_data["ok"]
        
        print(f"[HIBP] Making API call for breaches to {account}")
        # Rate limit the request
        self._wait_for_rate_limit()
        
        headers = {
            "hibp-api-key": self.settings.hibp_api_key,
            "User-Agent": self.settings.user_agent,
        }
        encoded = quote(account, safe="")
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{HIBP_BASE}/breachedaccount/{encoded}?truncateResponse=false",
                headers=headers,
            )
            print(f"[HIBP] Breaches API response status: {r.status_code}")
            if r.status_code == 404:
                result = [], True
            elif r.status_code == 401:
                print("[HIBP] API key unauthorized")
                result = [], False
            elif r.status_code == 429:
                print("[HIBP] Rate limited for breaches")
                # Rate limited - return empty but mark as unavailable
                result = [], False
            else:
                r.raise_for_status()
                print(f"[HIBP] Got {len(r.json())} breaches for {account}")
                result = r.json(), True
            
            # Cache the result
            self._store_in_cache(account, "breaches", {"data": result[0], "ok": result[1]})
            return result

    async def get_pastes_for_account(self, account: str) -> tuple[list[dict], bool]:
        """Fetch pastes from HIBP only. Returns (pastes, hibp_ok). Never returns mock data."""
        print(f"[HIBP] Getting pastes for {account}")
        if not self.settings.hibp_api_key:
            print("[HIBP] No API key configured")
            return [], False
        
        # Check cache first
        cached_data = self._get_from_cache(account, "pastes")
        if cached_data is not None:
            print(f"[HIBP] Using cached pastes for {account}")
            return cached_data["data"], cached_data["ok"]
        
        print(f"[HIBP] Making API call for pastes to {account}")
        # Rate limit the request (additional delay since this is a separate API call)
        self._wait_for_rate_limit()
        
        encoded = quote(account, safe="")
        headers = {
            "hibp-api-key": self.settings.hibp_api_key,
            "User-Agent": self.settings.user_agent,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{HIBP_BASE}/pasteaccount/{encoded}",
                headers=headers,
            )
            print(f"[HIBP] Pastes API response status: {r.status_code}")
            if r.status_code == 404:
                result = [], True
            elif r.status_code == 401:
                print("[HIBP] API key unauthorized")
                result = [], False
            elif r.status_code == 429:
                print("[HIBP] Rate limited for pastes")
                # Rate limited - return empty but mark as unavailable
                result = [], False
            else:
                r.raise_for_status()
                print(f"[HIBP] Got {len(r.json())} pastes for {account}")
                result = r.json(), True
            
            # Cache the result
            self._store_in_cache(account, "pastes", {"data": result[0], "ok": result[1]})
            return result

    def _mock_breaches(self, account: str) -> list[dict]:
        """Demo data when no API key. Deterministic per account."""
        seed = int(hashlib.sha256(account.lower().encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)

        breach_pool = [
            ("ExampleShop", ["Emails", "Passwords"], "A sample e‑commerce breach. Account emails and hashed passwords were exposed."),
            ("PhotoCloud", ["Emails", "Names", "Locations"], "A cloud storage breach. User emails, display names, and location metadata were leaked."),
            ("FitnessForum", ["Usernames", "Email addresses", "IP addresses"], "A forum breach. Usernames, email addresses, and IP addresses were exposed."),
            ("DevCommunity", ["Usernames", "Emails"], "A developer community breach. Account identifiers and emails were compromised."),
            ("TravelDeals", ["Emails", "Phone numbers"], "A travel site breach. Email addresses and phone numbers were leaked."),
            ("OldSocial", ["Emails", "Dates of birth"], "A social network breach. Emails and dates of birth were exposed."),
            ("GameHub", ["Usernames", "Passwords"], "A gaming platform breach. Usernames and passwords were leaked."),
            ("Newsletters", ["Emails"], "A newsletter provider breach. Subscriber email addresses were exposed."),
        ]
        breach_count = rng.randint(0, 5)
        chosen = rng.sample(breach_pool, k=breach_count) if breach_count else []

        breaches: list[dict] = []
        for name, data_classes, description in chosen:
            year = rng.randint(2016, 2024)
            month = rng.randint(1, 12)
            day = rng.randint(1, 28)
            breaches.append(
                {
                    "Name": name,
                    "Title": name,
                    "BreachDate": f"{year:04d}-{month:02d}-{day:02d}",
                    "DataClasses": data_classes,
                    "Description": description,
                    "PwnCount": rng.randint(50_000, 5_000_000),
                }
            )
        return breaches

    def _mock_pastes(self, account: str) -> list[dict]:
        seed = int(hashlib.sha256(f"pastes:{account.lower()}".encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)

        paste_sources = ["Pastebin", "Ghostbin", "Rentry", "ControlC", "PrivateBin"]
        paste_titles = [
            "credentials dump",
            "misc notes",
            "account list",
            "leaked database snippet",
            "old backup",
            "emails & passwords",
        ]
        paste_count = rng.randint(0, 3)
        pastes: list[dict] = []
        for i in range(paste_count):
            src = rng.choice(paste_sources)
            title = rng.choice(paste_titles)
            pid = hashlib.sha256(f"{account.lower()}:{i}".encode("utf-8")).hexdigest()[:8]
            year = rng.randint(2018, 2024)
            month = rng.randint(1, 12)
            day = rng.randint(1, 28)
            pastes.append({
                "Source": src,
                "Id": pid,
                "Title": title,
                "Date": f"{year:04d}-{month:02d}-{day:02d}T12:00:00Z",
                "EmailCount": rng.randint(10, 500),
            })
        return pastes
