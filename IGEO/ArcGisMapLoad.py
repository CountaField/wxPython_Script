"""
Simple demo of the imshow function.
"""
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import math
import matplotlib.image as img
import numpy as np
from Oracle_connection import Gsrdb_Conn
from matplotlib.backends.backend_wx import  NavigationToolbar2Wx,wxc
import wx
import wx.lib.agw.aui as aui
from collections import OrderedDict
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from TidyUpStackPlotprodDate import  TidyUpStackPlotProdDate as tspd
import matplotlib.text
import wx.lib.scrolledpanel as ScrolledPanel
from AuiFrameTemple import  AuiTemple
from PolygonPlot3D import PolygonPlot3D as pp3
import datetime
from SingleWellProdReport import SingleWellProdReport as spr
import gc
import threading
from EventText import  EventText
from DailyProdTable import DailyProdTable
from BB9Frame import BB9Frame
import wx.aui
from PltReadImage import PltReadImage as pr
import time
if wx.Platform == '__WXMSW__':
    from wx.lib.flashwin import FlashWindow
import matplotlib.patches as mpatches
from matplotlib.widgets import Button

'''

          (1, 1, 0, 1): yellow
          (1, 0, 0, 1): Red
          (0, 0, 1, 1): blue (Default)
          (1, 0.64705,   0,  1): Orange
          ( 1. 0.75294118  0.79607843  1.) pink
          (0.80392157  0.36078431  0.36078431  0.6) indian red

'''

