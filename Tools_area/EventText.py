import wx
from Oracle_connection import Gsrdb_Conn



class EventText:
    def __init__(self,parent=None,wellid=None,tablename='well_event'):
        self.parent=parent
        self.wellid=wellid
        self.table_name=tablename
        print(self.wellid)
        self.DBQuery()


    def DBQuery(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cur=db.Sql("select note_date,events from well_event where wellid=\'"+self.wellid+"\' order by note_date desc")
        content_list=[]
        for id in cur.fetchall():
            content_list.append(str(id[0])+'\t')
            content_list.append(id[1]+'\n')
        content_text=''
        for id in content_list:
            content_text+=id
        db.close()
        return(content_text)


    def DBWrite(self,wellid=None,tablename=None,column=None,content=None):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        sql="insert into "+ tablename+" ("+column+") values ("+content+")"
        print(sql)
        db.Write(sql)
        db.close()



if __name__=='__main__':
    test=EventText(wellid='SN0055-01').DBQuery()
    print(test)