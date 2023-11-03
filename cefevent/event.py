import re
import socket
from typing import Any, AnyStr, List

from cefevent.extensions import extension_dictionary


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

    def __init__(self, strict: bool = False):
        """
        Create a new CEFEvent.

        Arguments:
        - strict (`bool`): Set to True to throw ValueError if trying to create an invalid CEFEvent.

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

    def load(self, headers: List[AnyStr], fields: List[Any]):
        for idx, value in enumerate(fields):
            self.set_field(headers[idx], value)

    def _validate_field_value(self, field: AnyStr, value: Any):
        obj = self._reverse_extension_dictionary[field]

        for dt in obj["data_type"]:
            if dt in ["Integer", "Long"]:
                try:
                    return int(value)
                except:
                    continue
            elif dt == "IPv4 Address":
                if not value.count(".") == 3:
                    continue
                try:
                    socket.inet_pton(socket.AF_INET, value)
                except AttributeError:  # no inet_pton here, sorry
                    try:
                        socket.inet_aton(value)
                    except socket.error:
                        continue
                except socket.error:  # not a valid address
                    continue
                return value
            elif dt == "IPv6 Address":
                if not value.count(":") >= 2:
                    continue
                try:
                    socket.inet_pton(socket.AF_INET6, value)
                except:
                    continue
                return value
            elif dt == "MAC Address":
                valid_mac = bool(
                    re.match(
                        "^" + "[\\:\\-]".join(["([0-9a-f]{2})"] * 6) + "$",
                        value.strip().lower(),
                    )
                )
                if valid_mac:
                    return value.strip().lower()
                else:
                    continue

            elif dt == "String":
                value = str(value).strip()

                if len(value) > obj["length"] > 0:
                    continue
                else:
                    value = value.replace("\\", "\\\\")
                    value = value.replace("=", "\\=")
                    value = value.replace("\n", "\\n")
                    return value
            elif dt == "Floating Point":
                try:
                    return float(value)
                except:
                    continue
            else:
                return value

        return False

    def set_prefix(self, prefix: AnyStr, value: Any):
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

    def set_field(self, field: AnyStr, value: Any):
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
            for dt in item[1]["data_type"]:
                if dt not in [
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

    def get_fields(self):
        return dict(**self.prefixes, **self.extensions)

    def get_cef_field_name(self, field: AnyStr):
        if field in self._extension_dictionary:
            return field
        elif field in self._reverse_extension_dictionary:
            return self._reverse_extension_dictionary[field]["name"]

    def get_field_metadata(self, field: AnyStr, metadata: AnyStr = None):
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
