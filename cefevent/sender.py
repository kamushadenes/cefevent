import random
import sched
import time
from datetime import datetime
from typing import List, AnyStr, Any, Callable

from cefevent.event import CEFEvent
from cefevent.syslog import Syslog


class CEFSender(object):
    def __init__(
        self, files: List[AnyStr], host: AnyStr, port: int, protocol: AnyStr = "UDP"
    ):

        self.cef_poll = []
        self.host = host
        self.port = port
        self.protocol = protocol
        self.syslog = Syslog(host, port=port, protocol=self.protocol)

        self.max_eps = 100

        self.sent_count = 0

        now = datetime.now()
        self.auto_send_start = now

        self.auto_send_checkpoint = now

        self.checkpoint_sent_count = 0

        self.scheduler = sched.scheduler(time.time, time.sleep)

        for fn in files:
            with open(fn, "r") as f:
                lines = f.readlines()

                headers = [i.strip() for i in lines[0].split(";")]

                for line in lines[1:]:
                    line = line.strip()
                    fields = [i.strip() for i in line.split(";")]
                    if len(fields) != len(headers):
                        continue
                    cef = CEFEvent()
                    cef.load(headers, fields)
                    self.cef_poll.append(cef)

    def get_cef_poll(self):
        self.log(self.cef_poll)

    def get_info(self):
        self.log(
            "There are {} events in the poll. The max EPS is set to {}".format(
                len(self.cef_poll), self.max_eps
            )
        )

    def send_log(self, cef: CEFEvent):
        self.syslog.send(cef.build_cef())
        self.sent_count += 1
        self.checkpoint_sent_count += 1

    def send_random_log(self, *args, **kw):
        self.send_log(random.choice(self.cef_poll))

    def timed_call(self, calls_per_second: float, callback: Callable, *args, **kw):
        period = 1.0 / calls_per_second

        def reload():
            callback(*args, **kw)
            self.scheduler.enter(period, 0, reload, ())

        self.scheduler.enter(period, 0, reload, ())

    def get_eps(self):
        now = datetime.now()
        time_diff = (now - self.auto_send_checkpoint).total_seconds()
        eps = self.checkpoint_sent_count / (time_diff if time_diff > 0 else 1)

        self.log("Current EPS: {}".format(eps))

        self.auto_send_checkpoint = now
        self.checkpoint_sent_count = 0

    @staticmethod
    def log(msg: Any):
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        print("[*] [{}] {}".format(now, msg))

    def get_total_event_count(self):
        self.log(
            "{} events sent since {}".format(self.sent_count, self.auto_send_start)
        )

    def auto_send_log(self, eps: int):
        self.max_eps = eps
        self.get_info()
        self.auto_send_start = datetime.now()
        self.timed_call(eps, self.send_random_log)
        self.timed_call(0.1, self.get_eps)
        self.timed_call(0.016, self.get_total_event_count)
        self.scheduler.run()

    def send_logs(self):
        for ev in self.cef_poll:
            self.send_log(ev)
        self.log("{} events sent".format(self.sent_count))
