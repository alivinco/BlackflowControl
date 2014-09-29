import datetime
import logging

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
        self.conn.execute(timeseries_table)

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


    def delete_all_for_dev(self, dev_id):
        try:
            self.lock.acquire()
            if type(dev_id) == int:
                dev_id = str(dev_id)
                self.conn.execute("DELETE FROM timeseries WHERE dev_id = ?", (dev_id,))
                self.conn.commit()
            if type(dev_id) == list:
                if len(dev_id) == 1:
                    self.conn.execute("DELETE FROM timeseries WHERE dev_id = ?", (dev_id[0],))
                else:
                    dev_list = str(tuple(dev_id))
                    self.conn.execute("DELETE FROM timeseries WHERE dev_id in " + dev_list)
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


    def get(self, dev_id, start, end, result_type="dict", ):
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


if __name__ == "__main__":
    import logging.config
    import configs.log
    logging.config.dictConfig(configs.log.config)
    t = Timeseries("timeseries_seg_fault.db")
    # t.conn.execute("VACUUM")
    # t.conn.commit()
    t.init_db()
    # t.insert(1,1.23442)

    print t.conn.execute("select count (*) from timeseries ").fetchone()
    import threading

    th = []
    for i in range(1, 5):
        t1 = threading.Thread(target=t.get, args=(21, 0, 2504836694, "array"))
        t1.start()
        th.append(t1)
        print i

    print "waiting"
    print t.get(21, 0, 2504836694, "array")
    print "Done"
    # t.delete_all_for_dev(1)
    # t.do_rotation()
    #t.delete_all_for_dev([2,3])
    t.cleanup()
