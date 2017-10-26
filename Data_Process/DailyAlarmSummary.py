
from Oracle_connection import Gsrdb_Conn
import datetime
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import time



class DailyAlarmSummary:
    def __init__(self):
        start = time.clock()
        db=Gsrdb_Conn()
        wellid_cur=db.Sql("select wellid from alarm_2hour_report_table where wellid like 'SN%' or wellid like 'SUN003' group by wellid order by wellid ")
        prod_date_cur=db.Sql("select max(production_date) from productioN_data")

        for id in prod_date_cur.fetchall():
            prod_date=id[0]

        local_date=datetime.datetime.now()

        for id in wellid_cur.fetchall():
            wellid=id[0]
            #self.OldDailyAlarmCheck(wellid, prod_date)
            if local_date>prod_date:
                alarm_report = self.InstPivotTable(wellid,local_date)
                self.SummaryAlarmDelete(wellid, local_date)
                print alarm_report
            else:
                alarm_report = self.InstPivotTable(wellid, prod_date)

            if alarm_report is not False:
                self.AlarmReportCheck(alarm_report)
            else:
                print wellid,'no alarm report'

            self.OldDailyAlarmCheck(wellid,prod_date)
            self.TypeValueInsert(wellid)
        db.close()
        end = time.clock()
        print "Program Lunching time is %f seconds" % (end - start)

    def InstPivotTable(self,wellid,prod_date):
        alarm_report_dict={}
        alarm_list=[]
        prv_date=prod_date-datetime.timedelta(days=1)

        sql_string = "select wellid,alarm_message from alarm_2hour_report_table where " \
                     "production_date between to_date('"+str(prv_date).split('.')[0]+"','yyyy/mm/dd hh24:mi:ss') and " \
                                                                   "to_date('"+str(prod_date).split('.')[0]+"','yyyy/mm/dd hh24:mi:ss')" \
                     " order by production_date"
        engine = create_engine('oracle+cx_oracle://gsrdba:oracle@gsrdb')
        df = pd.read_sql(sql=sql_string, con=engine)
        # print df

        table = pd.pivot_table(df, index=['wellid'], values=['alarm_message'], columns=['alarm_message'],
                               aggfunc={'alarm_message': np.count_nonzero}, fill_value=0)

        try:
            t1 = table.loc[wellid, "alarm_message"]
            for id in t1.values:
                if id > 0:
                    alist=list(t1.values)
                    index = alist.index(id)
                    alarm_report_dict[wellid]=(t1.axes[0][index],id)
            return alarm_report_dict # key is wellid,(1.name of alarm,2.report times)
        except:
            return False

    def AlarmReportCheck(self,alarm_report=None):
        local_date=str(datetime.datetime.now()).split('.')[0]
        db=Gsrdb_Conn()
        alarm_table_cur=db.Sql("select * from alarm_summary_table order by wellid")
        alarm_adict={}
        alarm_message_list=[]
        report_times=[]

        for id in alarm_table_cur.fetchall():

            if id[0] not in alarm_adict.keys():
                alarm_adict[id[0]] = {}
                alarm_adict[id[0]][id[2]]={}
                alarm_adict[id[0]][id[2]]=(id[1],id[3],id[4])
            else:
                alarm_adict[id[0]][id[2]] = {}
                alarm_adict[id[0]][id[2]] = (id[1], id[3], id[4])

            # id[0].Wellid; id[2] alarm name
            # id[1].Detected date,id[3].Alarm Report Times,id[4].Duration


        for id in alarm_report.keys():
            if id not in alarm_adict.keys():
                a_m, a_t = alarm_report[id]#1.name of alarm,2.report times
                value_string="'"+id + "'," +"to_date('"+local_date+"','yyyy/mm/dd hh24:mi:ss'),'" + str(a_m) + "'," +str(a_t)+',1'
                sql_string="insert into alarm_summary_table(wellid,detected_date,alarm_message,alarm_reported_times,duration) values ("+value_string+")"
                try:
                    db.Write(sql_string)
                except:
                    value_string = "'" + id + "'," + "to_date('" + local_date + "','yyyy/mm/dd hh24:mi:ss'),'" + str(
                        a_m) + "'," + str(a_t) + ',1'
                    sql_string = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + value_string + ")"
                    db.Write(sql_string)
            else:

                if alarm_report[id][0] in alarm_adict[id].keys():
                    alarm_type=alarm_report[id][0]
                    db_report_times=alarm_adict[id][alarm_type][1]
                    sum_reprot_times=alarm_report[id][1]+db_report_times
                    db_date=alarm_adict[id][alarm_type][0]
                    duration=(datetime.datetime.now()-db_date).days
                    print duration
                    rp_times_update_string="update alarm_summary_table set alarm_reported_times="+str(sum_reprot_times)+" where wellid='"+id+"' and alarm_message='"+alarm_type+"'"
                    duration_update_string="update alarm_summary_table set duration="+str(duration)+" where wellid='"+id+"' and alarm_message='"+alarm_type+"'"
                    db.Write(rp_times_update_string)
                    db.Write(duration_update_string)
                else:

                    a_m, a_t = alarm_report[id]
                    value_string = "'" + id + "'," + "to_date('" + local_date + "','yyyy/mm/dd hh24:mi:ss'),'" + str(
                        a_m) + "'," + str(a_t) + ',1'
                    sql_string = "insert into alarm_summary_table(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + value_string + ")"
                    try:
                        db.Write(sql_string)
                    except:
                        value_string = "'" + id + "'," + "to_date('" + local_date + "','yyyy/mm/dd hh24:mi:ss'),'" + str(
                            a_m) + "'," + str(a_t) + ',999'
                        sql_string = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + value_string + ")"
                        db.Write(sql_string)

        db.close()

    def TypeValueInsert(self,wellid):
        db = Gsrdb_Conn()
        pre_date = str(datetime.datetime.now() - datetime.timedelta(days=1)).split('.')[0]

        daily_alarm_check_cur = db.Sql("select alarm_message from alarm_summary_table where "
                                       "wellid='" + wellid + "' ")

        for id_m in daily_alarm_check_cur.fetchall():
            data_filter_list = []
            sql_string = "select type_value from alarm_2hour_report_table where" \
                         " alarm_message='" + id_m[
                             0] + "' and wellid='" + wellid + "'  and type_value is not null and production_date>to_date('" + pre_date + "','yyyy/mm/dd hh24:mi:ss') " \
                                                                                                                                         "order by  type_value"
            min_string=''
            unit_string=' '
            hour_alarm_cur = db.Sql(sql_string)
            for id in hour_alarm_cur.fetchall():
                if id[0] is not None:
                    data_filter_list.append(float(id[0].split(': ')[1].split(' ')[0]))
                    min_string=str(id[0].split(': ')[0])
                    if str(id[0].split(': ')[1].split(' ')[1])!='max_whp':
                        unit_string=str(id[0].split(': ')[1].split(' ')[1])
                    else:
                        unit_string=str(id[0].split('\n')[1])

            print id_m[0],data_filter_list
            if data_filter_list!=[]:
                insert_value = min_string + ": " + str(min(data_filter_list))+unit_string
                update_string = "update alarm_summary_table set type_value='" + insert_value + "' where wellid='" + wellid + "' and alarm_message='" + \
                                id_m[0] + "'"
                db.Write(update_string)

        db.close()

    def OldDailyAlarmCheck(self,wellid,prod_date):
        db=Gsrdb_Conn()
        print wellid
        max_date_cur=db.Sql("select max(production_date) from production_data")
        for id in max_date_cur.fetchall():
            max_date=id[0]

        prv_date = max_date - datetime.timedelta(days=1)
        data_cur=db.Sql("select * from prod_alarm_report_table where "
                        "wellid='"+wellid+"' and production_date >"
                                          "to_date('"+str(prv_date).split('.')[0]+"','yyyy/mm/dd hh24:mi:ss') ")
        for id in data_cur.fetchall():
            #try:
                if id[2]=='Data Anomalies':
                    a_m='Data Anomalies'
                    a_t=1
                    #type_value= daily_prod_gas+casing_pressure (daily)
                    values_string= "'" + wellid + "'," + "to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss'),'" + str(a_m) + "'," + str(a_t) + ',1'
                    insert_string="insert into alarm_summary_table(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                    print insert_string
                    try:
                        db.Write(insert_string)
                    except:

                        insert_string = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                        print 'insert error',insert_string
                        db.Write(insert_string)

                if id[2]=='Liquid Loading':
                    a_m='Liquid Loading'
                    a_t=1
                    values_string = "'" + wellid + "'," + "to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss'),'" + str(a_m) + "'," + str(a_t) + ',1'
                    insert_string = "insert into alarm_summary_table(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                    try:
                        print insert_string
                        db.Write(insert_string)

                    except:

                       insert_string = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                       print 'insert error', insert_string
                       db.Write(insert_string)

                if id[2]=='Casing Pressure Anomalies':
                    a_m = 'Casing Pressure Anomalies'
                    a_t = 1
                    values_string = "'" + wellid + "'," + "to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss'),'" + str(a_m) + "'," + str(a_t) + ',1'
                    insert_string = "insert into alarm_summary_table(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                    try:
                        print insert_string
                        db.Write(insert_string)
                    except:
                        insert_string = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                        print 'insert error', insert_string
                        db.Write(insert_string)

                if id[2] == 'Casing Pressure Out of Range':
                    a_m = 'Casing Pressure Out of Range'
                    a_t = 1
                    values_string = "'" + wellid + "'," + "to_date('" + str(max_date) + "','yyyy/mm/dd hh24:mi:ss'),'" + str(a_m) + "'," + str(a_t) + ',1'
                    insert_string = "insert into alarm_summary_table(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                    try:
                        print insert_string
                        db.Write(insert_string)
                    except:
                       insert_string = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values (" + values_string + ")"
                       print 'insert error', insert_string
                       db.Write(insert_string)


            #except:
             #   print "error deteceted~!"
        print "Daily alarm detected finished!"

    def SummaryAlarmDelete(self,wellid,max_date):
        db = Gsrdb_Conn()
        alarm_tuple=("Unexpected rate increase(DHC Failure?)","Casing Pressure Out of Range","Liquid Loading","Flowline Pressure Anomaly",
                     "Low Flow Line Temperature","Non expected pressure turbulence",'no production-suspected Orifice problem', 'no production')

        min_date = max_date - datetime.timedelta(days=1)
        data_cur=db.Sql("select alarm_message from alarm_2hour_report_table where "
                        "wellid='"+wellid+"' and production_date between to_date('"+str(min_date).split('.')[0]+"','yyyy/mm/dd hh24:mi:ss') and "
                                                                                                  " to_date('"+str(max_date).split('.')[0]+"','yyyy/mm/dd hh24:mi:ss')")
        alarm_list=[]
        for id in data_cur.fetchall():
            alarm_list.append(id[0])

        for id in alarm_tuple:
            if id not in alarm_list:
                sql = "delete from alarm_summary_table where wellid='" + wellid + "' and alarm_message='"+id+"'"
                check_sql = "insert into aux_alarm_error(wellid,detected_date,alarm_message,alarm_reported_times,duration) values " \
                            "('"+wellid+"',to_date('" + str(max_date).split('.')[0] + "','yyyy/mm/dd hh24:mi:ss'),'" + id + "',0,777)"
                db.Write(sql)
                db.Write(check_sql)







if __name__=='__main__':
    test=DailyAlarmSummary()
