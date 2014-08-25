import datetime

__author__ = 'aleksandrsl'
import sqlite3
import time


class Timeseries():
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.is_enabled = True
        self.max_messages_per_device = 10000
        self.rows_to_delete_per_cleanup = 2000
        # doing rotation check after the number of inserts
        self.do_rotation_after = 1000
        self.insert_counter = 0

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
            if self.is_enabled:
                timestamp = int(time.time())

                if type(value) is float and precision:
                    value = round(value, precision)

                self.conn.execute("INSERT into timeseries(timestamp,dev_id,value) values(?,?,?)", (timestamp, dev_id, value))
                self.conn.commit()
                self.insert_counter += 1
                if self.insert_counter > self.do_rotation_after :
                    self.do_rotation()
                    self.insert_counter = 0
        except :
            print "error during timeseries insert"

    def delete_all_for_dev(self, dev_id):
        # c = self.conn.cursor()
        dev_id = str(dev_id)
        self.conn.execute("DELETE FROM timeseries WHERE dev_id = ?", (dev_id,))
        # self.conn.commit()

    def do_rotation(self):
        print "Doing rotation after "+str(self.insert_counter)+" inserts"
        # c = self.conn.cursor()
        count_result =  "select dev_id , count(dev_id) as count from timeseries group by dev_id "
        self.conn.execute(count_result)
        for item in c.fetchall():
           if item[1] > self.max_messages_per_device:
              print "Device with Id = "+str(item[0])+" needs to be cleaned. Doing cleanup"
              dev_id_to_clean = item[0]
              self.conn.execute("delete from timeseries where id in (select id from timeseries where dev_id = ? order by timestamp asc LIMIT ?);",(item[0],self.rows_to_delete_per_cleanup))
              self.conn.commit()


    def get(self, dev_id, start, end, result_type="dict"):
        c = self.conn.cursor()
        result = []
        if dev_id:
            c.execute(
                "select dev_id,timestamp,value from timeseries where dev_id = ? and timestamp > ? and timestamp < ? ",
                (dev_id, start, end))
        else:
            c.execute("select dev_id,timestamp,value from timeseries where  timestamp > ? and timestamp < ? ",
                      (start, end))
        result = []
        for item in c.fetchall():
            t_iso = datetime.datetime.fromtimestamp(item[1]).isoformat(" ")
            if result_type == "dict":
                result.append({"dev_id": item[0], "time": item[1], "time_iso": t_iso, "value": item[2]})
            elif result_type == "array":
                result.append([item[1]*1000, item[2]])
        c.close()
        return result


if __name__ == "__main__":
    t = Timeseries("timeseries.db")
    t.init_db()
    # t.insert(1,1.23442)
    #print t.get(1, 0, 1504836694)
    # t.delete_all_for_dev(1)
    t.do_rotation()
    t.cleanup()
