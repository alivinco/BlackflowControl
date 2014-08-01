import datetime

__author__ = 'aleksandrsl'
import sqlite3
import time

class Timeseries():

    def __init__(self,db_path):
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.cur = self.conn.cursor()
        self.is_enabled = True

    def enable(self,enable):
        # the method enables or disables
        self.is_enabled = enable

    def init_db(self):
        # check if tables exists , if not create one
        timeseries_table = "create table if not exists timeseries (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp integer , dev_id integer , value real )"
        self.cur.execute(timeseries_table)

    def cleanup(self):
        self.conn.close()

    def insert(self,dev_id,value,precision=None):
        if self.is_enabled:
            timestamp = int(time.time())

            if type(value)is float and precision:
               value = round(value,precision)

            self.cur.execute("INSERT into timeseries(timestamp,dev_id,value) values(?,?,?)",(timestamp,dev_id,value))
            self.conn.commit()

    def get(self,dev_id,start,end):
        c = self.conn.cursor()
        result = []
        if dev_id:
           c.execute("select id,dev_id,timestamp,value from timeseries where dev_id = ? and timestamp > ? and timestamp < ? ",(dev_id,start,end))
        else :
           c.execute("select id,dev_id,timestamp,value from timeseries where  timestamp > ? and timestamp < ? ",(start,end))
        result = []
        for item in c.fetchall():
           t_iso =  datetime.datetime.fromtimestamp(item[2]).isoformat(" ")
           result.append({"id":item[0],"dev_id":item[1],"time":item[2],"time_iso":t_iso,"value":item[3]})
        return result



if __name__ == "__main__":
   t = Timeseries("timeseries.db")
   t.init_db()
   t.insert(1,1.23442)
   print t.get(1,0,1504836694)
   t.cleanup()
