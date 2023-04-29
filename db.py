import sqlite3
import pandas as pd
from datetime import timedelta

class Database:
    def __init__(self, db_path):
        db_path += '/database.db'
        self.conn = sqlite3.connect(db_path, isolation_level=None)
        c = self.conn.cursor()
        
        query = """create table if not exists user (
                id integer primary key,
                nickname text,
                alliance text,
                location integer);"""
        c.execute(query)

        query = """create table if not exists timeline (
                id integer primary key,
                user_id integer,
                bf_loc integer,
                timestamp integer);"""
        c.execute(query)
        c.close()

    def insert_user(self, data):
        c = self.conn.cursor()
        query = f"""insert into user (nickname, alliance, location) 
            values ('{data['nickname']}','{data['alliance']}',{data['location']});"""
        c.execute(query)

        query = f"select id from user where location={data['location']};"
        idx = c.execute(query).fetchone()
        c.close()
        return idx[0]

    def insert_rally(self, data):
        c = self.conn.cursor()
        query = f"""insert into timeline (user_id, bf_loc, timestamp) 
            values ({data['user_id']},{data['bf_loc']}, {data['timestamp']})"""
        c.execute(query)
        c.close()

    def data_extract(self):
        query = """select c.nickname, max(c.alliance) as alliance, count(c.id) as bf_count from
            (select a.id, b.nickname, b.alliance from timeline a
                left join user b
                on a.user_id = b.id) c
                group by c.nickname
                order by bf_count desc;"""
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def timeline_extract(self):
        query = """select b.nickname, b.alliance, a.timestamp, a.bf_loc from timeline a
            left join user b
            on a.user_id = b.id;"""
        df = pd.read_sql_query(query, self.conn)
        df['datetime'] = pd.to_datetime(df['timestamp'],unit='s')
        df = df.drop('timestamp', axis=1)
        df['datetime'] = pd.DatetimeIndex(df['datetime']) + timedelta(hours=9)
        return df
    
    def user_check(self, location):
        c = self.conn.cursor()
        query = f"select * from user where location={location};"
        temp = c.execute(query).fetchall()
        if len(temp)==0:
            return False
        else:
            return True
