__author__ = 'alivinco'
import json
def update_config():
    conf_path = "/media/app/BlackflyTestSuite/configs/global.json"
    print "updating"+conf_path
    jobj = json.load(file(conf_path))
    jobj["db"]["db_path"] = "/tmp/timeseries.db"
    f = open(conf_path, "w")
    f.write(json.dumps(jobj, indent=True))
    f.close()
    print "Done."

update_config()