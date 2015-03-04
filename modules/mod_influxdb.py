import datetime
import json
import logging
import re

__author__ = 'aleksandrsl'
import sqlite3
import time
import threading


class InfluxDbTimeseries():
    def __init__(self, db_path):
        self.log = logging.getLogger("bf_timeseries")


    def enable(self, enable):
        # the method enables or disables
        self.is_enabled = enable

    def init_db(self):
        # check if tables exists , if not create one
       pass

    def cleanup(self):
        pass


    def insert(self, dev_id, value, precision=None):
        try:

            self.lock.acquire()
            if self.is_enabled:
                timestamp = int(time.time())

                if type(value) is float and precision:
                    value = round(value, precision)


        except Exception as ex:
            self.log.error("Timeseries can't be inserted because of error:")
            self.log.error(ex)
        finally:
            self.lock.release()

    def insert_msg_history(self, dev_id,msg_class,address, msg):
        try:
            msg = json.dumps(msg)
            self.lock.acquire()
            if self.is_enabled:
                timestamp = int(time.time())


        except Exception as ex:
            self.log.error("Msg history can't be inserted because of error:")
            self.log.error(ex)
        finally:
            self.lock.release()


    def delete_msg_history(self,del_type=None, row_id=None ,dev_id=None):

        if del_type:
            try:
                self.lock.acquire()
                if type(row_id) == int:
                    row_id = str(row_id)

                if type(row_id) == list:
                    pass
            except Exception as ex:
                self.log.error("Entries can't be deleted because of error")
                self.log.error(ex)
            finally:
                pass


    def do_rotation(self):
        pass


    def get(self, dev_id, start, end, result_type="dict" ):
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

    def get_timeline(self,address_mapping,filter_str,start,end,limit=2000,result_type="dict"):
        result = []
        return result

    def delete_all_for_dev(self, dev_id):
        try:
            pass
        except Exception as ex:
            self.log.error("Entries can't be deleted because of error")
            self.log.error(ex)

    def get_msg_history(self, dev_id=None, start=0, end=0, result_type="dict",rowid=None):
        pass




if __name__ == "__main__":
    import logging.config
    import configs.log
    logging.config.dictConfig(configs.log.config)
    t = Timeseries("timeseries.db")
    # t.conn.execute("VACUUM")
    # t.conn.commit()
    t.init_db()
    # t.insert(1,1.23442)
    from modules.msg_manager import MessageManager
    msg_man = MessageManager()

    print t.get_msg_history(rowid=4)
    #print t.get_timeline(msg_man.address_mapping,"/dev/zw/35/sen_temp/1/events", 0, 2504836694, 2000)
    # print t.conn.execute("select count (*) from timeseries ").fetchone()
    # import threading
    #
    # th = []
    # for i in range(1, 5):
    #     t1 = threading.Thread(target=t.get, args=(21, 0, 2504836694, "array"))
    #     t1.start()
    #     th.append(t1)
    #     print i
    #
    # print "waiting"
    # print t.get(21, 0, 2504836694, "array")
    # print "Done"


    # t.delete_all_for_dev(1)
    # t.do_rotation()
    #t.delete_all_for_dev([2,3])
    t.cleanup()
