import base64
import json
import time
import os
import datetime
import uuid
try:
    import pyrfc3339
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
    if str == "true" or str == "True":
        return True
    else:
        return False


def format_iso_time_from_sec(time_in_sec):
    t = time.localtime(time_in_sec)
    return time.strftime("%Y-%m-%d %H:%M:%S", t)


def split_app_full_name(app_full_name):
    delim_name = app_full_name.find("_n")
    developer = app_full_name[:delim_name]
    delim_version = app_full_name.find("_v")
    app_name = app_full_name[delim_name+2:delim_version]
    version = app_full_name[delim_version + 2:]
    return developer, app_name, version


def compose_app_full_name(app_name,version):
    return "%s_v%s"%(app_name,version)


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
    print split_app_full_name("alivinco_nPullCordSirenApp_v1")