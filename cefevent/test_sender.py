import csv
import os
import random
import select
import socket
import tempfile
import threading
from time import sleep

from cefevent.generator import generate_random_events
from cefevent.sender import CEFSender

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 0))
sock.setblocking(False)

recvd_pkt = 0


def listen(running: threading.Event):
    global recvd_pkt

    while running.is_set():
        ready = select.select([sock], [], [], 1)
        if ready[0]:
            data, _ = sock.recvfrom(1024)
            recvd_pkt += 1
    sock.close()


def test_sender():
    files = 3

    fnames = [tempfile.mktemp() for _ in range(files)]
    events = [
        generate_random_events(field_count=10, event_count=random.randint(1, 100))
        for _ in range(files)
    ]

    for idx, fn in enumerate(fnames):
        headers = events[idx][0].get_fields().keys()
        with open(fn, "w") as f:
            writer = csv.DictWriter(f, headers, extrasaction="ignore", delimiter=";")
            writer.writeheader()
            writer.writerows([ev.get_fields() for ev in events[idx]])

    running = threading.Event()
    running.set()

    sender = CEFSender(fnames, "127.0.0.1", sock.getsockname()[1])

    assert sum(map(len, events)) == len(sender.cef_poll)

    t = threading.Thread(target=listen, args=(running,))
    t.start()
    sleep(0.1)

    sender.send_logs()

    sleep(1)
    running.clear()

    if not os.environ.get('GITHUB_ACTIONS'):
        assert recvd_pkt == len(sender.cef_poll)

    map(os.remove, fnames)
