"""Registry der aktiven Institut-Adapter.

Jedes Institut, das hier gelistet ist, wird beim Build abgefragt. Neue Institute
werden ergänzt, indem ein Adapter unter scraper/adapters/ angelegt und hier
eingetragen wird.
"""
from scraper.adapters.ditf import DitfAdapter
from scraper.adapters.hohenstein import HohensteinAdapter

ACTIVE_ADAPTERS = [
    HohensteinAdapter(),
    DitfAdapter(),
]
