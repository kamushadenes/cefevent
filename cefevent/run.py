import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from cefevent.sender import CEFSender

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This library is able to generate, validate and send CEF events"
    )
    parser.add_argument(
        "files",
        metavar="DEFINITION_FILE",
        type=str,
        nargs="+",
        help="an file containing event definitions",
    )
    parser.add_argument(
        "--host", type=str, help="Syslog destination host", required=True
    )
    parser.add_argument("--port", type=int, default=514, help="Syslog destination port")
    parser.add_argument("--tcp", action="store_true", help="Use TCP instead of UDP")
    parser.add_argument(
        "--auto_send",
        action="store_true",
        help="Auto send logs, default to sending once",
    )
    parser.add_argument("--eps", type=int, default=100, help="Max EPS")

    args = parser.parse_args()

    cs = CEFSender(
        host=args.host,
        port=args.port,
        files=args.files,
        protocol="TCP" if args.tcp else "UDP",
    )

    if args.auto_send:
        cs.auto_send_log(args.eps)
    else:
        cs.send_logs()
