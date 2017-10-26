# !/usr/bin/python
# -*- coding:utf8 -*
import wx
import pandas as pd
import xlrd
import time
import datetime
import string
from collections import OrderedDict
from Oracle_connection import Gsrdb_Conn

class GGSImport(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self,parent,-1,size=(400,400))
        self.ControlInitial()
        self.Show()

    def ControlInitial(self):
        self.controls=OrderedDict()
        month_list = list(range(13))[1:]
        day_list = list(range(32))[1:]
        i = 0
        for x in month_list:
            if x<10:
                month_list[i]='0'+str(x)
            else:
                month_list[i] = str(x)
            i += 1

        z = 0
        for x in day_list:
            if x<10:
                day_list[z] = '0'+str(x)
            else:
                day_list[z] = str(x)
            z += 1
        self.controls['promottxt'] = wx.StaticText(self, -1, label='Please Choose the Date :')
        self.controls['yeartxt'] = wx.StaticText(self, -1, label='Year: ')
        self.controls['year_combobox'] = wx.ComboBox(self, -1,
                                                     choices=['2011', '2012', '2013', '2014', '2015', '2016', '2017',
                                                              '2018', '2019', '2020'])
        self.controls['monthtxt']=wx.StaticText(self,-1,label='Month: ')
        self.controls['month_combobox'] = wx.ComboBox(self, -1, choices=month_list)
        self.controls['daytxt']=wx.StaticText(self,-1,label='Day: ')
        self.controls['day_combobox'] = wx.ComboBox(self, -1, choices=day_list)
        import_button=wx.Button(self,-1,label='Import Data')
        close_button=wx.Button(self,-1,label='  Close ')
        sizer=wx.BoxSizer(wx.VERTICAL)
        button_sizer=wx.BoxSizer(wx.VERTICAL)
        button_sizer.AddSpacer(50)
        button_sizer.Add(import_button)
        button_sizer.AddSpacer(15)
        button_sizer.Add(close_button)
        frame_sizer=wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(20)
        for x in self.controls.keys():
            sizer.Add(self.controls[x])
            sizer.AddSpacer(10)
        frame_sizer.AddSpacer(30)
        frame_sizer.AddSizer(sizer)
        frame_sizer.AddSpacer(1)
        frame_sizer.AddSizer(button_sizer)
        self.SetSizer(frame_sizer)
        self.Bind(wx.EVT_BUTTON,self.OnImportClick,import_button)

    def OnImportClick(self,event):
        year=self.controls['year_combobox'].GetStringSelection()
        month=self.controls['month_combobox'].GetStringSelection()
        day=self.controls['day_combobox'].GetStringSelection()
        import_date=year+'-'+month+'-'+day
        ggs_dict=self.updateggs(import_date)
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        sql1 = "insert into  GGS (" + ggs_dict['ggs1_col'][:-1]+ ") values (" + ggs_dict['ggs1_data'][:-1] + ")"
        sql2=  "insert into  GGS (" + ggs_dict['ggs2_col'][:-1]+ ") values (" + ggs_dict['ggs2_data'][:-1] + ")"
        print sql1
        print sql2
        db.Write(sql1)
        db.Write(sql2)
        db.close()

    def monthinenglish(self,a):
        if a == '01':
            moneng = 'JANUARY'
            return moneng
        elif a == '02':
            moneng = 'FEBRUARY'
            return moneng
        elif a == '03':
            moneng = 'MARCH'
            return moneng
        elif a == '04':
            moneng = 'APRIL'
            return moneng
        elif a == '05':
            moneng = 'MAY'
            return moneng
        elif a == '06':
            moneng = 'JUNE'
            return moneng
        elif a == '07':
            moneng = 'JULY'
            return moneng
        elif a == '08':
            moneng = 'AUGUST'
            return moneng
        elif a == '09':
            moneng = 'SEPTEMBER'
            return moneng
        elif a == '10':
            moneng = 'OCTOBER'
            return moneng
        elif a == '11':
            moneng = 'NOVEMBER'
            return moneng
        elif a == '12':
            moneng = 'DECEMBER'
            return moneng
        else:
            print 'Date input is wrong, please redo it!'

    def updateggs(self, import_date, choice=False):

        t = time.strptime(import_date, "%Y-%m-%d")
        a = import_date.split('-')
        y, m, d = t[0:3]
        if m not in [10,11,12]:
            month='0'+str(m)
        else:
            month=str(m)
        moneng = self.monthinenglish(month)
        dateupdate0 = datetime.datetime(y, m, d)
        delta = datetime.timedelta(1)
        dateupdate = dateupdate0 - delta

        sheetname = str(m) + '月' + str(d) + '日'
        print sheetname
        sheetname = unicode(sheetname, "utf8")
        print sheetname
        '''inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
            t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + "年" + str(
            t[1]) + "月试井日报（SSOC WELLTEST DAILY REPORT OF AUGUST）" + str(t[1]) + "." + str(t[2]) + ".xls"
        uipath = unicode(inpath, "utf8")
        #newggs1 = xlrd.open_workbook(uipath, -1)
        try:
            dt = pd.read_excel(uipath, sheetname)
        except xlrd.biffh.XLRDError:
            print 'Excel File Sheet Name Error'
            return 0'''
        inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
            t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(m) + '月试井日报（SSOC WELLTEST DAILY REPORT OF ' + moneng + '）' + str(
            t[1]) + "." + str(t[2]) + ".xls"
        uipath = unicode(inpath, "utf8").encode('gbk')
        print uipath

        try:
            dt = pd.read_excel(uipath, sheetname)

            # newggs1=xlrd.open_workbook(uipath)
        except IOError:

            inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(
                m) + '月试井日报（SSOC WELLTEST DAILY REPORT OF ' + moneng + '）' + str(t[1]) + "." + str(t[2]) + ".xlsx"
            uipath = unicode(inpath, "utf8").encode('gbk')

            try:
                newggs1 = xlrd.open_workbook(uipath)
                dt = pd.read_excel(uipath, sheetname)
            except IOError:
                inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                    t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(
                    m) + '月试井日报（SSOC_WELLTEST_DAILY_REPORT_OF_' + moneng + '）' + str(t[1]) + "." + str(t[2]) + ".xls"
                uipath = unicode(inpath, "utf8").encode('gbk')
                try:
                    newggs1 = xlrd.open_workbook(uipath)
                    dt = pd.read_excel(uipath, sheetname)
                except IOError:
                    inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                        t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(
                        m) + '月试井日报（SSOC_WELLTEST_DAILY_REPORT_OF_' + moneng + '）' + str(t[1]) + "." + str(
                        t[2]) + ".xlsx"
                    uipath = unicode(inpath, "utf8").encode('gbk')
                    try:
                        newggs1 = xlrd.open_workbook(uipath)
                        dt = pd.read_excel(uipath, sheetname)
                    except IOError:
                        inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                            t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                            m) + '月试井日报（SSOC_WELLTEST_DAILY_REPORT_OF_' + moneng + '）' + str(t[1]) + "." + str(
                            t[2]) + ".xlsx"
                        uipath = unicode(inpath, "utf8").encode('gbk')
                        try:
                            newggs1 = xlrd.open_workbook(uipath)
                            dt = pd.read_excel(uipath, sheetname)
                        except IOError:
                            inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                m) + '月试井日报（SSOC WELLTEST DAILY REPORT OF ' + moneng + '）' + str(t[1]) + "." + str(
                                t[2]) + ".xlsx"
                            uipath = unicode(inpath, "utf8").encode('gbk')
                            try:
                                newggs1 = xlrd.open_workbook(uipath)
                                dt = pd.read_excel(uipath, sheetname)
                            except IOError:
                                inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                    t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                    m) + '月试井日报（SSOC WELLTEST DAILY REPORT OF ' + moneng + '）' + str(t[1]) + "." + str(
                                    t[2]) + ".xls"
                                uipath = unicode(inpath, "utf8").encode('gbk')
                                try:
                                    newggs1 = xlrd.open_workbook(uipath)
                                    dt = pd.read_excel(uipath, sheetname)
                                except IOError:
                                    inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                        t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                        m) + '月试井日报（SSOC_WELLTEST_DAILY_REPORT_OF_' + moneng + '）' + str(
                                        t[1]) + "." + str(t[2]) + ".xls"
                                    uipath = unicode(inpath, "utf8").encode('gbk')
                                    try:
                                        dt = pd.read_excel(uipath, sheetname)
                                    except IOError:
                                        inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                            t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                            m) + '月试井日报（SSOC_WELLTEST_DAILY_REPORT_OF_' + moneng + ')' + str(
                                            t[1]) + "." + str(t[2]) + ".xls"
                                        uipath = unicode(inpath, "utf8").encode('gbk')
                                        try:
                                            dt = pd.read_excel(uipath, sheetname)
                                        except IOError:
                                            inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                                t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                                m) + '月试井日报（SSOC_WELLTEST_DAILY_REPORT_OF_' + moneng + ')' + str(
                                                t[1]) + "." + str(t[2]) + ".xlsx"
                                            uipath = unicode(inpath, "utf8").encode('gbk')
                                            try:
                                                dt = pd.read_excel(uipath, sheetname)
                                            except IOError:
                                                inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                                    t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                                    m) + '月试井日报（SSOC WELLTEST DAILY REPORT OF ' + moneng + ')' + str(
                                                    t[1]) + "." + str(t[2]) + ".xlsx"
                                                uipath = unicode(inpath, "utf8").encode('gbk')
                                                try:
                                                    dt = pd.read_excel(uipath, sheetname)
                                                except IOError:
                                                    inpath = r"W:\GSR\040000-Reservoir_Studies\040300-RE_Prod\Production Data\Daily Production Report of SSOC No.1 Gas Zone" + '\\' + str(
                                                        t[0]) + '\\' + str(a[1]) + '\苏南分公司' + str(t[0]) + '年' + str(
                                                        m) + '月试井日报（SSOC WELLTEST DAILY REPORT OF ' + moneng + ')' + str(
                                                        t[1]) + "." + str(t[2]) + ".xls"
                                                    uipath = unicode(inpath, "utf8").encode('gbk')
                                                    dt = pd.read_excel(uipath, sheetname)




        ggs1_col_string = ''
        ggs1_data_string = ''
        ggs1_prod_comment = ''
        ggs2_col_string = ''
        ggs2_data_string = ''
        ggs2_prod_comment = ''
        ggs1_comments = dt.values[15, [4]][0]
        try:
            ggs2_comments = dt.values[30, [4]][0]
        except IndexError:
            ggs2_comments=''
        print 'this is dt',dt
        prod_date = "to_date(\'" + import_date + "\',\'yyyy-mm-dd\') "
        ggs1updatestr=OrderedDict()
        ggs2updatestr = OrderedDict()


        ggs1updatestr['GGS_NO']=str(1)
        ggs1updatestr['PRODUCTION_DATE'] =  prod_date
        ggs1updatestr['DAILY_PROD_GAS']= str(float(dt.ix[4, [32]] * 10))
        ggs1updatestr['LIQUID' ]= str(float(dt.ix[12, [7]]))
        ggs1updatestr['DAI_LIQ_GTP5_RECEIVED'] = str("")
        ggs1updatestr['WELL_NUMBER'] = str(float(dt.ix[12, [4]]))
        ggs1updatestr['WH_METHANOL'] = str(float(dt.ix[13, [10]]))
        ggs1updatestr['DAILY_FUEL_GAS'] = str(float(dt.ix[4, [35]] * 10))
        ggs1updatestr['GTP5_RECEIVED_GAS'] = str("")
        ggs1updatestr['GGS_DAI_HANDOVER_VOL'] = str(float(dt.ix[4, [34]] * 10))
        ggs1updatestr['GAS_EVACUATION'] = str(float(dt.ix[4, [36]] * 10))
        ggs1updatestr['FLOWLINE_FILLED_UP'] = str(0)
        ggs1updatestr['OPEN_WELL_COUNT'] = str(float(dt.ix[13, [4]]))
        ggs1updatestr['GGS_PROD_COMMENTS'] = ggs1_comments
        ggs1updatestr['STAB_CONDENSATE_T'] = str(float(dt.ix[13, [18]]))
        ggs1updatestr['HYDRO_CONDENSATE_T'] = str(float(dt.ix[14, [18]]))


        ggs2updatestr['GGS_NO'] = str(2)
        ggs2updatestr['PRODUCTION_DATE'] = prod_date
        ggs2updatestr['DAILY_PROD_GAS'] = str(float(dt.ix[19, [32]] * 10))
        ggs2updatestr['LIQUID'] = str(float(dt.ix[27, [7]]))
        ggs2updatestr['DAI_LIQ_GTP5_RECEIVED'] = str("")
        ggs2updatestr['WELL_NUMBER'] = str(float(dt.ix[27, [4]]))
        ggs2updatestr['WH_METHANOL'] = str(float(dt.ix[28, [10]]))
        ggs2updatestr['DAILY_FUEL_GAS'] = str(float(dt.ix[19, [35]] * 10))
        ggs2updatestr['GTP5_RECEIVED_GAS'] = str("")
        ggs2updatestr['GGS_DAI_HANDOVER_VOL'] = str(float(dt.ix[19, [34]] * 10))
        ggs2updatestr['GAS_EVACUATION'] = str(float(dt.ix[19, [36]] * 10))
        ggs2updatestr['FLOWLINE_FILLED_UP'] = str(0)
        ggs2updatestr['OPEN_WELL_COUNT'] = str(float(dt.ix[28, [4]]))
        ggs2updatestr['GGS_PROD_COMMENTS'] = ggs2_comments
        ggs2updatestr['STAB_CONDENSATE_T'] = str(float(dt.ix[28, [18]]))
        ggs2updatestr['HYDRO_CONDENSATE_T'] = str(float(dt.ix[29, [18]]))

        for x in ggs1updatestr.keys():
            if ggs1updatestr[x]=='' or ggs1updatestr[x] == None:
                ggs1updatestr[x]='Null'

        for x in ggs2updatestr.keys():
            if ggs2updatestr[x] == '' or ggs2updatestr[x] == None:
                ggs2updatestr[x] = 'Null'

        for x in ggs1updatestr['GGS_PROD_COMMENTS']:
            if x in string.printable:
                ggs1_prod_comment += x
        #ggs1updatestr['GGS_PROD_COMMENTS'] = '"'+ggs1_prod_comment+'"'
        ggs1updatestr['GGS_PROD_COMMENTS']='Null'
        for x in ggs2updatestr['GGS_PROD_COMMENTS']:
            if x in string.printable:
                ggs2_prod_comment += x
        #ggs2updatestr['GGS_PROD_COMMENTS'] = '"'+ggs2_prod_comment+'"'
        ggs2updatestr['GGS_PROD_COMMENTS'] ='Null'
        for key in ggs1updatestr.keys():
            ggs1_col_string += key + ','
            ggs1_data_string += ggs1updatestr[key] + ','

        for key in ggs2updatestr.keys():
            ggs2_col_string += key + ','
            ggs2_data_string += ggs2updatestr[key] + ','

        ggs_import_dict = {}
        ggs_import_dict['ggs1_col'] = ggs1_col_string
        ggs_import_dict['ggs1_data'] = ggs1_data_string
        ggs_import_dict['ggs2_col'] = ggs2_col_string
        ggs_import_dict['ggs2_data'] = ggs2_data_string



        return ggs_import_dict
