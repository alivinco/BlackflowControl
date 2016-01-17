import base64
import time

import datetime
import uuid

__author__ = 'alivinco'

def get_next_id(values):
    next_id = 0
    for item in values:
        if item["id"]>next_id:next_id = item["id"]
    return next_id + 1

def convert_bool(str):
    if str=="true":
        return True
    else:
        return False


def format_iso_time_from_sec(time_in_sec):
    t = time.localtime(time_in_sec)
    return time.strftime("%Y-%m-%d %H:%M:%S", t)


def gen_sid():
    # r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    # return r_uuid.replace('=', '')
    return hex(uuid.getnode()).replace("0x","")