from Oracle_connection import Gsrdb_Conn
import datetime
from collections import OrderedDict

class TidyUpStackPlotProdDate:
    def __init__(self,clusterid='',wellid_list=[],cluster_list=[]):

        self.prod_data_index_fix_dict = {}
        self.final_date_dict = {}
        self.result_date_dict={}
        self.WellidInCluster(clusterid,wellid_list)
        self.MinProdDateWells(clusterid,wellid_list,cluster_list)
        self.MaxProdDateWells(clusterid,wellid_list,cluster_list)
        print("min prod date well list",self.min_prod_date_wells_list)
        if (clusterid != '' or cluster_list!=[]) and wellid_list==[] :
            if self.min_prod_date_wells_list!=[] or self.pre_stander_well_list != []:
                if self.min_date is not None and self.max_date is not None:
                    if cluster_list==[] and clusterid!='':
                        self.DefineProdDateStander(clusterid=clusterid)
                    elif cluster_list!=[] and clusterid=='':
                        print('its here')
                        self.final_date_dict = {}
                        self.final_date_dict[cluster_list[0]] = []
                        self.result_date_dict = {}
                        self.prod_data_index_fix_dict = {}
                        self.DefineProdDateStander(cluster_list=cluster_list)
            else:
                pass
            self.CompareProdDateDiff(cluster_list)
            self.TidyUpProdData(clusterid,cluster_list)
        elif wellid_list!=[]:
            self.prod_data_index_fix_dict = {}
            self.final_date_dict = {}
            self.result_date_dict = {}


    def WellidInCluster(self,clusterid='',wellid_list=[],cluster_list=[]):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        if wellid_list==[] and cluster_list==[]:
            self.wellid_list=[]
            wellid_cur = db.Sql("select wellid from vw_prod_all_ssoc where "
                                "wellid in (select wellid from well_header where "
                                "clusterid=\'"+clusterid+"\') group by wellid order by wellid")
            for wellid in wellid_cur.fetchall():
                self.wellid_list.append(wellid[0])
        elif wellid_list!=[] and clusterid=='' and cluster_list==[]:
            self.wellid_list=wellid_list
        elif clusterid=='' and wellid_list==[] and cluster_list!=[]:
            self.wellid_list = cluster_list
        db.close()
        for x in self.final_date_dict.keys():
            print 'this is final date list',len(self.final_date_dict[x])
        if clusterid not in self.final_date_dict.keys():
            self.final_date_dict[clusterid] = []
        if cluster_list!=[]:
            self.final_date_dict[cluster_list[0]]=[]
        return self.wellid_list

    def MinProdDateWells(self,clusterid='',wellid_list=[],cluster_list=[]):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.min_prod_date_wells_list=[]
        if wellid_list==[] and cluster_list==[]:
            min_start_date_well_cur = db.Sql("select wellid from vw_prod_all_ssoc where "
                                             "production_date=(select min(production_date) "
                                             "from vw_prod_all_ssoc where wellid in"
                                             " (select wellid from well_header where "
                                             "clusterid=\'" + clusterid + "\')) and wellid in (select wellid  from well_header where clusterid=\'" + clusterid + "\') order by wellid")

            min_date_cur = db.Sql("select min(production_date) "
                                  "from vw_prod_all_ssoc where wellid in"
                                  " (select wellid from well_header where clusterid=\'" + clusterid + "\') and daily_prod_gas is not null")
        elif wellid_list!=[] and cluster_list==[]:
            wellid_string=''
            for id in wellid_list:
                wellid_string=wellid_string+"\'"+id+"\'"+','

            min_start_date_well_cur= db.Sql("select wellid from vw_prod_all_ssoc where production_date=(select min(production_date) "
                                             "from vw_prod_all_ssoc where wellid in ("+wellid_string[:-1]+"))")

            min_date_cur = db.Sql("select min(production_date) "
                                  "from vw_prod_all_ssoc where wellid in "
                                  "("+wellid_string[:-1]+") and daily_prod_gas is not null" )
        elif  cluster_list!=[] and wellid_list==[]:
            cluster_string=''
            for id in cluster_list:
                cluster_string=cluster_string+"\'"+id+"\'"+','
            #print(cluster_string)
            min_start_date_well_cur = db.Sql("select clusterid from vw_cluster_summary where production_date=(select min(production_date) "
                                             "from vw_cluster_summary where clusterid in ("+cluster_string[:-1]+")) and clusterid in ("+cluster_string[:-1]+")")

            min_date_cur = db.Sql("select min(production_date) "
                                  "from vw_cluster_summary where clusterid in "
                                  "(" + cluster_string[:-1] + ") ")

        self.no_min_date_wells_list = []

        for id in min_date_cur.fetchall():
            self.min_date = id[0]

        for wellid in min_start_date_well_cur.fetchall():
            self.min_prod_date_wells_list.append(wellid[0])

        for wellid in self.wellid_list:
            if wellid not in self.min_prod_date_wells_list:
                self.no_min_date_wells_list.append(wellid)
        for cluster in cluster_list:
            if cluster not in self.min_prod_date_wells_list:
                self.no_min_date_wells_list.append(cluster)
        db.close()


    def MaxProdDateWells(self,clusterid='',wellid_list=[],cluster_list=[]):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.max_prod_date_wells_list=[]
        self.no_max_date_wells_list = []
        if wellid_list == [] and cluster_list==[]:
            max_start_date_well_cur =db.Sql("select wellid from vw_prod_all_ssoc where "
                                         "production_date=(select max(production_date) "
                                         "from vw_prod_all_ssoc where wellid in"
                                         " (select wellid from well_header where clusterid=\'" + clusterid + "\')) ""and wellid in (select wellid  from well_header where clusterid=\'" + clusterid + "\') order by wellid")

            max_date_cur = db.Sql("select max(production_date) "
                                  "from vw_prod_all_ssoc where wellid in"
                                  " (select wellid from well_header where clusterid=\'" + clusterid + "\') and daily_prod_gas is not null")
        elif wellid_list != [] and cluster_list == []:
            wellid_string = ''
            for id in wellid_list:
                wellid_string = wellid_string + "\'" + id + "\'" + ','
            max_start_date_well_cur = db.Sql(
                    "select wellid from vw_prod_all_ssoc where production_date=(select max(production_date) "
                    "from vw_prod_all_ssoc where wellid in (" + wellid_string[:-1] + "))")
            max_date_cur = db.Sql("select max(production_date) "
                                  "from vw_prod_all_ssoc where wellid in "
                                  "(" + wellid_string[:-1] + ") and daily_prod_gas is not null")
        elif cluster_list != [] and wellid_list == []:
            cluster_string = ''
            for id in cluster_list:
                cluster_string = cluster_string + "\'" + id + "\'" + ','
            max_start_date_well_cur = db.Sql(
                "select clusterid from vw_cluster_summary where production_date=(select max(production_date) "
                "from vw_cluster_summary where clusterid in (" + cluster_string[:-1] + "))and clusterid in ("+cluster_string[:-1]+")")

            max_date_cur = db.Sql("select max(production_date) "
                                  "from vw_cluster_summary where clusterid in "
                                  "(" + cluster_string[:-1] + ") ")
        for id in max_date_cur.fetchall():
            self.max_date = id[0]

        for wellid in max_start_date_well_cur.fetchall():
            self.max_prod_date_wells_list.append(wellid[0])

        for wellid in self.wellid_list:
            if wellid not in self.max_prod_date_wells_list:
                self.no_max_date_wells_list.append(wellid)


        for cluster in cluster_list:
            if cluster not in self.max_prod_date_wells_list:
                self.no_max_date_wells_list.append(cluster)
        #print(self.max_prod_date_wells_list)
        db.close()

    def DefineProdDateStander(self,clusterid='',cluster_list=[]):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.pre_stander_well_list = []
        self.stander_well_list=[]
        self.fix_well_list=[]

        delta_days = self.max_date - self.min_date
        self.delta_days_count = delta_days.days

        for wellid_min in self.min_prod_date_wells_list:
            for wellid_max in self.max_prod_date_wells_list:
                if wellid_min==wellid_max:
                    self.pre_stander_well_list.append(wellid_min)
        #print('stander cluster',self.pre_stander_well_list)

        for wellid in self.pre_stander_well_list:
            if cluster_list==[]:
                pre_st_well_prod_date_check_cur=db.Sql("select count(production_date) from vw_prod_all_ssoc where wellid=\'"+wellid+"\' and daily_prod_gas is not null")
            else:
                pre_st_well_prod_date_check_cur = db.Sql("select count(production_date) from vw_cluster_summary where clusterid=\'" + wellid + "\' and sum_daily_prod_gas is not null")

            for date_count in pre_st_well_prod_date_check_cur.fetchall():
                 count_date=date_count[0]

            if count_date!=self.delta_days_count+1:
                self.fix_well_list.append(wellid)
                self.TidyUpDateData(wellid,cluster_list)
            else:
                self.stander_well_list.append(wellid)

        if self.stander_well_list!=[]:
            wellid=self.stander_well_list[0]
            self.stander_wells_exist=True
            if cluster_list==[]:
                stander_prod_date_cur=db.Sql("select production_date from vw_prod_all_ssoc where wellid=\'"+wellid+"\' and daily_prod_gas is not null order by production_date")
                for prod_date in stander_prod_date_cur.fetchall():
                    self.final_date_dict[clusterid].append(prod_date[0])
            else:
                stander_prod_date_cur=db.Sql("select production_date from vw_cluster_summary where clusterid=\'"+wellid+"\' and sum_daily_prod_gas is not null order by production_date")
                for prod_date in stander_prod_date_cur.fetchall():
                    self.final_date_dict[cluster_list[0]].append(prod_date[0])
        else:
            if self.min_date is not None and self.max_date is not None:
                delta_days=self.max_date-self.min_date
            else:
                pass
            i=0
            if cluster_list!=[]:
                for days in range(delta_days.days + 1):
                    self.final_date_dict[cluster_list[0]].append(self.min_date + datetime.timedelta(i))
                    i += 1
            else:
                for days in range(delta_days.days+1):
                    self.final_date_dict[clusterid].append(self.min_date+datetime.timedelta(i))
                    i+=1
            self.stander_wells_exist = False
        #print(self.final_date_dict)
        db.close()

    def TidyUpDateData(self,wellid='',cluster_list=[]):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        self.prod_data_index_fix_dict[wellid] = []

        stander_prod_date_list=[]
        i=0
        for prod_date in range(self.delta_days_count+1):
            stander_prod_date_list.append(self.min_date+datetime.timedelta(i))
            i+=1
        if cluster_list==[]:
            checked_well_prod_date_cur=db.Sql("select production_date from vw_prod_all_ssoc where "
                                              "wellid =\'"+wellid+"\' and daily_prod_gas is not null order by production_date ")
        else:
            checked_well_prod_date_cur = db.Sql("select production_date from vw_cluster_summary where "
                                                "clusterid =\'" + wellid + "\' and sum_daily_prod_gas is not null order by production_date")

        checked_well_prod_date_list=[]

        for prod_date in checked_well_prod_date_cur.fetchall():
            checked_well_prod_date_list.append(prod_date[0])
        index=0
        for id in  stander_prod_date_list:
            if id not in checked_well_prod_date_list:
                self.prod_data_index_fix_dict[wellid].append(index)
            index+=1
        #print('prod data index fix dict',self.prod_data_index_fix_dict)

    def CompareProdDateDiff(self,cluster_list=[]):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.no_min_wells_diff=OrderedDict()
        self.no_max_wells_diff=OrderedDict()
        if self.no_min_date_wells_list!=[]:
            if cluster_list==[]:
                for wellid in self.no_min_date_wells_list:
                    no_min_well_prod_cur=db.Sql("select min(production_date) from vw_prod_all_ssoc "
                                               " where wellid=\'"+wellid+"\' AND daily_prod_gas is not null order by production_date")
                    for prod_date in no_min_well_prod_cur.fetchall():
                        if prod_date[0] !=None:
                            delta_day=prod_date[0]-self.min_date
                            self.no_min_wells_diff[wellid] =delta_day.days
            else:
                for cluster in self.no_min_date_wells_list:
                    no_min_well_prod_cur=db.Sql("select min(production_date) "
                                  "from vw_cluster_summary where clusterid=\'"+cluster+"\' and sum_daily_prod_gas is not null")
                    for prod_date in no_min_well_prod_cur.fetchall():
                        if prod_date[0] != None:
                            delta_day = prod_date[0] - self.min_date
                            self.no_min_wells_diff[cluster] = delta_day.days
        if self.no_max_date_wells_list!=[]:
            if cluster_list == []:
                for wellid in self.no_max_date_wells_list:
                    no_max_well_prod_cur=db.Sql("select max(production_date) from vw_prod_all_ssoc "
                                               " where wellid=\'"+wellid+"\' and daily_prod_gas is not null order by production_date")
                    for prod_date in no_max_well_prod_cur.fetchall():
                        if prod_date[0] !=None:
                            delta_day = self.max_date-prod_date[0]
                            self.no_max_wells_diff[wellid]=delta_day.days
            else:
                for cluster in self.no_max_date_wells_list:
                    no_max_well_prod_cur = db.Sql("select max(production_date) "
                                                  " from vw_cluster_summary where clusterid=\'" + cluster + "\' and sum_daily_prod_gas is not null")
                    for prod_date in no_max_well_prod_cur.fetchall():
                        if prod_date[0] != None:
                            delta_day = self.max_date-prod_date[0]
                            self.no_max_wells_diff[cluster] = delta_day.days
        #print('no max diff',self.no_max_wells_diff)
        #print('no min diff', self.no_min_wells_diff)
        db.close()

    def TidyUpProdData(self,clusterid='',cluster_list=[]):
        no_min_well_pre_data_dict=OrderedDict()
        no_max_well_pre_data_dict=OrderedDict()
        self.prod_data_dict=OrderedDict()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        if self.no_min_date_wells_list!=[]:

            for wellid in self.no_min_wells_diff:
                self.prod_data_dict[wellid]=[]
                no_min_well_pre_data_dict[wellid]=[]
                for id in range(1,self.no_min_wells_diff[wellid]+1):
                    no_min_well_pre_data_dict[wellid].append(0)
                self.prod_data_dict[wellid]+=no_min_well_pre_data_dict[wellid]

                if cluster_list == []:
                    no_min_well_data_cur=db.Sql("select daily_prod_gas from vw_prod_all_ssoc where wellid=\'"+wellid+"\' and daily_prod_gas is not null")
                else:
                    no_min_well_data_cur = db.Sql("select sum_daily_prod_gas from vw_cluster_summary where clusterid=\'"+wellid+"\' and sum_daily_prod_gas is not null order by production_date")

                for data in no_min_well_data_cur.fetchall():
                    if data[0] is not None:
                        self.prod_data_dict[wellid].append(data[0])
                    else:
                        self.prod_data_dict[wellid].append(0.0)

                if cluster_list==[]:
                    if  len(self.prod_data_dict[wellid])!=len(self.final_date_dict[clusterid]):
                        if wellid not in self.no_max_date_wells_list:
                            if wellid not in self.fix_well_list:
                                self.fix_well_list.append(wellid)
                                self.TidyUpDateData(wellid,cluster_list)
                else:
                    if len(self.prod_data_dict[wellid]) != len(self.final_date_dict[cluster_list[0]]):
                        if wellid not in self.no_max_date_wells_list:
                            if wellid not in self.fix_well_list:
                                self.fix_well_list.append(wellid)
                                self.TidyUpDateData(wellid, cluster_list)
        #('fix well list',self.fix_well_list)

        #for cluster in self.prod_data_dict:
            #print('insert no min',cluster, len(self.prod_data_dict[cluster]))


        if self.no_max_date_wells_list!=[]:
            for wellid in self.no_max_wells_diff:
                no_max_well_pre_data_dict[wellid] = []
                if cluster_list==[]:
                    no_max_well_data_cur=db.Sql("select daily_prod_gas from vw_prod_all_ssoc where wellid=\'"+wellid+"\' and daily_prod_gas is not null")
                else:
                    #('no max here')
                    no_max_well_data_cur = db.Sql("select sum_daily_prod_gas from vw_cluster_summary where clusterid=\'" + wellid + "\' and sum_daily_prod_gas is not null order by production_date")
                if wellid not in self.no_min_wells_diff:
                    self.prod_data_dict[wellid] = []

                    for data in no_max_well_data_cur.fetchall():
                        if data[0] is not None:
                            self.prod_data_dict[wellid].append(data[0])
                        else:
                            self.prod_data_dict[wellid].append(0.0)



                #print('append after max data', wellid, len(self.prod_data_dict[wellid]))
                for id in range(0, self.no_max_wells_diff[wellid]):
                    no_max_well_pre_data_dict[wellid].append(0)

                self.prod_data_dict[wellid]+=no_max_well_pre_data_dict[wellid]

        #for cluster in self.prod_data_dict:
            #print('after no max', cluster, len(self.prod_data_dict[cluster]))

        if self.fix_well_list!=[]:

            for wellid in self.fix_well_list:
                if cluster_list==[]:
                    fix_well_data_cur = db.Sql("select daily_prod_gas from vw_prod_all_ssoc where wellid=\'"+wellid+"\' and daily_prod_gas is not null")
                else:
                    fix_well_data_cur = db.Sql("select sum_daily_prod_gas from vw_cluster_summary where clusterid=\'" + wellid + "\' and sum_daily_prod_gas is not null order by production_date")

                self.prod_data_dict[wellid] = []
                for data in fix_well_data_cur.fetchall():
                    if data[0] is not None:
                        self.prod_data_dict[wellid].append(data[0])
                    else:
                        self.prod_data_dict[wellid].append(0.0)

                if wellid in self.prod_data_index_fix_dict:
                    if self.prod_data_index_fix_dict[wellid]!=[]:
                        for id in self.prod_data_index_fix_dict[wellid]:
                            self.prod_data_dict[wellid].insert(id,0)
        #for cluster in self.prod_data_dict:
            #print('after fix', cluster, len(self.prod_data_dict[cluster]))

        if self.stander_well_list!=[]:
            for wellid in self.stander_well_list:
                if cluster_list==[]:
                    st_well_data_cur=db.Sql("select daily_prod_gas from vw_prod_all_ssoc where wellid=\'"+wellid+"\' and daily_prod_gas is not null")
                else:
                    st_well_data_cur = db.Sql("select sum_daily_prod_gas from vw_cluster_summary where clusterid=\'" + wellid + "\' and sum_daily_prod_gas is not null order by production_date")

                self.prod_data_dict[wellid]=[]

                for data in st_well_data_cur.fetchall():
                    if data[0] is not None:
                        self.prod_data_dict[wellid].append(data[0])
                    else:
                        self.prod_data_dict[wellid].append(0.0)

        #for cluster in self.prod_data_dict:
            #print('final result ',cluster,len(self.prod_data_dict[cluster]))


        #print('no min cluster',self.no_min_date_wells_list)
        #print('prod data dict',  self.prod_data_dict.keys())
        db.close()


if __name__=='__main__':
    test=TidyUpStackPlotProdDate(cluster_list=['C003','C084','C138','C002'])































