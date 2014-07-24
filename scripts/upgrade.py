import os , json
__author__ = 'aleksandrsl'


def update_address_mapping():
    app_root_path = os.getcwd()
    addr_path = os.path.join(app_root_path, "configs", "address_mapping.json")
    jobj = json.load(file(addr_path))
    counter = 1
    for item in jobj :
        if not("id" in item):
            item["id"] = counter
            counter += 1
            print "updated"


    f = open(addr_path, "w")
    f.write(json.dumps(jobj, indent=True))
    f.close()
    print "saved"

def get_address_mapping_id():
    app_root_path = os.getcwd()
    addr_path = os.path.join(app_root_path, "configs", "address_mapping.json")
    jobj = json.load(file(addr_path))

    r = sorted(jobj,key = lambda item:item["id"])[-1]["id"]

    print r

def update_global_config():
    print "updating global.json"
    app_root_path = os.getcwd()
    addr_path = os.path.join(app_root_path, "configs", "global.json")
    jobj = json.load(file(addr_path))
    if not "db" in jobj:
        jobj["db"]={"timeseries_enabled": True,"db_path": "/tmp/timeseries.db"}
        print "global.json updated"
    else :
        print "global.json is already up to date"
    jobj["system"]["version"]="1.2"
    f = open(addr_path, "w")
    f.write(json.dumps(jobj, indent=True))
    f.close()
update_address_mapping()
update_global_config()
#get_address_mapping_id()