__author__ = 'Administrator'

import cx_Oracle

class Gsrdb_Conn():
    def __init__(self,user='gsrdba',password='oracle',dsn='gsrdb'):
        self.db=cx_Oracle.connect(user=user,password='oracle',dsn=dsn)

    def Sql(self,sql):
        return self.db.cursor().execute(sql)

    def Write(self,sql):
        self.db.cursor().execute(sql)
        self.db.cursor().execute('commit')

    def Commit(self):
        self.db.cursor().execute('commit')

    def close(self):

        return self.db.close()


