import base64
import time

import datetime
import uuid
import pyrfc3339
try:
    import pytz
except :
    pass

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


def rfc3339_to_unix_time(rfc3339_str):
    dt = pyrfc3339.parse(rfc3339_str,True)
    t = (dt - datetime.datetime(1970,1,1,tzinfo=pytz.utc)).total_seconds()
    return int(t*1000)


if __name__ == "__main__":
    dt = rfc3339_to_unix_time("2016-01-18T12:49:51.372Z")
    print dt