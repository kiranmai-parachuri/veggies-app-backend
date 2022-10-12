import json


def string_marshal(ip_list):
    return '|'.join(json.loads(ip_list))


def string_unmarshal(ip_string):
    return ip_string.split('|')
