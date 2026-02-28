"""
Data broker opt-out hints. We don't scrape broker sites (legal/ToS); we return
a curated list of known brokers and opt-out links for the user to act on.
"""

import hashlib
import random

KNOWN_BROKERS = [
    {
        "name": "Whitepages",
        "opt_out_url": "https://www.whitepages.com/opt-out",
        "description": "Address, phone, and name lookup",
    },
    {
        "name": "Spokeo",
        "opt_out_url": "https://www.spokeo.com/opt-out",
        "description": "People search and background",
    },
    {
        "name": "BeenVerified",
        "opt_out_url": "https://www.beenverified.com/faq/opt-out/",
        "description": "Public records and people search",
    },
    {
        "name": "PeopleFinder",
        "opt_out_url": "https://www.peoplefinders.com/manage/",
        "description": "People search",
    },
    {
        "name": "TruePeopleSearch",
        "opt_out_url": "https://www.truepeoplesearch.com/removal",
        "description": "Free people search",
    },
    {
        "name": "Intelius",
        "opt_out_url": "https://www.intelius.com/opt-out/",
        "description": "Background and people search",
    },
]


class DataBrokerService:
    """Returns list of data brokers with opt-out links (no scraping)."""

    def get_broker_list(self) -> list[dict]:
        return list(KNOWN_BROKERS)

    def get_brokers_for_account(self, account: str) -> list[dict]:
        """
        In demo mode we cannot verify broker presence. Return a deterministic
        per-account subset so exposure scoring varies across inputs.
        """
        if not account.strip():
            return []
        seed = int(hashlib.sha256(f"brokers:{account.lower()}".encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)
        count = rng.randint(0, len(KNOWN_BROKERS))
        if count == 0:
            return []
        return rng.sample(list(KNOWN_BROKERS), k=count)

    def get_broker_count(self) -> int:
        return len(KNOWN_BROKERS)
