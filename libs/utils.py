import time

import datetime

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


def split_app_full_name(app_full_name):
    delim_name = app_full_name.find("_n")
    developer = app_full_name[:delim_name]
    delim_version = app_full_name.find("_v")
    app_name = app_full_name[delim_name+2:delim_version]
    version = app_full_name[delim_version + 2:]
    return developer, app_name, version


def compose_app_full_name(app_name,version):
    return "%s_v%s"%(app_name,version)

if __name__ == '__main__':
    print split_app_full_name("alivinco_nPullCordSirenApp_v1")