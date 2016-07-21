# cefevent
ArcSight's Common Event Format library

This library is able to generate, validate and send CEF events (currently peaking at about 3400 EPS)

It uses CSV files with the CEF field names as headers in the first line and then sends it at the specified EPS rate to the configured UDP Syslog destination.


## Usage

Below you can see cefevent being used as an standalone program to replay CEF events from a CSV file.

```
usage: run.py [-h] [--host HOST] [--port PORT] [--auto_send] [--eps EPS]
                   DEFINITION_FILE [DEFINITION_FILE ...]

CEF builder and replayer

positional arguments:
  DEFINITION_FILE  an file containing event definitions

optional arguments:
  -h, --help       show this help message and exit
  --host HOST      Syslog destination address
  --port PORT      Syslog destination port
  --auto_send      Auto send logs
  --eps EPS        Max EPS
```

### Replay Example
```
python run.py --host localhost --port 10514 --auto_send --eps 10000 /tmp/example_cef_csv
[*] [2016-07-21T03:27:30] There are 149 events in the poll. The max EPS is set to 10000
[*] [2016-07-21T03:27:40] Current EPS: 3479.0691266185677
[*] [2016-07-21T03:27:50] Current EPS: 3909.1143903948505
[*] [2016-07-21T03:28:00] Current EPS: 3703.146674687884
[*] [2016-07-21T03:28:10] Current EPS: 3521.793641832017
[*] [2016-07-21T03:28:20] Current EPS: 3678.019083580161
[*] [2016-07-21T03:28:30] Current EPS: 3649.0109641324752
[*] [2016-07-21T03:28:33] 228248 events sent since 2016-07-21 03:27:30.502906
```

### API Example

#### Get field metadata

```
from cefevent import CEFEvent
c = CEFEvent()

c.get_field_metadata('c6a1', 'full_name')
'deviceCustomIPv6Address1'


c.get_field_metadata('c6a1', 'data_type')

'IPv6 Address'


c.get_field_metadata('c6a1', 'description')

'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.'


c.get_field_metadata('c6a1')
 
{'data_type': 'IPv6 Address',
 'description': 'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.',
 'full_name': 'deviceCustomIPv6Address1',
 'length': 0,
 'name': 'c6a1'}
```

#### Convert ArcSight Naming to CEF naming
```
from cefevent import CEFEvent
c = CEFEvent()

c.get_cef_field_name('deviceAddress')

'dvc'
```

#### Build an CEF event from scratch

```
from cefevent import CEFEvent
c = CEFEvent()

c.set_field('name', 'Event Name')
c.set_field('deviceVendor', 'Hyades Inc.')
c.set_field('deviceProduct', 'cefevent')

# Equal signs will be automatically escaped (and so will pipes (|) and backslashes (\\), as per the white paper specification)
c.set_field('message', 'This is an test event (Answer=42)')

# All fields have some sort of validation, check the test() function for examples
c.set_field('sourceAddress', '192.168.67.1')
c.set_field('sourcePort', 12345)

# Finally, generate the CEF line
c.build_cef()

'CEF:0|Hyades Inc.|cefevent|1.0|0|Event Name|5|spt=12345 src=192.168.67.1 msg=This is an test event (Answer\\=42)'


