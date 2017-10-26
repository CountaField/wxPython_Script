# !/usr/bin/python
# -*- coding:utf8-*-
import string
from Oracle_connection import Gsrdb_Conn
import datetime
import time
import os
from multiprocessing import Process,Manager
import threading
import argparse
import sys
from AlarmPorcedure import AlarmProcedure
from DBTableStructure import  DBTableStructure as dbt
from collections import OrderedDict
import numpy as np
class InstDataInsert:
    def __init__(self,wellid=None,db_flag='gsrdb',well_list=[],):
        #print ("the pid is: ", os.getpid())
        start = time.clock()
        data=self.RawDataExtract()
        self.DataPrepare(data)
        end=time.clock()
        print "Program Lunching time is %f seconds" % (end - start)




    def RawDataExtract(self):

        db_raw = Gsrdb_Conn()
        data_list = []
        max_local_date_cur = db_raw.Sql('select max(production_date) from raw_inst_data_keep_2day ')

        for id in max_local_date_cur.fetchall():
            local_max_date = id[0]

        raw_db_extract_cur = db_raw.Sql("select * from  vw_raw_daily_inst_wh_pres_1min  where "
                                        "production_date>to_date('" + str(
            local_max_date) + "','yyyy/mm/dd hh24:mi:ss')")

        for id in raw_db_extract_cur.fetchall():
            data_list.append(id)

        db_raw.close()
        return data_list

    def DataPrepare(self,data_list):
        db=Gsrdb_Conn()
        for line in data_list:
            insert_string=''
            for id in line:
                if id is None:
                    insert_string+='null,'
                else:

                    if isinstance(id,datetime.datetime):
                        insert_string+="to_date('"+str(id)+"','yyyy/mm/dd hh24:mi:ss'),"
                    elif isinstance(id,str):
                        insert_string+="'"+id+"',"
                    else:
                        insert_string += "" + str(id) + ","
            try:
                insert_sql_string="insert into raw_inst_data_keep_2day( wellid,production_date,wh_pressure,casing_pressure,pipeline_temperature,pipeline_pres_diff,instant_production_gas,pipeline_abs_pressure) VALUES ("+insert_string[:-1]+")"
                db.Write(insert_sql_string)
            except:
                wellid=insert_string.split(',')[0]
                prod_date=insert_string.split(',')[1]+",'yyyy/mm/dd hh24:mi:ss')"
                error_string=wellid+','+prod_date
                error_report_string="insert into aux_inst_data_error(wellid,production_date) values("+error_string+")"
                print error_report_string
                db.Write(error_report_string)

        db.close()

    def STWellChange(self):
        db=Gsrdb_Conn()
        st_cur=db.Sql("select wellid from well_header where wellid like '%ST' order by wellid")
        for id in st_cur.fetchall():
            update_string="update raw_inst_data_keep_2day set wellid='"+id[0]+"' where wellid='"+id[0][:-2]+"'"
            db.Write(update_string)
        db.close()








class Inst5minDataInsert:
    def __init__(self,wellid,well_list=[]):
        #print ("the pid is: ", os.getpid())
        start = time.clock()
        #print wellid,'start processing'
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        #max_date_cur= db.Sql('select max(production_date) from vw_raw_daily_inst_wh_pres_1min where '
         #                     'wellid=\'' + wellid + '\' ')
        max_local_date_cur= db.Sql('select max(production_date) from raw_inst_data_keep_2day where '
                              'wellid=\'' + wellid + '\' ')
        max_5min_date_cur = db.Sql('select max(production_date) from aux_5min_data_keep_15day where '
                                    'wellid=\'' + wellid + '\' ')

        for id in max_local_date_cur.fetchall():
                local_max_date=id[0]

        for id in max_5min_date_cur.fetchall():
                cur_time=id[0]
        if cur_time is not None:
            while cur_time<=local_max_date:
                    next_time=cur_time+datetime.timedelta(minutes=5)
                    error_range_time=next_time+datetime.timedelta(minutes=1)
                    insert_sql_string = "insert into aux_5min_data_keep_15day select * " \
                                        "from raw_inst_data_keep_2day where " \
                                        "wellid='" + wellid + "' and production_date between " \
                                                              "to_date('" + str(next_time) + "','yyyy/mm/dd,hh24:mi:ss') and " \
                                                                                             "to_date('"+str(error_range_time) + "','yyyy/mm/dd,hh24:mi:ss')"
                    db.Write(insert_sql_string)
                    cur_time = next_time
        else:
            min_local_date_cur=db.Sql("select min(production_date) from raw_inst_data_keep_2day where wellid='" + wellid + "'")
            for id in min_local_date_cur.fetchall():
                cur_time=id[0]
            while cur_time <= local_max_date:
                try:
                    next_time = cur_time + datetime.timedelta(minutes=5)
                except:
                    print wellid,'no production date extract from database'
                error_range_time = next_time + datetime.timedelta(minutes=1)
                insert_sql_string = "insert into aux_5min_data_keep_15day select * " \
                                    "from raw_inst_data_keep_2day where " \
                                    "wellid='" + wellid + "' and production_date between " \
                                                          "to_date('" + str(
                    next_time) + "','yyyy/mm/dd,hh24:mi:ss') and " \
                                 "to_date('" + str(error_range_time) + "','yyyy/mm/dd,hh24:mi:ss')"
                db.Write(insert_sql_string)
                cur_time = next_time


        db.Commit()
        db.close()
        end = time.clock()
        print wellid,"Program Lunching time is %f seconds" % (end - start)




