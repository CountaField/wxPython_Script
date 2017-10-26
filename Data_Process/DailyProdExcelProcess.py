# !/usr/bin/python
# -*- coding:utf8-*-
import re
import os
from pyexcel_xls import get_data
from pyexcel_xls import save_data
from collections import OrderedDict
from TransferToCsvProcess import CVSformat
import string
from Oracle_connection import Gsrdb_Conn
import datetime
import json
class DailyReportProcess:
    def __init__(self,infile,outputpath):

        data=get_data(infile)
        self.db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.st_wells=self.ReturnSTwellList()
        self.sheet_name=self.GetSheetName(data,infile)
        print type(self.sheet_name),self.sheet_name
        self.FormatInputFile(self.sheet_name)
        self.position_dict=self.FindDataCol(data)
        self.outpath=outputpath
        self.importfile=self.SaveInputFile(self.ExtractData(data))
        self.final_output_file=CVSformat(self.importfile)



    def GetSheetName(self,data,inputfile=None):

        if isinstance(data,list):
            month=inputfile.split('.')[0][-1]
            return int(month)

        for x in data.keys():
            print 'this is x',x
            sheet_name=x

        return sheet_name


    def FormatInputFile(self,sheetname,year='2017'):
        year = datetime.datetime.now().year
        if isinstance(self.sheet_name,int):
            print self.sheet_name
            report_date=datetime.datetime(year=year,month=self.sheet_name,day=1)
            prod_date=report_date-datetime.timedelta(days=1)
            self.production_date=str(prod_date.month)+'-'+str(prod_date.day)+'-'+str(year)
            self.outputfilename=self.production_date
        else:
            path=''
            print 'this is sheet name',sheetname
            pat=r'\d+'
            prod_date=re.findall(pat,sheetname)
            print prod_date
            month,day=prod_date
            #prod_day=int(day)-1
            final_prod_date=datetime.datetime(year=year,month=int(month),day=int(day))
            final_prod_date=final_prod_date-datetime.timedelta(days=1)
            print final_prod_date
            #self.production_date=month+'/'+str(final_prod)'+year
            self.production_date=str(final_prod_date.month)+'-'+str(final_prod_date.day)+'-'+str(year)
            #self.outputfilename=month+'-'+str(int(day)-1)+'-'+year
            self.outputfilename = self.production_date
            print self.production_date
        print self.outputfilename


    def FindDataCol(self,data):
        pos_dict=OrderedDict()
        col_count=0
        if isinstance(data,list):
            for x in data[1]:
                if 'Well No.'.upper() in x.upper():
                    pos_dict['WELLID'] = col_count
                if 'production time'.upper() in x.upper():
                    prodtime_count = col_count
                    pos_dict['PROD_TIME'] = prodtime_count
                if 'oil pressure'.upper() in x.upper():
                    pos_dict['WELL_HEAD_PRESSURE'] = col_count
                if 'Wellhead temperature'.upper() in x.upper():
                    pos_dict['WELL_HEAD_TEMPERATURE'] = col_count
                if 'Gas production'.upper() in x.upper():
                    pos_dict['DAILY_PROD_GAS'] = col_count
                col_count += 1
            col_count2 = 0
            for x in data[2]:
                if 'TotalYearly'.upper() in x.upper():
                    pos_dict['PROD_CUM_GAS'] = col_count2
                col_count2 += 1
            col_count = 0
            for x in data[1]:

                if 'Comments'.upper() in x.upper():
                    pos_dict['PROD_COMMENTS'] = col_count
                col_count += 1
            return pos_dict
        else:
            for x in data[self.sheet_name][1]:
                if 'Well No.'.upper() in x.upper():
                    pos_dict['WELLID'] = col_count
                if 'production time'.upper() in x.upper():
                    prodtime_count = col_count
                    pos_dict['PROD_TIME'] = prodtime_count
                if 'oil pressure'.upper() in x.upper():
                    pos_dict['WELL_HEAD_PRESSURE'] = col_count
                if 'Wellhead temperature'.upper() in x.upper():
                    pos_dict['WELL_HEAD_TEMPERATURE'] = col_count
                if 'Gas production'.upper() in x.upper():
                    pos_dict['DAILY_PROD_GAS'] = col_count
                col_count += 1
            col_count2 = 0
            for x in data[self.sheet_name][2]:
                if 'TotalYearly'.upper() in x.upper():
                    pos_dict['PROD_CUM_GAS'] = col_count2
                col_count2 += 1
            col_count = 0
            for x in data[self.sheet_name][1]:

                if 'Comments'.upper() in x.upper():
                    pos_dict['PROD_COMMENTS'] = col_count
                col_count += 1
            return pos_dict

    def ExtractData(self, data):
        sheetname = 'InputFile'
        self.data_dict = OrderedDict()
        final_data = []
        if isinstance(data, list):
            for x in data:
                row_list = []
                if len(x) > 4 and 'SN' in x[self.position_dict['WELLID']]:
                    for colid in self.position_dict:
                        if len(x) > self.position_dict[colid]:
                            if isinstance(x[self.position_dict[colid]], unicode):
                                if '\n' in x[self.position_dict[colid]]:
                                    data_step1 = x[self.position_dict[colid]].split('\n')
                                    data_step2 = data_step1[1]
                                    final_data_step = data_step2.encode('utf8')
                                    row_list.append(final_data_step)
                                elif x[self.position_dict[colid]] == 'SN3':
                                    row_list.append('SUN003')
                                elif x[self.position_dict[colid]] + 'ST' in self.st_wells:
                                    row_list.append(x[self.position_dict[colid]] + 'ST')
                                else:
                                    row_list.append(x[self.position_dict[colid]].encode('utf8'))
                            elif colid == 'DAILY_PROD_GAS':
                                row_list.append(x[self.position_dict[colid]] * 10)
                            elif colid == 'WELL_HEAD_PRESSURE':
                                row_list.append(x[self.position_dict[colid]] * 10)
                            elif colid == 'PROD_CUM_GAS':
                                row_list.append(x[self.position_dict[colid]] / 100)
                            else:
                                row_list.append(x[self.position_dict[colid]])

                if row_list != []:
                        row_list.insert(1, self.production_date.encode('utf8'))
                        row_list.insert(3, '')
                        row_list1 = self.UnknowCProcess(row_list)
                        final_data.append(row_list1)
                        self.data_dict.update({sheetname: final_data})
            return self.data_dict
        else:
            for x in data[self.sheet_name]:
                row_list = []
                if len(x) > 4 and 'SN' in x[self.position_dict['WELLID']]:
                    for colid in self.position_dict:
                        if len(x) > self.position_dict[colid]:
                            if isinstance(x[self.position_dict[colid]],unicode):
                                if  '\n' in  x[self.position_dict[colid]]:
                                    data_step1=x[self.position_dict[colid]].split('\n')
                                    data_step2=data_step1[1]
                                    final_data_step=data_step2.encode('utf8')
                                    row_list.append(final_data_step)
                                elif x[self.position_dict[colid]]=='SN3':
                                    row_list.append('SUN003')
                                elif x[self.position_dict[colid]]+'ST' in self.st_wells:
                                    row_list.append(x[self.position_dict[colid]]+'ST' )
                                else:
                                    row_list.append(x[self.position_dict[colid]].encode('utf8'))
                            elif colid == 'DAILY_PROD_GAS':
                                row_list.append(x[self.position_dict[colid]]*10)
                            elif colid =='WELL_HEAD_PRESSURE':
                                row_list.append(x[self.position_dict[colid]] * 10)
                            elif colid=='PROD_CUM_GAS':
                                row_list.append(x[self.position_dict[colid]] / 100)
                            else:
                                row_list.append(x[self.position_dict[colid]])

                if row_list!= []:
                        row_list.insert(1, self.production_date.encode('utf8'))
                        row_list.insert(3,'')
                        row_list1=self.UnknowCProcess(row_list)
                        final_data.append(row_list1)
                        self.data_dict.update({sheetname:final_data})
            return self.data_dict

    def UnknowCProcess(self, alist):
        if isinstance(alist[-1],str):
            re_list=filter(lambda x: x in string.printable,alist[-1])
            rel_data_col=re_list.replace(',','')
            alist[-1]=rel_data_col
        else:
            pass
        return alist

    def SaveInputFile(self, data_dict):
        self.outputfile=self.outpath+'\\'+self.outputfilename+'.xls'
        save_data(self.outputfile,data_dict)
        return self.outputfile

    def PassFile(self):
        return self.final_output_file

    def ReturnSTwellList(self):
        st_well_list=[]
        cur=self.db.Sql("select wellid from well_header where wellid like \'%ST%\'")

        for col in cur.fetchall():
            st_well_list.append(col[0])
        return st_well_list




if __name__=='__main__':
    prod=DailyReportProcess()



