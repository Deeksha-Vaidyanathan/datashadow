"""
Data broker opt-out hints. We don't scrape broker sites (legal/ToS); we return
a curated list of known brokers and opt-out links for the user to act on.
"""

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

    def get_broker_count(self) -> int:
        return len(KNOWN_BROKERS)
