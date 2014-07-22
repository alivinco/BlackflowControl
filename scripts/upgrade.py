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

update_address_mapping()
#get_address_mapping_id()