import re
import socket

from .extensions import extension_dictionary


class CEFEvent(object):
    _prefix_list = [
        "name",
        "deviceVendor",
        "deviceProduct",
        "signatureId",
        "version",
        "deviceVersion",
        "severity",
    ]

    _extension_dictionary = extension_dictionary

    def __init__(self, strict=False):
        """
        Create a new CEFEvent.

        Arguments:
        - strict (`bool`): Set to True to throw ValueError if trying to create create an invalid CEFEvent.

        """

        self.extensions = None
        self.prefixes = {}
        self.reset()

        self._reverse_extension_dictionary = {}

        self._validate_extensions()
        self._build_reverse_extension_dictionary()

        self.strict = strict

    def __repr__(self):
        return self.build_cef()

    def _validate_field_value(self, field, value):
        obj = self._reverse_extension_dictionary[field]
        if obj["data_type"] in ["Integer", "Long"]:
            try:
                return int(value)
            except:
                return False
        elif obj["data_type"] == "IPv4 Address":
            try:
                socket.inet_pton(socket.AF_INET, value)
            except AttributeError:  # no inet_pton here, sorry
                try:
                    socket.inet_aton(value)
                except socket.error:
                    return False
                if not value.count(".") == 3:
                    return False
            except socket.error:  # not a valid address
                return False
            return value

        elif obj["data_type"] == "MAC Address":
            valid_mac = bool(
                re.match(
                    "^" + "[\:\-]".join(["([0-9a-f]{2})"] * 6) + "$",
                    value.strip().lower(),
                )
            )
            if valid_mac:
                return value.strip().lower()
            else:
                return False

        elif obj["data_type"] == "String":
            value = str(value).strip()

            if len(value) > obj["length"] > 0:
                return False
            else:
                value = value.replace("\\", "\\\\")
                value = value.replace("=", "\\=")
                value = value.replace("\n", "\\n")
                return value

        else:
            # TODO: add validations for IPv6 Address and Floating Point
            return value

    def set_prefix(self, prefix, value):

        if prefix in self._prefix_list:
            if prefix == "severity":
                if value in ["Unknown", "Low", "Medium", "High", "Very-High"]:
                    self.prefixes[prefix] = value
                    return self.prefixes[prefix]
                elif int(value) in range(0, 11):
                    self.prefixes[prefix] = int(value)
                    return self.prefixes[prefix]
                else:
                    if self.strict:
                        raise ValueError(
                            "The severity must be an int in [0-10]. Not: {}".format(
                                value
                            )
                        )
                    return False
            else:
                value = value.replace("\\", "\\\\")
                value = value.replace("|", "\\|")
                self.prefixes[prefix] = value.strip()
                return self.prefixes[prefix]
        if self.strict:
            raise ValueError("Unknown CEF prefix: {}".format(prefix))
        return False

    def set_field(self, field, value):

        if field in self._prefix_list:
            return self.set_prefix(field, value)

        if field in self._reverse_extension_dictionary:
            v = self._validate_field_value(field, value)
            if v is not False:
                self.extensions[field] = v
                return self.extensions[field]
            else:
                if self.strict:
                    raise ValueError(
                        "Invalid value for field: {}\nThe following rules apply: {}".format(
                            field, self.get_field_metadata(field)
                        )
                    )
                return False
        elif field in self._extension_dictionary:
            field = self._extension_dictionary[field]["full_name"]
            v = self._validate_field_value(field, value)
            if v:
                self.extensions[field] = v
                return self.extensions[field]
            else:
                if self.strict:
                    raise ValueError(
                        "Invalid value for field: {}\nThe following rules apply: {}".format(
                            field, self.get_field_metadata(field)
                        )
                    )
                return False
        if self.strict:
            raise ValueError("Unknown CEF field: {}".format(field))
        return False

    def _build_reverse_extension_dictionary(self):

        for item in self._extension_dictionary.items():
            self._reverse_extension_dictionary[item[1]["full_name"]] = item[1]
            self._reverse_extension_dictionary[item[1]["full_name"]]["name"] = item[0]

    def _validate_extensions(self):
        for item in self._extension_dictionary.items():
            if item[1]["data_type"] not in [
                "TimeStamp",
                "IPv4 Address",
                "String",
                "Long",
                "Integer",
                "MAC Address",
                "IPv6 Address",
                "Floating Point",
            ]:
                print(
                    "[-] Invalid data_type in item {}: {}".format(
                        item[0], item[1]["data_type"]
                    )
                )
            try:
                int(item[1]["length"])
            except:
                print(
                    "[-] Invalid length in item {}: {}".format(
                        item[0], item[1]["length"]
                    )
                )

    def build_cef(self):
        template = "CEF:{version}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{signatureId}|{name}|{severity}|{extensions}"

        extensions = [
            "{}={}".format(self.get_cef_field_name(field), self.extensions[field])
            for field in self.extensions.keys()
        ]

        return template.format(extensions=" ".join(extensions), **self.prefixes)

    def get_cef_field_name(self, field):
        if field in self._extension_dictionary:
            return field
        elif field in self._reverse_extension_dictionary:
            return self._reverse_extension_dictionary[field]["name"]

    def get_field_metadata(self, field, metadata=None):
        if field in self._extension_dictionary:
            if not metadata:
                return self._extension_dictionary[field]
            else:
                return self._extension_dictionary[field][metadata]
        elif field in self._reverse_extension_dictionary:
            if not metadata:
                return self._reverse_extension_dictionary[field]
            else:
                return self._reverse_extension_dictionary[field][metadata]

    def reset(self):
        self.extensions = {}
        self.prefixes = {
            "version": 0,
            "deviceVendor": "CEF Vendor",
            "deviceProduct": "CEF Product",
            "deviceVersion": "1.0",
            "signatureId": "0",
            "name": "CEF Event",
            "severity": 5,
        }

    def test(self):
        assert self.set_field("sourceAddress", "192.168.67.1") == "192.168.67.1"
        assert self.set_field("sourceAddress", "192.168.67.500") == False
        assert self.set_field("sourceAddress", "INVALID_DATA") == False

        assert self.set_field("sourceMacAddress", "INVALID_DATA") == False
        assert (
            self.set_field("sourceMacAddress", "00:11:22:33:44:55")
            == "00:11:22:33:44:55"
        )
        assert (
            self.set_field("sourceMacAddress", "AA:bb:CC:dd:EE:ff")
            == "aa:bb:cc:dd:ee:ff"
        )
        assert self.set_field("sourceMacAddress", "AA:bb:CC:ZZ:EE:ff") == False

        assert self.set_field("sourcePort", "INVALID_DATA") == False
        assert self.set_field("sourcePort", "123456") == 123456
        assert self.set_field("sourcePort", 123456) == 123456

        assert self.set_field("message", "INVALID_DATA") == "INVALID_DATA"
        assert self.set_field("message", 123456) == "123456"
        assert self.set_field("message", "test=123456") == "test\=123456"

        self.strict = True
        try:
            self.set_field("sourceAddress", "notaIPaddress")
        except ValueError as e:
            assert "The following rules apply" in str(
                e
            ), "The string 'The following rules apply' do not appear in thown error when setting an invalid ip"
        else:
            assert (
                False
            ), "The set_field() fields methods did ot throw an error when setting an invalid ip"

        try:
            self.set_field("src", "notaIPaddress")
        except ValueError as e:
            assert "The following rules apply" in str(
                e
            ), "The string 'The following rules apply' do not appear in thown error when setting an invalid ip"
        else:
            assert (
                False
            ), "The set_field() fields methods did ot throw an error when setting an invalid ip"

        try:
            self.set_field("not an field name", "VALUE")
        except ValueError as e:
            assert "Unknown CEF field" in str(
                e
            ), "The string 'Unknown CEF field' do not appear in thown error"
        else:
            assert (
                False
            ), "The set_field() fields methods did ot throw an error when setting an unknown field"

        try:
            self.set_prefix("not an prefix name", "VALUE")
        except ValueError as e:
            assert "Unknown CEF prefix" in str(
                e
            ), "The string 'Unknown CEF prefix' do not appear in thown error"
        else:
            assert (
                False
            ), "The set_prefix() fields methods did ot throw an error when setting an unknown prefix"

        try:
            self.set_prefix("severity", 42)
        except ValueError as e:
            assert "The severity must be an int in [0-10]" in str(
                e
            ), "The string 'The severity must be an int in [0-10]' do not appear in thown error"
        else:
            assert (
                False
            ), "The set_prefix() fields methods did ot throw an error when setting an severevity out of bounds"

        self.strict = False
        try:
            try:
                self.set_field("src", "notaIPaddress")
            except ValueError as e:
                assert "The following rules apply" in str(
                    e
                ), "The string 'The following rules apply' do not appear in thown error when setting an invalid ip"
            else:
                assert (
                    False
                ), "The set_field() fields methods did ot throw an error when setting an invalid ip"
        except AssertionError as e:
            pass
        else:
            assert False, "The strict test passed event if self.strict=False"

        self.reset()
