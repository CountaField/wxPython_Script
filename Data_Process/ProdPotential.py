from Oracle_connection import Gsrdb_Conn
import datetime

db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb') #connect database
#initial_date="to_date('2017/01/01','yyyy/mm/dd')"# define first date

#end_date=datetime.datetime(year=2017,month=1,day=20)

end_date_cur=db.Sql("select max(production_date) from production_data")
for id in end_date_cur.fetchall():
    max_date=id[0]


wellid_data_cur=db.Sql("select wellid,production_start_date from well_header where (wellid like 'SN%' or wellid='SUN003') and production_start_date is not Null")
#wellid_data_cur=db.Sql("select wellid,production_start_date from well_header where wellid='SN0002-01'")


for id in wellid_data_cur.fetchall():

    initial_date = datetime.datetime(year=2017, month=01, day=1)
    wellid=id[0]
    min_date=id[1]
    print "start well: " +wellid+" Processing....."
    if min_date<initial_date:
        print wellid,initial_date
        while initial_date <= max_date:
            prv_date = initial_date - datetime.timedelta(days=1)
            #print initial_date, prv_date, max_date
            sql_string = "select wellid,production_date,prod_time,daily_prod_gas from production_data where " \
                         "wellid='" + wellid + "' and production_date=to_date('" + str(
                initial_date) + "','yyyy-mm-dd hh24:mi:ss')"

            prv_sql_string = "select wellid,production_date,prod_time,daily_prod_gas from production_data where " \
                             "wellid='" + wellid + "' and production_date=to_date('" + str(
                prv_date) + "','yyyy-mm-dd hh24:mi:ss')"

            #print sql_string

            data_cur = db.Sql(sql_string)
            prv_data_cur = db.Sql(prv_sql_string)

            prod_time = 0
            daily_prod_gas = 0

            for x in data_cur.fetchall():
                prod_time = x[2]
                daily_prod_gas = x[3]

            for x in prv_data_cur.fetchall():
                prv_prod_time = x[2]
                prv_daily_prod = x[3]

            #print wellid, initial_date, prod_time, daily_prod_gas
            if prod_time == 24:
                cat = "'OPEN'"
                last_open_prod = daily_prod_gas
            else:
                cat = "'BU'"
                last_open_prod = prv_daily_prod

            insert_string = "insert into aux_prod_potential(wellid,production_date,daily_prod_gas,category,last_open_prod) values " \
                            "('" + wellid + "',to_date('" + str(initial_date) + "','yyyy-mm-dd hh24:mi:ss')," + str(
                daily_prod_gas) + "," + cat + "," + str(last_open_prod) + ")"
            #print insert_string
            db.Write(insert_string)
            initial_date += datetime.timedelta(days=1)



db.close()
















