__author__ = 'aleksandrsl'
import sqlite3
import time

class Timeseries():

    def __init__(self,db_path):
        self.conn = sqlite3.connect(db_path,check_same_thread=False)
        self.cur = self.conn.cursor()

    def init_db(self):
        # check if tables exists , if not create one
        timeseries_table = "create table if not exists timeseries (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp integer , dev_id integer , value real )"
        self.cur.execute(timeseries_table)

    def cleanup(self):
        self.conn.close()

    def insert(self,dev_id,value):
        timestamp = int(time.time())
        self.cur.execute("INSERT into timeseries(timestamp,dev_id,value) values(?,?,?)",(timestamp,dev_id,value))
        self.conn.commit()

    def get(self,dev_id,start,end):
        c = self.conn.cursor()
        result = []
        if dev_id:
           c.execute("select dev_id,timestamp,value from timeseries where dev_id = ? and timestamp > ? and timestamp < ? ",(dev_id,start,end))
        else :
           c.execute("select dev_id,timestamp,value from timeseries where  timestamp > ? and timestamp < ? ",(start,end))
        return c.fetchall()



if __name__ == "__main__":
   t = Timeseries("timeseries.db")
   t.init_db()
   #t.insert(1,22.4)
   print t.get(5,1404736694,1404836694)
   t.cleanup()
