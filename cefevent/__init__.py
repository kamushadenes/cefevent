import argparse
import random
import re
import sched
import socket
import time
from datetime import datetime

import syslog
from cefevent.syslog import Syslog


class CEFEvent(object):

    _prefix_list = ['name', 'deviceVendor', 'deviceProduct',
                    'signatureId', 'version', 'deviceVersion', 'severity']

    _extension_dictionary = {

        'act': {'full_name': 'deviceAction', 'data_type': 'String', 'length': 63, 'description': 'Action mentioned in the event.'},
        'app': {'full_name': 'applicationProtocol', 'data_type': 'String', 'length': 31, 'description': 'Application level protocol, example values are: HTTP, HTTPS, SSHv2, Telnet, POP, IMAP, IMAPS, etc.'},

        'c6a1': {'full_name': 'deviceCustomIPv6Address1', 'data_type': 'IPv6 Address', 'length': 0, 'description': 'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.'},
        'c6a1Label': {'full_name': 'deviceCustomIPv6Address1Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'c6a2': {'full_name': 'deviceCustomIPv6Address2', 'data_type': 'IPv6 Address', 'length': 0, 'description': 'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.'},
        'c6a2Label': {'full_name': 'deviceCustomIPv6Address2Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'c6a3': {'full_name': 'deviceCustomIPv6Address3', 'data_type': 'IPv6 Address', 'length': 0, 'description': 'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.'},
        'c6a3Label': {'full_name': 'deviceCustomIPv6Address3Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'c6a4': {'full_name': 'deviceCustomIPv6Address4', 'data_type': 'IPv6 Address', 'length': 0, 'description': 'One of four IPV6 address fields available to map fields that do not apply to any other in this dictionary.'},
        'c6a4Label': {'full_name': 'deviceCustomIPv6Address4Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'cfp1': {'full_name': 'deviceCustomFloatingPoint1', 'data_type': 'Floating Point', 'length': 0, 'description': 'One of four floating point fields available to map fields that do not apply to any other in this dictionary.'},
        'cfp1Label': {'full_name': 'deviceCustomFloatingPoint1Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'cfp2': {'full_name': 'deviceCustomFloatingPoint2', 'data_type': 'Floating Point', 'length': 0, 'description': 'One of four floating point fields available to map fields that do not apply to any other in this dictionary.'},
        'cfp2Label': {'full_name': 'deviceCustomFloatingPoint2Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'cfp3': {'full_name': 'deviceCustomFloatingPoint3', 'data_type': 'Floating Point', 'length': 0, 'description': 'One of four floating point fields available to map fields that do not apply to any other in this dictionary.'},
        'cfp3Label': {'full_name': 'deviceCustomFloatingPoint3Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},

        'cfp4': {'full_name': 'deviceCustomFloatingPoint4', 'data_type': 'Floating Point', 'length': 0, 'description': 'One of four floating point fields available to map fields that do not apply to any other in this dictionary.'},
        'cfp4Label': {'full_name': 'deviceCustomFloatingPoint4Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},


        'cat': {'full_name': 'deviceEventCategory', 'data_type': 'String', 'length': 1023, 'description': 'Represents the category assigned by the originating device. Devices oftentimes use their own categorization schema to classify events.'},
        'cn1': {'full_name': 'deviceCustomNumber1', 'data_type': 'Long', 'length': 0, 'description': 'There are three number fields available which can be used to map fields which do not fit into any other field of this dictionary. If possible, "these fields should not be used, but a more specific field from the dictionary. Also check the guidelines hereafter for hints on how to utilize these fields.'},
        'cn1Label': {'full_name': 'deviceCustomNumber1Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cn2': {'full_name': 'deviceCustomNumber1', 'data_type': 'Long', 'length': 0, 'description': 'There are three number fields available which can be used to map fields which do not fit into any other field of this dictionary. If possible, "these fields should not be used, but a more specific field from the dictionary. Also check the guidelines hereafter for hints on how to utilize these fields.'},
        'cn2Label': {'full_name': 'deviceCustomNumber2Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cn3': {'full_name': 'deviceCustomNumber1', 'data_type': 'Long', 'length': 0, 'description': 'There are three number fields available which can be used to map fields which do not fit into any other field of this dictionary. If possible, "these fields should not be used, but a more specific field from the dictionary. Also check the guidelines hereafter for hints on how to utilize these fields.'},
        'cn3Label': {'full_name': 'deviceCustomNumber3Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cnt': {'full_name': 'baseEventCount', 'data_type': 'Integer', 'length': 0, 'description': 'A count associated with this event. How many times was this same event observed?'},
        'cs1': {'full_name': 'deviceCustomString1', 'data_type': 'String', 'length': 1023, 'description': 'There are six strings available which can be used to map fields which do not fit into any other field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'cs1Label': {'full_name': 'deviceCustomString1Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cs2': {'full_name': 'deviceCustomString2', 'data_type': 'String', 'length': 1023, 'description': 'There are six strings available which can be used to map fields which do not fit into any other field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'cs2Label': {'full_name': 'deviceCustomString2Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cs3': {'full_name': 'deviceCustomString3', 'data_type': 'String', 'length': 1023, 'description': 'There are six strings available which can be used to map fields which do not fit into any other field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'cs3Label': {'full_name': 'deviceCustomString3Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cs4': {'full_name': 'deviceCustomString4', 'data_type': 'String', 'length': 1023, 'description': 'There are six strings available which can be used to map fields which do not fit into any other field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'cs4Label': {'full_name': 'deviceCustomString4Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cs5': {'full_name': 'deviceCustomString5', 'data_type': 'String', 'length': 1023, 'description': 'There are six strings available which can be used to map fields which do not fit into any other field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'cs5Label': {'full_name': 'deviceCustomString5Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'cs6': {'full_name': 'deviceCustomString6', 'data_type': 'String', 'length': 1023, 'description': 'There are six strings available which can be used to map fields which do not fit into any other field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'cs6Label': {'full_name': 'deviceCustomString6Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'destinationDnsDomain': {'full_name': 'destinationDnsDomain', 'data_type': 'String', 'length': 255, 'description': 'The DNS domain part of the complete fully qualified domain name (FQDN).'},
        'destinationServiceName': {'full_name': 'destinationServiceName', 'data_type': 'String', 'length': 1023, 'description': 'The service which is targeted by this event.'},
        'destinationTranslatedAddress': {'full_name': 'destinationTranslatedAddress', 'data_type': 'IPv4 Address', 'length': 0, 'description': 'Identifies the translated destination that the event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"'},
        'destinationTranslatedPort': {'full_name': 'destinationTranslatedPort', 'data_type': 'Integer', 'length': 0, 'description': 'Port after it was translated'},
        'deviceCustomDate1': {'full_name': 'deviceCustomDate1', 'data_type': 'TimeStamp', 'length': 0, 'description': 'There are two timestamp fields'},
        'deviceCustomDate1Label': {'full_name': 'deviceCustomDate1Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'deviceCustomDate2': {'full_name': 'deviceCustomDate2', 'data_type': 'TimeStamp', 'length': 0, 'description': 'There are two timestamp fields available which can be used to map fields which do not fit into any other "field of this dictionary. If possible, these fields should not be used, but a more specific field from the dictionary. Also check the guidelines later in this document for hints about utilizing these fields.'},
        'deviceCustomDate2Label': {'full_name': 'deviceCustomDate2Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'deviceCustomDate3Label': {'full_name': 'deviceCustomDate3Label', 'data_type': 'String', 'length': 1023, 'description': 'All custom fields have a corresponding label field where the field itself can be described. Each of the fields is a string describing the purpose of this field.'},
        'deviceDirection': {'full_name': 'deviceDirection', 'data_type': 'String', 'length': 0, 'description': 'Any information about what direction the communication that was observed has taken.'},
        'deviceDnsDomain': {'full_name': 'deviceDnsDomain', 'data_type': 'String', 'length': 255, 'description': 'The DNS domain part of the complete fully qualified domain name (FQDN).'},
        'deviceExternalId': {'full_name': 'deviceExternalId', 'data_type': 'String', 'length': 255, 'description': 'A name that uniquely identifies the device generating this event.'},
        'deviceFacility': {'full_name': 'deviceFacility', 'data_type': 'String', 'length': 1023, 'description': 'The facility generating this event. Syslog for example has an explicit facility associated with every event.'},
        'deviceInboundInterface': {'full_name': 'deviceInboundInterface', 'data_type': 'String', 'length': 15, 'description': 'Interface on which the packet or data entered the device.'},
        'deviceMacAddress': {'full_name': 'deviceMacAddress', 'data_type': 'MAC Address', 'length': 0, 'description': 'Six colon-separated hexadecimal numbers. Example: 00:0D:60:AF:1B:61'},
        'deviceNtDomain': {'full_name': 'deviceNtDomain', 'data_type': 'String', 'length': 255, 'description': 'The Windows domain name of the device address.'},
        'deviceOutboundInterface': {'full_name': 'deviceOutboundInterface', 'data_type': 'String', 'length': 15, 'description': 'Interface on which the packet or data left the device.'},
        'deviceProcessName': {'full_name': 'deviceProcessName', 'data_type': 'String', 'length': 1023, 'description': 'Process name associated to the event. In UNIX, the process generating the syslog entry for example.'},
        'deviceTranslatedAddress': {'full_name': 'deviceTranslatedAddress', 'data_type': 'IPv4 Address', 'length': 0, 'description': 'Identifies the translated device address that the event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"'},
        'dhost': {'full_name': 'destinationHostName', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the destination that an event refers to in an IP network. The format should be a fully qualified domain name associated with the destination node, when a node is available. Examples: "host.domain.com" or "host".'},
        'dhost': {'full_name': 'DestinationHostName', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the source that an event refers to in an IP network. The format should be a fully qualified domain name associated with the "destination node, when a node is available. Examples: "host.domain.com" or "host".'},
        'dmac': {'full_name': 'destinationMac', 'data_type': 'MAC Address', 'length': 0, 'description': 'Six colon-separated hexadecimal numbers. Example: "00:0D:60:AF:1B:61"'},
        'dntdom': {'full_name': 'destinationNtDomain', 'data_type': 'String', 'length': 255, 'description': 'The Windows domain name of the destination address.'},
        'dpid': {'full_name': 'destinationProcessId', 'data_type': 'Integer', 'length': 0, 'description': 'Provides the ID of the destination process associated with the event. For example, if an event contains process ID 105, "105" is the process ID.'},
        'dpriv': {'full_name': 'destinationUserPrivileges', 'data_type': 'String', 'length': 1023, 'description': 'The allowed values are: "Administrator", "User", and "Guest". This identifies the destination user\'s privileges. In UNIX, for example, activity executed on the root user would be identified with destinationUserPrivileges of "Administrator". This is an idealized and simplified view on privileges and can be extended in the future.'},
        'dproc': {'full_name': 'destinationProcessName', 'data_type': 'String', 'length': 1023, 'description': 'The name of the process which is the event\'s destination. For example: "telnetd", or "sshd".'},
        'dpt': {'full_name': 'destinationPort', 'data_type': 'Integer', 'length': 0, 'description': 'The valid port numbers are between 0 and 65535.'},
        'dst': {'full_name': 'destinationAddress', 'data_type': 'IPv4 Address', 'length': 0, 'description': 'Identifies destination that the event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"'},
        'duid': {'full_name': 'destinationUserId', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the destination user by ID. For example, in UNIX, the root user is generally associated with user ID 0.'},
        'duser': {'full_name': 'destinationUserName', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the destination user by name. This is the user associated with the event\'s destination. E-mail addresses are also mapped into the UserName fields. The recipient is a candidate to put into destinationUserName.'},
        'dvc': {'full_name': 'deviceAddress', 'data_type': 'IPv4 Address', 'length': 16, 'description': 'Identifies the device that an event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"'},
        'dvchost': {'full_name': 'deviceHostName', 'data_type': 'String', 'length': 100, 'description': 'The format should be a fully qualified domain name associated with the device node, when a node is available. Examples: "host.domain.com" or "host".'},
        'dvcpid': {'full_name': 'deviceProcessId', 'data_type': 'Integer', 'length': 0, 'description': 'Provides the ID of the process on the device generating the event.'},
        'end': {'full_name': 'endTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'The time at which the activity related to the event ended. The format is MMM dd yyyy HH:mm:ss or milliseconds since epoch (Jan 1st 1970). An example would be reporting the end of a session.'},
        'externalId': {'full_name': 'externalId', 'data_type': 'Integer', 'length': 0, 'description': 'An ID used by the originating device.'},
        'fileCreateTime': {'full_name': 'fileCreateTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'Time when file was created.'},
        'fileHash': {'full_name': 'fileHash', 'data_type': 'String', 'length': 255, 'description': 'Hash of a file.'},
        'fileId': {'full_name': 'fileId', 'data_type': 'String', 'length': 1023, 'description': 'An ID associated with a file could be the inode.'},
        'fileModificationTime': {'full_name': 'fileModificationTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'Time when file was last modified.'},
        'filePath': {'full_name': 'filePath', 'data_type': 'String', 'length': 1023, 'description': 'Full path to the file, including file name itself.'},
        'filePermission': {'full_name': 'filePermission', 'data_type': 'String', 'length': 1023, 'description': 'Permissions of the file.'},
        'fileType': {'full_name': 'fileType', 'data_type': 'String', 'length': 1023, 'description': 'Type of file (pipe, socket, etc.)'},
        'fname': {'full_name': 'fileName', 'data_type': 'String', 'length': 1023, 'description': 'Name of the file.'},
        'fsize': {'full_name': 'fileSize', 'data_type': 'Integer', 'length': 0, 'description': 'Size of the file.'},
        'in': {'full_name': 'bytesIn', 'data_type': 'Integer', 'length': 0, 'description': 'Number of bytes transferred inbound. Inbound relative to the source to destination relationship, meaning that data was flowing from source to destination.'},
        'msg': {'full_name': 'message', 'data_type': 'String', 'length': 1023, 'description': 'An arbitrary message giving more details about the event. Multi-line entries can be produced by using \n as the new-line separator.'},
        'oldFileCreateTime': {'full_name': 'oldFileCreateTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'Time when old file was created.'},
        'oldFileHash': {'full_name': 'oldFileHash', 'data_type': 'String', 'length': 255, 'description': 'Hash of the old file.'},
        'oldFileId': {'full_name': 'oldFileId', 'data_type': 'String', 'length': 1023, 'description': 'An ID associated with the old file could be the inode.'},
        'oldFileModificationTime': {'full_name': 'oldFileModificationTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'Time when old file was last modified.'},
        'oldFileName': {'full_name': 'oldFileName', 'data_type': 'String', 'length': 1023, 'description': 'Name of the old file.'},
        'oldFilePath': {'full_name': 'oldFilePath', 'data_type': 'String', 'length': 1023, 'description': 'Full path to the old file, including file name itself.'},
        'oldFilePermission': {'full_name': 'oldFilePermission', 'data_type': 'String', 'length': 1023, 'description': 'Permissions of the old file.'},
        'oldFileSize': {'full_name': 'oldFileSize', 'data_type': 'Integer', 'length': 0, 'description': 'Size of the old file.'},
        'oldFileType': {'full_name': 'oldFileType', 'data_type': 'String', 'length': 1023, 'description': 'Type of the old file (pipe, socket, etc.)'},
        'out': {'full_name': 'bytesOut', 'data_type': 'Integer', 'length': 0, 'description': 'Number of bytes transferred outbound. Outbound relative to the source to destination relationship, meaning that data was flowing from destination to source.'},
        'proto': {'full_name': 'transportProtocol', 'data_type': 'String', 'length': 31, 'description': 'Identifies the Layer-4 protocol used. The possible values are protocol names such as TCP or UDP.'},
        'reason': {'full_name': 'reason', 'data_type': 'String', 'length': 1023, 'description': 'The reason an audit event was generated. For example "Bad password" or "Unknown User". This could also be an error or return code. Example: "0x1234"'},
        'requestClientApplication': {'full_name': 'requestClientApplication', 'data_type': 'String', 'length': 1023, 'description': 'The User-Agent associated with the request.'},
        'requestCookies': {'full_name': 'requestCookies', 'data_type': 'String', 'length': 1023, 'description': 'Cookies associated with the request.'},
        'requestMethod': {'full_name': 'requestMethod', 'data_type': 'String', 'length': 1023, 'description': 'The method used to access a URL. Possible values: "POST", "GET", ...'},
        'request': {'full_name': 'requestURL', 'data_type': 'String', 'length': 1023, 'description': 'In the case of an HTTP request, this field contains the URL accessed. The URL should contain the protocol as well, e.g., "http://www.security.com"'},
        'request': {'full_name': 'requestURL', 'data_type': 'String', 'length': 1023, 'description': 'In the case of an HTTP request, this field contains the URL accessed. The URL should contain the protocol as well, e.g., http://www.security.com'},
        'rt': {'full_name': 'receiptTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'The time at which the event related to the activity was received. The format is MMM dd yyyy HH:mm:ss or milliseconds since epoch (Jan 1st 1970).'},
        'shost': {'full_name': 'sourceHostName', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the source that an event refers to in an IP network. The format should be a fully qualified domain name associated with the source node, when a node is available. Examples: "host.domain.com" or "host".'},
        'smac': {'full_name': 'sourceMacAddress', 'data_type': 'MAC Address', 'length': 0, 'description': 'Six colon-separated hexadecimal numbers. Example: "00:0D:60:AF:1B:61"'},
        'sntdom': {'full_name': 'sourceNtDomain', 'data_type': 'String', 'length': 255, 'description': 'The Windows domain name for the source address.'},
        'sourceDnsDomain': {'full_name': 'sourceDnsDomain', 'data_type': 'String', 'length': 255, 'description': 'The DNS domain part of the complete fully qualified domain name (FQDN).'},
        'sourceServiceName': {'full_name': 'sourceServiceName', 'data_type': 'String', 'length': 1023, 'description': 'The service which is responsible for generating this event.'},
        'sourceTranslatedAddress': {'full_name': 'sourceTranslatedAddress', 'data_type': 'IPv4 Address', 'length': 0, 'description': 'Identifies the translated source that the event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"'},
        'sourceTranslatedPort': {'full_name': 'sourceTranslatedPort', 'data_type': 'Integer', 'length': 0, 'description': 'Port after it was translated by for example a firewall. Valid port numbers are 0 to 65535.'},
        'spid': {'full_name': 'sourceProcessId', 'data_type': 'Integer', 'length': 0, 'description': 'The ID of the source process associated with the event.'},
        'spriv': {'full_name': 'sourceUserPrivileges', 'data_type': 'String', 'length': 1023, 'description': 'The allowed values are: "Administrator", "User", and "Guest". It identifies the source user\'s privileges. In UNIX, for example, activity executed by the root user would be identified with sourceUserPrivileges of "Administrator". This is an idealized and simplified view on privileges and can be extended in the future.'},
        'spriv': {'full_name': 'sourceUserPrivileges', 'data_type': 'String', 'length': 1023, 'description': 'The allowed values are: Administrator", "User", and "Guest". It identifies the source user\'s privileges. In UNIX, for example, activity executed by the root user would be identified with sourceUserPrivileges of "Administrator". This is an idealized and simplified view on privileges and can be extended in the future.'},
        'spt': {'full_name': 'sourcePort', 'data_type': 'Integer', 'length': 0, 'description': 'The valid port numbers are 0 to 65535.'},
        'src': {'full_name': 'sourceAddress', 'data_type': 'IPv4 Address', 'length': 0, 'description': 'Identifies the source that an event refers to in an IP network. The format is an IPv4 address. Example: "192.168.10.1"'},
        'start': {'full_name': 'startTime', 'data_type': 'TimeStamp', 'length': 0, 'description': 'The time when the activity the event referred to started. The format is MMM dd yyyy HH:mm:ss or milliseconds since epoch (Jan 1st 1970).'},
        'suid': {'full_name': 'sourceUserId', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the source user by ID. This is the user associated with the source of the event. For example, in "UNIX, the root user is generally associated with user ID 0.'},
        'suser': {'full_name': 'sourceUserName', 'data_type': 'String', 'length': 1023, 'description': 'Identifies the source user by name. E-mail addresses are also mapped into the UserName fields. The sender is a candidate to put into sourceUserName.'},

    }

    def __init__(self):

        self.reset()

        self._reverse_extension_dictionary = {}

        self._validate_extensions()
        self._build_reverse_extension_dictionary()

    def __repr__(self):
        return self.build_cef()

    def _validate_field_value(self, field, value):
        obj = self._reverse_extension_dictionary[field]
        if obj['data_type'] in ['Integer', 'Long']:
            try:
                return int(value)
            except:
                return False
        elif obj['data_type'] == 'IPv4 Address':
            try:
                socket.inet_pton(socket.AF_INET, value)
            except AttributeError:  # no inet_pton here, sorry
                try:
                    socket.inet_aton(value)
                except socket.error:
                    return False
                if not value.count('.') == 3:
                    return False
            except socket.error:  # not a valid address
                return False
            return value

        elif obj['data_type'] == 'MAC Address':
            valid_mac = bool(re.match(
                '^' + '[\:\-]'.join(['([0-9a-f]{2})'] * 6) + '$', value.strip().lower()))
            if valid_mac:
                return value.strip().lower()
            else:
                return False

        elif obj['data_type'] == 'String':
            value = str(value).strip()

            if len(value) > obj['length'] and obj['length'] > 0:
                return False
            else:
                value = value.replace('\\', '\\\\')
                value = value.replace('=', '\\=')
                value = value.replace('\n', '\\n')
                return value

        else:
            # TODO: add validations for IPv6 Address and Floating Point
            return value

    def set_prefix(self, prefix, value):

        if prefix in self._prefix_list:
            if prefix == 'severity':
                if int(value) in range(0, 11):
                    self.prefixes[prefix] = int(value)
                    return self.prefixes[prefix]
                else:
                    return False
            else:
                value = value.replace('\\', '\\\\')
                value = value.replace('|', '\\|')
                self.prefixes[prefix] = value.strip()
                return self.prefixes[prefix]

    def set_field(self, field, value):

        if field in self._prefix_list:
            return self.set_prefix(field, value)

        if field in self._reverse_extension_dictionary:
            v = self._validate_field_value(field, value)
            if v:
                self.extensions[field] = v
                return self.extensions[field]
            else:
                return False
        elif field in self._extension_dictionary:
            field = self._extension_dictionary[field]['full_name']
            v = self._validate_field_value(field, value)
            if v:
                self.extensions[field] = v
                return self.extensions[field]
            else:
                return False

    def _build_reverse_extension_dictionary(self):

        for item in self._extension_dictionary.items():
            self._reverse_extension_dictionary[item[1]['full_name']] = item[1]
            self._reverse_extension_dictionary[
                item[1]['full_name']]['name'] = item[0]

    def _validate_extensions(self):
        for item in self._extension_dictionary.items():
            if item[1]['data_type'] not in ['TimeStamp', 'IPv4 Address', 'String', 'Long', 'Integer', 'MAC Address', 'IPv6 Address', 'Floating Point']:
                print(
                    '[-] Invalid data_type in item {}: {}'.format(item[0], item[1]['data_type']))
            try:
                int(item[1]['length'])
            except:
                print(
                    '[-] Invalid length in item {}: {}'.format(item[0], item[1]['length']))

    def build_cef(self):
        template = 'CEF:{version}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{signatureId}|{name}|{severity}|{extensions}'

        extensions = ['{}={}'.format(self.get_cef_field_name(field), self.extensions[
                                     field]) for field in self.extensions.keys()]

        return template.format(extensions=' '.join(extensions), **self.prefixes)

    def get_cef_field_name(self, field):
        if field in self._extension_dictionary:
            return field
        elif field in self._reverse_extension_dictionary:
            return self._reverse_extension_dictionary[field]['name']

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
        self.prefixes = {}

        self.prefixes['version'] = 0
        self.prefixes['deviceVendor'] = 'CEF Vendor'
        self.prefixes['deviceProduct'] = 'CEF Product'
        self.prefixes['deviceVersion'] = '1.0'
        self.prefixes['signatureId'] = '0'
        self.prefixes['name'] = 'CEF Event'
        self.prefixes['severity'] = 5

    def test(self):
        assert self.set_field(
            'sourceAddress', '192.168.67.1') == '192.168.67.1'
        assert self.set_field('sourceAddress', '192.168.67.500') == False
        assert self.set_field('sourceAddress', 'INVALID_DATA') == False

        assert self.set_field('sourceMacAddress', 'INVALID_DATA') == False
        assert self.set_field(
            'sourceMacAddress', '00:11:22:33:44:55') == '00:11:22:33:44:55'
        assert self.set_field(
            'sourceMacAddress', 'AA:bb:CC:dd:EE:ff') == 'aa:bb:cc:dd:ee:ff'
        assert self.set_field(
            'sourceMacAddress', 'AA:bb:CC:ZZ:EE:ff') == False

        assert self.set_field('sourcePort', 'INVALID_DATA') == False
        assert self.set_field('sourcePort', '123456') == 123456
        assert self.set_field('sourcePort', 123456) == 123456

        assert self.set_field('message', 'INVALID_DATA') == 'INVALID_DATA'
        assert self.set_field('message', 123456) == '123456'
        assert self.set_field('message', 'test=123456') == 'test\=123456'

        self.reset()


class CEFSender(object):

    def __init__(self, files, host, port):

        self.cef_poll = []
        self.host = host
        self.port = port
        self.syslog = Syslog(host, port=port)

        self.max_eps = 100

        self.sent_count = 0

        now = datetime.now()
        self.auto_send_start = now

        self.auto_send_checkpoint = now

        self.checkpoint_sent_count = 0

        self.scheduler = sched.scheduler(time.time, time.sleep)

        for fn in files:
            with open(fn, 'r') as f:
                lines = f.readlines()

                headers = [i.strip() for i in lines[0].split(';')]

                for l in lines[1:]:
                    l = l.strip()
                    fields = [i.strip() for i in l.split(';')]
                    if len(fields) != len(headers):
                        continue
                    cef = CEFEvent()
                    for r in range(0, len(fields) - 1):
                        cef.set_field(headers[r], fields[r])
                    self.cef_poll.append(cef)

    def get_info(self):
        self.log('There are {} events in the poll. The max EPS is set to {}'.format(
            len(self.cef_poll), self.max_eps))

    def send_log(self, cef):
        self.syslog.send(cef)
        self.sent_count += 1
        self.checkpoint_sent_count += 1

    def send_random_log(self, *args, **kw):
        self.send_log(random.choice(self.cef_poll))

    def timed_call(self, calls_per_second, callback, *args, **kw):
        period = 1.0 / calls_per_second

        def reload():
            callback(*args, **kw)
            self.scheduler.enter(period, 0, reload, ())
        self.scheduler.enter(period, 0, reload, ())

    def get_eps(self):
        now = datetime.now()
        time_diff = (now - self.auto_send_checkpoint).total_seconds()
        eps = self.checkpoint_sent_count / (time_diff if time_diff > 0 else 1)

        self.log('Current EPS: {}'.format(eps))

        self.auto_send_checkpoint = now
        self.checkpoint_sent_count = 0

    def log(self, msg):
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print('[*] [{}] {}'.format(now, msg))

    def get_total_event_count(self):
        self.log('{} events sent since {}'.format(
            self.sent_count, self.auto_send_start))

    def auto_send_log(self, eps):
        self.max_eps = eps
        self.get_info()
        self.auto_send_start = datetime.now()
        self.timed_call(eps, self.send_random_log)
        self.timed_call(0.1, self.get_eps)
        self.timed_call(0.016, self.get_total_event_count)
        self.scheduler.run()


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
