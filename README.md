<h1 align="center">cefevent</h1>

<p align="center">
ArcSight's Common Event Format library
</p>

<hr>

[![Downloads](https://pepy.tech/badge/cefevent)](https://pepy.tech/project/cefevent)
![GitHub](https://img.shields.io/github/license/kamushadenes/cefevent)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/kamushadenes/cefevent)
![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/kamushadenes/cefevent)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kamushadenes/cefevent)
![PyPI - Format](https://img.shields.io/pypi/format/cefevent)


<hr>

This library is able to generate, validate and send CEF events.

<hr>

## Usage

```
usage: run.py [-h] --host HOST [--port PORT] [--tcp] [--auto_send] [--eps EPS] DEFINITION_FILE [DEFINITION_FILE ...]

CEF builder and replayer

positional arguments:
  DEFINITION_FILE  an file containing event definitions

optional arguments:
  -h, --help       show this help message and exit
  --host HOST      Syslog destination host
  --port PORT      Syslog destination port
  --tcp            Use TCP instead of UDP
  --auto_send      Auto send logs
  --eps EPS        Max EPS
```

By default, it will read the definition file and send each log line once.

If instead `--auto_send` is specified, it will send at `--eps` events per second.

You can use either TCP or UDP Syslog servers as destination.

### DEFINITION_FILE format
The definition file is a CSV file, delimited by `;`, with the CEF field names as headers in the first line.

### Send Once Example
```
python run.py --host localhost --port 10514 /tmp/example_cef_csv
[*] [2022-05-11T03:12:40] 42 events sent
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

### API Usage

#### Get field metadata

```python
>>> from cefevent.event import CEFEvent
>>> c = CEFEvent()

>>> c.get_field_metadata('c6a1', 'full_name')

'deviceCustomIPv6Address1'


>>> c.get_field_metadata('c6a1', 'data_type')

'IPv6 Address'


>>> c.get_field_metadata('c6a1', 'description')

'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.'


>>> c.get_field_metadata('c6a1')
 
{'data_type': 'IPv6 Address',
 'description': 'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.',
 'full_name': 'deviceCustomIPv6Address1',
 'length': 0,
 'name': 'c6a1'}
```

#### Convert ArcSight Naming to CEF Naming

```python
>>> from cefevent.event import CEFEvent
>>> c = CEFEvent()

>>> c.get_cef_field_name('deviceAddress')

'dvc'
```

#### Build an CEF event from scratch

```python
>>> from cefevent.event import CEFEvent
>>> c = CEFEvent()

>>> c.set_field('name', 'Event Name')
>>> c.set_field('deviceVendor', 'Hyades Inc.')
>>> c.set_field('deviceProduct', 'cefevent')

# Equal signs will be automatically escaped (and so will pipes (|) and backslashes (\\), as per the white paper specification)
>>> c.set_field('message', 'This is a test event (Answer=42)')

# All fields have some sort of validation, check the test() function for examples
>>> c.set_field('sourceAddress', '192.168.67.1')
>>> c.set_field('sourcePort', 12345)

# Finally, generate the CEF line
>>> c.build_cef()

CEF:0|Hyades Inc.|cefevent|1.0|0|Event Name|5|spt=12345 src=192.168.67.1 msg=This is a test event (Answer\\=42)
```

#### Event Generation

The library is able to generate events using random data, respecting each field's data type and length limits.

```python
>>> from cefevent.generator import generate_random_events
>>> events = generate_random_events(field_count=10, event_count=100)

>>> len(events)
100

>>> events[0]
CEF:0|CEF Vendor|CEF Product|1.0|0|Random CEF Event|5|cs5=okppjRMb57C3dLmTZc0gF2xcwCR9BWTG5IjhbiaPQj2RIYBM6frkKt4pFH6pGf7o7ajt1sQspiV6oCsfXRfl5mK199RjQvXpuU7K6JEDxF8F9SJxXHJrKVbl2Vlokfbet deviceDnsDomain=kV2F27lmrjig95bjUOqpAeeWD74VO0GOSfhvEZQ00NUW0TYuOzoEal0ksYmH8Epu5HRXTTn8IgwTcprN3ifcKQpNLZFfRxSCXMDYatWeE01UrOnlNr8cbHbVd9OxsiQwy6bWGd4UWl2Za2MS0A49vSEmYJtrkqUIZjskQGXxt8Aoz1myiqADIjyMm4HM3B oldFileType=nIPPu48a4zSAPy3jnsTc96Z3vDIKSmsEl8yFqWiAufVmAxAdNqJUlwCWFiG4VGtTrnPYfhIaAnbiu2Cg28oJWf2d2wB01BW29lXwoeE c6a1=fd00::8fba:74fb:c861:31cf cn3Label=IsTUoz63jtiHRTrOisYbMCxPCThcwvNDoTho00yobR4O2HOUVmiTuWJ1hk6otOkHZWCMeJVeflrJyE06pjFYDgp9raCQVPYwRTvAxGVzFNSJhQvq9Fe0nS8CdkQLUbbjho1upU0mrIMSWA09d9Jo5g5CzrHDdkRld7isaRrZELlG6WyVGuGT8A25uah2Hx9E6C7CzhRjSJbdJV86eH2MPMjj0KWmBbqs1CamMYjNC0KrBK19oDotIjONp6OHD01Dy2VUJcVR0u1kz8EO0bVls8YVYaxohy5L4vRKd5171z6z2MzIM8hVWfoVNpYPCMvCsDK1JqLyV98u3pMSIhHAWdtczaMSNzJ0oDiHRYczZVPLndPPjGkNRLiYggQVVekyfgEq9yYj4mNJ37aiaOfqaYAnMgTO45qZ2FOqeaJ2wNGuWFbwm0Ttr9unlmzzYw49UBVoDR1IIzKezTkfIzMDf6u04o5IYlUqjnIo7m3sfrUyNnvafA1htPG6uRjpDVeNTuJ4juQeUHzoK0yIOtCa7jR8gwjlx3YnR7NvntcZVkzfFzcQmkapFeuzmXBgRXRIm4FfneMSWZfzWHpikBGAD9GHJidcSoKC9pIExlsSgPufhQYnHI9b221si50aMwJNULGPZ134flM1FmGdOsvRDBoZx5Cu0zriA8cm0oSdWjhyP4vkYnT9oWmNAW0iCP8U0IM5sojtFaqSDLiDGFf6Gt45e2AvVoYZaIsjg8JhGmHOQ2zkoSql5dcNCIatmiMAwuNmh3DG3HBJREY23hR03LI1VNIPZH2YtmfeYQ4S7hzh2ulpYaAX7qrJtMKWdkEGAwsfaB6TgijL04nq7Hj9e0mnWrxcSPixlm98THZIhefYamh9ywq2hGzrgjEW1sNrvAUqKYhoQg6ORxvsoHVPT oldFilePermission=TEUtuXQWIM0qXlHJEK0HsM1TuWDvUOUKkIlTg8ZIdfJvxdT5CD6OXAXSkaaP4RsLRRnTGdpC4N8hbNbtBPVpug9XZHwQH9NCbKq8tE8j1VMWzilorUa60SAI4NcVhlmCF40NOH4A4kIcmvBAriU8DViCsySJ2DEBPKffXlNlnoZd38xCI9SOVzk7Y8dIRc34DRwqdjrKYNStbDA1xDvC9IlujF90W5TWutrh1tiRV16PqW7jPzggbVHYOZx0o8QimK5SMknQmERL2OsmIByc8RiZGzQbMfBKUGjJZNSR6d4RT68XvyN8Qqz9F9fmiWcPjx40yDkp4ATXIyhc8ClphIydsgbT7ucqvTwtnMi2w27Dp5MtxpiyLDRXcUlKu7yFwIlbU5JCIIj6esnM5zHK9e7VAxM5B1IWxYE0lxS7T8Y73vI3k0kziko1fQeckavQxjjKADloiMChkHwscOzF6k52tUzph8nqexVeclC9XoEMioQpTyKZTib4tYOqPvLW6vE7QtwmyOpOEFWpMb6nKRBZdprhI7jpzABSi5iF91IKHUgmaloiIAeaYC4J9NmEFUZwb7DTKL3MD7tSTbuIMbzhE3pAnwNTA3zMcjakULGgF8yJDijCDGogMFFjVQFyiYJfnZiNeAjpcV5YWMhc0gHB4wlaTuZPPhW0AxO0CdeaRKjM5St66EJ4QsMyvUiuUudH5DPHLRaGqfJJS0cjl3QhSD8MZ64l5MXb1OB1W1os4q cfp1=551727113.03403 destinationTranslatedPort=28984019 cn2Label=Ed7RC17O8V4v5XVB8hTbxypElVpCVEvelfurInKjehXOmj6UYACs5oaz4Yq15njcPzGyayTpMJ6NyYZDgvqSHCmd1uGld2JxVwQbqUdwpNEM66jjqbdPKJu2gEctNLtdJ8YmMvjKqqmBvdUEhKUDtJacSLSKWeqon36ww4lezQHh4mJxvHvQ2wXRvwgXSEHomuvTOQYA1EZ7TjzTjnBVr0GJgZPjJDIyLLeEbXMtXQQnOY0nKTkrciqPFEC7JgoFhwmNqq8p7fygcOed7yYEq9uAbgznyTekdWmv7fjVQFjc7CvtSkjGWijUUT7g2xQXXfYgklL3sgyBe3xGP83AA1x7hGWBFB7P60U7oWGpJcTt79bcbZqd3NJ18vKwiyUaV3ynUPGCEuFU0TUbirkg3eIIEfN0tgBYmbhJQPsLBITwmoDS8S041teA2ZRoFA5Pqbt8EWlarwbAdVCgIQtWthQe1QjJb7cnDy8m4kpx2ObkqEYrrxdCBSkOfvkhms8lRO3dyHtXBgi8x2U3ZP9GtGKjEG4zqKW6RSgbKKfAsEt1NmguQLaTl7q3UMZJTfFKjiSKy2EhP85CQflcjzioCcC5AnZN7nivtsuo31Wx5PVRcWx1cKnSlx2TAAQFxAMCOWmtdK1kWkLixQDLJgStNkDhe4Fy7keHbCNiJPy6ul7qeA9R76sDJIZPYptUzD3KsTpFtQvLkVpKsOak2PqXMLKSeliOg4J7xRiP9LoIl66pyud3LNegpKvU3BHrSuaDJANNpA6ZWfHxQdIo8QHpwsE6CzmjaxElMOUTxhSQZ9KpplXd8mOk cs6=M4gm4bKeOEDmrXCSRt4VWlwDI7REf99BtjDEUqcITnLEfP6k7m9YiuoBe5aoRNA351tRWS5U1fG4huiqnhKRDpgbaicoksujDlNELHFVpcdEfShkVf5jFAXOK0M06Z4nNHIWMoGukNM06pLxtfDwVeNXOFUSWfwzqeghqYXugO9H2V5qHC6jjwWiXDR2jdBLGchDsqisZbVIJPmTH5uJ7sayYPRE3DEoOfY7ZuX66rEJaaibWQJXIfWZYhIUZhLaZG7rrVBBeifAyfWqez9xsCBcNHj292B7YFEBuNoEJAcrUWsLSThf33MYvA1veIACUa7w1TcLsWeCBGoQ165fJa4m3LO0p5dEpMPkMlC7uiqItjpwofDchXSdqSVvF25AZ2XZ2h6pTodPF3Z7mwAbTlfLjyk00ncbziWuv2LYxNuvng81BNqp7mPhOzidIsT265SnZS69SQNzOzHciepWMMcJBu2aYyk4xyFUuClo6LQrn7ZzC5JPoQUhghpEajVE9vE4wRulW53qePJ9IDKjzXe1kWcnaMo3D0P3E4mZaohXZ1ApvJZxWFEnKP
```

#### Raise errors

By default, the methods `set_field()` and `set_prefix()` return `False` if the name or the value or the CEF field is invalid.  

Set `CEFEvent.strict=True` to raise `ValueError` if any invalid field name / values are passed.  

```python
>>> from cefevent.event import CEFEvent
>>> c = CEFEvent(strict=True)
>>> c.set_field('sourceAddress', '192.168.67.500')
```

```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "cefevent/cefevent/__init__.py", line 249, in set_field
    raise ValueError("Invalid value for field: {}\nThe following rules apply: {}".format(field, self.get_field_metadata(field)))
ValueError: Invalid value for field: sourceAddress
The following rules apply: {'full_name': 'sourceAddress', 'data_type': 'IPv4 Address', 'length': 0, 'description': 'Identifies the source that an event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"', 'name': 'src'}
```

## Running Tests

The project uses [pytest](https://pytest.org/).

```bash
pytest -v
```

```
================================================================== test session starts ==================================================================
platform darwin -- Python 3.9.12, pytest-7.1.2, pluggy-1.0.0 -- /opt/homebrew/opt/python@3.9/bin/python3.9
cachedir: .pytest_cache
rootdir: /Users/henrique.goncalves/Dropbox/Projects/Personal/Code/cefevent
collected 9 items

test_event.py::test_load PASSED                                                                                                                   [ 11%]
test_event.py::test_source_address PASSED                                                                                                         [ 22%]
test_event.py::test_source_mac_address PASSED                                                                                                     [ 33%]
test_event.py::test_source_port PASSED                                                                                                            [ 44%]
test_event.py::test_message PASSED                                                                                                                [ 55%]
test_event.py::test_strict PASSED                                                                                                                 [ 66%]
test_generator.py::test_random_addr PASSED                                                                                                        [ 77%]
test_generator.py::test_generate_random_events PASSED                                                                                             [ 88%]
test_sender.py::test_sender PASSED                                                                                                                [100%]

=================================================================== 9 passed in 6.71s ===================================================================
```
