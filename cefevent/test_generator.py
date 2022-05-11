import ipaddress
import random

from cefevent.event import CEFEvent
from cefevent.generator import generate_random_events, random_addr


def test_random_addr():
    for _ in range(0, 1000):
        try:
            ipaddress.ip_address(random_addr())
        except ValueError:
            assert False, "An invalid IPv4 address was generated"
        try:
            ipaddress.ip_address(random_addr(v6=True))
        except ValueError:
            assert False, "An invalid IPv4 address was generated"


def test_generate_random_events():
    field_count = random.randint(10, 100)
    event_count = random.randint(1000, 5000)

    events = generate_random_events(
        field_count=field_count, event_count=event_count, strict=True
    )

    assert len(events) == event_count
    assert all(isinstance(ev, CEFEvent) for ev in events)
