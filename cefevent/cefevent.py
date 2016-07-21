import argparse
from cefevent import CEFSender, CEFEvent

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CEF builder and replayer')
    parser.add_argument('files', metavar='DEFINITION_FILE', type=str,
                        nargs='+', help='an file containing event definitions')
    parser.add_argument('--host', type=str, help='Syslog destination address')
    parser.add_argument('--port', type=int, help='Syslog destination port')
    parser.add_argument('--auto_send', action='store_true',
                        help='Auto send logs')
    parser.add_argument('--eps', type=int, default=100, help='Max EPS')

    args = parser.parse_args()

    cs = CEFSender(host=args.host, port=args.port, files=args.files)

    if args.auto_send:
        cs.auto_send_log(args.eps)
