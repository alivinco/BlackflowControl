__author__ = 'alivinco'
import json
import argparse

def get_item(obj,next_el):
    if next_el in obj:
        get_item(obj[next_el])

def update_config(config_file,jpath,value):
    print "updating"+config_file
    jobj = json.load(file(conf_path))
    jp = jpath.split(".")
    next_obj = jobj
    ob = []
    ob.append(jobj)
    c = 1
    for item in jp :
        if item in ob[-1]:
            if c == len(jp) :
                print ob[-1][item]
                ob[-1][item] = value
                print ob[-1][item]
            else :
                ob.append(ob[-1].get(item))
        c +=1
    f = open(conf_path, "w")
    f.write(json.dumps(jobj, indent=True))
    f.close()
    print "Done."

# update_config()

if __name__ == "__main__":
    conf_path = "configs/global.json"

    parser = argparse.ArgumentParser()
    parser.add_argument("--file",help="path to config file")
    parser.add_argument("--jpath",help="json path . for example db.db_path")
    parser.add_argument("--value",help="value")
    args = parser.parse_args()
    update_config(args.file,args.jpath,args.value)
    print args.jpath