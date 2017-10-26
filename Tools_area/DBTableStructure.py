

from Oracle_connection import Gsrdb_Conn




class DBTableStructure:
    def __init__(self,db_name='gsrdb',schem='gsrdba',table_name=''):
        print db_name,schem,table_name

        db=Gsrdb_Conn(schem,'oracle',db_name)

        table_cur=db.Sql("select column_name from user_tab_cols where table_name=\'"+table_name.upper()+"\'")
        self.column_list=[]
        for id in table_cur.fetchall():
            self.column_list.append(id[0])
        db.close()
        print 'this column list',self.column_list

