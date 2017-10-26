# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 10:48:22 2017

@author: liu_adeline
"""

"""classifier application"""
import pandas as pd
import numpy as np
from Oracle_connection import Gsrdb_Conn
import matplotlib.pylab as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier


"""get features for knn"""

class DynamicWellGroupClassifier:

    def __init__(self,wellid):
        self.Feature_all()
        self.new_feature(wellid)
        self.wellgroup_update(wellid)


    def Feature_all(self):

        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        extrac_data_cur = db.Sql("select QG_700D,GP_700D,MAXRATE,AOF_STAB,CWHP_START,WELLID,DG,Greater_700d from F_KNN_DYNAMIC")
        Qg_700d=[]
        Gp_700d=[]
        Maxrate=[]
        AOF_Stab=[]
        CWHP_Start=[]
        WellID=[]
        DG=[]
        Comments=[]

        for id in extrac_data_cur.fetchall():
            Qg_700d.append(id[0])
            Gp_700d.append(id[1])
            Maxrate.append(id[2])
            AOF_Stab.append(id[3])
            CWHP_Start.append(id[4])
            WellID.append(id[5])
            DG.append(id[6])
            Comments.append(id[7])

        db.close()

        F_knn=pd.DataFrame([Qg_700d,Gp_700d,Maxrate,AOF_Stab,CWHP_Start,WellID,DG,Comments],index=['Qg_700d','Gp_700d','Maxrate','AOF_Stab','CWHP_Start','WellID','DG','Comments']).transpose()

        return F_knn


    """data normalisation,convert all kind of data into the range of [0,1]"""
    #columns could be int or string o(name of the columns)mnew_input is the value of new added wells
    def datascaler(self,Dataframe,columns,new_input=None):

        if new_input==None:
            Data_normalized=Dataframe.ix[:,columns].apply(lambda x:(x-Dataframe.ix[:,columns].min())/(Dataframe.ix[:,columns].max()-Dataframe.ix[:,columns].min()))
            return Data_normalized
        else:

            if new_input>Dataframe.ix[:,columns].max():
                Data_normalized=Dataframe.ix[:,columns].apply(lambda x:(x-Dataframe.ix[:,columns].min())/(new_input-Dataframe.ix[:,columns].min()))
                new_input_ratio=1
            elif new_input<Dataframe.ix[:,columns].min():
                Data_normalized=Dataframe.ix[:,columns].apply(lambda x:(x-new_input)/(Dataframe.ix[:,columns].max()-new_input))
                new_input_ratio=0
            else:
                Data_normalized=Dataframe.ix[:,columns].apply(lambda x:(x-Dataframe.ix[:,columns].min())/(Dataframe.ix[:,columns].max()-Dataframe.ix[:,columns].min()))
                new_input_ratio=(new_input-Dataframe.ix[:,columns].min())/(Dataframe.ix[:,columns].max()-Dataframe.ix[:,columns].min())
            return Data_normalized,new_input_ratio


    """prepare the features for a new well"""
    def new_feature(self,wellid):#string

        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        extrac_data_cur = db.Sql("select WELLID from PRODUCTION_DATA where WELLID ='" + wellid+"'")

        totaldays=[]
        for id in extrac_data_cur.fetchall():
            totaldays.append(id[0])

        """if total production days over 700d, extract prod data of 700 days and calculated Qg_700d and max rate"""

        if len(totaldays)>699:
            extrac_data_cur = db.Sql("select DAILY_PROD_GAS,PRODUCTION_DATE from PRODUCTION_DATA where WELLID ='" + wellid+"' order by PRODUCTION_DATE ")

            daily_rate=[]
            datelist=[]

            for id in extrac_data_cur.fetchall():
                daily_rate.append(id[0])
                datelist.append(id[1])

            """get initial training set"""
            F_Knn=self.Feature_all().dropna().iloc[:,:7]

            """cal Qg_700d and Gp_700d"""
            Prod=pd.DataFrame([daily_rate,datelist],index=['daily_rate','datelist']).transpose()
            Prod=Prod.iloc[:700,:]
            Qg_700d=Prod.daily_rate[Prod.daily_rate>=7].sum()/Prod.daily_rate.sum()
            F_Knn_Train=pd.DataFrame()
            F_Knn_Train["Qg_700d"]=1-F_Knn.Qg_700d


            Gp_700d=Prod.daily_rate.sum()/1000
            F_Knn_Train['Gp_700d'],Gp_700d_ratio=self.datascaler(F_Knn,columns='Gp_700d',new_input=Gp_700d)


            """cal Maxrate"""
            Maxrate=Prod.daily_rate.max()
            F_Knn_Train['Maxrate'],Maxrate_ratio=self.datascaler(F_Knn,columns='Maxrate',new_input=Maxrate)

            """get AOF_Stab"""
            extrac_data_cur = db.Sql("select AOF_STABILIZED from AOF where WELLID ='" + wellid+"'")
            AOF_stab=list(extrac_data_cur.fetchall()[0])[0]
            F_Knn_Train['AOF_Stab'],AOF_Stab_ratio=self.datascaler(F_Knn,columns='AOF_Stab',new_input=AOF_stab)

            feature_for_fit=[Qg_700d,Gp_700d_ratio,Maxrate_ratio,AOF_Stab_ratio,"1"]
            feature=[1-Qg_700d,Gp_700d,Maxrate,AOF_stab,"",wellid]
            return F_Knn_Train,feature_for_fit,feature
        else:
            extrac_data_cur = db.Sql("select DAILY_PROD_GAS,PRODUCTION_DATE from PRODUCTION_DATA where WELLID ='" + wellid+"' order by PRODUCTION_DATE ")

            daily_rate=[]
            datelist=[]

            for id in extrac_data_cur.fetchall():
                daily_rate.append(id[0])
                datelist.append(id[1])

            """get initial training set"""
            F_Knn=self.Feature_all().dropna().iloc[:,:7]

            """cal Qg_xxxd and Gp_xxd"""
            Prod=pd.DataFrame([daily_rate,datelist],index=['daily_rate','datelist']).transpose()

            Qg_less_700d=Prod.daily_rate[Prod.daily_rate>=7].sum()/Prod.daily_rate.sum()
            F_Knn_Train=pd.DataFrame()
            F_Knn_Train["Qg_700d"]=1-F_Knn.Qg_700d

            Gp_less_700d=Prod.daily_rate.sum()/1000
            F_Knn_Train['Gp_700d'],Gp_less_700d_ratio=self.datascaler(F_Knn,columns='Gp_700d',new_input=Gp_less_700d)

            """cal Maxrate"""
            Maxrate=Prod.daily_rate.max()
            F_Knn_Train['Maxrate'],Maxrate_ratio=self.datascaler(F_Knn,columns='Maxrate',new_input=Maxrate)


            """get AOF_Stab"""
            extrac_data_cur = db.Sql("select AOF_STABILIZED from AOF where WELLID ='" + wellid+"'")
            AOF_Stab=list(extrac_data_cur.fetchall()[0])[0]
            F_Knn_Train['AOF_Stab'],AOF_Stab_ratio=self.datascaler(F_Knn,columns='AOF_Stab',new_input=AOF_Stab)

            db.close
            feature_for_fit=[Qg_less_700d,Gp_less_700d_ratio,Maxrate_ratio,AOF_Stab_ratio,"0"]
            feature=[1-Qg_less_700d,Gp_less_700d,Maxrate,AOF_Stab,"",wellid]
            return F_Knn_Train,feature_for_fit,feature

    """update training set: add new well into the training set and write into database"""
    def wellgroup_update(self,wellid):
        """get initial training set """#to write in Oracle and update the code
        F_Knn=self.Feature_all()
        F_Knn.index=range(len(F_Knn))


        """if well aleady exist in F_Knn, get its group from the table, if well is new, updated the table with KNN method"""

        if wellid in list(F_Knn.WellID) and F_Knn.ix[F_Knn.WellID==wellid,'Comments']=='1':
            F_Knn.index=F_Knn.WellID
            wellgroup=F_Knn.ix[wellid,"DG"]
        elif wellid in list(F_Knn.WellID) and F_Knn.ix[F_Knn.WellID==wellid,'Comments']=='0':


            F_Knn_Train,feature_for_fit,feature=self.new_feature(wellid)
            F_Knn_Train.index=range(len(F_Knn_Train))

            """training set"""
            Trainning=[]
            for id in range(len(F_Knn_Train)):
                Trainning.append(list(F_Knn_Train.ix[id,:]))


            Groupset=[]
            for id in range(len(F_Knn)):
                Groupset.append(F_Knn.ix[id,"DG"])

            """training the data"""
            neigh=KNeighborsClassifier(n_neighbors=6)
            neigh.fit(Trainning,Groupset)

            """fit for new well"""
            wellgroup=neigh.predict(feature_for_fit[0:4])


            """update to excel"""#to write into Oracle and update the code
            F_Knn.index=F_Knn.WellID
            F_Knn=F_Knn.drop([wellid],axis=0)
            F_Knn.index=range(len(F_Knn))

            feature.append(int(wellgroup))
            feature.append(feature_for_fit[4])

            new_well=pd.DataFrame(feature,index=['Qg_700d','Gp_700d','Maxrate','AOF_Stab','CWHP_Start','WellID','DG','Comments']).transpose()
            F_Knn=F_Knn.append(new_well,ignore_index=True)
            F_Knn.to_excel('W:\\GSR\\050000-GeoInformation\\052300-Projects\\User_Interface\\Adeline_Scripts\\F_Knn_Dynamic.xlsx')

        else:
            F_Knn_Train,feature_for_fit,feature=self.new_feature(wellid)
            F_Knn_Train.index=range(len(F_Knn_Train))

            """training set"""
            Trainning=[]
            for id in range(len(F_Knn_Train)):
                Trainning.append(list(F_Knn_Train.ix[id,:]))


            Groupset=[]
            for id in range(len(F_Knn)):
                Groupset.append(F_Knn.ix[id,"DG"])

            """training the data"""
            neigh=KNeighborsClassifier(n_neighbors=6)
            neigh.fit(Trainning,Groupset)

            """fit for new well"""
            wellgroup=neigh.predict(feature_for_fit[0:4])


            """update to excel"""#to write into Oracle and update the code

            feature.append(int(wellgroup))
            feature.append(feature_for_fit[4])
            new_well=pd.DataFrame(feature,index=['Qg_700d','Gp_700d','Maxrate','AOF_Stab','CWHP_Start','WellID','DG','Comments']).transpose()
            F_Knn=F_Knn.append(new_well,ignore_index=True)
            F_Knn.to_excel('W:\\GSR\\050000-GeoInformation\\052300-Projects\\User_Interface\\Adeline_Scripts\\F_Knn_Dynamic.xlsx')
        return F_Knn,wellgroup



if __name__=='__main__':
    test=DynamicWellGroupClassifier('SN0002-01')