class InstDataDelete:
    def __init__(self,wellid=None,wellid_list=[]):
        print ("the pid is: ", os.getpid())
        start = time.clock()
        print wellid, 'start processing'
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        max_date_cur=db.Sql("select max(production_date)  from aux_5min_data_keep_15day")


        for id in max_date_cur.fetchall():
            max_date=id[0]

        cur_time=max_date
        next_time=cur_time-datetime.timedelta(days=2)
        delete_sql_string="delete from raw_inst_data_keep_2day where production_date < to_date('" + str(next_time) + "','yyyy/mm/dd,hh24:mi:ss')  "
        print delete_sql_string
        db.Write(delete_sql_string)
        db.close()

class BKtoDB:
    def __init__(self, wellid, target_db_name='gsrdb', source_db_name='gsrbk'):
        target_db = Gsrdb_Conn('gsrdba', 'oracle', target_db_name)
        source_db = Gsrdb_Conn('gsrdba', 'oracle', source_db_name)
        target_table = "raw_inst_data_keep_2day"
        self.target_data_dict = OrderedDict()
        target_max_date_cur = target_db.Sql(
            "select max(production_date) from " + target_table + "  where wellid='" + wellid + "'")
        for id in target_max_date_cur.fetchall():
            target_max_date = id[0]

        target_structure = dbt(db_name=target_db_name, schem='gsrdba', table_name=target_table)

        if target_max_date is not None:
            source_data_cur = source_db.Sql("select * from " + target_table + " where wellid='"+wellid+"' and production_date>to_date('" + str(
                target_max_date) + "','yyyy/mm/dd hh24:mi:ss') order by production_date")
        else:
            source_data_cur = source_db.Sql(
                "select * from " + target_table + " where wellid='" + wellid + "' ")

        column_string=''
        for col_id in target_structure.column_list:
            self.target_data_dict[col_id] = []
            column_string+=col_id+','
        print self.target_data_dict.keys()
        i=0
        for id in source_data_cur.fetchall():
            value_string=''
            for i in range(len(self.target_data_dict.keys())):
                if i==0:
                    value_string += "'"+str(id[i])+"',"
                elif i==1:
                    value_string += "to_date('"+str(id[i])+"','yyyy/mm/dd hh24:mi:ss')" + ','
                # self.target_data_dict[self.target_data_dict.keys()[i]].append(id[i])
                else:
                    if id[i] is None:
                        value_string += "Null" + ','
                    else:
                        value_string+=str(id[i])+','

            insert_string="insert into "+target_table+"("+column_string[:-1]+") values ("+value_string[:-1] + ")"
            print insert_string
            target_db.Write(insert_string)

        target_db.close()
        source_db.close()




class  NewProgress:
    def __init__(self,flag,db_flag='gsrdb'):
        start = time.clock()
        self.process_dict={}
        self.wellidInitial()
        if flag=='delete':
            self.CreateThread(self.process_dict,flag='delete')
        if flag=='insert':
            insert=InstDataInsert()
        if flag=='insert_5min':
            self.CreateThread(self.process_dict, flag='insert_5min')
        if flag=='2hour_alarm' :
            self.CreateThread(self.process_dict, flag='2hour_alarm')
        if flag=='bk_to_db' :
            #self.CreateThread(self.process_dict, flag='bk_to_db')
            pass
        end = time.clock()
        print "Program Lunching time is %f seconds" % (end - start)
        print flag+" "+str(time.localtime().tm_year)+"/"+str(time.localtime().tm_mon)+"/"+\
              str(time.localtime().tm_mday)+" "+str(time.localtime().tm_hour)+":"+str(time.localtime().tm_min)

    def CreateThread(self,process_dict,flag,db_flag=None):
        process_list=[]
        for id in process_dict.keys():
            process=Process(target=self.ThreadInitial,args=(process_dict[id],flag,db_flag))
            process_list.append(process)
        for id in process_list:
            #id.daemon=True
            id.start()

    def ThreadInitial(self,wellid_list,flag,db_flag=None):
        threads=[]
        del_well_list=wellid_list[:]

        if flag=='insert':
            for wellid in wellid_list:
                new_thread=threading.Thread(target=InstDataInsert,args=(wellid,db_flag))
                new_thread.start()
                new_thread.join()

        if flag=='delete':
            '''for wellid in wellid_list:
                new_thread=threading.Thread(target=InstDataDelete,args=(wellid,))
                new_thread.start()
                new_thread.join()'''
            InstDataDelete()

        if flag == 'insert_5min':
            for wellid in wellid_list:
                new_thread = threading.Thread(target=Inst5minDataInsert, args=(wellid,))
                new_thread.start()
                new_thread.join()

        if flag == '2hour_alarm':
            for wellid in wellid_list:
                new_thread = threading.Thread(target=AlarmProcedure, args=(wellid,))
                new_thread.start()
                new_thread.join()

        if flag == 'bk_to_db':
            for wellid in wellid_list:
                new_thread = threading.Thread(target=BKtoDB, args=(wellid,))
                new_thread.start()
                new_thread.join()

    def wellidInitial(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        #wellid_cur = db.Sql("select wellid from well_header where connected_to_prod='YES' and (wellid like 'SN%' or wellid='SUN003') order by wellid")

        wellid_cur = db.Sql("select wellid from allocation_dhc where dhc_type='VS' group by wellid order by wellid")

        i=1
        for id in wellid_cur.fetchall():
            if i not in self.process_dict.keys():
                self.process_dict[i]=[]
            self.process_dict[i].append(id[0])
            if len(self.process_dict[i])==6:
                i+=1
        print self.process_dict
        db.close()


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Data Insert Processing')
    parser.add_argument('--flag', action="store", dest="flag", type=str, required=True)
    parser.add_argument('--db_flag', action="store", dest="db_flag", type=str, required=False)
    given_args = parser.parse_args()
    print(given_args)
    flag = given_args.flag
    db_flag=given_args.db_flag
    test=NewProgress(flag,db_flag)

