from cefevent.event import CEFEvent


def test_load():
    ev = CEFEvent()

    headers = ["sourceAddress", "name", "message", "sourcePort"]
    fields = ["127.0.0.1", "Test Event", "Answer=42", 1234]
    ev.load(headers, fields)

    assert (
        ev.build_cef()
        == "CEF:0|CEF Vendor|CEF Product|1.0|0|Test Event|5|src=127.0.0.1 msg=Answer\\=42 spt=1234"
    )


def test_source_address():
    ev = CEFEvent()

    assert ev.set_field("sourceAddress", "192.168.67.1") == "192.168.67.1"
    assert ev.set_field("sourceAddress", "192.168.67.500") is False
    assert ev.set_field("sourceAddress", "INVALID_DATA") is False


def test_source_mac_address():
    ev = CEFEvent()

    assert ev.set_field("sourceMacAddress", "INVALID_DATA") is False
    assert ev.set_field("sourceMacAddress", "00:11:22:33:44:55") == "00:11:22:33:44:55"
    assert ev.set_field("sourceMacAddress", "AA:bb:CC:dd:EE:ff") == "aa:bb:cc:dd:ee:ff"
    assert ev.set_field("sourceMacAddress", "AA:bb:CC:ZZ:EE:ff") is False


def test_source_port():
    ev = CEFEvent()

    assert ev.set_field("sourcePort", "INVALID_DATA") is False
    assert ev.set_field("sourcePort", "123456") is False
    assert ev.set_field("sourcePort", 123456) is False
    assert ev.set_field("sourcePort", "12345") == 12345
    assert ev.set_field("sourcePort", 12345) == 12345


def test_message():
    ev = CEFEvent()

    assert ev.set_field("message", "INVALID_DATA") == "INVALID_DATA"
    assert ev.set_field("message", 123456) == "123456"
    assert ev.set_field("message", "test=123456") == "test\\=123456"


def test_deviceCustomIPv6Address4():
    ev = CEFEvent()

    assert ev.set_field("deviceCustomIPv6Address4", "INVALID_DATA") is False
    assert ev.set_field("deviceCustomIPv6Address4", "2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    assert ev.set_field("deviceCustomIPv6Address4", "2001:0db8:85a3::1") == "2001:0db8:85a3::1"


def test_strict():
    ev = CEFEvent()

    ev.strict = True
    try:
        ev.set_field("sourceAddress", "not_a_ip_address")
    except ValueError as e:
        assert "The following rules apply" in str(
            e
        ), "The string 'The following rules apply' do not appear in thrown error when setting an invalid ip"
    else:
        assert (
            False
        ), "The set_field() fields methods did ot throw an error when setting an invalid ip"

    try:
        ev.set_field("src", "not_a_ip_address")
    except ValueError as e:
        assert "The following rules apply" in str(
            e
        ), "The string 'The following rules apply' do not appear in thrown error when setting an invalid ip"
    else:
        assert (
            False
        ), "The set_field() fields methods did ot throw an error when setting an invalid ip"

    try:
        ev.set_field("not an field name", "VALUE")
    except ValueError as e:
        assert "Unknown CEF field" in str(
            e
        ), "The string 'Unknown CEF field' do not appear in thrown error"
    else:
        assert (
            False
        ), "The set_field() fields methods did ot throw an error when setting an unknown field"

    try:
        ev.set_prefix("not an prefix name", "VALUE")
    except ValueError as e:
        assert "Unknown CEF prefix" in str(
            e
        ), "The string 'Unknown CEF prefix' do not appear in thrown error"
    else:
        assert (
            False
        ), "The set_prefix() fields methods did ot throw an error when setting an unknown prefix"

    try:
        ev.set_prefix("severity", 42)
    except ValueError as e:
        assert "The severity must be an int in [0-10]" in str(
            e
        ), "The string 'The severity must be an int in [0-10]' do not appear in thrown error"
    else:
        assert (
            False
        ), "The set_prefix() fields methods did ot throw an error when setting an severity out of bounds"

    ev.strict = False
    try:
        try:
            ev.set_field("src", "notaIPaddress")
        except ValueError as e:
            assert "The following rules apply" in str(
                e
            ), "The string 'The following rules apply' do not appear in thrown error when setting an invalid ip"
        else:
            assert (
                False
            ), "The set_field() fields methods did ot throw an error when setting an invalid ip"
    except AssertionError:
        pass
    else:
        assert False, "The strict test passed event if ev.strict=False"
