import random
import string
from datetime import datetime, timedelta
import ipaddress
import sys
from cefevent.event import CEFEvent

from typing import AnyStr

random.seed(datetime.now().timestamp())

ipv4_networks = ["10.0.0.0/8", "172.16.0.0/16", "192.168.0.0/24"]
ipv6_networks = ["fd00::/48", "fd00::/64"]

allowed_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

start_date = datetime(1970, 1, 1)
end_date = datetime(2999, 1, 1)
delta = end_date - start_date
int_delta = (delta.days * 24 * 60 * 60) + delta.seconds


def random_addr(network: AnyStr = None, v6: bool = False):
    if network is None:
        network = random.choice(ipv6_networks) if v6 else random.choice(ipv4_networks)
    net = ipaddress.IPv6Network(network) if v6 else ipaddress.IPv4Network(network)
    # Which of the network.num_addresses we want to select?
    addr_no = random.randint(0, net.num_addresses)
    # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
    network_int = int.from_bytes(net.network_address.packed, byteorder="big")
    addr_int = network_int + addr_no
    if v6:
        return str(ipaddress.IPv6Address(addr_int.to_bytes(16, byteorder="big")))
    else:
        return str(ipaddress.IPv4Address(addr_int.to_bytes(4, byteorder="big")))


def generate_random_events(
    field_count: int = 10, event_count: int = 1, strict: bool = False
):
    cef = CEFEvent()

    events = []

    fields = random.choices(
        list(cef._reverse_extension_dictionary.keys()), k=field_count
    )

    for _ in range(0, event_count):
        ev = CEFEvent(strict=strict)
        ev.set_prefix("name", "Random CEF Event")
        ev.set_prefix("severity", random.randint(0, 10))
        for field in fields:
            fdef = cef._reverse_extension_dictionary[field]
            if fdef["data_type"] == "String":
                ev.set_field(
                    field,
                    "".join(
                        random.choices(
                            allowed_chars, k=random.randint(1, fdef["length"])
                        )
                    ),
                ) if fdef["length"] else ""
            elif fdef["data_type"] == "Integer":
                ev.set_field(field, random.randint(0, 2147483647))
            elif fdef["data_type"] in ["Floating Point", "Long"]:
                ev.set_field(field, round(random.uniform(0, 2147483647), 5))
            elif fdef["data_type"] == "IPv4 Address":
                ev.set_field(field, random_addr())
            elif fdef["data_type"] == "IPv6 Address":
                ev.set_field(field, random_addr(v6=True))
            elif fdef["data_type"] == "MAC Address":
                ev.set_field(
                    field,
                    "{}:{}:{}:{}:{}:{}".format(
                        *map(
                            lambda x: hex(x)[2:].upper().zfill(2),
                            random.sample(range(0, 255), 6),
                        )
                    ),
                )
            elif fdef["data_type"] == "TimeStamp":
                ev.set_field(
                    field, start_date + timedelta(seconds=random.randrange(int_delta))
                )
            else:
                print(fdef)

        events.append(ev)

    return events
