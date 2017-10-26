import wx
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
from PolygonPlot3D import PolygonPlot3D as pp3
import matplotlib.dates as dates
from DailyProdTable import DailyProdTable
from collections import OrderedDict
from BarPlot import BarPlot
from PlotClickTest import PlotClick
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_wx import  NavigationToolbar2Wx,wxc
from matplotlib.widgets import MultiCursor
import datetime
import pandas as pd
import time
import numpy as np
from mpldatacursor import datacursor

class GGSFrame(AuiTemple,tspd,pp3):
    def __init__(self,parent):
        AuiTemple.__init__(self,parent)
        tspd.__init__(self, '')
        #self.GGSTreeList()
        self.parent=parent
        self.extract_ggs1_data=self.extractDailyData(1)
        self.extract_ggs2_data = self.extractDailyData(2)
        self.text3 = wx.TextCtrl(self, -1, "Main content window",
                                 wx.DefaultPosition, wx.Size(200, 150),
                                 wx.NO_BORDER | wx.TE_MULTILINE)
        self._mgr.AddPane(self.text3, aui.AuiPaneInfo().CenterPane())
        self._mgr.Update()
        self.MenuPane()
        self.bar_plot_dict={}
        self.checked_dict_5min={}
        self.checked_dict_daily={}
        self.checked_list=[]
        self.prod_5min_list=[]
        self.text3_exist=True
        self.prod_daily_list=[]
        self.plot_5min_exist=False
        self.daily_plot_exist=False
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_MAXIMIZE,self.OnMaximize,self)

    def GGSTreeList(self):
        ggs_tree_list=['GTP5','GGS1','GGS2']
        parent_panel = self.CustomPanel('GGS Tree List', (150, 700))[0]
        self.ggs_tree_list = ct.CustomTreeCtrl(parent_panel, size=parent_panel.GetSize(), agwStyle=wx.TR_DEFAULT_STYLE)
        tree_root = self.ggs_tree_list.AddRoot("South Sulige Field")
        self.ggs_tree_list.SetBackgroundColour('white')
        self.ggs_dict = {}
        for id in ggs_tree_list:
            self.ggs_dict[id] = self.ggs_tree_list.AppendItem(tree_root, id, ct_type=1)

        self.CustomLayout(parent_panel, 'left')
        self._mgr.Update()

    def MenuPane(self):


        self.TreeListQuery_button = wx.Button(self._toolbar, -1, 'Field Summary Plot')
        prod_5min_hist_button = wx.Button(self._toolbar, -1, '5 minutes Prod Data')

        control_list = []

        control_list.append(self.TreeListQuery_button)
        control_list.append(prod_5min_hist_button)

        FrameDisplay = self.CustomAuiToolBar('Menu Bar', control_list)
        self._mgr.Update()
        self.Bind(wx.EVT_BUTTON,self.On5minPlotClick,prod_5min_hist_button)
        self.Bind(wx.EVT_BUTTON,self.OnStackPlotClick,self.TreeListQuery_button)

    def OnRestoreButton(self,event):
        print 'restore window....'
        self.Restore()

    def extract5mindata(self,flag):

        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        now_date=datetime.datetime.now()
        min_date=now_date-datetime.timedelta(days=30)
        extrac_data_cur = db.Sql("select * from GGS_GTP5_5MIN_PROD_TABLE where"
                                 " Flag ='" + flag + "' and production_date between to_date('" + str(min_date).split('.')[0] + "','yyyy/mm/dd hh24:mi:ss') and to_date('" + str(now_date).split('.')[0] + "','yyyy/mm/dd hh24:mi:ss') order by production_date")
        flag_list = []
        proddate_list = []
        prodrate_list = []
        for id in extrac_data_cur.fetchall():
            flag_list.append(id[0])
            proddate_list.append(id[1])
            if id[2] == None:
                prodrate_list.append(0)
            else:
                prodrate_list.append(id[2])
        db.close()
        return proddate_list, prodrate_list

    def extractDailyData(self,flag):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        extrac_data_cur = db.Sql(
            "select GGS_NO,DAILY_PROD_GAS,PRODUCTION_DATE,WH_METHANOL,LIQUID,OPEN_WELL_COUNT,WELL_NUMBER from GGS where GGS_NO=" + str(
                flag) + "ORDER BY PRODUCTION_DATE,GGS_NO")
        flag_list = []
        proddate_list = []
        prodrate_list = []
        methanol_inject = []
        liquid = []
        open_well = []
        total_well_number = []
        for id in extrac_data_cur.fetchall():
            flag_list.append(id[0])
            proddate_list.append(id[2])
            prodrate_list.append(id[1])
            methanol_inject.append(id[3])
            liquid.append(id[4])
            open_well.append(id[5])
            total_well_number.append(id[6])
        db.close()
        return proddate_list, prodrate_list, methanol_inject, liquid, open_well, total_well_number

    def AnnotateDraw(self,ax,x,y,text,color,size,x_offset=-80,y_offset=30,arrow=False):
        if arrow==False:
            atext=ax.annotate(text, xy=(x, y), xycoords='data',xytext=(x_offset, y_offset),
                         textcoords='offset points'
                        )
        else:
            atext = ax.annotate(text, xy=(x, y), xycoords='data', xytext=(x_offset, y_offset),
                                textcoords='offset points',
                                arrowprops=dict(arrowstyle="->",color=color,
                                                connectionstyle="arc3,rad=.2")
                                )
        atext.set_style('oblique')
        atext.set_weight('extra bold')
        atext.set_size(int(size))
        atext.set_color(color)

    def DailyGGSplot(self):

        canvas_panel = self.CustomPanel("Field Summary Plot")[0]
        canvas_panel_ggs=self.CustomPanel("GGS Summary Plot")[0]
        ggs1date, ggs1_gas_rate =self.extract_ggs1_data[0],self.extract_ggs1_data[1]
        ggs2date, ggs2_gas_rate = self.extract_ggs2_data[0],self.extract_ggs2_data[1]
        annual_date_list,annual_rate_dict,self.annual_cum_rate_dict=self.ProdDataByProdStartDate()


        ggs = self.DailyGGSall()

        summary_list=ggs['Date'][:]
        '''axes initializing'''
        self.summary_plot=plt.figure()
        self.ggs_plot=plt.figure()
        self.summary_axes=self.summary_plot.add_subplot(311)
        self.summary_axes.set_ylabel('Daily Production Km3/d\nCumulative Production MMm3/d',size=10)
        self.ggs_stackplot_axes=self.summary_plot.add_subplot(312)
        self.ggs_stackplot_axes.set_ylabel('Km3/d',size=20)
        self.ggs_annual_axes=self.summary_plot.add_subplot(313)
        self.ggs_annual_axes.set_ylabel('Km3/d',size=20)
        self.ggs1_plot_axes=self.ggs_plot.add_subplot(121)
        self.ggs1_plot_axes.set_ylabel('Km3/d',size=20)
        self.ggs2_plot_axes=self.ggs_plot.add_subplot(122)

        self.ggs2_plot_axes.set_ylabel('Km3/d', size=20)
        x_max=[]
        x_max.append(datetime.datetime(year=2013,month=1,day=1))
        x_min=datetime.datetime(year=2012,month=1,day=1)


        '''Plot Creating'''
        self.ggs1_plot_sec_axes=self.ggs1_plot_axes.twinx()
        self.ggs2_plot_sec_axes = self.ggs2_plot_axes.twinx()
        self.ggs_stackplot=self.ggs_stackplot_axes.stackplot(ggs['Date'][:],ggs['GGS1'],ggs['GGS2'],colors=['skyblue','pink'],alpha=0.9)
        self.ggs1_plot_line=self.ggs1_plot_axes.plot(summary_list,ggs['GGS1'],color='black',linewidth=2,label='GGS1 Production Gas')
        self.ggs1_plot_methanol_line=self.ggs1_plot_sec_axes.plot(summary_list,ggs['GGS1_Methanol_Injection'],color='orange',linewidth=2,label='GGS1 Methanol')
        self.ggs2_plot_line = self.ggs2_plot_axes.plot(summary_list, ggs['GGS2'],color='black',linewidth=2,label='GGS2 Produftion Gas')
        self.ggs2_plot_methanol_line=self.ggs2_plot_sec_axes.plot(summary_list,ggs['GGS2_Methanol_Injection'],color='orange',linewidth=2,label='GGS2 Methanol')
        self.summary_plot_line = {}
        year_list = []
        min_year = 2012
        cur_year = time.localtime().tm_year
        color_list = ['DARKTURQUOISE', 'green', 'blue', 'grey', 'orange', 'yellow', 'pink', 'skyblue', 'maroon']
        i = 0
        self.summary_sec_axes=self.summary_axes.twinx()
        self.summary_sec_axes.set_ylabel('Producing Wells Count',size=14)
        self.summary_plot_line['GTP5'], = self.summary_axes.plot(ggs['Date'], ggs['GTP5'],label='Daily Production Gas',linewidth=2, marker='o',color='greenyellow')
        self.summary_plot_line['Cum'],=self.summary_axes.plot(ggs['Date'],ggs['Cum_Gas_Prod'],linewidth=3,color='MAROON',label='Cumlative Production')
        self.summary_plot_line['Open_Well'],=self.summary_sec_axes.plot(ggs['Date'], ggs['Open_Well_Count'], label='Open Wells Number',linewidth=2,color='VIOLET')
        self.summary_plot_line['Total_Well'], = self.summary_sec_axes.plot(ggs['Date'], ggs['Total_Well_Count'],label='Total Wells Number', linewidth=2,color='PURPLE')

        '''Annual Prod Plot'''
        currentyear=time.localtime()
        year_list=range(2012,currentyear.tm_year+1,1)
        year_data_list=str()
        for z in year_list:
            year_data_list+='annual_rate_dict['+str(z)+'],'
        well_list = []
        ggs_color_dict={}
        for id in ['GGS1','GGS2']:
            ggs_color_dict[id] = plt.Rectangle((0, i), 1, 1, angle=90.0, fc=color_list[i], alpha=0.7)
            well_list.append(ggs_color_dict[id])
        #ggs_stack_legend=self.ggs_stackplot_axes.legend(well_list,ggs_color_dict.keys(),loc='upper center',ncol=9,fontsize=10)
        colors = "'ORANGERED','green','blue','ORCHID','orange','yellow','pink','skyblue','maroon','cyan','brown','cadetblue','gold','wheat','violet','seagreen'"

        color_list = ['ORANGERED', 'green', 'blue', 'ORCHID', 'orange', 'yellow', 'pink', 'skyblue', 'maroon', 'cyan', 'brown',
                      'cadetblue', 'gold', 'wheat', 'violet', 'seagreen']

        exec('self.ggs_annual_stack=self.ggs_annual_axes.stackplot(annual_date_list,'+year_data_list[:-1]+',colors=['+colors+'],alpha=0.70)')

        anno_ggs_annual_y_max=self.ggs_annual_axes.get_ylim()[1]
        anno_ggs_annual_x_min=annual_date_list[int(len(annual_date_list)*0.1)]
        color_dict = OrderedDict()
        i = 0
        z=0.8
        well_list=[]
        for id in year_list:
            color_dict[id] = plt.Rectangle((0, i), 1, 1, angle=90.0, fc=color_list[i],alpha=0.7)
            well_list.append(color_dict[id])

            i+=1
            '''self.AnnotateDraw(self.ggs_annual_axes,anno_ggs_annual_x_min,anno_ggs_annual_y_max*z,
                              str(annual_rate_dict['wells_'+str(id)])+' Wells Started Produce in '+str(id),
                              color='black',size=12)'''
            z-=0.1
        ggs_annual_legend=self.ggs_annual_axes.legend(well_list,color_dict.keys(),loc='upper center',ncol=9,fontsize=10)
        ggs_annual_legend.draggable(state=True)
        i=0
        for x in range(min_year, cur_year + 1):
            year_list.append(x)
            #print(x)
            excute_string = 'ggs_' + str(x) + "=self.DailyGGSyear(\'" + str(x) + "\')"
            exec (excute_string)
            excute_string_plot = "self.summary_plot_line['GTP5_" + str(
                x) + "']=self.summary_axes.fill_between(ggs_" + str(x) + "['Date'],0,ggs_" + str(
                x) + "['GTP5'],facecolor='" + color_list[i] + "',linestyle='dashed')"
            exec (excute_string_plot)
            excute_ggs1_plot="self.summary_plot_line['GGS1_" + str(
                x) + "']=self.ggs1_plot_axes.fill_between(ggs_" + str(x) + "['Date'],0,ggs_" + str(
                x) + "['GGS1'],facecolor='white',linestyle='dashed',color='red')"
            exec (excute_ggs1_plot)
            if x!=2012:
                excute_ggs2_plot = "self.summary_plot_line['GGS2_" + str(
                    x) + "']=self.ggs2_plot_axes.fill_between(ggs_" + str(x) + "['Date'],0,ggs_" + str(
                    x) + "['GGS2'],facecolor='white',linestyle='dashed',color='red')"
                exec (excute_ggs2_plot)
                anno_ggs2_string = "self.AnnotateDraw(self.ggs2_plot_axes,ggs_" + str(x) + "['Date'][-1],0," + str(
                    x) + ",color='blue',size=10,x_offset=-20)"
                exec (anno_ggs2_string)
            else:
                pass

            if x==2016:
                anno_cum_data_string = "self.AnnotateDraw(self.summary_axes,ggs_" + str(x) + \
                                       "['Date'][-1],0,'prod cumulative: '+str(round(self.CumProdYear('" + str(
                    x) + "','GTP5'),2))+'\\n',x_offset=-100,color='black',size=10)"
                anno_string = "self.AnnotateDraw(self.summary_axes,ggs_" + str(x) + \
                              "['Date'][-1],0,'" + str(x) + "\\n',color='black',size=25)"
            elif x == 2017:
                anno_cum_data_string = "self.AnnotateDraw(self.summary_axes,ggs_" + str(x) + \
                                       "['Date'][-1],0,'prod cumulative: '+str(round(self.CumProdYear('" + str(
                    x) + "','GTP5'),2))+'\\n',x_offset=-150,y_offset=100,color='blue',size=10)"
                anno_string = "self.AnnotateDraw(self.summary_axes,ggs_" + str(x) + \
                              "['Date'][-1],0,'" + str(x) + "\\n',y_offset=100,color='blue',size=25)"
            else:
                anno_string = "self.AnnotateDraw(self.summary_axes,ggs_" + str(x) + \
                              "['Date'][-1],0,'" + str(x) + "\\n',color='white',size=25)"
                anno_cum_data_string="self.AnnotateDraw(self.summary_axes,ggs_" + str(x)+\
                                     "['Date'][-1],0,'prod cumulative: '+str(round(self.CumProdYear('"+str(x)+"','GTP5'),2))+'\\n',x_offset=-100,color='white',size=10)"

            #print anno_string2
            anno_ggs1_string = "self.AnnotateDraw(self.ggs1_plot_axes,ggs_" + str(x) + "['Date'][-1],0," + str(
                x) + ",color='red',size=10,x_offset=-20)"

            cum_anno=self.AnnotateDraw(self.summary_axes,ggs['Date'][-1],ggs['Cum_Gas_Prod'][-1],'prod cumulative: '+str(round(ggs['Cum_Gas_Prod'][-1]))+' Mm3 ',
                              color='black',x_offset=-200,y_offset=+10,size=18,arrow=True)
            self.AnnotateDraw(self.summary_axes, ggs['Date'][-1], ggs['Cum_Gas_Prod'][-1],
                              'Update To: '+str(ggs['Date'][-1]), color='black',
                              x_offset=-1000, y_offset=20, size=12, arrow=False)
            exec(anno_string)
            exec(anno_cum_data_string)
            exec(anno_ggs1_string)
            i += 1


        '''Atribute Setting'''
        self.summary_axes.set_title('Field Summary Plot')
        self.summary_axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        self.ggs_stackplot_axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        self.ggs_annual_axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        self.ggs1_plot_axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        self.ggs1_plot_axes.set_title('Daily Production of GGS1,km3/d')
        self.ggs2_plot_axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        self.ggs2_plot_axes.set_title('Daily Production of GGS2,km3/d')
        '''self.summary_legend_1=self.summary_axes.legend(loc='upper left',framealpha=98.9,fontsize=10)
        self.summary_legend_2=self.summary_sec_axes.legend(loc='upper right',framealpha=98.9,fontsize=10)
        self.summary_legend_1.draggable(state=True)
        self.summary_legend_2.draggable(state=True)'''
        for tick in self.summary_axes.get_xticklabels():
            tick.set_rotation(30)
        for tick in self.ggs_stackplot_axes.get_xticklabels():
            tick.set_rotation(30)
        for tick in self.ggs_stackplot_axes.get_xticklabels():
            tick.set_rotation(30)
        for tick in self.ggs1_plot_axes.get_xticklabels():
            tick.set_rotation(30)
        for tick in self.ggs2_plot_axes.get_xticklabels():
            tick.set_rotation(30)
        for tick in self.ggs_annual_axes.get_xticklabels():
            tick.set_rotation(30)
        canvas = FigureCanvas(canvas_panel, wx.NewId(), self.summary_plot)
        canvas_ggs=FigureCanvas(canvas_panel_ggs,wx.NewId(),self.ggs_plot)
        self.summary_canvas=canvas
        self.summary_legend_1 = self.summary_axes.legend(loc='upper left', framealpha=98.9, fontsize=10)
        self.summary_legend_2 = self.summary_sec_axes.legend(loc='upper right', framealpha=98.9, fontsize=10)
        self.summary_legend_1.draggable(state=True)
        self.summary_legend_2.draggable(state=True)
        #datacursor()
        toolbar = self.add_toolbar(canvas)
        ggs_toolbar=self.add_toolbar(canvas_ggs)
        self.CustomLayout(canvas_panel,'Center')
        self.CustomLayout(canvas_panel_ggs, 'Center')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, flag=wx.GROW)
        sizer.Add(toolbar,0,wx.BOTTOM)
        canvas_panel.SetSizer(sizer)
        sizer_ggs = wx.BoxSizer(wx.VERTICAL)
        sizer_ggs.Add(canvas_ggs, 1, flag=wx.GROW)
        sizer_ggs.Add(ggs_toolbar, 0, wx.BOTTOM)
        canvas_panel_ggs.SetSizer(sizer_ggs)
        ggs_annual_legend = self.ggs_annual_axes.legend(well_list, color_dict.keys(), loc='upper center', ncol=9,
                                                        fontsize=10)
        ggs_annual_legend.draggable(state=True)
        self.AnnualProdStatisticPlot(annual_rate_dict,self.annual_cum_rate_dict)
        self._mgr.Update()

    def AnnualProdStatisticPlot(self,open_well_dict,prod_data_dict):

        year_data_list=[]
        height_list=[]
        open_wells_list=[]
        canvas_panel = self.CustomPanel("Annual Statistic Plot",size=(400,800))[0]
        self.annual_statistic_plot=plt.figure()
        self.annual_statistic_axes=self.annual_statistic_plot.add_subplot(111)
        self.annual_statistic_sec_axes=self.annual_statistic_axes.twiny()
        self.annual_statistic_axes.set_title('Cumulative Production \nby Annual Well Connect\n')
        min_year = 2012
        cur_year = time.localtime().tm_year
        year_list=np.arange(min_year,cur_year+1)
        y_tick_list=['']
        for year in year_list:
            year_data_list.append(prod_data_dict[year][-1]/1000)
            height_list.append(0.1)
            y_tick_list.append(str(year))
            open_wells_list.append(open_well_dict['wells_'+str(year)])

        y_data=np.arange(len(year_list))

        self.annual_statistic_axes.barh(y_data,year_data_list,height=height_list,align='center',alpha=0.9,linewidth=2,color='red')
        self.annual_statistic_sec_axes.plot(open_wells_list,y_data,color='blue',marker='o',linewidth=2,linestyle='dotted',
                                            markeredgecolor='black',markerfacecolor='green',
                                            markeredgewidth=2)
        self.annual_statistic_axes.set_yticklabels(y_tick_list)
        for tick in self.annual_statistic_axes.get_xticklabels():
            tick.set_rotation(30)
        self.annual_statistic_axes.set_xlabel('\nMm3')
        i=0
        for year in year_list:
            self.AnnotateDraw(self.annual_statistic_axes,year_data_list[i],i,"cum prod:\n"+str(year_data_list[i])+" Mm3",
                              color='black',size=12,x_offset=-30,y_offset=20,arrow=True)
            self.AnnotateDraw(self.annual_statistic_sec_axes, open_wells_list[i], i,
                              ' connected \n'+str(open_wells_list[i])+' wells',
                              color='green', size=12, x_offset=-30, y_offset=-30, arrow=True)
            i+=1

        canvas = FigureCanvas(canvas_panel, wx.NewId(), self.annual_statistic_plot)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, flag=wx.GROW)
        canvas_panel.SetSizer(sizer)
        self.CustomLayout(canvas_panel, 'left')

    def ProdDataByProdStartDate(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        prod_date_list=[]
        compare_length=0

        prod_year_data_dict={}
        for year in range(2012,time.localtime().tm_year+1):
            compare_list = []
            exec("prod_"+str(year)+"_list=[]")
            prod_extract_string = "prod_start_"+str(year)+"_cur=db.Sql(\'select production_date,sum(daily_prod_gas) " \
                                                          "from production_data where wellid in (select wellid from well_header " \
                                                          "where production_start_date between " \
                                                          "to_date(\\'"+str(year)+"/01/01\\',\\'yyyy/mm/dd\\') and to_date (\\'"+str(year)+"/12/31\\',\\'yyyy/mm/dd\\'))" \
                                                                                                                                 " group by production_date " \
                                                                                                                                   " order by production_date\')"
            print 'thi is prod string',prod_extract_string
            exec(prod_extract_string)
            if year==2012:
                prod_year_data_dict[2012]=[]
                excute_2012_cur_string="for id in prod_start_2012_cur:\n " \
                                       "    prod_year_data_dict[2012].append(id[1])\n " \
                                       "    prod_date_list.append(id[0])"

                exec(excute_2012_cur_string)
            else:
                prod_year_data_dict[year]=[]
                excute_other_cur_string="for id in prod_start_"+str(year)+"_cur:\n  prod_year_data_dict["+str(year)+"].append(id[1])"
                exec(excute_other_cur_string)
                exec("compare_length=len(prod_date_list)-len(prod_year_data_dict["+str(year)+"])")
                for x in range(1,compare_length+1):
                    compare_list.append(0)
                exec("prod_year_data_dict["+str(year)+"]=compare_list+prod_year_data_dict["+str(year)+"]")
            year_wells_cur=db.Sql("select count(*) from well_header where production_start_date between to_date('"+str(year)+"/01/01','yyyy/mm/dd') and "
                                                                                      " to_date('"+str(year)+"/12/31','yyyy/mm/dd')")

            for x in year_wells_cur.fetchall():
                prod_year_data_dict['wells_' + str(year)]=x[0]


        prod_year_cum_data_dict={}

        length=len(prod_date_list)
        for x in prod_year_data_dict.keys():
            if isinstance(x, int):
                prod_year_cum_data_dict[x]=np.empty(shape=(length,))
                prod_year_cum_data_dict[x][0]=prod_year_data_dict[x][0]


        for x in prod_year_data_dict.keys():
            i=0
            if isinstance(x,int):
                for y in range(0,len(prod_date_list)-1):

                    last_data=prod_year_cum_data_dict[x][i]
                    next_data=prod_year_data_dict[x][i+1]
                    prod_year_cum_data_dict[x][i+1]=last_data+next_data
                    i+=1
        db.close()


        return prod_date_list,prod_year_data_dict,prod_year_cum_data_dict

    def DailyGGSall(self):
        # year: string
        ggs1date, ggs1_gas_rate, methanol_inject_1, liquid_1, open_well_1, total_well_number_1 = self.extract_ggs1_data
        ggs2date, ggs2_gas_rate, methanol_inject_2, liquid_2, open_well_2, total_well_number_2 = self.extract_ggs2_data
        lendate = len(ggs1date)
        # dateplt=[str(ggs1date[x]) for x in range(lendate)]

        gtp5_gas_rate = [ggs1_gas_rate[x] + ggs2_gas_rate[x] for x in range(lendate)]
        ggs1_gas_rate = [ggs1_gas_rate[x] for x in range(lendate)]
        ggs2_gas_rate = [ggs2_gas_rate[x] for x in range(lendate)]

        cum_gas_prod = [gtp5_gas_rate[0]/1000]
        for i in range(1, lendate):
            cum = cum_gas_prod[i - 1] + gtp5_gas_rate[i]/1000
            cum_gas_prod.append(cum)

        openwell=[int(open_well_1[x]+open_well_2[x]) for x in range(lendate)]
        totalwell=[int(total_well_number_1[x]+total_well_number_2[x]) for x in range(lendate)]

        ggs = {'Date': ggs1date,
               'GGS1': ggs1_gas_rate,
               'GGS2': ggs2_gas_rate,
               'GTP5': gtp5_gas_rate,
               'GGS1_Methanol_Injection': methanol_inject_1,
               'GGS2_Methanol_Injection': methanol_inject_2,
               'GGS1_Open_Well': open_well_1,
               'GGS2_Open_Well': open_well_2,
               'GGS1_Total_Well': total_well_number_1,
               'GGS2_Total_Well': total_well_number_2,
               'GGS1_Liquid': liquid_1,
               'GGS2_Liquid': liquid_2,
               'Cum_Gas_Prod': cum_gas_prod,
               'Open_Well_Count':openwell,
               'Total_Well_Count':totalwell}
        return ggs

    def DailyGGSyear(self,year):
        # year: string

        ggs1date, ggs1_gas_rate = self.extract_ggs1_data[0],self.extract_ggs1_data[1]
        ggs2date, ggs2_gas_rate = self.extract_ggs2_data[0],self.extract_ggs2_data[1]
        lendate = len(ggs1date)
        dateplt = [str(ggs1date[x]) for x in range(lendate)]

        yearlist = [dateplt[x].split(' ')[0].split('-')[0] for x in range(lendate)]

        ggs_df = pd.DataFrame([yearlist, ggs1date, ggs1_gas_rate, ggs2_gas_rate],
                              index=['Year', 'DATE', 'GGS1', 'GGS2']).transpose()
        ggs_df['GTP5'] = ggs_df['GGS1'] + ggs_df['GGS2']

        # get annual data
        ggs_year = ggs_df.loc[ggs_df.Year == year]
        length = ggs_year.index.size

        ggs_year = {'Date': [ggs_year.DATE.values[x] for x in range(length)],
                    'GGS1': [ggs_year['GGS1'].values[x] for x in range(length)],
                    'GGS2': [ggs_year['GGS2'].values[x] for x in range(length)],
                    'GTP5': [ggs_year['GTP5'].values[x] for x in range(length)]}
        return ggs_year

    def CumProdYear(self,year, location):  # location='GGS1','GGS2',GTP5' represent ggs1 and 2
        if location == 'GGS1':
            idnum = 1
        elif location == 'GGS2':
            idnum = 2
        elif location == 'GTP5':
            idnum = 3
        else:

            return

        if idnum == 1 or idnum == 2:
            ggsdate, ggsrate = self.extractdata(idnum)[0],self.extractdata(idnum)[1]
            lendate = len(ggsrate)
            dateplt = [str(ggsdate[x]) for x in range(lendate)]
            yearlist = [dateplt[x].split(' ')[0].split('-')[0] for x in range(lendate)]
            ggs_df = pd.DataFrame([yearlist, ggsdate, ggsrate], index=['Year', 'DATE', location]).transpose()
            ggs_year = ggs_df.loc[ggs_df.Year == year]
            cumprod = ggs_year[[2]].sum()
            return cumprod.values[0] / 1000

        else:
            ggs1date, ggs1rate =self.extract_ggs1_data[0],self.extract_ggs1_data[1]
            ggs2date, ggs2rate = self.extract_ggs2_data[0],self.extract_ggs2_data[1]
            lendate = len(ggs1rate)
            dateplt = [str(ggs1date[x]) for x in range(lendate)]
            yearlist = [dateplt[x].split(' ')[0].split('-')[0] for x in range(lendate)]
            ggs_df = pd.DataFrame([yearlist, ggs1date, ggs1rate, ggs2rate],
                                  index=['Year', 'DATE', 'GGS1', 'GGS2']).transpose()
            ggs_df['GTP5'] = ggs_df['GGS1'] + ggs_df['GGS2']
            ggs_year = ggs_df.loc[ggs_df.Year == year]
            cumprod = ggs_year[[4]].sum()
            return cumprod.values[0] / 1000  # million m3

    def GGS5minPlot(self,ggs_list=['GGS1','GGS2','GTP5']):
        ggs_in_list=[]
        color_list=[]
        ggs_string=''
        y_data_dict={}
        x_date_dict={}
        for ggs in ggs_list:
            if ggs=='GGS1':
                ggs_in_list.append('SN_C1')
                color_list.append('blue')
            elif ggs=='GGS2':
                ggs_in_list.append('SN_C2')
                color_list.append('red')
            elif ggs=='GTP5':
                ggs_in_list.append('WC_4L')
                ggs_in_list.append('WC_3L')
                ggs_in_list.append('WC_2L')
                ggs_in_list.append('WC_1L')
                color_list.append('yellow')
            ggs_string+=ggs+','[:-1]
        canvas_panel = self.CustomPanel("GGS1 and GGS2 5min Data Plot")[0]
        canvas_gtp5_panel=self.CustomPanel("GTP5 5min Data Plot")[0]
        prod_5min_colors=''

        for x in color_list:
            prod_5min_colors+='\''+x+'\','


        max_len_list=[]

        for id in ggs_in_list:
            x_date_dict[id]=[]
            y_data_dict[id]=[]
            x_date_dict[id],y_data_dict[id]=self.extract5mindata(id)
            max_len_list.append(len(y_data_dict[id]))

        max_len=max(max_len_list)

        del max_len_list

        for id in ggs_in_list:
            if len(y_data_dict[id])!=0:
                print id,len(y_data_dict[id])
                len_diff_list=[]
                diff_range=max_len-len(y_data_dict[id])
                for x in range(diff_range):
                    len_diff_list.append(0)
                y_data_dict[id]=np.array(len_diff_list+y_data_dict[id])

        '''print len(y_data_dict['WC_4L']),len(y_data_dict['WC_1L'])
        wc1l_len_diff=len(y_data_dict['WC_4L'])-len(y_data_dict['WC_1L'])
        wc1l_len_fill_list=[]
        for x in range(wc1l_len_diff):
            wc1l_len_fill_list.append(0)
        y_data_dict['WC_1L']=wc1l_len_fill_list+y_data_dict['WC_1L']
        print len(y_data_dict['WC_4L']), len(y_data_dict['WC_1L'])'''

        ssoc_supply = (y_data_dict['SN_C1'][-1]+y_data_dict['SN_C2'][-1])
        final_gtp5_data_string=''
        final_gtp5_data_list=[]
        gtp5_recieve=0
        for id in y_data_dict.keys():
            if 'WC_' in id:
                if len(y_data_dict[id])!=0:
                    gtp5_recieve+=y_data_dict[id][-1]
                    final_gtp5_data_string+="y_data_dict['"+id+"']+"
                    print final_gtp5_data_string
        exec("final_gtp5_data_list="+final_gtp5_data_string[:-1])
        #gtp5_recieve =(y_data_dict['WC_1L'][-1]+y_data_dict['WC_4L'][-1])
        final_query_ggs_list=''
        final_query_gtp5_list = ''
        self.prod_5min_fig=plt.figure()
        self.prod_5min_axes=self.prod_5min_fig.add_subplot(211,axisbg='#FFFFCC')
        self.prod_gtp5_axes=self.prod_5min_fig.add_subplot(212)
        for id in y_data_dict:
            if 'WC_' not in id:
                final_query_ggs_list+="y_data_dict[\'"+id+"\'],"

        excute_string="self.prod_ggs_5min_plot=self.prod_5min_axes.stackplot(x_date_dict[x_date_dict.keys()[0]],"+final_query_ggs_list[:-1]+",colors=["+ prod_5min_colors[:-1]+"])"


        #print y_data_dict['WC_4L'][:100],final_gtp5_data_list[:100]
        print 'length testing',len(y_data_dict['WC_4L']),len(final_gtp5_data_list)
        print 'length testing 2',len(x_date_dict[x_date_dict.keys()[0]]),len(final_gtp5_data_list)
        print x_date_dict[x_date_dict.keys()[0]][-1],final_gtp5_data_list[-1]
        print x_date_dict[x_date_dict.keys()[0]][0], final_gtp5_data_list[0]
        print x_date_dict[x_date_dict.keys()[0]][1], final_gtp5_data_list[1]
        try:
            self.prod_gtp5_5min_plot=self.prod_gtp5_axes.stackplot(x_date_dict[x_date_dict.keys()[0]],final_gtp5_data_list,colors=('yellow',))
        except:
            pass
        ano_x_date=x_date_dict[x_date_dict.keys()[0]][-1]
        ano_x_date_2=x_date_dict[x_date_dict.keys()[0]][0]
        ano_x_date_3=ano_x_date+datetime.timedelta(minutes=60)

        self.AnnotateDraw(self.prod_5min_axes, ano_x_date, ssoc_supply, 'GGS1 and GGS2 Sum Instant Value :'+ str(ssoc_supply) + '\n' + str(ano_x_date), x_offset=-280, y_offset=-50,
                          color='white', size=15, arrow=True)
        self.AnnotateDraw(self.prod_gtp5_axes, ano_x_date, gtp5_recieve, 'GTP5 Received Instant Value : '+ str(gtp5_recieve)+'\n'+str(ano_x_date),
                          x_offset=-280, y_offset=-50, color='red', size=15,
                          arrow=True)
        self.AnnotateDraw(self.prod_5min_axes, ano_x_date_2, gtp5_recieve,
                          'Plot will update at '+str(ano_x_date_3)+'\nDon\'t stare on it',
                          x_offset=40, y_offset=-30, color='black', size=12,
                          arrow=False)


        exec(excute_string)

        self.prod_5min_axes.set_title(ggs_string+' 5 Minutes Production Data Plot')
        self.prod_5min_axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d %H:%M:%S'))
        self.prod_5min_axes.set_ylabel('10Km3/d',size=20)
        self.prod_gtp5_axes.set_ylabel('10Km3/d',size=20)
        for tick in self.prod_5min_axes.get_xticklabels():
            tick.set_rotation(30)
        for tick in self.prod_gtp5_axes.get_xticklabels():
            tick.set_rotation(30)


        canvas=FigureCanvas(canvas_panel,wx.NewId(),self.prod_5min_fig)
        self.prod_5min_cursor = Cursor(self.prod_5min_axes, useblit=True, color='red', linewidth=2)
        self.canvas=canvas
        toobar=self.add_toolbar(canvas)
        self.CustomLayout(canvas_panel,'Center')
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, flag=wx.GROW)
        sizer.Add(toobar,0,wx.Bottom)
        canvas_panel.SetSizer(sizer)
        self._mgr.Update()

    def On5minPlotClick(self,event):

        if self.text3_exist == True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist = False
        id_string=''

        if self.plot_5min_exist==False:
            self.plot_5min_exist =True
            self.GGS5minPlot()
        else:
            pass


        self._mgr.Update()

    def OnStackPlotClick(self,event):

        if self.text3_exist == True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist = False
        #id_string = ''
        if self.daily_plot_exist==False:
            self.daily_plot_exist=True
            self.DailyGGSplot()
        else:
            pass
        self.ProdDataByProdStartDate()
        self._mgr.Update()

    def add_toolbar(self, canvas):
        """Copied verbatim from embedding_wx2.py"""
        self.toolbar = NavigationToolbar2Wx(canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        # update the axes menu on the toolbar
        self.toolbar.update()
        return self.toolbar

    def OnClose(self,event):
        print 'GGS closing procedure is starting......'
        self.Restore()
        try:
            del self.summary_canvas
            del self.summary_sec_axes
            del self.summary_axes
            del self.summary_plot_line
            del self.summary_plot
            del self.ggs_dict
            del self.ggs1_plot_line
            del self.ggs1_plot_methanol_line
            del self.ggs1_plot_axes
            del self.ggs1_plot_sec_axes
            del self.ggs2_plot_line
            del self.ggs2_plot_methanol_line
            del self.ggs2_plot_axes
            del self.ggs2_plot_sec_axes
            del self.prod_5min_cursor
            del self.prod_5min_list
            del self.prod_5min_axes
            del self.prod_daily_list
            del self.prod_5min_fig
            del self.prod_gtp5_5min_plot
            del self.prod_gtp5_axes
            del self.prod_data_index_fix_dict
            del self.max_prod_date_wells_list
            del self.min_prod_date_wells_list
            del self.bar_plot_dict
            del self.extract_ggs1_data
            del self.extract_ggs2_data
            del self.Panel_dict

        except Exception:
            pass
        self.Destroy()

    def OnMaximize(self,event):
        print 'frame is maximizing.......'

































