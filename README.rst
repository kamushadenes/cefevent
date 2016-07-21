cefevent
========

ArcSight's Common Event Format library

This library is able to generate, validate and send CEF events
(currently peaking at about 3400 EPS)

It uses CSV files with the CEF field names as headers in the first line
and then sends it at the specified EPS rate to the configured UDP Syslog
destination.

Usage
-----
.. code:: bash
        usage: __init__.py [-h] [--host HOST] [--port PORT] [--auto\_send] [--eps EPS] DEFINITION\_FILE [DEFINITION\_FILE ...]

        CEF builder and replayer

        positional arguments: 
        DEFINITION\_FILE an file containing event definitions

        optional arguments: 
        -h, --help show this help message and exit 
        --host HOST Syslog destination address 
        --port PORT Syslog destination port
        --auto\_send Auto send logs 
        --eps EPS Max EPS

Example
-------

.. code:: bash
        python **init**.py --host localhost --port 10514 --auto\_send --eps 10000 /tmp/example\_cef\_csv 
        
        [\*] [2016-07-21T03:27:30] There are 149
        events in the poll. The max EPS is set to 10000 
        [\*] [2016-07-21T03:27:40] Current EPS: 3479.0691266185677
        [\*] [2016-07-21T03:27:50] Current EPS: 3909.1143903948505 
        [\*] [2016-07-21T03:28:00] Current EPS: 3703.146674687884 
        [\*] [2016-07-21T03:28:10] Current EPS: 3521.793641832017 
        [\*] [2016-07-21T03:28:20] Current EPS: 3678.019083580161
        [\*] [2016-07-21T03:28:30] Current EPS: 3649.0109641324752 
        [\*] [2016-07-21T03:28:33] 228248 events sent since 2016-07-21 03:27:30.502906
