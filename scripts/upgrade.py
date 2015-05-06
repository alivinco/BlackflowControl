import os , json
import sqlite3

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
        if not("record_history" in item):
            item["record_history"]=False


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
        # jobj["db"]["db_path"] = "/tmp/timeseries.db"
        print "global.json is already up to date"
    if not ("use_default_class_lookup" in jobj):
        jobj["use_default_class_lookup"]=True
    if "system" in jobj:
        jobj["system"]["version"]="1.4.8"
        jobj["mqtt"]["enable_sys"]=False
        jobj["system"]["http_server_port"]=5000
        jobj["system"]["distro_server_uri"]="http://lego.fiicha.net/blackfly"
        jobj["system"]["ui_security_disabled"]=False


    else :
        print "******************* YOUR EXISTING BLACKFLY INSTALLATION IS TOO OLD.PLEASE DELETE EXISTING INSTALLATION AND RUN INSTALLATION AGAIN ******************"

    if not "smartly" in jobj:
        jobj["smartly"]={"sdc_uri":"https://prov-stg.service.smartly.no"}

    f = open(addr_path, "w")
    f.write(json.dumps(jobj, indent=True))
    f.close()

def update_cmd_class_mapping ():
    print "updating msg_class_mapping.json"
    app_root_path = os.getcwd()
    addr_path = os.path.join(app_root_path, "configs", "msg_class_mapping.json")
    jobj = json.load(file(addr_path))
    for item in jobj :
        if item["msg_class"]=="config.set":
           item["ui_mapping"]["properties_are_key_value"] = True
           print "config.set command definition updated"
    f = open(addr_path, "w")
    f.write(json.dumps(jobj, indent=True))
    f.close()

def update_db():
    app_root_path = os.getcwd()
    addr_path = os.path.join(app_root_path, "configs", "global.json")
    jobj = json.load(file(addr_path))
    db_path = jobj["db"]["db_path"]
    conn =  sqlite3.connect(db_path)
    # check if script needs to run upda
    cur = conn.cursor()
    need_for_update = False
    try :
        cur.execute("select id from timeseries limit 1")
        need_for_update = True
        print "DB teble will be updated "
    except:
        print "DB is up to date"
    cur.close()

    if need_for_update:
        update_timeseries_sql = "CREATE TEMPORARY TABLE timeseries_backup(timestamp integer , dev_id integer , value real );" \
                      "INSERT INTO timeseries_backup SELECT timestamp,dev_id,value FROM timeseries;" \
                      "DROP TABLE timeseries;" \
                      "create table timeseries (timestamp integer , dev_id integer , value real );" \
                      "INSERT INTO timeseries SELECT timestamp,dev_id,value FROM timeseries_backup;" \
                      "DROP TABLE timeseries_backup;"
        conn.executescript(update_timeseries_sql)
        conn.close()
        print "timeseries table updated"

update_address_mapping()
update_global_config()
update_cmd_class_mapping()
update_db()



#get_address_mapping_id()

'''
To add

 {
  "ui_mapping": {
   "ui_element": "msg_class_ui",
   "num_type": "int",
   "properties_are_key_value":true,
   "override_properties": false
  },
  "msg_type": "command",
  "msg_class": "config.set"
 }

'''