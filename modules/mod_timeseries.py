import datetime
import json
import logging
import re

__author__ = 'aleksandrsl'
import sqlite3
import time
import threading


class Timeseries():
    def __init__(self, db_path):
        self.log = logging.getLogger("bf_timeseries")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.log.info("Connected to timeseries database "+str(db_path))
        self.is_enabled = True
        self.max_messages_per_device = 10000
        self.rows_to_delete_per_cleanup = 2000
        # doing rotation check after the number of inserts
        self.do_rotation_after = 1000
        self.insert_counter = 0
        # sqlight es not good in sharing connections , therefore is better to use lock and do single file operation at once
        self.lock = threading.Lock()

    def enable(self, enable):
        # the method enables or disables
        self.is_enabled = enable

    def init_db(self):
        # check if tables exists , if not create one
        timeseries_table = "create table if not exists timeseries (timestamp integer , dev_id integer , value real )"
        msg_history_table = "create table if not exists msg_history (timestamp integer , dev_id,msg_class text,address text , msg blob )"
        self.conn.execute(timeseries_table)
        self.conn.execute(msg_history_table)

    def cleanup(self):
        self.conn.close()


    def insert(self, dev_id, value, precision=None):
        try:

            self.lock.acquire()
            if self.is_enabled:
                timestamp = int(time.time())

                if type(value) is float and precision:
                    value = round(value, precision)

                self.conn.execute("INSERT into timeseries(timestamp,dev_id,value) values(?,?,?)",
                                  (timestamp, dev_id, value))
                self.conn.commit()
                self.insert_counter += 1
                if self.insert_counter > self.do_rotation_after:
                    self.do_rotation()
                    self.insert_counter = 0
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

                self.conn.execute("INSERT into msg_history(timestamp,dev_id,msg_class,address,msg) values(?,?,?,?,?)",
                                  (timestamp, dev_id, msg_class , address , msg))
                self.conn.commit()
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
                    self.conn.execute("DELETE FROM msg_history WHERE rowid = ?", (row_id,))
                    self.conn.commit()
                if type(row_id) == list:
                    if len(row_id) == 1:
                        self.conn.execute("DELETE FROM msg_history WHERE rowid = ?", (row_id[0],))
                    else:
                        dev_list = str(tuple(row_id))
                        self.conn.execute("DELETE FROM msg_history WHERE rowid in " + dev_list)
                    self.conn.commit()
            except Exception as ex:
                self.log.error("Entries can't be deleted because of error")
                self.log.error(ex)
            finally:
                self.lock.release()


    def do_rotation(self):
        """
        The method performs database analysis and if number of datapoints for certain device is bigger then
        max_messages_per_device then everything that exceeds max_messages_per_device is deleted .

        """
        self.log.info("Performing db rotation after " + str(self.insert_counter) + " inserts")
        c = self.conn.cursor()
        count_result = "select dev_id , count(dev_id) as count from timeseries group by dev_id "
        c.execute(count_result)
        for item in c.fetchall():
            if item[1] > self.max_messages_per_device:
                self.log.debug("Device with Id = " + str(item[0]) + " needs to be cleaned. Doing cleanup")
                dev_id_to_clean = item[0]
                self.conn.execute(
                    "delete from timeseries where rowid in (select rowid from timeseries where dev_id = ? order by timestamp asc LIMIT ?);",
                    (dev_id_to_clean, self.rows_to_delete_per_cleanup))
                self.conn.commit()


    def get(self, dev_id, start, end, result_type="dict" ):
        self.lock.acquire()
        c = self.conn.cursor()

        result = []
        if dev_id:
            iter = c.execute(
                "select dev_id,timestamp,value from timeseries where dev_id = ? and timestamp > ? and timestamp < ? ",
                (dev_id, start, end))
        else:
            iter = c.execute("select dev_id,timestamp,value from timeseries where  timestamp > ? and timestamp < ? ",
                             (start, end))
        result = []
        for item in iter:
            t_iso = datetime.datetime.fromtimestamp(item[1]).isoformat(" ")
            if result_type == "dict":
                result.append({"dev_id": item[0], "time": item[1], "time_iso": t_iso, "value": item[2]})
            elif result_type == "array":
                result.append([item[1] * 1000, item[2]])
        c.close()
        self.lock.release()
        return result

    def get_timeline(self,address_mapping,filter_str,start,end,limit=2000,result_type="dict"):
        result = []
        if filter_str :
            p = re.compile(filter_str,re.IGNORECASE)
            mapping = filter(lambda item: (p.search(item["address"])),address_mapping)
        else :
            mapping = address_mapping
        addr_id_list = []
        for item in mapping : addr_id_list.append(str(item["id"]))

        sql = "select dev_id,timestamp,value from timeseries where dev_id in ({seq}) and timestamp > ? and timestamp < ? order by timestamp desc LIMIT ?".format(seq=','.join(addr_id_list))
        self.log.debug("Query sql = "+sql)

        self.lock.acquire()
        c = self.conn.cursor()
        c.execute(sql,(start,end,limit))
        fetch_result = c.fetchall()
        c.close()
        self.lock.release()

        for item in fetch_result:
            t_iso = datetime.datetime.fromtimestamp(item[1]).isoformat(" ")

            if result_type == "dict":
                map = filter(lambda m: (item[0]==m["id"]),mapping)[0]
                result.append({"dev_id": item[0], "time": item[1], "time_iso": t_iso, "value": item[2],"name":map["name"],"address":map["address"]})

        return result

    def get_msg_history(self, dev_id=None, start=0, end=0, result_type="dict",rowid=None):
        self.lock.acquire()
        c = self.conn.cursor()

        if rowid :
            iter = c.execute(
                "select dev_id,timestamp,msg_class,address,msg ,rowid from msg_history where rowid=? order by timestamp desc ",
                (rowid,))
        elif dev_id:
            iter = c.execute(
                "select dev_id,timestamp,msg_class,address,msg ,rowid from msg_history where dev_id = ? and timestamp > ? and timestamp < ? order by timestamp desc",
                (dev_id, start, end))
        else:
            iter = c.execute("select dev_id,timestamp,msg_class,address,msg,rowid from msg_history where  timestamp > ? and timestamp < ? order by timestamp desc",
                             (start, end))

        result = []
        for item in iter:
            t_iso = datetime.datetime.fromtimestamp(item[1]).isoformat(" ")
            try:
                msg = json.loads(item[4])
                msg = json.dumps(msg,indent=True)
            except :
                msg = item[4]
            if result_type == "dict":
                result.append({ "dev_id": item[0], "time": item[1], "time_iso": t_iso, "msg_class": item[2],"address": item[3],"msg": msg,"id":item[5]})
            elif result_type == "array":
                result.append([item[1] * 1000, msg])
        c.close()
        self.lock.release()
        return result




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
