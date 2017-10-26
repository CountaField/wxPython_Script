import wx
import wx.aui
import wx.grid
from DailyProdPlot import PlotDrawing
from AuiFrameTemple import  AuiTemple
from Oracle_connection import Gsrdb_Conn
from TidyUpStackPlotprodDate import TidyUpStackPlotProdDate as tspd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx.lib.agw.customtreectrl as ct
import wx.lib.agw.aui as aui
from CanvasNavigationTool import add_toolbar
import matplotlib.dates as mdates
import matplotlib.dates as dates
from DailyProdTable import DailyProdTable
from collections import OrderedDict
import datetime
from PlotAttributeFrame import  ClusterOrderChange as coc
import time
from GridEdit import PyWXGridEditMixin
from CreateGrid import CreateGrid
from GridTable import MarkerTable
import numpy as np

class DashboardFrame(AuiTemple):
    def __init__(self,parent):
        AuiTemple.__init__(self,parent,'Dashboard Summary')
        self.parent=parent
        self.checked_list=[]
        self.grid_data={}
        self.table_dict={}
        self.row_count={}
        w, h = self.GetSize()

        plt_w = w * 0.65
        plt_h = h * 0.65
        if PyWXGridEditMixin not in wx.grid.Grid.__bases__:  # import copy paste cut etc. function from external module
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)  # put these action be attribute into original function of grid table
        self.nb=wx.aui.AuiNotebook(self)

        self.grid = wx.grid.Grid(self.nb, -1, size=(600, 600), style=wx.BORDER_SUNKEN)
        self.open_well_grid=wx.grid.Grid(self.nb, -1, size=(600, 600), style=wx.BORDER_SUNKEN)
        self.nb.AddPage(self.grid,'DashBoard Table')
        self.nb.AddPage(self.open_well_grid, 'Open Well Status')

        #self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Center().MinimizeButton(True).CloseButton(False))
        #self._mgr.AddPane(self.open_well_grid, aui.AuiPaneInfo().Bottom().MinimizeButton(True).CloseButton(False))
        self._mgr.AddPane(self.nb, aui.AuiPaneInfo().Center().MinimizeButton(True).CloseButton(False))
        print self.nb.GetPage(0)
        self._mgr.Update()
        self.MenuPane()


    def MenuPane(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        date_cur=db.Sql("select production_date from production_data group by production_date order by production_date desc")
        date_list=[]
        for day in date_cur.fetchall():
             date_list.append(day[0].strftime('%Y-%m-%d %H:%M:%S'))
        self.menu_dict=OrderedDict()
        dashboard_list=['Daily Dashboard','Open Well Status']
        self.menu_dict['Dash_type']=wx.StaticText(self._toolbar,-1,' Dashboard Choose:  ')
        self.menu_dict['dashboard_list'] = wx.ComboBox(self._toolbar, -1, choices=dashboard_list)
        self.menu_dict['Date_type'] = wx.StaticText(self._toolbar, -1, ' Select Date:  ')
        self.menu_dict['date_list']=wx.ComboBox(self._toolbar,-1,choices=date_list)
        self.menu_dict['confirm'] = wx.Button(self._toolbar, -1, 'Confirm')
        control_list=[]
        for key in self.menu_dict.keys():
            control_list.append(self.menu_dict[key])
        self.CustomAuiToolBar('Menu Bar',control_list)
        self.Bind(wx.EVT_BUTTON,self.OnConfirmClick,self.menu_dict['confirm'])
        self._mgr.Update()
        db.close()

    def PieChartDataExtract(self,query_date):
        w, h = self.GetSize()
        plt_w = w * 0.65
        plt_h = h * 0.65
        try:
            self._mgr.DetachPane(self.pie_canvas_panel)
            self.pie_canvas_panel.Destroy()
        except AttributeError:
            pass
        self.pie_canvas_panel=self.CustomPanel("Open Wells Situation Summary",size=(plt_w,plt_h))[0]
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        open_well_cur=db.Sql("select wellid,daily_prod_gas from PRODUCTION_DATA where "
                             " production_date=to_date('"+query_date+"','yyyy/mm/dd hh24:mi:ss') order by wellid")
        self.well_open_dict=OrderedDict()
        labels_key = ["Closed", "Qg<1", "1<Qg<3", "3<Qg<5", "5<Qg<10", "10<Qg<20", "20<Qg<30", "30<Qg<40", "40<Qg<50",
                 "50<Qg<80", "Qg>80"]
        grid_dict={}
        for id in labels_key:
            grid_dict[id]=[]

        labels=[]
        colors=[ 'gold','yellowgreen', 'lightskyblue', 'lightcoral', 'KHAKI', 'ORCHID', 'PALEGREEN', 'pink','cyan','PLUM','cadetblue']#'wheat','green','seagreen']
        #explode=np.zeros(len(labels),dtype=int)
        explode=[]


        for key in labels_key:
            self.well_open_dict[key]=0
        data_list=[]
        for prod_data in open_well_cur.fetchall():
            if prod_data[1]==0:
                self.well_open_dict['Closed']+=1
                grid_dict['Closed'].append(prod_data[0])
            elif prod_data[1]<1:
                self.well_open_dict['Qg<1'] += 1
                grid_dict['Qg<1'].append(prod_data[0])
            elif 1<prod_data[1]<3:
                self.well_open_dict['1<Qg<3'] += 1
                grid_dict['1<Qg<3'].append(prod_data[0])
            elif 3<prod_data[1]<5:
                self.well_open_dict['3<Qg<5'] += 1
                grid_dict['3<Qg<5'].append(prod_data[0])
            elif 5 < prod_data[1] < 10:
                self.well_open_dict['5<Qg<10'] += 1
                grid_dict['5<Qg<10'].append(prod_data[0])
            elif 10 < prod_data[1] < 20:
                self.well_open_dict['10<Qg<20'] += 1
                grid_dict['10<Qg<20'].append(prod_data[0])
            elif 20 < prod_data[1] < 30:
                self.well_open_dict['20<Qg<30'] += 1
                grid_dict['20<Qg<30'].append(prod_data[0])
            elif 30 < prod_data[1] < 40:
                self.well_open_dict['30<Qg<40'] += 1
                grid_dict['30<Qg<40'].append(prod_data[0])
            elif 40 < prod_data[1] < 50:
                self.well_open_dict['40<Qg<50'] += 1
                grid_dict['40<Qg<50'].append(prod_data[0])
            elif 50 < prod_data[1] < 80:
                self.well_open_dict['50<Qg<80'] += 1
                grid_dict['50<Qg<80'].append(prod_data[0])
            elif  prod_data[1] >80 :
                self.well_open_dict['Qg>80'] += 1
                grid_dict['Qg>80'].append(prod_data[0])
            print prod_data[1]

        for key in self.well_open_dict.keys():
            labels.append(key+':\n'+str(self.well_open_dict[key])+' Wells')
            explode.append(0)

        explode[0] = 0.26
        #explode[5] = 0.2
        explode[-1]=0.1

        for x in self.well_open_dict.keys():
            data_list.append(self.well_open_dict[x])
        total_wells=sum(data_list)
        open_wells=total_wells-self.well_open_dict['Closed']
        self.open_well_pie_plot=plt.figure()
        self.open_well_pie_axes=self.open_well_pie_plot.gca()
        self.open_well_pie_axes.set_title(query_date.split(' ')[0]+" Open Wells "
                                                                   "Plot\n"+"Total Wells: "+str(total_wells)+"      Open Wells: "+str(open_wells)+"\n")
        self.open_well_pie_axes.pie(data_list,explode=explode,labels=labels,autopct='%1.1f%%',pctdistance=0.8,colors=colors,shadow=True,startangle=30)#autopct='%1.1f%%'
        plt.axis('equal')
        self.OpenWellsGrid(labels_key,grid_dict,max(data_list))

        canvas=FigureCanvas(self.pie_canvas_panel,wx.NewId(),self.open_well_pie_plot)
        self.CustomLayout(self.pie_canvas_panel,'left')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, flag=wx.GROW)
        self.pie_canvas_panel.SetSizer(sizer)
        self._mgr.Update()
        db.close()


    def OpenWellsGrid(self,label,data_dict,row_count):
        result_data={}
        self.nb.DeletePage(1)
        for row in range(row_count):

            for col in range(len(label)):

                try:
                    result_data[(row,col)]=data_dict[label[col]][row]
                except IndexError:
                    result_data[(row, col)]=''

        self.open_wells_table=MarkerTable(data=result_data,col_label=label,row_count=row_count)
        self.open_well_grid=wx.grid.Grid(self, -1, size=(600, 600), style=wx.BORDER_SUNKEN)
        self.open_well_grid.__init_mixin__()
        self.open_well_grid.SetTable(self.open_wells_table,True)
        self.open_well_grid.EnableDragColMove()
        self.open_well_grid.EnableDragGridSize()
        self.open_well_grid.EnableGridLines()
        self.open_well_grid.AutoSize()
        self.Refresh()
        self.nb.InsertPage(1, self.open_well_grid, 'Open Well Status', select=True)
        self._mgr.Update()


    def DashBoardDataExtract(self, query_date):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        dashboard_cur =db.Sql("SELECT WELL_HEADER.WELLID,PRODUCTION_DATA.DAILY_PROD_GAS,WELL_HEADER.PRODUCTION_START_DATE,"
                              "WELL_HEADER.GGS, WELL_HEADER.CLUSTERID, VW_ALLOCATION_DHC_last.DHC_TYPE, "
               "VW_ALLOCATION_DHC_last.DHC_SET_DATE, VW_ALLOCATION_DHC_last.DHC_INITIAL_DIAM, PRODUCTION_DATA.PRODUCTION_DATE, PRODUCTION_DATA.PROD_TIME, "
               "PRODUCTION_DATA.PROD_CUM_GAS, PRODUCTION_DATA.WELL_HEAD_PRESSURE, PRODUCTION_DATA.WELL_HEAD_TEMPERATURE "
               "FROM (WELL_HEADER INNER JOIN PRODUCTION_DATA ON WELL_HEADER.WELLID =  PRODUCTION_DATA.WELLID) INNER JOIN VW_ALLOCATION_DHC_LAST ON WELL_HEADER.WELLID =  VW_ALLOCATION_DHC_LAST.WELLID "
               "WHERE PRODUCTION_DATA.PRODUCTION_DATE = to_date('" + query_date + "' ,'yyyy/mm/dd hh24:mi:ss')")

        self.dashboard_col_list=["WELLID","DAILY_PROD_GAS","PRODUCTION_START_DATE","GGS", "CLUSTERID",  "DHC_TYPE",
            "DHC_SET_DATE","DHC_INITIAL_DIAM", "PRODUCTION_DATE", "PROD_TIME",
            "PROD_CUM_GAS", "WELL_HEAD_PRESSURE", "WELL_HEAD_TEMPERATURE"]
        if query_date in self.grid_data.keys():
            pass
        else:
            self.grid_data[query_date],self.row_count[query_date]=CreateGrid(self.dashboard_col_list,dashboard_cur,'WELLID').ReturnDictionary()
        print len(self.grid_data[query_date])
        db.close()

    def DashboardDataPorcess(self,query_date):
        attr = wx.grid.GridCellAttr()
        attr_2012_prod=wx.grid.GridCellAttr()
        col=1
        attr.SetBackgroundColour("red")
        for row in range(len(self.grid_data[query_date])/len(self.dashboard_col_list)):
            if self.grid.GetCellValue(row,col)!='':
                try:
                    if float(self.grid.GetCellValue(row,col))==0:
                        self.grid.SetAttr(row,col,attr)
                except:
                    pass


    def DashboardShow(self,date_checked):
        #self._mgr.DetachPane(self.grid)
        self.nb.DeletePage(0)
        self.DashBoardDataExtract(date_checked)

        self.table_dict[date_checked] = MarkerTable(data=self.grid_data[date_checked],
                                                    col_label=self.dashboard_col_list,
                                                   row_count=self.row_count[date_checked])

        self.grid = wx.grid.Grid(self, -1, size=(600, 600), style=wx.BORDER_SUNKEN)
        self.grid.__init_mixin__()
        self.grid.SetTable(self.table_dict[date_checked], True)
        self.grid.EnableDragColMove()
        self.grid.EnableDragGridSize()
        self.grid.EnableGridLines()
        self.grid.AutoSize()
        self.DashboardDataPorcess(date_checked)
        self.Refresh()
        self.nb.InsertPage(0,self.grid, 'DashBoard Table',select=True)
        #self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Caption(date_checked.split(' ')[0]+' Dashboard').Center().MinimizeButton(True).CloseButton(False))
        self._mgr.Update()


    def OnConfirmClick(self,event):
        date_checked = self.menu_dict['date_list'].GetStringSelection()
        if self.menu_dict['dashboard_list'].GetStringSelection()=='Open Well Status':
            self.PieChartDataExtract(date_checked)
        elif self.menu_dict['dashboard_list'].GetStringSelection()=='Daily Dashboard':
            self.DashboardShow(date_checked)









