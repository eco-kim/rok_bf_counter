import sqlite3
import pandas as pd

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('./database.db', isolation_level=None)
        c = self.conn.cursor()
        
        query = """create table if not exists user (
                id integer primary key,
                nickname text,
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
        query = f"""insert into user (nickname, location) 
            values ('{data['nickname']}',{data['location']});"""
        c.execute(query)

        query = f"select id from user where location={data['location']};"
        idx = c.execute(query).fetchone()
        c.close()
        return idx[0]

    def insert_rally(self, data):
        c = self.conn.cursor()
        query = f"""insert into timeline (user_id, bf_loc, timestamp) 
            values ({data['user_id']},{data['bf_loc']},{data['timestamp']})"""
        c.execute(query)
        c.close()

    def data_extract(self):
        query = """select c.nickname, count(c.id) as bf_count from
            (select a.id, b.nickname from timeline a
                left join user b
                on a.user_id = b.id) c
                group by c.nickname;"""
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def timeline_extract(self):
        query = """select b.nickname, a.timestamp, a.bf_loc from timeline a
            left join user b
            on a.user_id = b.id;"""
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def user_check(self, location):
        c = self.conn.cursor()
        query = f"select * from user where location={location};"
        temp = c.execute(query).fetchall()
        if len(temp)==0:
            return False
        else:
            return True
