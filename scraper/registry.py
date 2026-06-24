"""Registry der aktiven Institut-Adapter.

Es werden ausschließlich Institute aus der offiziellen t+m-Liste berücksichtigt:
https://textil-mode.de/de/forschung/institute/

Neue Institute werden ergänzt, indem ein Adapter unter scraper/adapters/ angelegt
und hier eingetragen wird.
"""
from scraper.adapters.ditf import DitfAdapter
from scraper.adapters.ita_aachen import ItaAachenAdapter
from scraper.adapters.wfk import WfkAdapter

ACTIVE_ADAPTERS = [
    DitfAdapter(),
    ItaAachenAdapter(),
    WfkAdapter(),
]