class ArcGisMapLoad(AuiTemple):
    def __init__(self,parent,map_path):
        AuiTemple.__init__(self,parent)

        self.parent=parent
        self.colors = " 'gold','yellowgreen', 'lightskyblue', 'lightcoral', 'KHAKI', 'ORCHID', 'PALEGREEN', 'pink','cyan','PLUM','cadetblue','gold','wheat','green','seagreen'"
        self.color_list = ['gold', 'yellowgreen', 'lightskyblue', 'lightcoral', 'KHAKI', 'ORCHID', 'PALEGREEN', 'pink',
                           'cyan', 'PLUM', 'cadetblue', 'gold', 'wheat', 'green', 'seagreen']

        self.plot_exist=False
        self.map_path=map_path
        self.well_loc_dict = {}
        self.well_id_dict = {}
        self.well_vs_list = []
        self.x_vs_axis_list = []
        self.y_vs_axis_list = []
        self.x_alarm_axis_list=[]
        self.y_alarm_axis_list=[]
        self.x_no_vs_axis_list = []
        self.y_no_vs_axis_list = []
        self.well_no_vs_list = []
        self.clicked_dict={}
        self._mgr = aui.AuiManager(agwFlags=aui.AUI_MGR_ALLOW_ACTIVE_PANE)
        self._mgr.SetManagedWindow(self)
        self.PanelInitial(map_path)

        self.MenuPane()
        self.SubPlotDataPrepare(wellid='SN0003-02')
        self.SubPlotDataPrepare(cluster='C003')
        self.MapInitial(map_path,radiuse_size=0.4)
        self.Maximize(True)
        time.sleep(2)
        self.OnPlotClear(event=None)

    def MultiThread(self):
        pass

    def MapInitial(self,map_path,radiuse_size):

        self.well_header_map = map_path + 'well_header.jpg'
        well_header_map1 = map_path + '03_Production_Map\SSOC_Cum_Production_PerWell_To_20170103.jpg'
        image_file = cbook.get_sample_data(self.well_header_map)
        self.image = plt.imread(image_file)
        self.ProdMapInitial(radiuse_size,self.image)
        self.StatisticMapInital()
        self.map_select = 'Production Map'

    def MenuPane(self):
        self.Menu_button_dict=OrderedDict()
        map_type_list=['Well Map','Cluster Map','GGS Map','Alarm Map']
        well_map_type_list=['Production Map','Alarm','BB9 & Cluster'] # should add cluster delta p map
        self.Menu_button_dict['map_type_text']=wx.StaticText(self._toolbar, -1,label=' Map Type Select: ')
        self.Menu_button_dict['map_type_combobox']=wx.ComboBox(self._toolbar, -1,choices=map_type_list)
        self.Menu_button_dict['map_choose_text']=wx.StaticText(self._toolbar, -1,label=' Map Select : ')
        self.Menu_button_dict['map_choose_combobox']=wx.ComboBox(self._toolbar, -1,choices=well_map_type_list)
        self.Menu_button_dict['confirm'] = wx.Button(self._toolbar, -1, label='Confirm')
        self.Menu_button_dict['plot_clear'] = wx.Button(self._toolbar, -1, label='Plot Clear')
        self.Bind(wx.EVT_BUTTON, self.OnPlotClear, self.Menu_button_dict['plot_clear'])
        self.Bind(wx.EVT_BUTTON, self.OnMenuConfirmButton, self.Menu_button_dict['confirm'])
        control_list=[]
        for x in self.Menu_button_dict.keys():
            control_list.append(self.Menu_button_dict[x])
        self.CustomAuiToolBar('Menu Bar',control_list)
        self._mgr.Update()

    def OnMenuConfirmButton(self,event):
        self.map_select=self.Menu_button_dict['map_choose_combobox'].GetStringSelection()

        if self.map_select=='Alarm':


            self.AlarmMapInitial(0.4,self.image)


        if self.map_select=='Production Map':
            self.ProdMapInitial()

        if self.map_select=='BB9 & Cluster':
            self.BB9MapInitial()

    def PanelInitial(self,clock_path):
        self.Panel_dict = OrderedDict()
        self.main_map_nb = wx.aui.AuiNotebook(self)
        self.Panel_dict['main_map']=wx.Panel(self.main_map_nb,-1,name='VS Map')

        self.Panel_dict['field_summary'] = wx.Panel(self, -1, name='Field Summary',size=(500,350))
        #self.Panel_dict['prod_year_map'] = wx.Panel(self.main_map_nb, -1, name='Connected Well By Year Map')
        self.Panel_dict['clock_area'] = wx.Panel(self, -1, name='Home Clock', size=(200, 750))
        self.Panel_dict['well_tree'] = wx.Panel(self, -1, name='Well Tree Selection', size=(200, 750))

        self.Panel_dict['plot_set'] =ScrolledPanel.ScrolledPanel(self, -1, name='Plot Setting', size=(200, 750),style=wx.ALWAYS_SHOW_SB)
        self.Panel_dict["plot_set"].SetupScrolling()
        self.Panel_dict['alarm_report'] = ScrolledPanel.ScrolledPanel(self, -1, name='Alarm Report', size=(200, 750),
                                                                  style=wx.ALWAYS_SHOW_SB)

        self.Panel_dict['well_plot_area']=wx.Panel(self, -1, name='well plot area', size=(500, 550))
        self.Panel_dict['cluster_plot_area'] = wx.Panel(self, -1, name='cluster plot area', size=(500, 550))
        self.Panel_dict["alarm_report"].SetupScrolling()
        try:
            self.ClockInitial(image_path=clock_path)
        except:
            pass
        self.MapTitalInitial()

        self.wells_tree_list = wx.TreeCtrl(self.Panel_dict['well_tree'], size=self.Panel_dict['well_tree'].GetSize())
        self.ClusterTreeList()
        self.PlotSetInitial()
        self.AlarmPlotSetting()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wells_tree_list)

        self.Panel_dict['well_tree'].SetSizer(sizer)
        self._mgr.AddPane(self.main_map_nb,
                          aui.AuiPaneInfo().CentrePane().MinimizeButton(True).CloseButton(False).Resizable(
                              resizable=True))
        for id in self.Panel_dict:
            if id in ('clock_area','well_tree', 'plot_set','alarm_report'):
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Left().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            elif 'MAP' in id.upper():
                     pass
            else:
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Right().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
        self.main_map_nb.AddPage(self.Panel_dict['main_map'],'VS Map Area')

        self.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeClick,self.wells_tree_list)
        self._mgr.Update()
        self._mgr.DoFrameLayout()

    def ClockInitial(self,image_path):
        clock_flash=FlashWindow(self.Panel_dict['clock_area'],style=wx.SUNKEN_BORDER)
        clock_flash.LoadMovie(0,image_path+'hamster.swf')
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(clock_flash,1,flag=wx.GROW)
        self.Panel_dict['clock_area'].SetSizer(sizer)
        self.Panel_dict['clock_area'].SetAutoLayout(True)

    def PlotSetInitial(self):
        self.button_area_control = OrderedDict()
        self.button_area_control['well_type_text']=wx.StaticText(self.Panel_dict['plot_set'], -1,label='Well Type Select :')
        self.button_area_control['well_type_combobox']=wx.ComboBox(self.Panel_dict['plot_set'], -1,choices=['VS & No VS','VS Only','No VS Only'])
        self.button_area_control['GGS_text'] = wx.StaticText(self.Panel_dict['plot_set'], -1,
                                                                   label='\n\nGGS Select :')
        self.button_area_control['GGS_combobox'] = wx.ComboBox(self.Panel_dict['plot_set'], -1,
                                                                       choices=['GGS 1 & GGS 2','GGS 1','GGS 2'])
        self.button_area_control['confirm'] = wx.Button(self.Panel_dict['plot_set'], -1, label='Confirm')
        sizer = wx.BoxSizer(wx.VERTICAL)
        final_sizer=wx.BoxSizer(wx.HORIZONTAL)
        final_sizer.AddSpacer(15)
        for x in self.button_area_control.keys():
            sizer.Add(self.button_area_control[x])
            sizer.AddSpacer(5)
        final_sizer.AddSizer(sizer)
        self.Panel_dict['plot_set'].SetSizer(final_sizer)

    def SubPlotDataPrepare(self,wellid='',cluster=''):
        # NEED TO BE MULTI THREAD
        print 'single wellid',wellid
        db = Gsrdb_Conn()
        if wellid!='':
            well_date_list = []
            well_data_list = []
            well_cum_data=[]
            data_cur=db.Sql("select production_date,daily_prod_gas, prod_cum_gas from production_data where wellid='"+wellid+"' order by production_date")
            for id in data_cur.fetchall():
                well_date_list.append(id[0])
                well_data_list.append(id[1])
                well_cum_data.append(id[2])
            self.SubwellPlotCreate(wellid=wellid,x_data=well_date_list,y_data=well_data_list,well_cum_data=well_cum_data[-1])

        if cluster!='':
            print cluster
            cluster_date_list=[]
            cluster_data_list=[]
            cluster_cum_data=[]
            data_cur=db.Sql("select production_date,sum_daily_prod_gas,sum_prod_cum_gas from vw_cluster_summary where clusterid='"+cluster+"' order by production_date")
            for id in data_cur.fetchall():
                cluster_date_list.append(id[0])
                cluster_data_list.append(id[1])
                cluster_cum_data.append(id[2])
            self.SubclusterPlotCreate(cluster,cluster_date_list,cluster_data_list,cluster_cum_data)
        #self.sub_plot_wellid=wellid
        print 'sub_plot_wellid',wellid
        self.sub_plot_clusterid=cluster
        db.close()

    def OnClusterPlotClick(self,event):
        db=Gsrdb_Conn()
        cluster_cur=db.Sql("select clusterid from well_header where wellid='"+self.selected_well+"'")
        for id in cluster_cur.fetchall():
            clusterid=id[0]
        db.close()
        print clusterid
        self.SubPlotDataPrepare(cluster=clusterid)

    def SubwellPlotCreate(self,wellid=False,cluster=False,x_data=[],y_data=[],well_cum_data=''):

        if wellid!=False:
            fig=plt.figure()
            ax=fig.add_subplot(111)
            ax.stackplot(x_data,y_data,color='green',colors='green',alpha=0.5)
            annot_string = wellid + " Cumulative Production is: " + str(well_cum_data) + "Mm3"
            self.cluster_annotate = self.AnnotateDraw(ax, x=min(x_data), y=max(y_data), astring=annot_string,
                                                      x_offset=50, y_offset=-30, color='black', size=11)
            self.well_plot_canvas=FigureCanvas(self.Panel_dict['well_plot_area'],wx.NewId(),fig)
            fig.autofmt_xdate()
            tool_bar = self.add_toolbar(self.well_plot_canvas)


            cluster_plot_button=wx.Button(self.Panel_dict['well_plot_area'],-1,label='Cluster Plot')
            well_detail_button=wx.Button(self.Panel_dict['well_plot_area'],-1,label='Production Detail')
            prod_table_button = wx.Button(self.Panel_dict['well_plot_area'], -1, label='Production Table')
            button_sizer=wx.BoxSizer(wx.HORIZONTAL)

            button_sizer.AddSpacer(5)
            button_sizer.Add(cluster_plot_button)
            button_sizer.AddSpacer(5)
            button_sizer.Add(well_detail_button)
            button_sizer.AddSpacer(5)
            button_sizer.Add(prod_table_button)

            sizer=wx.BoxSizer(wx.VERTICAL)

            sizer.Add(self.well_plot_canvas,1,wx.GROW)
            sizer.AddSizer(button_sizer)
            sizer.Add(tool_bar,0,wx.Bottom|wx.GROW)
            self.Panel_dict['well_plot_area'].SetSizer(sizer)
            self.Bind(wx.EVT_BUTTON,self.OnClusterPlotClick,cluster_plot_button)
            self.Bind(wx.EVT_BUTTON, self.OnSingleDetailClick, well_detail_button)
            self.Bind(wx.EVT_BUTTON, self.OnWellProdTableShow,prod_table_button)
        self._mgr.Update()

    def SubclusterPlotCreate(self,cluster,date_list,data_list,cum_list):
        try:
            self.cluster_canvas.Destroy()
            self.cluster_tool_bar.Destroy()
        except:
            pass
        fig=plt.figure()
        ax=fig.add_subplot(111)
        ax.stackplot(date_list,data_list,color='red',colors='red',alpha=0.5)
        fig.autofmt_xdate()
        annot_string=cluster+" Cumulative Production is: "+str(cum_list[-1])+"Mm3"
        self.cluster_annotate=self.AnnotateDraw(ax,x=min(date_list),y=max(data_list),astring=annot_string,x_offset=50,y_offset=-30,color='black',size=11)
        self.cluster_annotate.draggable(True)
        self.cluster_canvas=FigureCanvas(self.Panel_dict['cluster_plot_area'],-1,fig)
        self.cluster_tool_bar=self.add_toolbar(self.cluster_canvas)
        cluster_detail_button = wx.Button(self.Panel_dict['cluster_plot_area'], -1, label='Cluster Prod Detail')
        cluster_table_button = wx.Button(self.Panel_dict['cluster_plot_area'], -1, label='Cluster Prod Table')
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddSpacer(5)
        button_sizer.Add(cluster_detail_button)
        button_sizer.AddSpacer(5)
        button_sizer.Add(cluster_table_button)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.cluster_canvas, 1, flag=wx.GROW)
        sizer.AddSizer(button_sizer)
        sizer.Add(self.cluster_tool_bar,0,wx.BOTTOM|wx.GROW)
        self.Panel_dict['cluster_plot_area'].SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.OnClusterDetailClick,cluster_detail_button)
        self._mgr.Update()

    def AlarmPlotSetting(self):
        self.alarm_area_control=OrderedDict()
        self.alarm_area_control['alarm_type_text']=wx.StaticText(self.Panel_dict['alarm_report'], -1,
                                                                   label='Alarm Type Choose :')
        self.alarm_area_control['alarm_type_combobox']=wx.ComboBox(self.Panel_dict['alarm_report'], -1,choices=[])
        self.alarm_area_control['report_select_text']=wx.StaticText(self.Panel_dict['alarm_report'], -1,label='Report Select:')
        self.alarm_area_control['report_select_combobox']=wx.ComboBox(self.Panel_dict['alarm_report'], -1,choices=[])
        self.alarm_area_control['confirm'] = wx.Button(self.Panel_dict['alarm_report'], -1, label='Confirm')
        sizer = wx.BoxSizer(wx.VERTICAL)
        final_sizer = wx.BoxSizer(wx.HORIZONTAL)
        final_sizer.AddSpacer(15)
        for x in self.alarm_area_control.keys():
            sizer.Add(self.alarm_area_control[x])
            sizer.AddSpacer(2)
        final_sizer.AddSizer(sizer)
        self.Panel_dict['alarm_report'].SetSizer(final_sizer)

    def NoVsWellDataInitial(self):
        db = Gsrdb_Conn('gsrdba', 'oracle11111', 'gsrdb')
        well_coor_dict = self.WellsCoordinate()
        wellid_no_vs_cur = db.Sql(
            "select wellid from well_header where connected_to_prod='YES'and easting_at_td is not null and northing_at_td is not null and wellid not in"
            " (select wellid from allocation_dhc where dhc_type='VS') and (wellid  like 'SN%' or wellid like 'SUN%') "
            " order by wellid")

        for id in wellid_no_vs_cur.fetchall():
            self.well_no_vs_list.append(id[0])
        for wellid in self.well_no_vs_list:
            x_ns,y_ns=well_coor_dict[wellid]
            self.x_no_vs_axis_list.append(x_ns)
            self.y_no_vs_axis_list.append(y_ns)

        zip_data=zip(self.x_no_vs_axis_list,self.y_no_vs_axis_list)
        self.no_vs_end_data=np.array(zip_data)
        print 'no_vs_wells',len(zip_data)
        db.close()
        return zip_data

    def ClusterTreeList(self):

        tree_root = self.wells_tree_list.AddRoot("South Sulige Field")
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        vs_wells_summary = self.wells_tree_list.AppendItem(tree_root, 'VS Wells')
        h_wells_summary = self.wells_tree_list.AppendItem(tree_root, 'Horizontal Wells')
        Normal_wells_summary = self.wells_tree_list.AppendItem(tree_root, 'Normal Wells')

        vs_cluster_cur = db.Sql("select clusterid from well_header where wellid in "
                                "(select wellid from allocation_dhc where dhc_type='VS') "
                                "group by clusterid order by clusterid")

        h_cluster_cur = db.Sql("select clusterid from well_header where wellid like '%H%' and clusterid is not null "
                               "group by clusterid order by clusterid")

        Normal_cluster_cur = db.Sql("select clusterid from well_header where wellid not like '%H%' and  wellid not in"
                                    "(select wellid from allocation_dhc where dhc_type='VS') and clusterid is not null "
                                    "group by clusterid order by clusterid")

        self.vs_clusterid_dict = {}
        self.h_clusterid_dict = {}
        self.Normal_clusterid_dict = {}
        self.vs_wells_tree_dict = {}
        self.h_wells_tree_dict = {}
        self.Normal_wells_tree_dict = {}
        self.wellid_dict = {}
        self.wellid_tree_dict = {}

        for clusterid in vs_cluster_cur.fetchall():
            if clusterid[0] != None:
                self.vs_clusterid_dict[clusterid[0]] = []
                self.vs_wells_tree_dict[clusterid[0]] = self.wells_tree_list.AppendItem(vs_wells_summary,
                                                                                        str(clusterid[0]))

        for clusterid in h_cluster_cur.fetchall():
            if clusterid[0] != None:
                self.h_clusterid_dict[clusterid[0]] = []
                self.h_wells_tree_dict[clusterid[0]] = self.wells_tree_list.AppendItem(h_wells_summary,
                                                                                       str(clusterid[0]))

        for clusterid in Normal_cluster_cur.fetchall():
            if clusterid[0] != None:
                self.Normal_clusterid_dict[clusterid[0]] = []
                self.Normal_wells_tree_dict[clusterid[0]] = self.wells_tree_list.AppendItem(Normal_wells_summary,
                                                                                            str(clusterid[0]))

        for clusterid in self.vs_clusterid_dict:
            vs_wellid_cur = db.Sql(
                "select wellid from well_header where clusterid=\'" + clusterid + "\' and wellid  in "
                                                                                  "(select wellid from allocation_dhc where dhc_type='VS') order by wellid")
            for wellid in vs_wellid_cur.fetchall():
                self.vs_clusterid_dict[clusterid].append(wellid[0])
                self.wellid_tree_dict[wellid[0]] = self.wells_tree_list.AppendItem(self.vs_wells_tree_dict[clusterid],
                                                                                   str(wellid[0]))
        for clusterid in self.h_clusterid_dict:
            h_wellid_cur = db.Sql(
                "select wellid from well_header where clusterid=\'" + clusterid + "\' order by wellid")
            for wellid in h_wellid_cur.fetchall():
                self.h_clusterid_dict[clusterid].append(wellid[0])
                self.wellid_tree_dict[wellid[0]] = self.wells_tree_list.AppendItem(self.h_wells_tree_dict[clusterid],
                                                                                   str(wellid[0]))
        for clusterid in self.Normal_clusterid_dict:
            Normal_wellid_cur = db.Sql(
                "select wellid from well_header where clusterid=\'" + clusterid + "\' and wellid not in "
                                                                                  " (select wellid from allocation_dhc where dhc_type='VS') order by wellid")
            for wellid in Normal_wellid_cur.fetchall():
                self.Normal_clusterid_dict[clusterid].append(wellid[0])
                self.wellid_tree_dict[wellid[0]] = self.wells_tree_list.AppendItem(
                    self.Normal_wells_tree_dict[clusterid],
                    str(wellid[0]))
        db.close()

    def VsWellDataInital(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        well_coor_dict = self.WellsCoordinate()
        wellid_vs_cur = db.Sql(
            "select wellid from allocation_dhc where dhc_type='VS' and wellid in (select wellid from well_header where "
            "easting_at_td is not null and northing_at_td is not null   "
            "and connected_to_prod='YES' and wellid like 'SN%' or wellid like 'SUN%') group by wellid order by wellid")

        for id in wellid_vs_cur.fetchall():
            self.well_vs_list.append(id[0])


        for wellid in self.well_vs_list:
            x_vs, y_vs = well_coor_dict[wellid]
            self.x_vs_axis_list.append(x_vs)
            self.y_vs_axis_list.append(y_vs)

        zip_data=zip(self.x_vs_axis_list,self.y_vs_axis_list)
        self.vs_end_data=np.array(zip_data)
        print 'vs_wells', len(zip_data)
        db.close()
        return zip_data

    def AnnotateDraw(self,ax,x,y,astring,color='black',size=10,x_offset=-80,y_offset=30,arrow=False,bbox=False):

        if bbox==False:
            if arrow==False:
                atext=ax.annotate(astring, xy=(x, y), xycoords='data',xytext=(x_offset, y_offset),
                             textcoords='offset points'
                            )
            else:
                atext = ax.annotate(astring, xy=(x, y), xycoords='data', xytext=(x_offset, y_offset),
                                    textcoords='offset points',
                                    arrowprops=dict(arrowstyle="->",color=color,
                                                    connectionstyle="arc3,rad=.0"

                                                    )
                                    )
            atext.set_style('oblique')
            atext.set_weight('extra bold')
            atext.set_size(int(size))
            atext.set_color(color)

        else:
            print '1 step'
            if arrow == False:
                atext = ax.annotate(astring, xy=(x, y), xycoords='data', xytext=(x_offset, y_offset),
                                    textcoords='offset points',
                                    bbox=dict(boxstyle='round',
                                              fc='yellow',
                                              ec='black',
                                              alpha=0.7)
                                    )
            else:
                print '2 step'
                print astring

                atext = ax.annotate(astring, xy=(x, y), xycoords='data', xytext=(x_offset, y_offset),
                                    textcoords = 'offset points',
                                    arrowprops=dict(arrowstyle="->", color=color,
                                                    connectionstyle="arc3,rad=.0"),
                                    bbox=dict(boxstyle='round',
                                              fc='yellow',
                                              ec='black',
                                              alpha=0.7)
                                    )
        print '3 step'
        print type(atext) is matplotlib.text.Annotation
        return atext

    def VSMapInitial(self,radiuse_size=0.4,image_path=None):
        area = np.pi * (15 * radiuse_size) ** 2  # 0 to 15 point radiuses
        if self.plot_exist==False:
            self.main_map_figure=plt.figure()
            self.main_map_nb.DeletePage(0)
            self.Panel_dict['main_map'] = wx.Panel(self.main_map_nb, -1, name='Main Map')
            self.well_header_axes = self.main_map_figure.add_subplot(111)
            self.no_vs_list = self.NoVsWellDataInitial()
            self.vs_list = self.VsWellDataInital()
            self.result_prod_data = np.array(self.no_vs_list + self.vs_list)
            self.im = plt.imshow(image_path);
            plt.draw()
            del self.im
            sizer=wx.BoxSizer(wx.VERTICAL)
            self.plot_main_map= self.well_header_axes.scatter(self.result_prod_data[:, 0], self.result_prod_data[:, 1], picker=0.1, s=area,
                                                                               c=['blue'] * len(self.result_prod_data), alpha=1)

            print self.plot_main_map.get_facecolors()

            for id in range(len(self.result_prod_data)):

                if id>(len(self.no_vs_list)):
                    self.plot_main_map._facecolors[id]=(1, 0, 0, 1)

            self.canvas_main_map=FigureCanvas(self.Panel_dict['main_map'],wx.NewId(),self.main_map_figure)
            self.main_map_toolbar=self.add_toolbar(self.canvas_main_map)
            sizer.Add(self.canvas_main_map,1,wx.GROW)
            sizer.Add(self.main_map_toolbar,0,wx.BOTTOM | wx.GROW)
            self.cid_pick = self.main_map_figure.canvas.mpl_connect('pick_event', self.OnClick)
            #plt.grid(True)
            self.main_map_nb.InsertPage(0,self.Panel_dict['main_map'],'SSOC Field Map',select=True)
            self.Panel_dict['main_map'].SetSizer(sizer)
            self.main_map_nb.Update()
            self._mgr.Update()
            self.plot_exist='VS'
        elif self.plot_exist=='VS':
            pass
        else:
            try:
                for id in self.plot_sub_dict.keys():
                    self.plot_sub_dict[id].remove()
                del self.plot_sub_dict
            except:
                pass


            self.OnPlotClear(event=None)
            self.plot_main_map.remove()
            self.main_map_figure.canvas.mpl_disconnect(self.cid_pick)
            self.main_map_figure.canvas.draw()
            gc.collect()
            self.plot_main_map = self.well_header_axes.scatter(self.result_prod_data[:, 0], self.result_prod_data[:, 1],
                                                               picker=0.1, s=area,
                                                               c=['blue'] * len(self.result_prod_data), alpha=1)
            for id in range(len(self.result_prod_data)):

                if id>(len(self.no_vs_list)):
                    self.plot_main_map._facecolors[id]=(1, 0, 0, 1)
            self.cid_pick = self.main_map_figure.canvas.mpl_connect('pick_event', self.OnClick)
            self.main_map_figure.canvas.draw()
            self.main_map_nb.Update()
            self._mgr.Update()
            self.plot_exist = 'VS'

    def AlarmMapInitial(self,radiuse_size=0.6,image_path=''):
        if self.plot_exist!='alarm':
            try:
                for id in self.plot_sub_dict.keys():
                    self.plot_sub_dict[id].remove()
                del self.plot_sub_dict
            except:
                pass
            self.plot_sub_dict = {}
            self.OnPlotClear(event=None)
            self.plot_main_map.remove()
            self.main_map_figure.canvas.mpl_disconnect(self.cid_pick)
            self.main_map_figure.canvas.draw()
            gc.collect()
            print 'its start alarm map initial'
            area_list =[]

            '''Extrac Data From database for Alarm Report '''
            alarm_dict,self.alarm_end_data,alarm_1_data,alarm_2_data,alarm_3_data,alarm_3_xy,alarm_3_size,\
            alarm_2_xy,fianl_alarm_duration,alarm_1_dur,alarm_2_dur,alarm_3_dur=self.AlarmDataExtract()


            for id in fianl_alarm_duration:
                rad=radiuse_size+id*0.01
                print 'this is rad',rad
                if rad > 0.7:
                    rad = 0.7

                area_list.append(np.pi * (15 * rad) ** 2)


            self.plot_main_map = self.well_header_axes.scatter(self.alarm_end_data[:, 0], self.alarm_end_data[:, 1],
                                                                 picker=0.1, s=area_list,
                                                                 c=['blue'] * len(self.prod_end_data), alpha=0.9)


            i1=0
            for id in alarm_2_data:
                rad=radiuse_size+alarm_2_dur[i1]*0.01
                if rad>0.7:
                    rad=0.7
                area=np.pi * (15 * rad) ** 2

                self.plot_sub_dict[i1]=self.well_header_axes.scatter(id[0], id[1], picker=0.1, marker=(alarm_2_xy, 0),
                                            s=area,
                                            c=['yellow'] * len(alarm_2_data), alpha=1)
                i1+=1


            i = 0
            i2=i1+1
            for id in alarm_3_data:
                rad = radiuse_size+alarm_3_dur[i]*0.01
                if rad > 0.7:
                    rad = 0.7
                area = np.pi * (15 * rad) ** 2
                xy = alarm_3_xy[i]
                self.plot_sub_dict[i2+i]=self.well_header_axes.scatter(id[0], id[1], picker=0.1,marker=(xy,0),
                                            s=area,
                                            c=['yellow'] * len(alarm_3_data), alpha=1)
                i+=1

            legend_blue_rec=mpatches.Rectangle((0, 0), 1, 1, fc='blue',edgecolor='black',linewidth=1)
            legend_yellow_rec = mpatches.Rectangle((0, 0), 1, 1, fc='yellow', edgecolor='black', linewidth=1)
            legend_rec_tuple=(legend_blue_rec,legend_yellow_rec)
            print type(legend_blue_rec)
            alarm_legend=self.well_header_axes.legend(legend_rec_tuple,('Equipment Error','Abnormal Production Status'),scatterpoints=1,fontsize=15,loc=3,shadow=True,fancybox=True)
            self.cid_pick = self.main_map_figure.canvas.mpl_connect('pick_event', self.OnAlarmMapClick)
            alarm_legend.draggable(state=True)
            rec=[0.11, 0.01, 0.2, 0.055]
            button_axes=self.main_map_figure.add_axes(rec)
            Button(button_axes,'Show Alarm Table ')
            self.main_map_figure.canvas.draw()

            self.main_map_nb.Update()
            self._mgr.Update()
            self.plot_exist='alarm'
        else:
            pass

    def AlarmDataExtract(self,columns=None,min_date=None,max_date=None):
        db=Gsrdb_Conn()
        well_coor_dict = self.WellsCoordinate()
        alarm_dict=OrderedDict()
        data_cur = db.Sql("select * from alarm_summary_table order by wellid")

        eq_issue_tuple=("Casing Pressure Out of Range",
                        "Flowline Pressure Anomaly",
                        "Orifice need to change",
                        "Suspension of data transmission",
                        "Non expected pressure turbulence",
                        "lack of casing pressure",
                        'no production-suspected Orifice problem')

        prod_issue_tuple=("Liquid Loading",
                          "Low Flow Line Temperature",
                          "The well is closing",
                          "well to be shut-in",
                          "Unexpected rate increase(DHC Failure?)",
                          'no production')

        alarm_x_1=[]
        alarm_y_1=[]
        alarm_1_dur=[]
        alarm_x_2=[]
        alarm_y_2=[]
        alarm_2_dur = []
        alarm_x_3 = []
        alarm_y_3 = []
        alarm_3_dur = []
        alarm_3_xy=[]
        alarm_3_size=[]
        alarm_x_end_data=[]
        alarm_y_end_data = []
        self.alarm_wellid_list=[]
        well_alarm_duration=[]
        final_alarm_duration=[]
        for id in data_cur.fetchall(): # ALAMR_SUMMARY_TABLE ( WELLID, DETECTED_DATE, ALARM_MESSAGE, ALARM_REPORTED_TIMES, DURATION)
            self.alarm_wellid_list.append(id[0])
            if id[0] not in alarm_dict.keys():

                alarm_dict[id[0]]={}

                alarm_dict[id[0]][id[2]]=[]
                alarm_dict[id[0]][id[2]].append(id[1])
                alarm_dict[id[0]][id[2]].append(id[3])
                alarm_dict[id[0]][id[2]].append(id[4])

            else:
                if id[2] not in alarm_dict[id[0]].keys():
                    alarm_dict[id[0]][id[2]] = []
                    alarm_dict[id[0]][id[2]].append(id[1])
                    alarm_dict[id[0]][id[2]].append(id[3])
                    alarm_dict[id[0]][id[2]].append(id[4])

        for id in self.alarm_wellid_list:
            well_alarm_duration=[]
            for alarm_id in alarm_dict[id].keys():
                well_alarm_duration.append(alarm_dict[id][alarm_id][2])

            final_alarm_duration.append(max(well_alarm_duration))


            eq_issue_count=0.0
            prod_issue_count=0.0

            x_alarm,y_alarm=well_coor_dict[id]

            alarm_x_end_data.append(x_alarm)
            alarm_y_end_data.append(y_alarm)

            for am in alarm_dict[id].keys():
                if am in eq_issue_tuple:
                    eq_issue_count+=1
                elif am in prod_issue_tuple:
                    prod_issue_count+=1

            if eq_issue_count!=0:
                if prod_issue_count!=0:
                    final_count=eq_issue_count+prod_issue_count
                    eq_r=eq_issue_count/final_count
                    prod_r=prod_issue_count/final_count
                    alarm_type=3
                else:

                    alarm_type=1
            else:
                if prod_issue_count != 0:

                    alarm_type = 2

            if alarm_type==1:
                alarm_x_1.append(x_alarm)
                alarm_y_1.append(y_alarm)
                alarm_1_dur.append(max(well_alarm_duration))
            elif alarm_type==2:
                alarm_x_2.append(x_alarm)
                alarm_y_2.append(y_alarm)
                alarm_2_dur.append(max(well_alarm_duration))
            elif alarm_type==3:
                alarm_x_3.append(x_alarm)
                alarm_y_3.append(y_alarm)
                x1 = [0] + np.cos(np.linspace(0,2 * math.pi * prod_r,  10)).tolist()
                y1 = [0] + np.sin(np.linspace(0,2 * math.pi * prod_r,  10)).tolist()
                alarm_3_dur.append(max(well_alarm_duration))
                xy=list(zip(x1,y1))
                alarm_3_size.append(max(max(x1),max(y1)))
                alarm_3_xy.append(xy)

        alarm_1_data=np.array(zip(alarm_x_1,alarm_y_1))
        alarm_2_data=np.array(zip(alarm_x_2,alarm_y_2))
        alarm_3_data = np.array(zip(alarm_x_3, alarm_y_3))

        x = [0] + np.cos(np.linspace(0, 2 * math.pi , 10)).tolist()
        y = [0] + np.sin(np.linspace(0, 2 * math.pi , 10)).tolist()
        alarm_2_xy=list(zip(x,y))


        alarm_end_data=np.array(zip(alarm_x_end_data, alarm_y_end_data))
        db.close()
        return alarm_dict,alarm_end_data,alarm_1_data,alarm_2_data,alarm_3_data,alarm_3_xy,alarm_3_size,\
               alarm_2_xy,final_alarm_duration,alarm_1_dur,alarm_2_dur,alarm_3_dur

    def AlarmTableShow(self):
        pass

    def ProdMapInitial(self,radiuse_size=0.4,image=None):
        legend_list = []
        color_dict = OrderedDict()
        i = 0
        for year in range(2012, datetime.datetime.now().year + 1):
            color_dict[year] = self.color_list[i]
            i += 1
        for id in color_dict.keys():
            legend_list.append(mpatches.Rectangle((0, 0), 1, 1, fc=color_dict[id]))
        legend_title_list = color_dict.keys()
        if self.plot_exist==False:


            self.main_map_figure=plt.figure()
            self.main_map_nb.DeletePage(0)
            self.Panel_dict['main_map'] = wx.Panel(self.main_map_nb, -1, name='Main Map')
            self.well_header_axes = self.main_map_figure.add_subplot(111)
            self.im = plt.imshow(image);
            self.plot_sub_dict=OrderedDict()
            plt.draw()
            del self.im
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.prod_end_data, prod_data_dict, wellid_list, prod_start_list, self.vs_split,well_close_list,max_prod_date = self.ProdDataExtract()
            self.prod_wellid_list = wellid_list
            area_list = []

            self.prod_wellid_list = wellid_list


            for id in wellid_list:
                if id in prod_data_dict.keys():
                    #print "this is error well",id
                    rad = radiuse_size + prod_data_dict[id][1] * 0.01
                    area_list.append(np.pi * (15 * rad) ** 2)

            self.plot_main_map = self.well_header_axes.scatter(self.prod_end_data[:, 0], self.prod_end_data[:, 1],
                                                               picker=0.1, s=area_list,
                                                               c=['gray'] * len(self.prod_end_data), alpha=1)
            i = 0


            for id in self.prod_end_data:
                if i < self.vs_split-1:
                    if well_close_list[i]==1:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]], alpha=0.9,
                                                                                      marker='*')
                        if 'VS Well' not in legend_title_list:
                            legend_title_list.append('VS Well')
                            legend_list.append(self.plot_sub_dict[i])

                    else:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]],
                                                                              alpha=0.9,
                                                                              marker='*',
                                                                              edgecolor='red',
                                                                              linewidths=1.8)



                else:
                    if well_close_list[i] == 1:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]], alpha=0.9,
                                                                               )
                        if 'No VS Well' not in legend_title_list:
                            legend_title_list.append('No VS Well')
                            legend_list.append(self.plot_sub_dict[i])
                    else:
                        print i
                        try:
                            self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                                  s=area_list[i],
                                                                                  c=color_dict[prod_start_list[i]],
                                                                                  alpha=0.9,
                                                                                  edgecolors='red', linewidths=1.8)
                        except:
                            pass



                i+=1

            legend_list.append(mpatches.Rectangle((0, 0), 1, 1, fc='white',edgecolor='red',linewidth=1.8))
            legend_title_list.append('Closed Well')

            print legend_title_list,legend_list
            self.prod_axes_legend=self.well_header_axes.legend(legend_list,legend_title_list,scatterpoints=1,fontsize=15,loc=3,shadow=True,fancybox=True)



            self.canvas_main_map = FigureCanvas(self.Panel_dict['main_map'], wx.NewId(), self.main_map_figure)
            self.main_map_toolbar = self.add_toolbar(self.canvas_main_map)
            #sizer.Add(canvas_summary,1,wx.GROW)
            sizer.Add(self.canvas_main_map, 1, wx.GROW)
            sizer.Add(self.main_map_toolbar, 0, wx.BOTTOM | wx.GROW)
            self.cid_pick = self.main_map_figure.canvas.mpl_connect('pick_event', self.OnClick)
            self.prod_axes_legend.draggable(state=True)
            with plt.xkcd():
                self.well_header_axes.set_title("South Sulige GP Bubble Map in "+str(max_prod_date).split(' ')[0],fontdict={'fontsize':20})
            self.main_map_figure.canvas.draw()

            self.Panel_dict['main_map'].SetSizer(sizer)
            self.main_map_nb.InsertPage(0, self.Panel_dict['main_map'], 'SSOC Field Map', select=True)
            self.main_map_nb.Update()
            self._mgr.Update()
            self.plot_exist = 'prod'

        if self.plot_exist!='prod':

            try:
                for id in self.plot_sub_dict.keys():
                    self.plot_sub_dict[id].remove()
                del self.plot_sub_dict
            except:
                pass
            self.plot_sub_dict = {}
            self.plot_main_map.remove()
            self.OnPlotClear(event=None)

            self.main_map_figure.canvas.mpl_disconnect(self.cid_pick)
            self.main_map_figure.canvas.draw()
            gc.collect()
            self.prod_end_data, prod_data_dict, wellid_list, prod_start_list, self.vs_split,well_close_list,max_prod_date = self.ProdDataExtract()
            self.prod_wellid_list = wellid_list
            area_list = []
            color_dict = {}
            self.prod_wellid_list = wellid_list
            i = 0
            for year in range(2012, datetime.datetime.now().year + 1):
                color_dict[year] = self.color_list[i]
                i += 1

            for id in wellid_list:
                if id in prod_data_dict.keys():
                    rad = radiuse_size + prod_data_dict[id][1] * 0.01
                    area_list.append(np.pi * (15 * rad) ** 2)

            self.plot_main_map = self.well_header_axes.scatter(self.prod_end_data[:, 0], self.prod_end_data[:, 1],
                                                               picker=0.1, s=area_list,
                                                               c=['blue'] * len(self.prod_end_data), alpha=1)

            i = 0
            scatter_string = ''
            title_string = ''

            for id in self.prod_end_data:
                if i < self.vs_split:
                    if well_close_list[i] == 1:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]],
                                                                              alpha=0.9,
                                                                              marker='*')


                    else:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]],
                                                                              alpha=0.9,
                                                                              marker='*',
                                                                              edgecolor='red',
                                                                              linewidths=1.8)




                else:
                    if well_close_list[i] == 1:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]],
                                                                              alpha=0.9,
                                                                              )

                    else:
                        self.plot_sub_dict[i] = self.well_header_axes.scatter(id[0], id[1],
                                                                              s=area_list[i],
                                                                              c=color_dict[prod_start_list[i]],
                                                                              alpha=0.9,
                                                                              edgecolors='red', linewidths=1.8)

                i += 1



            self.cid_pick = self.main_map_figure.canvas.mpl_connect('pick_event', self.OnClick)
            legend_list.append(mpatches.Rectangle((0, 0), 1, 1, fc='white', edgecolor='red', linewidth=1.8))
            legend_title_list.append('Closed Well')
            self.well_header_axes.set_title("South Sulige GP Bubble Map in " + str(max_prod_date).split(' ')[0],
                                            fontdict={'fontsize': 20})
            print legend_title_list, legend_list
            self.prod_axes_legend = self.well_header_axes.legend(legend_list, legend_title_list, scatterpoints=1,
                                                                 fontsize=15, loc=3, shadow=True, fancybox=True)
            self.prod_axes_legend.draggable(state=True)
            self.main_map_figure.canvas.draw()
            plt.draw()
            self.main_map_nb.Update()
            self._mgr.Update()
            self.plot_exist = 'prod'

    def ProdDataExtract(self):
        db = Gsrdb_Conn()
        well_coor_dict=self.WellsCoordinate()
        vs_prod_data_dict={}
        vs_wellid_list=[]
        vs_prod_start_list=[]
        no_vs_prod_data_dict = {}
        no_vs_wellid_list = []
        no_vs_prod_start_list = []
        vs_well_close_list=[]
        no_vs_well_close_list=[]
        vs_data_cur = db.Sql("select wellid,production_start_date from well_header where wellid in "
                             "(select wellid from allocation_dhc where dhc_type='VS') and connected_to_prod='YES' order by wellid  ")

        vs_prod_data_cur=db.Sql("select wellid,daily_prod_gas,prod_cum_gas from production_data where "
                             "production_date=(select max(production_date) from production_data) and (wellid in "
                                "(select wellid from allocation_dhc where dhc_type='VS') and "
                                "wellid in (select wellid from well_header where connected_to_prod='YES'))"
                                "order by wellid ")
        no_vs_data_cur = db.Sql(
            "select wellid,production_start_date from well_header where "
            "wellid not in (select wellid from allocation_dhc where dhc_type='VS') and "
            "(wellid like 'SN%' or wellid='SUN003') and connected_to_prod='YES' order by wellid  ")

        no_vs_prod_data_cur = db.Sql("select wellid,daily_prod_gas,prod_cum_gas from production_data where "
                                  "production_date=(select max(production_date) from production_data) and "
                                     "(wellid not in (select wellid from allocation_dhc where dhc_type='VS')and (wellid like 'SN%' or wellid='SUN003') and "
                                     "wellid in (select wellid from well_header where connected_to_prod='YES')) order by wellid ")

        max_prod_date_cur=db.Sql("select max(production_date) from production_data")

        for id in max_prod_date_cur.fetchall():
            max_prod_date=id[0]

        vs_prod_x_end_data=[]
        vs_prod_y_end_data=[]
        no_vs_prod_x_end_data = []
        no_vs_prod_y_end_data = []

        for id in vs_data_cur.fetchall():
            vs_wellid_list.append(id[0])
            vs_prod_start_list.append(id[1].year)

        for id in vs_wellid_list:
            x_prod,y_prod=well_coor_dict[id]
            vs_prod_x_end_data.append(x_prod)
            vs_prod_y_end_data.append(y_prod)

        for id in no_vs_data_cur.fetchall():
            no_vs_wellid_list.append(id[0])
            no_vs_prod_start_list.append(id[1].year)

        for id in no_vs_wellid_list:
            x_prod,y_prod=well_coor_dict[id]
            no_vs_prod_x_end_data.append(x_prod)
            no_vs_prod_y_end_data.append(y_prod)
        prod_x_end_data=vs_prod_x_end_data+no_vs_prod_x_end_data
        prod_y_end_data = vs_prod_y_end_data + no_vs_prod_y_end_data
        prod_end_data = np.array(zip(prod_x_end_data, prod_y_end_data))
        prod_data_dict=OrderedDict()

        for id in vs_prod_data_cur.fetchall():
            if id!=():
               prod_data_dict[id[0]]=(id[1],id[2])
               if id[1]==0:
                    vs_well_close_list.append(0)
               else:
                   vs_well_close_list.append(1)
            else:
                print 'absence well',id

        for id in no_vs_prod_data_cur.fetchall():
            if id!=():
                prod_data_dict[id[0]]=(id[1],id[2])
                if id[1] == 0:
                    no_vs_well_close_list.append(0)
                else:
                    no_vs_well_close_list.append(1)
            else:
                print 'absence well',id
        well_close_list=vs_well_close_list+no_vs_well_close_list

        db.close()


        for id in no_vs_prod_data_dict.keys():
            prod_data_dict[id]=no_vs_prod_data_dict[id]
        wellid_list=vs_wellid_list+no_vs_wellid_list
        prod_start_list=vs_prod_start_list+no_vs_prod_start_list
        print 'close well list', len(well_close_list)
        print 'well list', len(wellid_list)

        return prod_end_data,prod_data_dict,wellid_list,prod_start_list,len(vs_wellid_list),well_close_list,max_prod_date

    def WellsCoordinate(self):
        db = Gsrdb_Conn()
        well_coord_dict={}
        cur = db.Sql("select wellid,easting_at_td,northing_at_td from well_header where"
                     " (wellid like 'SN%' or wellid='SUN003') and easting_at_td is not null and northing_at_td is not null")
        for id in cur.fetchall():
            x_s=id[1]
            y_s=id[2]
            x,y=self.CoefficientInitial(x_s,y_s)
            well_coord_dict[id[0]]=(x,y)
        db.close()
        return well_coord_dict

    def CoefficientInitial(self,x_s,y_s):
        fx = 4675.0 / 50173.0
        fy = 6612.0 / 70416.0
        x1=(x_s-19233110)*fx
        y1 = 6612 - (y_s - 4163110) * fy
        return x1,y1

    def OnClick(self,event):
        try:
            print type(event.ind),event.ind[0]

            print self.plot_main_map._facecolors[event.ind[0]]

            x_axis,y_axis= self.prod_end_data[event.ind[0]]
            wellid=self.prod_wellid_list[event.ind[0]]

            print wellid
            self.selected_well=wellid
            self.sub_plot_wellid=wellid
            self._mgr.DetachPane(self.Panel_dict['well_plot_area'])
            self.well_plot_canvas.Destroy()
            self.Panel_dict['well_plot_area'].Destroy()
            self.Panel_dict['well_plot_area']=wx.Panel(self, -1, name='well plot area', size=(500, 350))
            self._mgr.AddPane(self.Panel_dict['well_plot_area'], aui.AuiPaneInfo().Caption(self.Panel_dict['well_plot_area'].GetName()).
                              Right().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            self.SubPlotDataPrepare(wellid=wellid)

            text=wellid+'\n'
            prod_data_dict=self.ClickDataCollection(wellid)

            for id in prod_data_dict.keys():
                text+=prod_data_dict[id]
            if event.ind[0] not in self.clicked_dict.keys():
                self.clicked_dict[event.ind[0]]=self.AnnotateDraw(self.well_header_axes, x=x_axis, y=y_axis, astring=text, color='black',
                                                                    size=15,arrow=True,bbox=True)
            else:
                pass

            self.clicked_dict[event.ind[0]].draggable()
            print '4 step'
            self.plot_main_map._facecolors[event.ind[0]] = (1, 1, 0, 1)
            self.main_map_figure.canvas.draw()
            self.wells_tree_list.SetItemDropHighlight(self.wellid_tree_dict[wellid], highlight=True)
            self.OnClusterPlotClick(event=None)
        except:
            self.main_map_figure.canvas.draw()

    def OnAlarmMapClick(self,event):
        print 'alarm click'
        try:
            print event.ind[0]
            wellid=self.alarm_wellid_list[event.ind[0]]
            x_axis, y_axis = self.alarm_end_data[event.ind[0]]
            self._mgr.DetachPane(self.Panel_dict['well_plot_area'])
            self.well_plot_canvas.Destroy()
            self.Panel_dict['well_plot_area'].Destroy()
            self.Panel_dict['well_plot_area']=wx.Panel(self, -1, name='well plot area', size=(500, 350))
            self._mgr.AddPane(self.Panel_dict['well_plot_area'], aui.AuiPaneInfo().Caption(self.Panel_dict['well_plot_area'].GetName()).
                              Right().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            self.SubPlotDataPrepare(wellid=wellid)
            text = self.ClickAlarmDataCollection(wellid)
            if event.ind[0] not in self.clicked_dict.keys():
                self.clicked_dict[event.ind[0]]=self.AnnotateDraw(self.well_header_axes, x=x_axis, y=y_axis, astring=text, color='red',
                                                                    size=15,arrow=True,bbox=True)
                self.clicked_dict[event.ind[0]].draggable()
            else:
                pass
            self.main_map_figure.canvas.draw()
            self.sub_plot_wellid=wellid
            self.selected_well=wellid
            self.OnClusterPlotClick(event=None)

        except AttributeError:
            self.main_map_figure.canvas.draw()

    def OnProdMapClick(self,event):
        print 'prod click'
        print event.ind[0]
        wellid=self.prod_wellid_list[event.ind[0]]
        print wellid

    def ClickAlarmDataCollection(self,wellid):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        alarm_data_dict = OrderedDict()
        alarm_data_dict['detected_date']=[]
        alarm_data_dict['alarm_message']=[]
        alarm_data_dict['duration']=[]
        text=wellid+'\n'
        text+=(' '*4)+'Detected Date'+(' '*10)+'Alarm Message'+(' '*8)+'Report Times'+'\n'
        alarm_data_cur=db.Sql("select detected_date,alarm_message,alarm_reported_times from alarm_summary_table where wellid='"+wellid+"'")
        for id in alarm_data_cur.fetchall():
            text+=str(id[0])+(' '*4)+str(id[1])+(' '*4)+str(id[2])+'\n'
        db.close()
        return text

    def ClickDataCollection(self,wellid):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        prod_data_dict=OrderedDict()
        cum_prod_cur=db.Sql("select prod_cum_gas from production_data where wellid='"+wellid+"' and production_date=(select max(production_date) from production_data)")
        prod_start_date=db.Sql("select production_start_date,ggs from well_header where wellid='"+wellid+"'")
        instant_prod_cur=db.Sql("select instant_production_gas from raw_inst_data_keep_2day where "
                                "wellid='"+wellid+"' and production_date=(select max(production_date) from raw_inst_data_keep_2day where wellid='"+wellid+"')")
        cum_total_prod_day_cur=db.Sql("select max(cum_days),max(total_days) from cum_prod_aux where wellid='"+wellid+"'")

        for id in prod_start_date.fetchall():
            prod_data_dict['conn_date']="Start Prod: "+str(id[0]).split(' ')[0]+"\n"
            prod_data_dict['GGS']="GGS: "+str(id[1])+"\n"
        for id in cum_prod_cur.fetchall():
            prod_data_dict['cum_prod_gas']="Cum Prod: "+str(id[0])+"Mm3\n"

        for id in instant_prod_cur.fetchall():
            prod_data_dict['inst_prod']="Inst Prod: "+str(id[0])+"m3/h\n"

        for id in cum_total_prod_day_cur.fetchall():
            prod_data_dict['prod_days']="Cum Prod Days: "+str(id[0])+" Days\n"

        db.close()
        return prod_data_dict

    def OnPlotClear(self,event):
        for x in self.clicked_dict.keys():
            self.clicked_dict[x].remove()
            s=self.clicked_dict.pop(x)
            del s


        for id in range(len(self.prod_end_data)):
            if id>self.vs_split:
                try:
                    self.plot_main_map._facecolors[id]=(1, 0, 0, 1)
                except:
                    pass
            else:
                try:
                    self.plot_main_map._facecolors[id] = (0, 0, 1, 1)
                except:
                    pass

        self.main_map_figure.canvas.draw()

    def OnTreeClick(self,event):

        wellid = self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
        print 'tree wellid ',wellid
        if wellid in self.prod_wellid_list:
            index=self.prod_wellid_list.index(wellid)
            x_axis,y_axis=self.prod_end_data[index]

        if self.map_select=='Production Map':
            prod_data_dict = self.ClickDataCollection(wellid)
            text=wellid+'\n'
            for id in prod_data_dict.keys():
                text += prod_data_dict[id]
            if index not in self.clicked_dict.keys():
                self.clicked_dict[index] = self.AnnotateDraw(self.well_header_axes, x=x_axis, y=y_axis, astring=text,
                                                                    color='black',
                                                                    size=15, arrow=True, bbox=True)

            else:
                pass

            self.clicked_dict[index].draggable()
        elif self.map_select=='Alarm':
            text = self.ClickAlarmDataCollection(wellid)
            self.clicked_dict[index] = self.AnnotateDraw(self.well_header_axes, x=x_axis, y=y_axis, astring=text,
                                                                color='red',
                                                                size=15, arrow=True, bbox=True)
            self.clicked_dict[index].draggable()



        print '4 step'

        '''
        (1, 1, 0, 1): yellow
        (1, 0, 0, 1): Red
        (0, 0, 1, 1): blue (Default)
        '''
        self.plot_main_map._facecolors[index] = (1, 1, 0, 1)
        self.main_map_figure.canvas.draw()
        self.selected_well=wellid
        self.sub_plot_wellid=wellid
        self.SubPlotDataPrepare(wellid=wellid)

        self.OnClusterPlotClick(event=None)

    def OnSingleDetailClick(self,event):
        self.spr_frm=spr(self.parent)
        wellid=self.sub_plot_wellid
        print "single well id",wellid
        print 'this is wellid in tree list', self.wellid_tree_dict[self.sub_plot_wellid]
        #new_thread = threading.Thread(target=self.ShowSingleWellReport, args=(self.spr_frm,wellid))
        #new_thread.start()
        self.ShowSingleWellReport(self.spr_frm,wellid)

    def ShowSingleWellReport(self,frm,wellid):
        if True:
            self.single_well_frm=frm
            self.single_well_frm.SetSize((800, 600))
            self.single_well_frm.Show()
            self.single_well_frm._mgr.DetachPane(self.single_well_frm.text3)
            self.single_well_frm.text3.Destroy()
            self.single_well_frm.inst_plot = False
            self.single_well_frm.DailyprodPrepare(wellid)

            self.single_well_frm.PiePlotShow(wellid)
            self.single_well_frm.InstNewThreadExtract(wellid)
            print 'processing.....', self.single_well_frm.daily_prod_canvas


            piesizer = wx.BoxSizer(wx.VERTICAL)
            piesizer1 = wx.BoxSizer(wx.VERTICAL)
            piesizer.Add(self.single_well_frm.pie_canvas, 1, wx.GROW)
            piesizer1.Add(self.single_well_frm.pie_canvas_yesterday, 1, wx.GROW)
            self.single_well_frm.daily_toolbar = self.single_well_frm.daily_plot_sample.add_toolbar(
                self.single_well_frm.daily_prod_canvas)
            '''self.single_well_frm.hist_toolbar = self.single_well_frm.hist_plot_sample.add_toolbar(
                self.single_well_frm.hist_prod_canvas)'''
            self.single_well_frm.pie_toolbar = NavigationToolbar2Wx(self.single_well_frm.pie_canvas)
            self.single_well_frm.pie_yesterday_toolbar = NavigationToolbar2Wx(self.single_well_frm.pie_canvas_yesterday)
            self.single_well_frm.pie_toolbar.Realize()
            self.single_well_frm.pie_yesterday_toolbar.Realize()
            self.single_well_frm.pie_toolbar.update()
            self.single_well_frm.pie_yesterday_toolbar.update()
            piesizer.Add(self.single_well_frm.pie_toolbar, 0, wx.BOTTOM | wx.GROW)
            piesizer1.Add(self.single_well_frm.pie_yesterday_toolbar, 0, wx.BOTTOM | wx.GROW)
            self.single_well_frm.Panel_dict['Pie_Plot_Area'].SetSize((200, 200))
            self.single_well_frm.Panel_dict['Pie_Plot_Area_Yesterday'].SetSize((200, 200))

            self.single_well_frm.Panel_dict['Pie_Plot_Area'].SetSizer(piesizer)
            self.single_well_frm.Panel_dict['Pie_Plot_Area_Yesterday'].SetSizer(piesizer1)

            w, h = self.single_well_frm.GetSize()

            pie_pane = self.single_well_frm._mgr.AddPane(self.single_well_frm.Panel_dict['Pie_Plot_Area'],
                                                         aui.AuiPaneInfo().Center().
                                                         Top().CloseButton(False).MinimizeButton(True))
            self.single_well_frm._mgr.AddPane(self.single_well_frm.Panel_dict['Pie_Plot_Area_Yesterday'],
                                              aui.AuiPaneInfo().Center().
                                              Top().CloseButton(False).MinimizeButton(True))

            print type(pie_pane)
            self.single_well_frm.Panel_dict['Event_Output'].AppendText(EventText(wellid=wellid).DBQuery())
            self.single_well_frm._mgr.Update()
            self.single_well_frm.pre_center_exist = True
            self.single_well_frm.GetDefaultPlotValue()
        #except:
            #pass

    def OnWellProdTableShow(self,event):
        frm=DailyProdTable(self.parent,self.sub_plot_wellid,table_name="PRODUCTION_DATA")
        frm.Show()

    def OnClusterDetailClick(self,event):
        self.sub_cluster_frm=BB9Frame(self.parent)
        self.sub_cluster_frm.Show()
        if self.sub_cluster_frm.text3_exist == True:
            self.sub_cluster_frm._mgr.DetachPane(self.sub_cluster_frm.text3)
            self.sub_cluster_frm.text3.Destroy()
            self.sub_cluster_frm.text3_exist = False
        self.sub_cluster_frm.prod_datadict = {}
        self.sub_cluster_frm.final_date_dict = {}
        clusterid=self.sub_plot_clusterid
        self.sub_cluster_frm.WellidInCluster(clusterid, [], [])
        self.sub_cluster_frm.MinProdDateWells(clusterid, [], [])
        self.sub_cluster_frm.MaxProdDateWells(clusterid, [], [])

        try:
            self.sub_cluster_frm.DefineProdDateStander(clusterid, [])
        except TypeError:
            wx.MessageDialog(self.sub_cluster_frm.parent,
                             'Soryy,' + clusterid + ' is not producing',
                             style=wx.OK | wx.ICON_ERROR)
        self.sub_cluster_frm.CompareProdDateDiff()
        self.sub_cluster_frm.TidyUpProdData(clusterid, [])
        self.sub_cluster_frm.prod_data_cluster_dict[clusterid] = self.sub_cluster_frm.prod_data_dict
        self.sub_cluster_frm.checked_dict[id] = self.sub_cluster_frm.WellsInClusterDataPrepare(
            clusterid,final_date_dict=self.sub_cluster_frm.final_date_dict,prod_data_dict=self.sub_cluster_frm.prod_data_dict)

    def add_toolbar(self, canvas):
            """Copied verbatim from embedding_wx2.py"""
            self.toolbar = NavigationToolbar2Wx(canvas)
            self.toolbar.Realize()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # update the axes menu on the toolbar
            self.toolbar.update()
            return self.toolbar

    def StatisticMapInital(self):

        ax_leg=False
        self.stat_dic=OrderedDict()
        self.Panel_dict['stat'] = wx.Panel(self.main_map_nb, -1, name='Statistic Plot')
        fig = plt.figure()
        axes = fig.add_subplot(111)
        data_dict=self.StatisticDataPrepare()
        cur_year = datetime.datetime.now().year
        years = cur_year - 2011+1
        year_list=[]
        for year in range(2011,cur_year+1):
            year_list.append(year)
        drill_data_list = []
        prod_data_list=[]
        frac_data_list=[]
        vs_data_list=[]
        year_labels_list = []
        bar_width = 0.15
        ind = np.arange(years)
        for year in data_dict.keys():
            drill_data_list.append(data_dict[year]['drilling'])
            frac_data_list.append(data_dict[year]['frac'])
            prod_data_list.append(data_dict[year]['prod'])
            vs_data_list.append(data_dict[year]['vs'])
            year_labels_list.append(str(year))
        print drill_data_list
        print ind
        self.stat_dic['Drilled Wells'] = axes.bar(ind, drill_data_list, bar_width, color='r')
        self.stat_dic['Frac Wells'] = axes.bar(ind + bar_width , frac_data_list, bar_width, color='b')
        self.stat_dic['Start Production Wells']=axes.bar(ind+bar_width*2, prod_data_list, bar_width, color='g')

        self.stat_dic['VS Wells'] = axes.bar(ind + bar_width * 3, vs_data_list, bar_width, color='y')

        canvas = FigureCanvas(self.Panel_dict['stat'], wx.NewId(), fig)
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas,1,wx.GROW)
        axes.set_title('Field Statistic')
        axes.set_xticks(ind+bar_width*2)
        axes.set_xticklabels(year_list)
        bar_string=''
        name_string=''
        for id in self.stat_dic.keys():
            self.autolabel(axes,self.stat_dic[id])
            bar_string+="self.stat_dic['"+id+"'],"
            name_string+="'"+id+"',"

        legend_string="ax_leg=axes.legend(("+bar_string+"),("+name_string+"))"
        print legend_string
        exec(legend_string)
        ax_leg.draggable(state=True)
        fig.canvas.draw()
        self.main_map_nb.InsertPage(1,self.Panel_dict['stat'],'Statistic Plot',select=False)
        self.Panel_dict['stat'].SetSizer(sizer)
        self.main_map_nb.Update()
        self._mgr.Update()

    def autolabel(self,ax,rects):
        """
        Attach a text label above each bar displaying its height
        """
        for rect in rects:
            height = rect.get_height()
            if height!=0:
                ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                        '%d' % int(height),
                        ha='center', va='bottom')

    def StatisticDataPrepare(self):
        db=Gsrdb_Conn()
        cur_year=datetime.datetime.now().year
        data_dict = OrderedDict()

        for year in range(2011,cur_year+1):
            data_dict[year]={'drilling':0,'prod':0,'vs':0,'frac':0}

        base_info_cur=db.Sql("select drilling_program,production_start_date from well_header where "
                             "(wellid like 'SN%' ) AND production_start_date is not null order by production_start_date")

        frac_info_cur=db.Sql('select max(frac_year) from fracture where frac_year is not null   group by wellid order by wellid')

        vs_info_cur=db.Sql("select dhc_set_date from allocation_dhc where dhc_type='VS' and dhc_set_date is not null and dhc_removal_date is null order by dhc_set_date")
        for id in base_info_cur.fetchall():
            data_dict[id[0]]['drilling']+=1
            year=id[1].year
            data_dict[year]['prod']+=1

        for id in frac_info_cur.fetchall():
            data_dict[id[0]]['frac']+=1

        for id in vs_info_cur.fetchall():
            data_dict[id[0].year]['vs']+=1

        print data_dict


        db.close()
        return data_dict

    def BB9MapInitial(self):
        if self.plot_exist != 'bb9':
            try:
                for id in self.plot_sub_dict.keys():
                    self.plot_sub_dict[id].remove()
                del self.plot_sub_dict
            except:
                pass
            area_list=[]
            self.plot_sub_dict = {}
            self.OnPlotClear(event=None)
            self.plot_main_map.remove()
            self.main_map_figure.canvas.mpl_disconnect(self.cid_pick)
            self.main_map_figure.canvas.draw()
            gc.collect()
            bb9_list,bb9_coor_list,cluster_list,cluster_coor_list=self.BB9DataExtract()
            print bb9_coor_list[:, 1]
            for id in bb9_list:
                area_list.append(np.pi * (15 * 0.7) ** 2)
            self.plot_main_map=self.well_header_axes.scatter(bb9_coor_list[:, 0], bb9_coor_list[:, 1],
                                                                   picker=0.1,s=area_list,
                                                                   c=['red'] * len(bb9_list), alpha=1)

            self.main_map_figure.canvas.draw()

            self.main_map_nb.Update()
            self._mgr.Update()
            self.plot_exist='bb9'

    def BB9DataExtract(self):
        db = Gsrdb_Conn()
        bb9_data_cur=db.Sql("select bb9 from well_cluster where bb9 is not null group by bb9 order by bb9")
        cluster_data_cur=db.Sql("select clusterid from well_cluster group by clusterid order by clusterid")
        bb9_coor_dict=OrderedDict()
        well_coor_dict=self.WellsCoordinate()
        bb9_list=[]
        bb9_x_coor_list=[]
        bb9_y_coor_list = []
        cluster_x_coor_list=[]
        cluster_y_coor_list=[]
        cluster_list=[]


        for id in cluster_data_cur.fetchall():
             cluster_list.append(id[0])


        for id in bb9_data_cur.fetchall():
            bb9_list.append(id[0])
            cluster_id='C'+id[0].split('-')[1]
            print cluster_id
            cluster_list.remove(cluster_id)
            well_id_coor_cur=db.Sql("select wellid from well_header where wellid like '%-05%' AND clusterid='"+cluster_id+"'")
            for wellid in well_id_coor_cur.fetchall():
                bb9_x_coor_list.append(well_coor_dict[wellid[0]][0])
                bb9_y_coor_list.append(well_coor_dict[wellid[0]][1])

        for id in cluster_list:
            well_id_coor_cur = db.Sql("select wellid from well_header where wellid like '%-05%' AND clusterid='" + cluster_id + "'")
            for wellid in well_id_coor_cur.fetchall():
                cluster_x_coor_list.append(well_coor_dict[wellid[0]][0])
                cluster_y_coor_list.append(well_coor_dict[wellid[0]][1])

        db.close()
        bb9_coor_list=np.array(zip(bb9_x_coor_list,bb9_y_coor_list))
        cluster_coor_list=np.array(zip(cluster_x_coor_list,cluster_y_coor_list))
        return bb9_list,bb9_coor_list,cluster_list,cluster_coor_list

    def MapTitalInitial(self):
        max_prod_date, sum_field_daily, ggs_daily_prod_list, field_cum, field_year_cum, total_wells, ggs1_open_wells,ggs2_open_wells = self.MapDataExtract()
        x_label=['GGS1','GGS2','GTP5']
        open_x_label=['GGS1 \nOpen Wells','GGS2 \nOpen Wells','Total Wells']
        fig = plt.figure()

        with plt.xkcd():
            try:
                ax=fig.add_subplot(211)
                ax_open_well=fig.add_subplot(212)

                ax.bar((0,1,2,3),[0]+ggs_daily_prod_list+[sum_field_daily],0.25,hatch='//',color='lightblue')
                ax_open_well.bar((0,1,2,3),(0,ggs1_open_wells,ggs2_open_wells,total_wells),0.25,hatch='//',color='pink')

                ax.set_yticks([])
                ax_open_well.set_yticks([])
                ax.set_xticks([1,2,3])
                ax_open_well.set_xticks([1, 2,3])
                ax.set_xticklabels(x_label)
                ax_open_well.set_xticklabels(open_x_label)
                ax.set_title('Field Summary & Well Open Status')
                field_summary_list=[0]+ggs_daily_prod_list+[sum_field_daily]
                i=1
                for id in field_summary_list[1:]:
                    self.AnnotateDraw(ax, x=i, y=id, astring=str(round(id/100,2))+" Msm3/d",
                                      x_offset=-50, y_offset=-20, color='black', size=11,arrow=True)
                    i+=1
                i=1
                for id in (ggs1_open_wells,ggs2_open_wells,total_wells):
                    self.AnnotateDraw(ax_open_well, x=i, y=id, astring=str(id) + " Wells",
                                      x_offset=-50, y_offset=-10, color='black', size=11, arrow=True)
                    i+=1

                self.AnnotateDraw(ax,x=0.25,y=field_summary_list[-1],astring="Prod Date: "+str(max_prod_date).split(' ')[0],x_offset=20, y_offset=-10,size=15)
            except:
                pass

        canvas = FigureCanvas(self.Panel_dict['field_summary'], wx.NewId(), fig)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.GROW)
        self.Panel_dict['field_summary'].SetSizer(sizer)
        self._mgr.Update()

    def MapDataExtract(self):
        db = Gsrdb_Conn()
        daily_sum_prod=db.Sql("select max(production_date) from production_data ")

        for id in daily_sum_prod.fetchall():
            max_prod_date=id[0]

        max_prod_8clock=str(max_prod_date+datetime.timedelta(hours=8))
        next_max_prod_8clock = str(max_prod_date+datetime.timedelta(hours=8) + datetime.timedelta(days=1))



        field_data_cur=db.Sql("select avg(sum(production_gas)) from ggs_gtp5_5min_prod_table where "
                              "flag like 'WC_%' and production_Date between to_date('"+max_prod_8clock+"', 'yyyy/mm/dd hh24:mi:ss') and "
                                                                                                                     "to_date('"+next_max_prod_8clock+"','yyyy/mm/dd hh24:mi:ss') and"
                                                                                                                                                 " production_gas != 0 group by production_date")

        for id in field_data_cur.fetchall():
            sum_field_daily = id[0]
        field_cum_cur=db.Sql("select sum(daily_prod_gas)/1000 from ggs") # Unit is Mm3

        for id in field_cum_cur.fetchall():
            field_cum=id[0]

        cur_year = datetime.datetime.now().year
        min_cur_year = str(cur_year) + "/01/01"
        max_cur_year = str(cur_year) + "/12/31"

        year_cum_cur=db.Sql("select sum(daily_prod_gas)/1000 from ggs where production_date between to_date('"+min_cur_year+"', 'yyyy/mm/dd') and "
                                                                                                                     "to_date('"+max_cur_year+"','yyyy/mm/dd')")
        for id in year_cum_cur.fetchall():
            field_year_cum=id[0]


        total_well_cur=db.Sql("select count(*) from production_data where production_date=(select max(production_date) from production_data)")
        ggs1_open_well_cur=db.Sql("select count(*) from production_data where "
                                  "production_date=(select max(production_date) from production_data) and"
                                  " daily_prod_gas!=0 and wellid in (select wellid from well_header where ggs=1)")

        ggs2_open_well_cur = db.Sql("select count(*) from production_data where "
                                    "production_date=(select max(production_date) from production_data) and"
                                    " daily_prod_gas!=0 and wellid in (select wellid from well_header where ggs=2)")
        for id in total_well_cur.fetchall():
            total_wells=id[0]
        for id in ggs1_open_well_cur.fetchall():
            ggs1_open_wells=id[0]

        for id in ggs2_open_well_cur.fetchall():
                ggs2_open_wells = id[0]


        ggs_daily_prod_cur=db.Sql("select daily_prod_gas/10 from ggs where production_date=(select max(production_date) from ggs) order by ggs_no")
        ggs_daily_prod_list=[]
        for id in ggs_daily_prod_cur.fetchall():
            ggs_daily_prod_list.append(id[0])


        db.close()
        return max_prod_date,sum_field_daily,ggs_daily_prod_list,field_cum,field_year_cum,total_wells,ggs1_open_wells,ggs2_open_wells



if __name__=='__main__':
    test=ArcGisMapLoad(r'c:\test\test4.jpg')
