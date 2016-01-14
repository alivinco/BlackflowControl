import datetime
import json
import logging
import sys
sys.path.append("./../libs")
from influxdb import InfluxDBClient
import time
__author__ = 'aleksandrsl'

log = logging.getLogger("bf_influxdb")


class InfluxDbTimeseries():

    def __init__(self, host="localhost", port=8085 ,username="root", passwd="root" , db_name=None):
        self.db_client = None
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.db_name = db_name
        self.is_enabled = True

    def enable(self, enable):
        # the method enables or disables
        self.is_enabled = enable

    def init_db(self):
        self.db_client = InfluxDBClient(self.host,self.port, self.username,self.passwd ,self.db_name)
        db_list = self.db_client.get_list_database()
        print db_list
        if len(filter(lambda dbi: dbi["name"] == self.db_name,db_list)) == 0:
            log.info("Creating DB %s"%self.db_name)
            self.db_client.create_database(self.db_name)

    def cleanup(self):
        pass

    def insert(self,sid,address, dev_type, msg_type, serv_id , value, precision=None):
        """
        Insert timeseries data
        :param sid: software id / service point id . Id which identifies gateway or blackfly installation
        :param address: message topic
        :param dev_type: device type
        :param msg_type: full message type
        :param serv_id: service id , for instance in blackfly each service has it's own id
        :param value: value
        :param precision:
        """
        try:

            if self.is_enabled:
                # timestamp = int(time.time()*1000)
                dp = [
                        {
                            "measurement": "generic_ts",
                            "tags": {
                                "address": address,
                                "dev_type": dev_type,
                                "msg_type": msg_type,
                                "serv_id": serv_id,
                                "sid":sid
                            },
                            # "time": timestamp,
                            "fields": {
                                "value": value
                            }
                        }
                    ]

                self.db_client.write_points(dp,time_precision="ms")

        except Exception as ex:
            print ex
            log.error("Timeseries can't be inserted because of error:")
            log.error(ex)

    def get(self, dev_id, start, end, result_type="dict"):
        c = self.conn.cursor()

        result = []
        if dev_id:
            pass
        else:
            pass
        for item in iter:
            t_iso = datetime.datetime.fromtimestamp(item[1]).isoformat(" ")
            if result_type == "dict":
                result.append({"dev_id": item[0], "time": item[1], "time_iso": t_iso, "value": item[2]})
            elif result_type == "array":
                result.append([item[1] * 1000, item[2]])
        c.close()
        return result

    def get_timeline(self, address_mapping, filter_str, start, end, limit=2000, result_type="dict"):
        result = []
        return result

    def delete_all_for_dev(self, dev_id):
        try:
            pass
        except Exception as ex:
            self.log.error("Entries can't be deleted because of error")
            self.log.error(ex)


if __name__ == "__main__":
    import logging.config
    import configs.log

    logging.config.dictConfig(configs.log.config)
    t = InfluxDbTimeseries("192.168.99.100",8086,db_name="blackfly")
    t.init_db()
    print t.insert("t1,","/ta/zw/2/sen_temp/1/event","sen_temp","level.sensor","3",21.5)

