import httpx
from app.config import get_settings

HIBP_BASE = "https://haveibeenpwned.com/api/v3"


class HIBPService:
    def __init__(self):
        self.settings = get_settings()

    async def get_breaches_for_account(self, account: str) -> list[dict]:
        """Fetch breaches for email/username. Requires HIBP API key."""
        if not self.settings.hibp_api_key:
            return self._mock_breaches(account)
        headers = {
            "hibp-api-key": self.settings.hibp_api_key,
            "User-Agent": self.settings.user_agent,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{HIBP_BASE}/breachedaccount/{account}",
                headers=headers,
            )
            if r.status_code == 404:
                return []
            if r.status_code == 401:
                return self._mock_breaches(account)
            r.raise_for_status()
            return r.json()

    async def get_pastes_for_account(self, account: str) -> list[dict]:
        """Fetch pastes for email/username. Requires HIBP API key."""
        if not self.settings.hibp_api_key:
            return self._mock_pastes(account)
        headers = {
            "hibp-api-key": self.settings.hibp_api_key,
            "User-Agent": self.settings.user_agent,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{HIBP_BASE}/pasteaccount/{account}",
                headers=headers,
            )
            if r.status_code == 404:
                return []
            if r.status_code == 401:
                return self._mock_pastes(account)
            r.raise_for_status()
            return r.json()

    def _mock_breaches(self, account: str) -> list[dict]:
        """Demo data when no API key. Replace with real HIBP key for production."""
        return [
            {"Name": "ExampleBreach1", "BreachDate": "2022-01-15", "DataClasses": ["Emails", "Passwords"]},
            {"Name": "ExampleBreach2", "BreachDate": "2021-06-01", "DataClasses": ["Usernames", "IP addresses"]},
        ]

    def _mock_pastes(self, account: str) -> list[dict]:
        return [
            {"Source": "Pastebin", "Id": "demo1", "Title": "Sample paste"},
        ]
