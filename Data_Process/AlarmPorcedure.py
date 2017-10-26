# !/usr/bin/python
# -*- coding:utf8-*-
import string
from Oracle_connection import Gsrdb_Conn
import datetime
import time
import os
import pandas as pd


class AlarmProcedure:
    def __init__(self,wellid):
        print ("the pid is: ", os.getpid())
        print wellid
        start = time.clock()

        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        max_date_cur = db.Sql('select max(production_date) from raw_inst_data_keep_2day where '
                              'wellid=\'' + wellid + '\' ')

        prod_cur=db.Sql("select count(*) from production_data where wellid='"+wellid+"'")

        for id in prod_cur.fetchall():
            if id[0]!=0:
                open_cur=db.Sql("select count(*) from aux_prod_shut_wells where wellid='"+wellid+"'")
                for x in open_cur.fetchall():
                    if x[0]!=0:
                        return

        for id in max_date_cur.fetchall():
            print type(id[0])
            max_date=id[0]


        self.max_date=max_date
        print max_date
        print "If Delta WHT>20% then record error message"

        '''
        井口温度和井口压力检测
        '''
        if self.WHT10minDelta(wellid,max_date): # If Delta WHT>20% then record error message

            insert_value=wellid+",to_date('"+str(max_date)+"','yyyy/mm/dd hh24:mi:ss'),'Unstable WHT'"
            print insert_value
            sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value+")"
            try:
                db.Write(sql)
            except:
                pass

        else: #I f Delta WHT<20% then go to next step
            print "If Delta WHT<20% then go to next step"
            if self.WHTMin(wellid,max_date): #
                print "If Min WHT<-19 then record error message and go to next step"
                insert_value = "'"+wellid+"'" + ",to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Low Flow Line Temperature','WHT: "+str(self.min_pip_temp)+"'"
                print insert_value
                sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"
                try:
                    db.Write(sql)
                except:
                    pass
            else: # If Min WHT>-19 then record error message then go to next step directly
                print "If Min WHT>-19 then then go to next step directly"
                whpcheck,min_whp,max_whp=self.WHPCompare(wellid,max_date)
                if whpcheck:
                    print 'if Min WHP<20 or MAX WHP>50 then record error message'
                    insert_value = "'"+wellid+"'" + ",to_date('" + str(
                        max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Flowline Pressure Anomaly','min_whp: "+str(min_whp)+"\n max_whp: "+str(max_whp)+"'"
                    print insert_value
                    sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"

                    try:
                        db.Write(sql)
                    except:
                        pass
                    '''
                    孔板检测
                    '''
                else:# if (Min WHP<20 or MAX WHP>50) is False then go to next step
                    print "if (Min WHP < 20 or MAX WHP > 50) is False then go to next step"
                    if self.OrificeRnage(wellid)==1:

                        insert_value = "'"+wellid+"'" + ",to_date('" + str(
                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Orifice need to change','min orifice record: "+str(round(self.minrate_non_0,2))+" km3/d'"
                        print insert_value
                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"

                        try:
                            db.Write(sql)
                        except:
                            pass
                    elif self.OrificeRnage(wellid)==2:
                        insert_value = "'"+wellid+"'" + ",to_date('" + str(
                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'The well is closing'"
                        print insert_value
                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                        db.Write(sql)
                    elif self.OrificeRnage(wellid)==3:
                        insert_value = "'"+wellid+"'" + ",to_date('" + str(
                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Liquid Loading'"
                        print insert_value
                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                        try:
                            db.Write(sql)
                        except:
                            pass
                    elif self.OrificeRnage(wellid)==4:
                        insert_value = "'"+wellid+"'" + ",to_date('" + str(
                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'lack of casing pressure'"
                        print insert_value
                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                        try:
                            db.Write(sql)
                        except:
                            pass

                    elif self.OrificeRnage(wellid) == 5:
                        insert_value = "'" + wellid + "'" + ",to_date('" + str(
                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'no production-suspected Orifice problem'','CP_Now: "+str(self.orific_cp_now)+"\n avgP_2nd Hour: "+str(self.avgP_2nd_hour)+" km3/d'"
                        print insert_value
                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"

                        try:
                            db.Write(sql)
                        except:
                            pass
                    elif self.OrificeRnage(wellid) == 6:
                        insert_value = "'" + wellid + "'" + ",to_date('" + str(
                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'no production'"
                        print insert_value
                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                        try:
                            db.Write(sql)
                        except:
                            pass

                    else:
                        '''
                        产量条件检测

                        '''

                        '''Go To Next Step 2'''
                        print "1 STEP FINISHED........"
                        print " STEP 2 STARTING........"
                        if self.DeltaQgCompare(wellid,max_date)==1:

                            insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Liquid Loading','Qg Now: "+str(round(self.delta_qg_now,2))+" km3/d'"
                            print insert_value
                            sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"

                            try:
                                db.Write(sql)
                            except:
                                pass
                        elif self.DeltaQgCompare(wellid,max_date)==2:
                            insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Hydrate or Well Closed'"
                            print insert_value
                            sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                            try:
                                db.Write(sql)
                            except:
                                pass
                        elif self.DeltaQgCompare(wellid,max_date)==3:
                            insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Unexpected rate increase(DHC Failure?)'','delta max qg: "+str(self.delta_max_qg)+" km3/d'"
                            print insert_value
                            sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"
                            try:
                                db.Write(sql)
                            except:
                                pass
                        elif self.DeltaQgCompare(wellid,max_date)==4:
                            insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Opening the Well'"
                            print insert_value
                            sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"
                            try:
                                db.Write(sql)
                            except:
                                pass
                        else:
                            '''Go To Next Step 3'''
                            '''

                            环空压力检测

                            '''
                            print "2 STEP FINISHED........"
                            print " STEP 3 STARTING........"
                            remote_cp_check=self.RemoteTransDetect(wellid,max_date)
                            if remote_cp_check is True:
                                cp10mincheck,cp_now=self.CP10minCompare(wellid,max_date)
                                if cp10mincheck:  # if CP<20 bara or CP>250 bara then record error message

                                    print "if CP<20 bara or CP>250 bara then record error message"
                                    insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                        max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Casing Pressure Out of Range','cp_now: "+str(cp_now)+' bara'
                                    print insert_value
                                    sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message,type_value) values (" + insert_value + ")"
                                    try:
                                        db.Write(sql)
                                    except:
                                        pass
                                else:  # if CP in the range then go to next step orifice plate check

                                    if self. DeltaCP10minDelta(wellid,max_date)==1:
                                        insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                            max_date) + "','yyyy/mm/dd hh24:mi:ss')," \
                                                        "'Non expected pressure turbulence','Min CP: "+str(self.delta_min_cp)+"\n Max CP: "+str(self.delta_max_cp)+"'"
                                        print insert_value
                                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                                        try:
                                            db.Write(sql)
                                        except:
                                            pass
                                    elif self. DeltaCP10minDelta(wellid,max_date)==2:
                                        insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                            max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Suspension of data transmission'"
                                        print insert_value
                                        sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                                        try:
                                            db.Write(sql)
                                        except:
                                            pass
                                    else:
                                        if self.CPContinue(wellid,max_date)==1:
                                            insert_value = "'"+wellid+"'" + ",to_date('" + str(
                                                max_date) + "','yyyy/mm/dd hh24:mi:ss'),'Wireline Connection'"
                                            print insert_value
                                            sql = "insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"

                                            try:
                                                db.Write(sql)
                                            except:
                                                pass
                                        else:
                                            print 'this well is working well'


        self.DataDeleteDetected(wellid)


        db.close()
        end = time.clock()
        print "Program Lunching time is %f seconds" % (end - start)

    '''-------------------------------STEP 1------------------------------------------------------------'''
    '''STEP1.1 10分钟内温度变化小于20%'''
    def WHT10minDelta(self, wellid, max_time):
        start = time.clock()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        min_time = max_time - datetime.timedelta(hours=2)
        inter_time = max_time

        while inter_time >= min_time:

            pre_time = inter_time - datetime.timedelta(minutes=10)
            print inter_time, pre_time;

            now_sql_string = "select avg(pipeline_temperature) from raw_inst_data_keep_2day where " \
                             "wellid='" + wellid + "' and production_date between to_date('" + str(
                pre_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                            "to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')"

            now_cur = db.Sql("select avg(pipeline_temperature) from raw_inst_data_keep_2day where "
                             "wellid='" + wellid + "' and production_date between "
                                                   "to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(
                inter_time) + "','yyyy/mm/dd hh24:mi:ss')")
            inter_time = pre_time
            pre_time = inter_time - datetime.timedelta(minutes=10)
            print inter_time, pre_time
            pre_cur = db.Sql("select avg(pipeline_temperature) from raw_inst_data_keep_2day where "
                             "wellid='" + wellid + "' and production_date between "
                                                   "to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(
                inter_time) + "','yyyy/mm/dd hh24:mi:ss')")
            pre_sql_string = "select avg(pipeline_temperature) from raw_inst_data_keep_2day where " \
                             "wellid='" + wellid + "' and production_date between to_date('" + str(
                pre_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                            "to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')"

            print 'now', now_sql_string
            print 'pre', pre_sql_string
            for id in now_cur.fetchall():
                wht_now = id[0]
            for id in pre_cur.fetchall():
                wht_pre = id[0]
            print wht_now, wht_pre
            delta_wht = (wht_now - wht_pre) / wht_now

            if delta_wht > 0.2:
                db.close()
                return True

        db.close()
        end = time.clock()
        print " WHT10minDelta Lunching time is %f seconds" % (end - start)

    '''STEP1.2 管线温度小于零下19度'''

    def WHTMin(self,wellid,max_date):
        start = time.clock()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        delta_time=0.0833333333
        sql_string="select min(pipeline_temperature) from raw_inst_data_keep_2day where" \
                   " wellid='"+wellid+"' and " \
                                      "production_date >to_date('"+str(max_date)+"','yyyy/mm/dd hh24:mi:ss')-"+str(delta_time)
        print sql_string
        data_initial_cur=db.Sql(sql_string)
        #cp_zero_count_cur=db.Sql("select count(*) from  raw_inst_data_keep_2day where "
        #                       " wellid='"+wellid+" ' and production_date >to_date('"+str(max_date)+"','yyyy/mm/dd hh24:mi:ss')-"+str(delta_time)+" and "
                                                                                                                                                  #"casing_pressure=0")

        for id in data_initial_cur.fetchall():
            min_pip_temp=id[0]
        #for id in cp_zero_count_cur.fetchall():
            #cp_zero_count=id[0]

        db.close()
        end = time.clock()
        print " WHTMin Lunching time is %f seconds" % (end - start)
        if min_pip_temp<-19:
            self.min_pip_temp=min_pip_temp
            return True
        else:
            return False

    '''STEP1.3 井口压力小于20bara或大于50bara'''

    def WHPCompare(self, wellid, max_date):
        start = time.clock()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        delta_time = 0.0833333333
        sql_string="select min(wh_pressure)*10,max(wh_pressure)*10 from raw_inst_data_keep_2day where " \
                   "wellid='" + wellid + "' and" \
                                         " production_date >to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss')-" + str(delta_time)
        print sql_string
        data_initial_cur = db.Sql(sql_string)

        for id in data_initial_cur.fetchall():
            min_whp = id[0]
            max_whp = id[1]

        db.close()
        end = time.clock()
        print " WHPCompare Lunching time is %f seconds" % (end - start)
        print 'min_whp',min_whp,'max_whp',max_whp
        if min_whp < 20 or max_whp > 50:
                return True,min_whp,max_whp
        else:
            return False,False,False

    def OrificeRnage(self,well):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        '''read data from DB'''
        now_t = time.localtime()
        max_time_cur=db.Sql("select max(production_date) from raw_inst_data_keep_2day where wellid='"+well+"'")
        for id in max_time_cur.fetchall():
            max_time=id[0]

        twohoursAgo = (max_time - datetime.timedelta(hours=2))
        onehourAgo=(max_time - datetime.timedelta(hours=1))
        time_interval_start = twohoursAgo.strftime("%Y-%m-%d %H:%M:%S")
        print str(onehourAgo),str(twohoursAgo)
        extrac_data_cur = db.Sql(
            "select PRODUCTION_DATE,INSTANT_PRODUCTION_GAS from RAW_INST_DATA_keep_2day where "
            "WELLID ='" + well + "' and PRODUCTION_DATE between to_date('" + time_interval_start + "','yyyy-mm-dd hh24:mi:ss') and "
                                                                                                   "to_date('" + str(max_time) + "','yyyy-mm-dd hh24:mi:ss') order by production_date")
        cp_now_cur=db.Sql("select casing_pressure from RAW_INST_DATA_keep_2day where "
            "WELLID ='" + well + "' and PRODUCTION_DATE=to_date('" +str(max_time)+ "','yyyy-mm-dd hh24:mi:ss') ")
        cp_pre_cur = db.Sql("select casing_pressure from RAW_INST_DATA_keep_2day where "
                            "WELLID ='" + well + "' and PRODUCTION_DATE =to_date('" + time_interval_start+ "','yyyy-mm-dd hh24:mi:ss') ")

        avgp_2end_hour_cur=db.Sql("select casing_pressure from RAW_INST_DATA_keep_2day where "
            "WELLID ='" + well + "' and PRODUCTION_DATE between to_date('" +str(onehourAgo)+ "','yyyy-mm-dd hh24:mi:ss') and to_date('" +str(max_time)+ "','yyyy-mm-dd hh24:mi:ss')")

        avgp_1st_hour_cur = db.Sql("select casing_pressure from RAW_INST_DATA_keep_2day where "
                                   "WELLID ='" + well + "' and PRODUCTION_DATE between to_date('" + str(
            twohoursAgo) + "','yyyy-mm-dd hh24:mi:ss') and to_date('" + str(onehourAgo) + "','yyyy-mm-dd hh24:mi:ss')")

        for id in avgp_2end_hour_cur.fetchall():
            avgP_2nd_hour=id[0]
        for id in avgp_1st_hour_cur.fetchall():
            avgp_1st_hour=id[0]

        for id in cp_now_cur.fetchall():
            cp_now=id[0]

        for id in cp_pre_cur.fetchall():
            cp_pre=id[0]

        proddate_list = []
        prodrate_list = []

        for id in extrac_data_cur.fetchall():
            proddate_list.append(id[0])
            prodrate_list.append(id[1])
        db.close()

        '''find if there is range pb'''

        well_frame = pd.DataFrame([proddate_list, prodrate_list], index=['DATE', 'RATE']).transpose()  # 读取最近两个小时的数据
        minrate = well_frame.RATE.min()  # '''find min value during the two hours'''
        maxrate = well_frame.RATE.max()

        if minrate == 0:
            # rank according to the rate
            well_frame = well_frame.sort_values('RATE')
            well_frame_non_0 = well_frame[well_frame.RATE > 0]  # 产量不为0的数据集
            well_frame_0 = well_frame[well_frame.RATE == 0]  # 产量为0的数据集

            # get minrate except 0
            minrate_non_0 = well_frame_non_0.RATE.min()
            mindate_0 = well_frame_0.DATE.min()  # earliest rate=0
            maxdate_non_0 = well_frame_non_0.DATE.max()  # latest rate non 0
            if minrate_non_0 > 300:
                if mindate_0 < maxdate_non_0:
                    print well, 'Orifice to be changed'
                    self.minrate_non_0=minrate_non_0*24/1000
                    return 1  # 非0最小值大于300且最后一个不为0的时间大于第一个为0的时间（产量为0），则需要更换孔板

                elif avgP_2nd_hour-avgp_1st_hour > 0.05:  # 单位兆帕，Mpa，截断值待查，检查产量为0后是否出现环空压力升高现象,若环空压力升高，表示正在关井，若环空压力保持稳定，提示孔板计量失真
                    print well, 'the well is closing'
                    return 2  # 非0最小值大于300且最后一个不为0的时间小于第一个为0的时间，且环空压力升高，正在关井

                elif avgP_2nd_hour==0 and avgp_1st_hour == 0:  # 环空压力持续为0或者空值，提示环空压力值缺失
                    print "lack of casing pressure"
                    return 4
                else:
                    self.minrate_non_0 = minrate_non_0 * 24 / 1000
                    print well, 'Orifice to be changed'
                    return 1,minrate_non_0*24/1000  # 产量为0后持续为0，但环空压力不升高，提示孔板未正常记录生产气量
            elif maxrate > 0:

                print well, 'Liquid Loading'
                return 3  # 非0最小值小于300，产能较弱，需要关井压恢

            elif maxrate == 0 and avgP_2nd_hour-avgp_1st_hour < 0.05 and avgP_2nd_hour < 5 and avgP_2nd_hour > 0:
                print well, 'no production-suspected Orifice problem'
                self.orific_cp_now=cp_now
                self.avgP_2nd_hour=avgP_2nd_hour

                return 5

            else:
                print well, 'no production'
                return 6
        else:
            print well, 'Orifice is OK'
            return False  # 正常


    '''-----------------------STEP 2------------------------------------------------------------'''
    '''STEP2.1 产量'''
    def DeltaQgCompare(self,wellid,max_time):
        start = time.clock()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        min_time = max_time - datetime.timedelta(hours=2)
        inter_time = max_time
        while inter_time >= min_time:
            pre_time = inter_time - datetime.timedelta(minutes=10)

            now_sql_string = "select avg(instant_production_gas) from raw_inst_data_keep_2day where " \
                             "wellid='" + wellid + "' and production_date between to_date('" + str(
                pre_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                            "to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')"

            now_cur = db.Sql("select avg(instant_production_gas) from raw_inst_data_keep_2day where "
                             "wellid='" + wellid + "' and production_date between "
                                                   "to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(
                inter_time) + "','yyyy/mm/dd hh24:mi:ss')")
            inter_time = pre_time
            pre_time = inter_time - datetime.timedelta(minutes=10)
            print inter_time, pre_time
            pre_cur = db.Sql("select avg(instant_production_gas) from raw_inst_data_keep_2day where "
                             "wellid='" + wellid + "' and production_date between "
                                                   "to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')")

            pre_sql_string = "select avg(instant_production_gas) from raw_inst_data_keep_2day where wellid='" + wellid + "' and production_date between to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')"


            max_qg_cur=db.Sql("select max(instant_production_gas) from raw_inst_data_keep_2day where wellid='" + wellid + "' and production_date between to_date('" + str(min_time) + "','yyyy/mm/dd hh24:mi:ss') and to_date('" + str(max_time) + "','yyyy/mm/dd hh24:mi:ss')")

            for id in max_qg_cur.fetchall():
                self.delta_max_qg=id[0]



            print 'now', now_sql_string
            print 'pre', pre_sql_string
            for id in now_cur.fetchall():
                Qg_now = id[0]
            for id in pre_cur.fetchall():
                Qg_pre = id[0]
            print Qg_now, Qg_pre
            delta_Qg = (Qg_now - Qg_pre) / Qg_now



            if delta_Qg<-0.1 and Qg_now!=0 and Qg_now<300:
                '''1.气量骤降不为0 - --》 积液'''
                self.delta_qg_now=Qg_now*24/1000
                db.close()
                end = time.clock()
                print " QG Lunching time is %f seconds" % (end - start)
                return 1

            elif delta_Qg<-0.1 and Qg_now==0:
                '''2.气量骤降为0---》水合物或关井'''
                db.close()
                end = time.clock()
                print " QG Lunching time is %f seconds" % (end - start)
                return 2

            elif delta_Qg>0.1 and Qg_pre!=0 and Qg_now>2000:
                '''3.气量突然升高且此前不为0---》节流器实效待查'''
                db.close()
                end = time.clock()
                print "QG Lunching time is %f seconds" % (end - start)
                return 3
            elif delta_Qg>0.1 and Qg_pre==0:
                '''4.气量突然升高且此前为0---》开井'''
                db.close()
                end = time.clock()
                print " QG time is %f seconds" % (end - start)
                return 4

            else:
                db.close()
                end = time.clock()
                print " QG time is %f seconds" % (end - start)
                return 5

    '''-----------------------STEP 3------------------------------------------------------------'''


    '''STEP3.1 环空压力在20到250bara之间，现场传输单位为Mpa,所以要乘以10'''

    def CP10minCompare(self,wellid,max_time):
        start = time.clock()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        min_time = max_time - datetime.timedelta(hours=2)
        inter_time = max_time
        while inter_time>=min_time:
            pre_time=inter_time-datetime.timedelta(minutes=10)
            sql_string="select avg(casing_pressure)*10 from raw_inst_data_keep_2day where " \
                       "wellid='"+wellid+"' and production_date between to_date('"+str(pre_time)+"','yyyy/mm/dd hh24:mi:ss') and " \
                                                                                                 "to_date('"+str(inter_time)+"','yyyy/mm/dd hh24:mi:ss')"
            print sql_string
            now_cur=db.Sql(sql_string)
            inter_time=pre_time

            for id in now_cur.fetchall():
                if id[0] is None:
                    return False
                else:
                    cp_now=id[0]
            print "cp_now",cp_now
            if cp_now<20 or cp_now>250:
                db.close()
                return True,cp_now
            else:
                return False,False
        db.close()
        end = time.clock()
        print " WHPCompare Lunching time is %f seconds" % (end - start)


    '''STEP 3.2 前后两次压差变化在正负10%以内，且不为常数--》环空异常波动        '''

    def DeltaCP10minDelta(self,wellid,max_time):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        min_time = max_time - datetime.timedelta(hours=2)
        inter_time = max_time
        max_min_sql_string="select max(casing_pressure),min(casing_pressure) from raw_inst_data_keep_2day where " \
                           "wellid='" + wellid + "' and production_date between to_date('" + str(min_time) + "','yyyy/mm/dd hh24:mi:ss') " \
                                                                                                            "and to_date('" + str(max_time) + "','yyyy/mm/dd hh24:mi:ss')"
        print 'this is max_min_sql_string',max_min_sql_string

        max_min_cp_cur = db.Sql(max_min_sql_string)
        for id in max_min_cp_cur.fetchall():
            max_cp=id[0]
            min_cp=id[1]

        while inter_time >= min_time:

            pre_time = inter_time - datetime.timedelta(minutes=10)
            print inter_time, pre_time

            now_sql_string = "select avg(casing_pressure) from raw_inst_data_keep_2day where " \
                             "wellid='" + wellid + "' and production_date between to_date('" + str(
                pre_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                            "to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')"

            now_cur = db.Sql("select avg(casing_pressure) from raw_inst_data_keep_2day where "
                             "wellid='" + wellid + "' and production_date between "
                                                   "to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(
                inter_time) + "','yyyy/mm/dd hh24:mi:ss')")
            inter_time = pre_time
            pre_time = inter_time - datetime.timedelta(minutes=10)
            print inter_time, pre_time
            pre_cur = db.Sql("select avg(casing_pressure) from raw_inst_data_keep_2day where "
                             "wellid='" + wellid + "' and production_date between "
                                                   "to_date('" + str(pre_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(
                inter_time) + "','yyyy/mm/dd hh24:mi:ss')")

            pre_sql_string = "select avg(casing_pressure) from raw_inst_data_keep_2day where " \
                             "wellid='" + wellid + "' and production_date between to_date('" + str(
                pre_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                            "to_date('" + str(inter_time) + "','yyyy/mm/dd hh24:mi:ss')"

            print 'now', now_sql_string
            print 'pre', pre_sql_string
            for id in now_cur.fetchall():
                cp_now = id[0]
            for id in pre_cur.fetchall():
                cp_pre = id[0]
            print cp_now, cp_pre
            delta_cp = abs((cp_now - cp_pre) / cp_pre)

            if delta_cp<0.1:
                db.close()
                return False
            elif max_cp==min_cp:
                db.close()
                return 2
            else:
                db.close()
                self.delta_min_cp=min_cp
                self.delta_max_cp=max_cp
                return 1

    '''STEP 3.3 计量数据时断时续---》 线路解除不良'''
    def CPContinue(self,wellid,max_time):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        min_time = max_time - datetime.timedelta(hours=2)
        min_cp_cur=db.Sql("select min(casing_pressure) from raw_inst_data_keep_2day where "
                          "wellid='"+wellid+"' and production_date between to_date('" + str(min_time) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                 "to_date('" + str(max_time) + "','yyyy/mm/dd hh24:mi:ss')")

        sec_min_cp_string="select min(casing_pressure) from raw_inst_data_keep_2day where" \
                          " wellid='"+wellid+"' and production_date between to_date('" + str(min_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                                                                                                         "to_date('" + str(max_time) + "','yyyy/mm/dd hh24:mi:ss') and casing_pressure>0"

        cp_count_string="select min(casing_pressure) from raw_inst_data_keep_2day where " \
                        "wellid='"+wellid+"' and production_date between to_date('" + str(min_time) + "','yyyy/mm/dd hh24:mi:ss') and " \
                                                                                                      "to_date('" + str(max_time) + "','yyyy/mm/dd hh24:mi:ss') and casing_pressure=0"

        for id in min_cp_cur.fetchall():
            if id[0] is not None and id[0]==0:
                min_cp=id[0]
                sec_min_cp_cur=db.Sql(sec_min_cp_string)
                cp_zero_count_cur=db.Sql(cp_count_string)

                for id in cp_zero_count_cur.fetchall():
                    cp_zero_count=id[0]
                    if cp_zero_count>3:
                        for id in sec_min_cp_cur.fetchall():
                            sec_min_cp = id[0]
                            if sec_min_cp!=0:
                                db.close()
                                return 1
                            else:
                                db.close()
                                return False
                    else:
                        db.close()
                        return False

            else:
                db.close()
                return False

    '''STEP 4 远传数据检查'''
    def RemoteTransDetect(self,wellid,max_time):
        '''
         若即时产量及环空压力都为空
         No instant data transmission
         Insert into the alarm summary table
         '''

        print 'start remote transfer detected.....'
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        min_time = max_time - datetime.timedelta(hours=2)
        max_min_sql_string = "select count(*) from raw_inst_data_keep_2day where " \
                             "wellid='" + wellid + "' and (production_date between to_date('" + str(
            min_time) + "','yyyy/mm/dd hh24:mi:ss') " \
                        "and to_date('" + str(max_time) + "','yyyy/mm/dd hh24:mi:ss')) and casing_pressure is null"
        print max_min_sql_string
        data_cur=db.Sql(max_min_sql_string)
        for id in data_cur.fetchall():
            if id[0]>12:
                print wellid,'no instant data transmission'
                insert_value=wellid+",to_date('"+str(max_time)+"','yyyy/mm/dd hh24:mi:ss'),'No Instant Casing Pressure transmission'"
                sql="insert into alarm_2hour_report_table (wellid,production_date,alarm_message) values (" + insert_value + ")"
                try:
                    db.Write(sql)
                except:
                    pass
                return False
            else:
                data_cur=db.Sql("select count(*) from alarm_2hour_report_table where wellid='"+wellid+"' and alarm_message='No Instant data transmission'")
                for id in data_cur.fetchall():
                    if id[0]>0:
                        sql="delete from alarm_2hour_report_table where wellid='"+wellid+"' and alarm_message='No Instant data transmission'"
                        check_sql="insert into aux_alarm_error(wellid,detected_date,alarm_message,duration) values " \
                                  "('"+wellid+"',to_date('"+str(max_time)+"','yyyy/mm/dd hh24:mi:ss'),'No Instant data transmission',333)"
                        try:
                            db.Write(sql)
                            db.Write(check_sql)
                        except:
                            pass
                return True
        db.close()


    '''STEP 5 数据删除检测'''

    def DataDeleteDetected(self,wellid):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        max_time = str(datetime.datetime.now()).split('.')[0]
        '''
           If alarm massage='
           well to be shut-in'&"open" exist in daily report
           Delete in daily alarm report

        max_time=str(datetime.datetime.now()).split('.')[0]
        data_cur = db.Sql(
            "select  detected_date from alarm_summary_table where wellid='" + wellid + "' and alarm_message like '%shut-in%'")
        for id in data_cur.fetchall():
            if id[0] is not None:
                daily_report_cur=db.Sql("select count(*) from production_data where "
                                        "lower(prod_comments) like '%open%' and wellid='"+wellid+"'and "
                                                                                                 "production_date>to_date('" + str(id[0]) + "','yyyy/mm/dd hh24:mi:ss') ")
                for rid in daily_report_cur.fetchall():
                    if rid[0]>0:
                        sql_string="delete from alarm_summary_table where wellid='"+wellid+"' and alarm_message like '%shut%in%'"
                        sql_check="insert into aux_alarm_error(wellid,detected_date,alarm_message,duration) values " \
                                  "('"+wellid+"',to_date('"+max_time+"','yyyy/mm/dd hh24:mi:ss'),'Well Opened',444)"
                        db.Write(sql_string)
                        db.Write(sql_check)
                        try:
                            db.Write(sql_string)
                            db.Write(sql_check)
                        except:
                            pass'''


        '''
        If alarm massage='
        Orifice need to change
        '&"Orifice" exist in daily report

        Delete in daily alarm report

        '''
        data_cur = db.Sql(
            "select  detected_date from alarm_summary_table where wellid='" + wellid + "' and lower(alarm_message) like '%orifice%need%change%'")
        for id in data_cur.fetchall():
            if id[0] is not None:
                daily_report_cur = db.Sql("select count(*) from production_data where "
                                          "lower(prod_comments) like '%orifice%' and wellid='" + wellid + "'and "
                                                                                                       "production_date>to_date('" + str(id[0]) + "','yyyy/mm/dd hh24:mi:ss') ")
                for rid in daily_report_cur.fetchall():
                    if rid[0]>0:
                        sql_string="delete from alarm_summary_table where wellid='"+wellid+"' and lower(alarm_message) like '%orifice%change%'"
                        sql_check = "insert into aux_alarm_error(wellid,detected_date,alarm_message,duration) values " \
                                    "('"+wellid+"',to_date('" + max_time + "','yyyy/mm/dd hh24:mi:ss'),'orifice changed',666)"
                        db.Write(sql_string)
                        db.Write(sql_check)
                        '''try:
                            db.Write(sql_string)
                            db.Write(sql_check)
                        except:
                            pass'''
        '''
        If alarm massage='
        lack of casing pressure
        '& "instant casing pressure'>0

        Delete in daily alarm report
        '''
        data_cur = db.Sql(
            "select  detected_date from alarm_summary_table where "
            "wellid='" + wellid + "' and lower(alarm_message) like '%lack%casing%'")

        for id in data_cur.fetchall():
            if id[0] is not None:
                daily_report_cur = db.Sql("select count(*) from raw_inst_data_keep_2day where "
                                          "production_date>to_date('" + str(id[0]) + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                     "casing_pressure>0")
                for rid in daily_report_cur.fetchall():
                    if rid[0]>0:
                        sql_string="delete from alarm_summary_table where wellid='"+wellid+"' and lower(alarm_message) like '%lack%casing%'"
                        sql_check = "insert into aux_alarm_error(wellid,detected_date,alarm_message,duration) values " \
                                    "('"+wellid+"',to_date('" + max_time + "','yyyy/mm/dd hh24:mi:ss'),'lack casing pressure solved',555)"

                        db.Write(sql_string)
                        db.Write(sql_check)
                        '''try:
                            db.Write(sql_string)
                            db.Write(sql_check)
                        except:
                            pass'''


        db.close()


if __name__=='__main__':

    test=AlarmProcedure('SN0112-05')




