# !/usr/bin/python
# -*- coding:utf8-*--

from Oracle_connection import Gsrdb_Conn
import datetime
import time
import os
import pandas as pd
from DBTableStructure import  DBTableStructure as dbt


class PBUDays:
    def __init__(self):
        db = Gsrdb_Conn()
        wellid_cur=db.Sql("select wellid from production_data where wellid LIKE 'SN%' or wellid='SUN003' group by wellid order by wellid")
        for wellid in wellid_cur.fetchall():
            print wellid[0]
            self.DailyReportCheck(wellid=wellid[0])


    def DailyReportCheck(self,wellid):

        db = Gsrdb_Conn()
        max_date_cur=db.Sql("select max(production_date) from production_data where wellid='"+wellid+"'")
        for id in max_date_cur.fetchall():
            max_date=id[0]

        data_extract_cur=db.Sql("select prod_comments,daily_prod_gas from production_data where "
                            "wellid='"+wellid+"' and production_date=to_date('"+str(max_date)+"','yyyy/mm/dd hh24:mi:ss')")

        for id in data_extract_cur.fetchall():
                prod_comments=id[0]
                prod_rate=id[1]
        if prod_comments is None:
            prod_comments='None'
        if 'open'.upper() in prod_comments.upper() and prod_rate>0:

            '''
                1.查找日报中井的备注中是否存在开井关键字，若该
                井同时存在于压恢关井名单中，则从名单中删除
            '''

            pbu_check_cur=db.Sql("select count(*) from pbu_plan where wellid='"+wellid+"'")
            for pbu in pbu_check_cur.fetchall():
                        if pbu[0]>0:
                            sql_string="delete from pbu_plan where wellid='"+wellid+"'"
                            try:
                                db.Write(sql_string)
                            except:
                                pass
                            db.close()
                            return
                        else:
                            db.close()
                            return
        elif prod_rate==0 and ('CLOSE' in prod_comments.upper() or 'SHUT' in prod_comments.upper()):

            '''
                2.若备注中标明无井口产量且关井，加入压恢名单并设
                置相应表单的值,若该井已在名单中，则删除原纪录后更新
            '''
            wg_cur=db.Sql("select groups from pbu_well_group where wellid='"+wellid+"'")
            for id in wg_cur.fetchall():
                well_group=id[0]


            pbu_check_cur = db.Sql("select count(*) from pbu_plan where wellid='" + wellid + "'")
            for pbu in pbu_check_cur.fetchall():
                    if pbu[0] > 0:
                        sql_string = "delete from pbu_plan where wellid='" + wellid + "'"
                        '''try:
                            db.Write(sql_string)
                        except:
                            pass'''
                        db.Write(sql_string)

                    self.PBUInsert(wellid,max_date,well_group)
                    db.close()
                    return

        elif prod_rate>0 and prod_rate<0.5:
                '''
                 查询是否有单井需要关井
                根据压恢策略表：若关井条件为产量为０
                criteria<0.5km3/d
                需要后续根据关井条件对该步骤进行调整

                '''
                max_date_string = "to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss')"
                detect_date=max_date+datetime.timedelta(days=1)
                detect_date_string = "to_date('" + str(detect_date) + "','yyyy/mm/dd hh24:mi:ss')"
                table_structure=dbt(db_name='gsrdb',schem= 'gsrdba', table_name='PBU_PLAN')
                col_string=''
                for col_id in table_structure.column_list:
                    col_string+=col_id+','

                sql_string="insert into pbu_plan("+col_string[:-1]+") values " \
                           "('"+wellid+"',"+max_date_string+","+detect_date_string+",null,null,null,null,null) "
                print sql_string
                try:
                    db.Write(sql_string)
                except:
                    pass
                #db.Write(sql_string)
                db.close()
                return

        elif prod_rate>0.5:
            '''
                若备注无特殊说明且日产量大于0.5km3/d，循环到
                日报中下一口井
                需要后续根据关井条件对该步骤进行调整
            '''

            return

    def PBUInsert(self,wellid,max_date,well_group):
        db = Gsrdb_Conn()
        pbu_duration_cur=db.Sql("select pbu_days from pbu_strategy where well_group="+str(well_group))
        for id in pbu_duration_cur.fetchall():
            pbu_duration=id[0]
        pbu_duration=0
        start_date=max_date+datetime.timedelta(days=1)

        end_date=start_date+datetime.timedelta(days=pbu_duration)
        max_date_string="to_date('"+str(max_date)+"','yyyy/mm/dd hh24:mi:ss')"
        start_date_string="to_date('"+str(start_date)+"','yyyy/mm/dd hh24:mi:ss')"
        end_date_string="to_date('"+str(end_date)+"','yyyy/mm/dd hh24:mi:ss')"

        table_structure = dbt(db_name='gsrdb', schem='gsrdba', table_name='PBU_PLAN')
        col_string = ''
        for col_id in table_structure.column_list:
            col_string += col_id + ','

        sql_string = "insert into pbu_plan(" +col_string[:-1] + ") values " \
                                                                "('"+wellid+"',"+max_date_string+",null,"+start_date_string+","+end_date_string+",0,"+str(well_group)+",null)"

        print sql_string
        '''try:
            db.Write(insert_string)
        except:
            pass'''
        db.Write(sql_string)
        db.close()

    def DailyRateCheck(self):
        '''

        :return:
        '''

if __name__=='__main__':
    test=PBUDays()