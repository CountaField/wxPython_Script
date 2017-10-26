import wx
import matplotlib
#matplotlib.interactive(True)
#matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import wx.lib.buttons as buttons
from Oracle_connection import Gsrdb_Conn
from DailyProdPlot import DailyProdMain
import wx.lib.agw.aui as aui
from PlotSample import PlotSample
import wx.grid
from PlotDraw import *
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DailyProdTable import DailyProdTable
from EventText import  EventText
import datetime
import time
import os
from multiprocessing import Process,Queue,Manager
from threading import Thread
from collections import OrderedDict
from PlotAttributeFrame import PlotAttributeFrame
from matplotlib.patches import Ellipse
from DailyProdPlot import SingleWellSummaryFrame
from LineSelectProcess import LineSelected
from mpldatacursor import datacursor
import calendar
import wx.lib.scrolledpanel as ScrolledPanel
from matplotlib.backends.backend_wx import  NavigationToolbar2Wx,wxc
import gc
import wx.aui
import numpy as np
import matplotlib.dates as mdate

class SingleWellProdReport(wx.MDIChildFrame):

    def __init__(self,parent=None):
        wx.MDIChildFrame.__init__(self, parent, -1, ' Production Data Summary', size=(4000, 4000))
        self.parent=parent
        self.daily_plot=False
        self.hist_plot=False
        self.inst_plot=False
        self.mpl_test =self
        self._mgr = aui.AuiManager(agwFlags=aui.AUI_MGR_ALLOW_ACTIVE_PANE)
        self._mgr.SetManagedWindow(self)
        self.pre_center_exist = False
        self.text3 = wx.TextCtrl(self, -1, "Main content window",
                                 wx.DefaultPosition, wx.Size(200, 150),
                                 wx.NO_BORDER | wx.TE_MULTILINE)
        self.Initializing()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnWellSelection, self.wells_tree_list)
        self.new_thread={}
        self.attribute_frame={}
        self.well_table={}
        self.attribute_Daily=False
        self.attribute_Hist = False
        self.attribute_Inst = False
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def Initializing(self):
        w,h=self.GetSize()
        self.main_map_nb = wx.aui.AuiNotebook(self,style=wx.aui.AUI_NB_TOP|wx.aui.AUI_NB_TAB_SPLIT  | wx.aui.AUI_NB_SCROLL_BUTTONS )
        self.Panel_dict = OrderedDict()

        self.Panel_dict['Inst_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Inst Plot Area')
        self.Panel_dict['Hist_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Hist Plot Area')
        self.Panel_dict['Pie_Plot_Area'] = wx.Panel(self, -1, name='Pie Plot Area')
        self.Panel_dict['Pie_Plot_Area_Yesterday'] = wx.Panel(self, -1, name='Pie Plot Area Yesterday',
                                                              )
        #self.Panel_dict['Pie_Plot_Area'] = wx.Panel(self, -1, name='Pie Plot Area',size=(w/4,h/4))
        self.Panel_dict['well_tree'] = wx.Panel(self, -1, name='Well Tree Selection', size=(200, 750))
        self.Panel_dict["Event_Output"] = wx.TextCtrl(self, -1, value='',
                                                      style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY,
                                                      name='Event Text')
        self.Panel_dict["Button_Area"]=ScrolledPanel.ScrolledPanel(self, -1, name='Advance Setting', size=(350, 750),style=wx.ALWAYS_SHOW_SB)
        self.Panel_dict["Button_Area"].SetupScrolling()
        self.Panel_dict["Event_Update"] = wx.Panel(self, -1, name='Event Update', size=(380, 400))
        self._mgr.AddPane(self.text3, aui.AuiPaneInfo().CenterPane())
        self.wells_tree_list = wx.TreeCtrl(self.Panel_dict['well_tree'], size=self.Panel_dict['well_tree'].GetSize())
        self.ClusterTreeList()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wells_tree_list)
        self.Panel_dict['well_tree'].SetSizer(sizer)
        self.ButtonAreaInitial()
        for id in self.Panel_dict:
            if id == 'well_tree':
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Left().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            elif id == "Event_Output":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Left().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            elif id == "Button_Area":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Right().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
                self.Panel_dict[id].SetScrollbar(wx.VERTICAL,0,200,1000)
            elif id=='Event_Update':
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Right().MinimizeButton(True).CloseButton(True).Resizable(resizable=True))
        self._mgr.AddPane(self.main_map_nb,aui.AuiPaneInfo().CentrePane().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
        #self.main_map_nb.AddPage(self.Panel_dict['Daily_Plot_Area'],'Daily Production Plot')
        self.main_map_nb.AddPage(self.Panel_dict['Hist_Plot_Area'], 'Monthly Histrical Prod Plot(5min)')
        self.main_map_nb.AddPage(self.Panel_dict['Inst_Plot_Area'], 'Instant prod 2day plot(1min)')
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED,self.OnHistPageChange,self.main_map_nb)
        ###print self.Panel_dict['Daily_Plot_Area'].GetSize()
        self.main_map_nb.Update()
        self.EventUpdateFrame()
        self._mgr.Update()
        self._mgr.DoFrameLayout()

    def ButtonAreaInitial(self):

        self.plot_list_name = ['Daily Plot Setting', 'Historical Plot Setting', 'Instant Plot Setting']
        self.button_area_control=OrderedDict()
        self.area_select_control=OrderedDict()
        #self.button_area_control['plot_choose'] = wx.StaticText(self.Panel_dict['Button_Area'], -1,label='Select Plot :')
        self.button_area_control['list_combobox']=wx.ComboBox(parent=self.Panel_dict['Button_Area'],id=-1,choices=self.plot_list_name,style=wx.CB_READONLY)
        #self.button_area_control['refreash_button']=wx.Button(self.Panel_dict['Button_Area'],-1,label='Plot Refresh')
        self.button_area_control['show_table_button']=wx.Button(self.Panel_dict['Button_Area'],-1,label='Check Table')
        self.button_area_control['well_info'] = wx.Button(self.Panel_dict['Button_Area'], -1,label='Summary Info')
        #self.button_area_control['plot_edit'] = wx.Button(self.Panel_dict['Button_Area'], -1, label='Edit Plot')
        #self.button_area_control['attribute_setting'] = wx.Button(self.Panel_dict['Button_Area'], -1,
         #                                                         label='Attribute Setup')
        #self.button_area_control['instant_create_button'] = wx.Button(self.Panel_dict['Button_Area'], -1,label='Show Instant Plot')
        start_date_txt=wx.StaticText(self.Panel_dict['Button_Area'], -1,label=' Start Date :')
        end_date_txt=wx.StaticText(self.Panel_dict['Button_Area'], -1,label=' End Date :')


        date_list=self.DateSelectInitial()
        self.area_select_control['start_date_combobox']=wx.ComboBox(parent=self.Panel_dict['Button_Area'],id=-1,choices=date_list)
        self.area_select_control['end_date_combobox'] = wx.ComboBox(parent=self.Panel_dict['Button_Area'], id=-1,
                                                                      choices=date_list)
        #Yaxis_setting_txt=wx.StaticText(self.Panel_dict['Button_Area'], -1,label='Y Axis Limit Setting')
        Yaxis_min = wx.StaticText(self.Panel_dict['Button_Area'], -1, label='Y Axis Min Value :')
        Yaxis_max=wx.StaticText(self.Panel_dict['Button_Area'], -1, label='Y Axis Max Value :')
        self.area_select_control['Y_min'] = wx.TextCtrl(parent=self.Panel_dict['Button_Area'], id=-1)
        self.area_select_control['Y_max'] = wx.TextCtrl(parent=self.Panel_dict['Button_Area'], id=-1)

        Ysec_axis_min = wx.StaticText(self.Panel_dict['Button_Area'], -1, label='Second Y Axis Min Value :')
        Ysec_axis_max = wx.StaticText(self.Panel_dict['Button_Area'], -1, label='Second Y Axis Max Value :')
        self.area_select_control['Ysec_min'] = wx.TextCtrl(parent=self.Panel_dict['Button_Area'], id=-1)
        self.area_select_control['Ysec_max'] = wx.TextCtrl(parent=self.Panel_dict['Button_Area'], id=-1)
        self.area_select_control['refreash_button'] = wx.Button(self.Panel_dict['Button_Area'], -1,
                                                                label='Plot Refresh')
        self.area_select_control['restore_button'] = wx.Button(self.Panel_dict['Button_Area'], -1,
                                                                label='Plot Restore')
        #self.button_area_control['plot_edit'].Disable()


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        for x in self.button_area_control:
            sizer.Add(self.button_area_control[x])
            sizer.AddSpacer(7)

        sizer.AddSpacer(55)
        sizer.Add(start_date_txt)
        sizer.Add(self.area_select_control['start_date_combobox'])
        sizer.Add(end_date_txt)
        sizer.Add(self.area_select_control['end_date_combobox'])

        sizer.AddSpacer(20)
        #sizer.Add(Yaxis_setting_txt)
        sizer.AddSpacer(5)
        sizer.Add(Yaxis_min)
        sizer.Add(self.area_select_control['Y_min'])
        sizer.AddSpacer(5)
        sizer.Add(Yaxis_max)
        sizer.Add(self.area_select_control['Y_max'])
        sizer.AddSpacer(20)
        # sizer.Add(Yaxis_setting_txt)
        sizer.AddSpacer(5)
        sizer.Add(Ysec_axis_min)
        sizer.Add(self.area_select_control['Ysec_min'])
        sizer.AddSpacer(5)
        sizer.Add(Ysec_axis_max)
        sizer.Add(self.area_select_control['Ysec_max'])
        sizer.AddSpacer(20)
        sizer.Add(self.area_select_control['refreash_button'])
        sizer.AddSpacer(5)
        sizer.Add(self.area_select_control['restore_button'])
        self.Panel_dict['Button_Area'].SetSizer(sizer)
        self.button_area_control['list_combobox'].SetSelection(self.plot_list_name.index('Daily Plot Setting'))
        #self.Bind(wx.EVT_BUTTON,self.OnShowInstantButton,self.button_area_control['instant_create_button'])
        #self.Bind(wx.EVT_BUTTON,self.OnAttributeButton,self.button_area_control['attribute_setting'])
        self.Bind(wx.EVT_BUTTON,self.OnPlotRefresh,self.area_select_control['refreash_button'])
        self.Bind(wx.EVT_BUTTON,self.OnRestoreButton,self.area_select_control['restore_button'])
        self.Bind(wx.EVT_BUTTON,self.OnCheckTable,self.button_area_control['show_table_button'])
        self.Bind(wx.EVT_BUTTON,self.OnSummaryInfoShow,self.button_area_control['well_info'])

    def DateSelectInitial(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cur=db.Sql('select production_date from raw_daily_production group by production_date order by production_date desc')
        prod_date_list=[]
        for id in cur.fetchall():
            prod_date_list.append(str(id[0]))
        db.close()

        return prod_date_list

    def OnCheckTable(self,event):
        w, h = self.GetSize()
        ##print w, h
        w2,h2=self.Panel_dict['Pie_Plot_Area'].GetSize()
        ##print w2,h2
        ##print self._mgr.GetManagedWindow()
        try:
            wellid = self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
        except:
            wellid=self.single_wellid


        #plot_select = self.button_area_control['list_combobox'].GetStringSelection()
        plot_select=self.main_map_nb.GetCurrentPage().GetName()
        #print 'plot_select',plot_select

        if self.area_select_control['start_date_combobox'].GetStringSelection() is not unicode(''):
            start_date = self.area_select_control['start_date_combobox'].GetStringSelection()
        else:
            start_date = None

        if self.area_select_control['end_date_combobox'].GetStringSelection() is not unicode(''):
            end_date = self.area_select_control['end_date_combobox'].GetStringSelection()
        else:
            end_date = None
        self.well_table[wellid]={}
        if 'Daily' in plot_select:
            table_name='vw_prod_all_ssoc'.upper()
            try:
                if self.well_table[wellid][plot_select]:
                    self.well_table[wellid][plot_select].TopLevel()

            except KeyError:

                self.well_table[wellid][plot_select]=self.CreateTable(wellid,table_name,start_date,end_date,plot_select)
                self.well_table[wellid][plot_select].Show()

        elif 'Hist' in plot_select:
            if self.vs_well==True:
                table_name='AUX_5MIN_DATA_KEEP_15DAY'
                try:
                    if self.well_table[wellid][plot_select]:
                        self.well_table[wellid][plot_select].TopLevel()

                except KeyError:

                    self.well_table[wellid][plot_select] = self.CreateTable(wellid, table_name, start_date, end_date,
                                                                            plot_select)
                    self.well_table[wellid][plot_select].Show()
            else:
                table_name = 'RAW_DAILY_INST_WH_PRES_HOUR'
                try:
                    if self.well_table[wellid][plot_select]:
                        self.well_table[wellid][plot_select].TopLevel()

                except KeyError:

                    self.well_table[wellid][plot_select] = self.CreateTable(wellid, table_name, start_date, end_date,
                                                                            plot_select)
                    self.well_table[wellid][plot_select].Show()
        if plot_select == 'Instant Plot Setting':
            table_name = 'raw_inst_data_keep_2day'.upper()
            try:
                if self.well_table[wellid][plot_select]:
                    self.well_table[wellid][plot_select].TopLevel()

            except KeyError:

                self.well_table[wellid][plot_select] = self.CreateTable(wellid, table_name, start_date, end_date,
                                                                        plot_select)
                self.well_table[wellid][plot_select].Show()

    def CreateTable(self, wellid, table_name, start_date, end_date, plot_select):
        ###print 'this is self.cid',self.cid

        frm = DailyProdTable(self.parent, wellid, table_name, start_date, end_date,table_title=plot_select)
        return frm

    def OnSummaryInfoShow(self,event):
        try:
            wellid = self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
        except:
            wellid=self.single_wellid
        frm=SingleWellSummaryFrame(self.parent,wellid)
        frm.Show()

    def OnShowInstantButton(self,event):
        if self.inst_plot==False:
            el = Ellipse((2, -1), 0.5, 0.5)
            self.main_map_nb.DeletePage(2)
            self.Panel_dict['Inst_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Instant Plot Area')


            try:
                wellid = self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
            except:
                wellid = self.single_wellid

            self.inst_prod_plot = PlotDrawing(parent=self, wellid=wellid, parameter_list=self.inst_par_list, cursor=None,
                                              Xaxis='PRODUCTION_DATE', Yaxis_list=self.inst_prod_ylist,
                                              Ysec_axis_list=self.inst_prod_ysec_list,
                                              prod_data_dict=self.inst_prod_dict[wellid],plot_type='inst')
            self.inst_prod_canvas = FigureCanvas(self.Panel_dict['Inst_Plot_Area'], wx.NewId(),
                                                 self.inst_prod_plot.ReturnObject())




            self.inst_plot_sample=PlotSample(parent=self, wellid=wellid, table_name='raw_inst_data_keep_2day')
            self.inst_plot_sample.X_Y_sec_Axis_list(parameter_list=self.inst_par_list, ysec_list=self.inst_prod_ysec_list)
            self.inst_plot_sample.LineTypeInitializing()

            self.inst_toolbar =  self.inst_plot_sample.add_toolbar(self.inst_prod_canvas)
            instplotsizer = wx.BoxSizer(wx.VERTICAL)
            instplotsizer.Add(self.inst_prod_canvas, 1, wx.GROW)
            instplotsizer.Add(self.inst_toolbar, 0, wx.BOTTOM | wx.GROW)
            self.Panel_dict['Inst_Plot_Area'].SetSizer(instplotsizer)

            self.inst_prod_legend_dict = OrderedDict()
            self.inst_prod_ax_dict = OrderedDict()
            try:
                for legline, origline in zip(self.inst_prod_plot.plot_legend.get_lines(),
                                             self.inst_prod_plot.plot_instance_dict.values()):
                    legline.set_picker(5)  # 5 pts tolerance
                    ##print 'legend test', legline
                    self.inst_prod_legend_dict[legline] = origline

                for axline, origaxline in zip(self.inst_prod_plot.axes2.get_lines(),
                                              self.inst_prod_plot.plot_instance_dict.values()):

                    self.inst_prod_ax_dict[axline] = origaxline

                self.inst_prod_plot.plot_legend.draggable(True)
            except:
                pass
            self.inst_plot_pick = self.inst_prod_canvas.mpl_connect('pick_event', self.OnInstPlotClick)
            #print "x len",len(self.inst_scatter_x_list),'y len',len(self.inst_scatter_y_list)
            if self.inst_scatter_x_list != [] and self.inst_scatter_y_list != []:
                i = 0
                for id in self.inst_scatter_x_list:
                    if self.inst_alarm_summary_dict[id][-1] is not None:
                        type_value = self.inst_alarm_summary_dict[id][-1]
                    else:
                        type_value = ' '
                    alarm_string = "Alarm Message: " + str(self.inst_alarm_summary_dict[id][0]) + "\nReptor Times: " + \
                                   str(self.inst_alarm_summary_dict[id][1]) + "\nType Value: " + type_value
                    yid = self.inst_scatter_y_list[i]
                    x_offset = -110
                    if i % 2 == 0:
                        y_offset = 100
                    else:
                        y_offset = -100

                    self.alarm_annotate[id] = self.inst_prod_plot.axes2.annotate(alarm_string, xy=(id, yid),
                                                                                 xycoords='data',
                                                                                 xytext=(x_offset, y_offset),
                                                                                 textcoords='offset points',
                                                                                 # x_offset=x_offset, y_offset=y_offset,
                                                                                 size=10, bbox=dict(boxstyle="round",
                                                                                                    fc=(1.0, 0.7, 0.7),
                                                                                                    ec=(1., .5, .5)),
                                                                                 arrowprops=dict(
                                                                                     arrowstyle="wedge,tail_width=1.",
                                                                                     fc=(1.0, 0.7, 0.7),
                                                                                     ec=(1., .5, .5),
                                                                                     patchA=None, patchB=el,
                                                                                     relpos=(0.2, 0.8),
                                                                                     connectionstyle="arc3,rad=-0.1")
                                                                                 )

                    i += 1
            area = np.pi * (15 * 0.3) ** 2
            self.inst_prod_plot.axes2.scatter(self.inst_scatter_x_list, self.inst_scatter_y_list, picker=5, s=area,
                                              c=['orange'] * len(self.inst_scatter_x_list))
            self.plot_default_value_dict['inst_default_x_min'] = self.inst_prod_plot.x_list[0]
            self.plot_default_value_dict['inst_default_x_max'] = self.inst_prod_plot.x_list[-1]
            self.plot_default_value_dict['inst_default_y_min'], self.plot_default_value_dict[
                'inst_default_y_max'] = self.inst_prod_plot.axes.get_ylim()
            self.plot_default_value_dict['inst_default_ysec_min'], self.plot_default_value_dict[
                'inst_default_ysec_max'] = self.inst_prod_plot.axes2.get_ylim()
            self.inst_prod_plot.axes.set_ylabel('Cainsg_Pressure Mpa, Pipeline_Temperature Celsius degree\n Pipeline_Pres_Diff Barg,Pipeline_ABS_Pressure Mpa\nWH_PRESSURE Mpa')
            self.inst_prod_plot.axes2.set_ylabel('Instant_Production_Gas km3/d')
            self.main_map_nb.InsertPage(2, self.Panel_dict['Inst_Plot_Area'], 'Instant prod 2day plot(1min)')
            self.main_map_nb.Update()
            self._mgr.Update()
            self.inst_plot = True

    def OnAttributeButton(self,event):
        plot_select=self.button_area_control['list_combobox'].GetStringSelection()
        wellid=self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
        if wellid not in self.attribute_frame.keys():
            self.attribute_frame[wellid]={}

        if plot_select=='Daily Plot Setting':
            if self.attribute_Daily==False:
                self.attribute_frame[wellid][plot_select] = PlotAttributeFrame(None, -1,self.daily_prod_plot,self.daily_prod_canvas,
                                                                       self.daily_plot_sample,self.daily_par_list,title=plot_select,
                                                                               datacursor_dict=self.daily_prod_datacursor_dict)
                self.attribute_frame[wellid][plot_select].Show()
                self.attribute_Daily=True
            else:
                self.attribute_frame[wellid][plot_select].Show()
        elif plot_select=='Historical Plot Setting':
            if self.attribute_Hist==False:
                self.attribute_frame[wellid][plot_select] = PlotAttributeFrame(None, -1,self.hist_prod_plot, self.hist_prod_canvas,
                                                                       self.hist_plot_sample, self.hist_par_list,title=plot_select)
                self.attribute_frame[wellid][plot_select].Show()
                self.attribute_Hist=True
            else:
                self.attribute_frame[wellid][plot_select].Show()

        elif plot_select=='Instant Plot Setting':
            if self.inst_plot==True:
                if self.attribute_Inst==False:
                    self.attribute_frame[wellid][plot_select] = PlotAttributeFrame(None, -1, self.inst_prod_plot,
                                                                                   self.inst_prod_canvas,
                                                                                   self.inst_plot_sample,
                                                                                   self.inst_par_list,
                                                                                   title=plot_select)
                    self.attribute_frame[wellid][plot_select].Show()
                    self.attribute_Inst = True
                else:
                    self.attribute_frame[wellid][plot_select].Show()

        ##print self.daily_prod_plot.plot_y_select_dict

    def GetDefaultPlotValue(self):
        self.plot_default_value_dict={}
        self.plot_default_value_dict['daily_default_x_min'] = self.daily_prod_plot.x_list[0]
        self.plot_default_value_dict['daily_default_x_max'] = self.daily_prod_plot.x_list[-1]
        self.plot_default_value_dict['daily_default_y_min'], self.plot_default_value_dict['daily_default_y_max'] = self.daily_prod_plot.axes.get_ylim()
        #self.plot_default_value_dict['daily_default_ysec_min'], self.plot_default_value_dict[
            #'daily_default_ysec_max'] = self.daily_prod_plot.axes2.get_ylim()
        '''self.plot_default_value_dict['hist_default_x_min'] = self.hist_prod_plot.x_list[0]
        self.plot_default_value_dict['hist_default_x_max'] = self.hist_prod_plot.x_list[-1]
        self.plot_default_value_dict['hist_default_y_min'], self.plot_default_value_dict[
            'hist_default_y_max'] = self.hist_prod_plot.axes.get_ylim()
        self.plot_default_value_dict['hist_default_ysec_min'], self.plot_default_value_dict[
            'hist_default_ysec_max'] = self.hist_prod_plot.axes2.get_ylim()'''

    def OnPlotRefresh(self,event):
        plot_select=self.button_area_control['list_combobox'].GetStringSelection()

        if self.area_select_control['start_date_combobox'].GetStringSelection() is not unicode(''):
            start_date=datetime.datetime.strptime(self.area_select_control['start_date_combobox'].GetStringSelection(),'%Y-%m-%d %H:%M:%S')
        else:
            start_date=None


        if self.area_select_control['end_date_combobox'].GetStringSelection() is not unicode(''):
            end_date=datetime.datetime.strptime(self.area_select_control['end_date_combobox'].GetStringSelection(),'%Y-%m-%d %H:%M:%S')
        else:
            end_date=None

        if self.area_select_control['Y_min'].GetValue() is not unicode(''):
            y_min=float(self.area_select_control['Y_min'].GetValue())
        else:
            y_min=None
        if self.area_select_control['Y_max'].GetValue() is not unicode(''):
            y_max=float(self.area_select_control['Y_max'].GetValue())
        else:
            y_max=None

        if self.area_select_control['Ysec_min'].GetValue() is not unicode(''):
            ysec_min=float(self.area_select_control['Ysec_min'].GetValue())
        else:
            ysec_min=None

        if self.area_select_control['Ysec_max'].GetValue() is not unicode(''):
            ysec_max = float(self.area_select_control['Ysec_max'].GetValue())
        else:
            ysec_max = None

        if plot_select=='Daily Plot Setting':
            if start_date is not None and end_date is not None:
                ##print start_date,end_date
                self.daily_prod_plot.axes.set_xlim(start_date,end_date)
            else:
                self.daily_prod_plot.axes.set_xlim(self.plot_default_value_dict['daily_default_x_min'],self.plot_default_value_dict['daily_default_x_max'])
            if y_min is not None and y_max is not None:
                self.daily_prod_plot.axes.set_ylim(y_min,y_max)

            else:
                self.daily_prod_plot.axes.set_ylim(self.plot_default_value_dict['daily_default_y_min'],
                                                   self.plot_default_value_dict['daily_default_y_max'])
            if ysec_min is not None and ysec_max is not None:
                self.daily_prod_plot.axes2.set_ylim(ysec_min, ysec_max)
            else:
                self.daily_prod_plot.axes2.set_ylim(self.plot_default_value_dict['daily_default_ysec_min'],
                                                   self.plot_default_value_dict['daily_default_ysec_max'])

            self.daily_prod_canvas.draw()

        elif plot_select=='Historical Plot Setting':
            if start_date is not None and end_date is not None:
                self.hist_prod_plot.axes.set_xlim(start_date, end_date)
            else:
                self.hist_prod_plot.axes.set_xlim(self.plot_default_value_dict['hist_default_x_min'],

                                                  self.plot_default_value_dict['hist_default_x_max'])
            if y_min is not None and y_max is not None:
                self.hist_prod_plot.axes.set_ylim(y_min, y_max)

            else:
                self.hist_prod_plot.axes.set_ylim(self.plot_default_value_dict['hist_default_y_min'],
                                                  self.plot_default_value_dict['hist_default_y_max'])
            if ysec_min is not None and ysec_max is not None:
                self.hist_prod_plot.axes2.set_ylim(ysec_min, ysec_max)
            else:
                self.hist_prod_plot.axes2.set_ylim(self.plot_default_value_dict['hist_default_ysec_min'],
                                                   self.plot_default_value_dict['hist_default_ysec_max'])

            self.hist_prod_canvas.draw()
        elif plot_select=='Instant Plot Setting':
            if start_date is not None and end_date is not None:
                self.inst_prod_plot.axes.set_xlim(start_date, end_date)
            else:
                self.inst_prod_plot.axes.set_xlim(self.plot_default_value_dict['inst_default_x_min'],
                                                   self.plot_default_value_dict['inst_default_x_max'])
            if y_min is not None and y_max is not None:
                self.inst_prod_plot.axes.set_ylim(y_min, y_max)

            else:
                self.inst_prod_plot.axes.set_ylim(self.plot_default_value_dict['inst_default_y_min'],
                                                  self.plot_default_value_dict['inst_default_y_max'])
            if ysec_min is not None and ysec_max is not None:
                self.inst_prod_plot.axes2.set_ylim(ysec_min, ysec_max)
            else:
                self.inst_prod_plot.axes2.set_ylim(self.plot_default_value_dict['inst_default_ysec_min'],
                                                   self.plot_default_value_dict['inst_default_ysec_max'])

            self.inst_prod_canvas.draw()

    def OnRestoreButton(self,event):

        plot_select = self.button_area_control['list_combobox'].GetStringSelection()
        if plot_select == 'Daily Plot Setting':
            self.daily_prod_plot.axes.set_ylim(self.plot_default_value_dict['daily_default_y_min'],
                                               self.plot_default_value_dict['daily_default_y_max'])

            self.daily_prod_plot.axes.set_xlim(self.plot_default_value_dict['daily_default_x_min'],
                                               self.plot_default_value_dict['daily_default_x_max'])

            self.daily_prod_plot.axes2.set_ylim(self.plot_default_value_dict['daily_default_ysec_min'],
                                               self.plot_default_value_dict['daily_default_ysec_max'])

            self.daily_prod_canvas.draw()

        elif plot_select == 'Historical Plot Setting':
            self.hist_prod_plot.axes.set_xlim(self.plot_default_value_dict['hist_default_x_min'],
                                              self.plot_default_value_dict['hist_default_x_max'])

            self.hist_prod_plot.axes.set_ylim(self.plot_default_value_dict['hist_default_y_min'],
                                              self.plot_default_value_dict['hist_default_y_max'])
            self.hist_prod_plot.axes2.set_ylim(self.plot_default_value_dict['hist_default_ysec_min'],
                                               self.plot_default_value_dict['hist_default_ysec_max'])
            self.hist_prod_canvas.draw()

        elif plot_select == 'Instant Plot Setting':
            self.inst_prod_plot.axes.set_xlim(self.plot_default_value_dict['inst_default_x_min'],
                                              self.plot_default_value_dict['inst_default_x_max'])

            self.inst_prod_plot.axes.set_ylim(self.plot_default_value_dict['inst_default_y_min'],
                                              self.plot_default_value_dict['inst_default_y_max'])
            self.inst_prod_plot.axes2.set_ylim(self.plot_default_value_dict['inst_default_ysec_min'],
                                               self.plot_default_value_dict['inst_default_ysec_max'])
            self.inst_prod_canvas.draw()

    def ClusterTreeList(self):
        ##print 'start import wellid'
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
        ##print 'finished import wellid'

    def DailyprodPrepare(self,wellid):

        if self.daily_plot==False:
            processid = os.getpid()
            self.Panel_dict['Daily_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Daily Plot Area')

            parameter="PRODUCTION_DATE,daily_prod_gas,well_head_pressure,casing_pressure," \
                          "well_head_temperature,prod_cum_gas,raw_daily_prod_gas,pipeline_pres_diff,bhp_barg,bht_degc".upper()
            self.daily_par_list = parameter.split(",")
            self.daily_prod_ylist=self.daily_par_list[:]
            self.daily_prod_ylist.remove('PRODUCTION_DATE')
            self.daily_prod_ylist.remove('prod_cum_gas'.upper())
            self.daily_prod_ylist.remove('casing_pressure'.upper())
            self.daily_prod_ylist.remove('daily_prod_Gas'.upper())
            self.daily_prod_ysec_list = ['prod_cum_gas'.upper(), 'casing_pressure'.upper(),'daily_prod_Gas'.upper()]
            self.DailyProdExtract(parameter,self.daily_par_list,wellid)

            self.daily_prod_canvas = FigureCanvas(self.Panel_dict['Daily_Plot_Area'], wx.NewId(),
                                                  self.daily_prod_plot.ReturnObject())
            self.daily_prod_datacursor_dict={}
            self.daily_toolbar = self.daily_plot_sample.add_toolbar(self.daily_prod_canvas)

            self.daily_prod_legend_dict=OrderedDict()
            self.daily_prod_ax_dict=OrderedDict()

            for legline, origline in zip(self.daily_prod_plot.plot_legend.get_lines(), self.daily_prod_plot.plot_instance_dict.values()):
                legline.set_picker(5)  # 5 pts tolerance
                ##print 'legend test',legline
                self.daily_prod_legend_dict[legline] = origline

            for axline,origaxline in zip(self.daily_prod_plot.axes2.get_lines(),self.daily_prod_plot.plot_instance_dict.values()):
                #print 'ax_line',axline
                self.daily_prod_ax_dict[axline] = origaxline

            ###print 'lines ',self.daily_prod_plot.plot_instance_dict.keys()
            self.daily_prod_plot.plot_legend.draggable(True)
            self.daily_plot_pick=self.daily_prod_canvas.mpl_connect('pick_event',self.OnLegendClick)
            self.daily_plot_click=self.daily_prod_canvas.mpl_connect('button_press_event',self.OnPlotRightClick)
            self.daily_plot_click = self.daily_prod_canvas.mpl_connect('motion_notify_event', self.OnPlotMove)
            for id in self.alarm_annotate.keys():
                self.alarm_annotate[id].draggable(state=True)
            plotsizer = wx.BoxSizer(wx.VERTICAL)
            plotsizer.Add(self.daily_prod_canvas, 1, wx.GROW)
            plotsizer.Add(self.daily_toolbar, 0, wx.BOTTOM | wx.GROW)
            self.Panel_dict['Daily_Plot_Area'].SetSizer(plotsizer)

            self.single_wellid=wellid
            self.main_map_nb.InsertPage(0, self.Panel_dict['Daily_Plot_Area'], 'Daily Production Plot', select=True)
            self.main_map_nb.Update()
            self._mgr.Update()
            self.daily_plot=True

    def InstprodPrepare(self,wellid):
        if self.inst_plot==False:
            start = time.clock()
            #self.button_area_control['instant_create_button'].SetLabel('Downloading '+wellid+' Inst Data...')
            #self.button_area_control['instant_create_button'].Disable()
            parameter ="production_date,instant_production_gas*24/1000 as instant_production_gas,casing_pressure,WH_pressure,pipeline_temperature,pipeline_pres_diff,pipeline_abs_pressure".upper()
            self.inst_par_list = parameter.split(",")

            for id in self.inst_par_list:
                if 'instant_production'.upper() in id:
                    self.inst_par_list[self.inst_par_list.index(id)]='instant_production_gas'.upper()


            self.inst_prod_ylist = self.inst_par_list[:]

            self.inst_prod_ylist.remove('PRODUCTION_DATE')
            self.inst_prod_ylist.remove('INSTANT_PRODUCTION_GAS')
            self.inst_prod_ysec_list=['INSTANT_PRODUCTION_GAS']
            self.InstProdExtract(parameter,self.inst_par_list,wellid)
            try:
                self.button_area_control['instant_create_button'].Enable()
                self.button_area_control['instant_create_button'].SetLabel('Show Instant Data Plot')
            except Exception:
                ##print 'exception is detective.....'
                pass

            end = time.clock()
            ###print 'sub threading running time is %f ' % (end - start)

    def HistoricalprodPrepare(self,wellid):
        if self.hist_plot==False:
            self.main_map_nb.DeletePage(1)
            self.Panel_dict['Hist_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Hist Plot Area')

            db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
            vs_wells_list = []
            vs_wells_cur = db.Sql('SELECT WELLID FROM ALLOCATION_DHC WHERE DHC_TYPE=\'VS\' GROUP BY WELLID ORDER BY WELLID')
            for id in vs_wells_cur.fetchall():
                vs_wells_list.append(id[0])
            db.close()


            if wellid in vs_wells_list:
                self.vs_well=True
                table_name = 'AUX_5MIN_DATA_KEEP_15DAY'
                self.hist_plot_sample = PlotSample(parent=self, wellid=wellid, table_name=table_name)
                now_date=datetime.datetime.now()
                month_ago_date=now_date-datetime.timedelta(days=30)
                query_cur = self.hist_plot_sample.PlotCursor(wellid, table_name,min_date=str(month_ago_date).split('.')[0],max_date=str(now_date).split('.')[0])[0]

                self.hist_par_list = self.hist_plot_sample.PlotCursor(wellid, table_name)[1]
                self.hist_prod_ylist=self.hist_par_list[:]
                self.hist_prod_ylist.remove('INSTANT_PRODUCTION_GAS')
                self.hist_prod_ysec_list=['INSTANT_PRODUCTION_GAS']
            else:
                self.vs_well = False
                table_name = 'RAW_DAILY_INST_WH_PRES_HOUR'
                self.hist_plot_sample = PlotSample(parent=self, wellid=wellid, table_name=table_name)
                query_cur = self.hist_plot_sample.PlotCursor(wellid, table_name)[0]
                self.hist_par_list = self.hist_plot_sample.PlotCursor(wellid, table_name)[1]
                self.hist_prod_ylist = self.hist_par_list[:]
                self.hist_prod_ylist.remove('INSTANT_PRODUCTION_GAS_HOUR')
                self.hist_prod_ysec_list = ['INSTANT_PRODUCTION_GAS_HOUR']

            self.hist_prod_ylist.remove('PRODUCTION_DATE')
            self.HistProdExtract(wellid,query_cur,table_name)
            self.hist_prod_canvas = FigureCanvas(self.Panel_dict['Hist_Plot_Area'], wx.NewId(),
                                                self.hist_prod_plot.ReturnObject())
            '''for x in self.hist_prod_plot.axes.get_lines():
                datacursor(x,draggable=True)
            for x in self.hist_prod_plot.axes2.get_lines():
                datacursor(x,draggable=True)'''
            self.hist_toolbar = self.hist_plot_sample.add_toolbar(self.hist_prod_canvas)
            self.hist_plot_sample.LineTypeInitializing()
            self.hist_plot_sample.X_Y_sec_Axis_list(parameter_list=self.hist_par_list,ysec_list=self.hist_prod_ysec_list)
            histplotsizer = wx.BoxSizer(wx.VERTICAL)
            histplotsizer.Add(self.hist_prod_canvas, 1, wx.GROW)
            histplotsizer.Add(self.hist_toolbar, 0, wx.BOTTOM | wx.GROW)

            self.hist_prod_legend_dict = OrderedDict()
            self.hist_prod_ax_dict = OrderedDict()

            for legline, origline in zip(self.hist_prod_plot.plot_legend.get_lines(), self.hist_prod_plot.plot_instance_dict.values()):
                legline.set_picker(5)  # 5 pts tolerance
                ##print 'legend test',legline
                self.hist_prod_legend_dict[legline] = origline

            for axline, origaxline in zip(self.hist_prod_plot.axes2.get_lines(),
                                          self.hist_prod_plot.plot_instance_dict.values()):
                ##print 'ax_line', axline
                self.hist_prod_ax_dict[axline] = origaxline

            self.hist_prod_plot.plot_legend.draggable(True)
            self.hist_plot_pick = self.hist_prod_canvas.mpl_connect('pick_event', self.OnHistPlotClick)
            self.hist_plot_click = self.hist_prod_canvas.mpl_connect('button_press_event', self.OnPlotRightClick)
            self.Panel_dict['Hist_Plot_Area'].SetSizer(histplotsizer)
            self.Panel_dict['Hist_Plot_Area'].SetAutoLayout(True)
            ##print 'auto lay out',self.Panel_dict['Hist_Plot_Area'].GetAutoLayout()
            self.hist_plot=True
            self.main_map_nb.InsertPage(1, self.Panel_dict['Hist_Plot_Area'], 'Monthly Histrical Prod Plot(5min)')
            self.main_map_nb.Update()
            self._mgr.Update()

    def DailyProdExtract(self,parameter,daily_par_list,wellid):
        ##print('prod data prepare process id',os.getpid())
        el = Ellipse((2, -1), 0.5, 0.5)
        self.alarm_annotate={}
        self.daily_comments_list=[]
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        daily_prod_cur=db.Sql("select "+parameter+" from vw_prod_all_ssoc where wellid=\'"+wellid+"\' order by production_date")
        dhc_extract_cur=db.Sql("select allocated_rate from allocation_dhc where wellid=\'"+wellid+"\' and allocated_rate is not null ")
        orifice_plate_cur=db.Sql("select orifice_plate from well_header where wellid = \'"+wellid+"\' and orifice_plate is not null")
        prod_start_date_cur=db.Sql("select production_start_date from well_header where wellid=\'"+wellid+"\' and production_start_date is not null")
        alarm_extract_cur=db.Sql("select * from alarm_summary_table where wellid='"+wellid+"' order by detected_date")
        comment_cur=db.Sql("select production_date,prod_comments,daily_prod_gas,prod_cum_gas from vw_prod_all_ssoc where wellid='"+wellid+"' and prod_comments is not null order by production_date")

        self.daily_alarm_summary_dict={}
        ##print 'this is wellid',wellid
        self.daily_prod_dict={}
        area = np.pi * (15 * 0.3) ** 2
        for parameter in daily_par_list:
            self.daily_prod_dict[parameter]=[]
        for id in daily_prod_cur.fetchall():
            i=0
            for par in  daily_par_list:
                self.daily_prod_dict[par].append(id[i])
                i+=1
        allocate_rate=''
        for id in dhc_extract_cur.fetchall():
            allocate_rate=id[0]
        orifice_plate=''
        for id in orifice_plate_cur.fetchall():
            if id[0] is not None or id[0]!='0':
                orifice_plate=id[0]
            else:
                orifice_plate='Unknown'
        prod_start_date=''
        for id in prod_start_date_cur.fetchall():
            if id[0] is not None:
                prod_start_date=id[0]

        for id in alarm_extract_cur.fetchall():
            year=id[1].year
            month=id[1].month
            day=id[1].day
            date=datetime.datetime(year,month,day,0,0,0)
            self.daily_alarm_summary_dict[date] = []
            i=2
            for x in id[2:]:
                self.daily_alarm_summary_dict[date].append(id[i])
                i+=1
        comments_prod=[]
        comments_value=OrderedDict()
        comments_prod_cum=[]
        comments_filter_list=[]
        i=0

        for id in comment_cur.fetchall():
            comments_filter_list.append(id[1])
            if i>0:
                if comments_filter_list[i]!=comments_filter_list[i-1]:
                    comments_value[id[0]]=id[1]
                    comments_prod.append(id[2])
                    comments_prod_cum.append(id[3])
            i+=1


        scatter_x_list=[]
        scatter_y_list=[]

        for x in self.daily_alarm_summary_dict.keys():
            scatter_x_list.append(x)
            if x in self.daily_prod_dict['PRODUCTION_DATE']:
                index=self.daily_prod_dict['PRODUCTION_DATE'].index(x)
                scatter_y_list.append(self.daily_prod_dict['DAILY_PROD_GAS'][index])


        ##print self.daily_prod_dict.keys()
        db.close()
        ##print 'ploting.....'
        self.daily_prod_plot = PlotDrawing(parent=self, wellid=wellid, parameter_list=self.daily_par_list, cursor=None,
                                           Xaxis='PRODUCTION_DATE', Yaxis_list=self.daily_prod_ylist,
                                           Ysec_axis_list=self.daily_prod_ysec_list,
                                           prod_data_dict=self.daily_prod_dict,plot_type='daily')
        self.daily_plot_sample=PlotSample(parent=self, wellid=wellid, table_name="VW_PROD_ALL_SSOC")
        self.daily_plot_sample.X_Y_sec_Axis_list(parameter_list=daily_par_list,ysec_list=self.daily_prod_ysec_list)
        self.daily_plot_sample.LineTypeInitializing()
        self.daily_prod_plot.axes.set_ylabel('WHP Bara,Raw_Daily_Prod km3/d,\nPipeline_Pres_Diff Barg,WHT Celsius degree')
        self.daily_prod_plot.axes2.set_ylabel('Daily_Prod_Gas km3/d, Casing_Pressure Barg\nProd_Cum_Gas Mm3')
        try:
            y_max_value = self.daily_prod_plot.axes.get_ylim()[1] * 0.7
            op_y_max_value = self.daily_prod_plot.axes.get_ylim()[1] * 0.6
            psd_y_max_value= self.daily_prod_plot.axes.get_ylim()[1] *                       0.5
            x_min_value=self.daily_prod_plot.x_list[int(len(self.daily_prod_plot.x_list)*0.2)]
            ###print 'this is x min value', x_min_value
            ##print 'this is y _max value', y_max_value
            self.AnnotateDraw(self.daily_prod_plot.axes, x_min_value, y_max_value,
                              'Allocated Rate: ' + str(allocate_rate) + ' Km3/d', color='blue', size=14, x_offset=20,
                              y_offset=-200)
            self.AnnotateDraw(self.daily_prod_plot.axes, x_min_value, op_y_max_value,
                              'Orifice Plate Range: ' + str(orifice_plate) + " Km3/d", color='red', size=14, x_offset=20,
                              y_offset=-200)
            self.AnnotateDraw(self.daily_prod_plot.axes, x_min_value, psd_y_max_value,
                              'Production Start Date: ' + str(prod_start_date) , color='black', size=14,
                              x_offset=20,
                              y_offset=-200)

            if scatter_x_list!=[] and scatter_y_list!=[]:
                i=0
                for id in scatter_x_list:
                    if self.daily_alarm_summary_dict[id][-1] is not None:
                        type_value=self.daily_alarm_summary_dict[id][-1]
                    else:
                        type_value=' '
                    alarm_string="Alarm Message: "+str(self.daily_alarm_summary_dict[id][0])+"\nReptor Times: "+\
                                 str(self.daily_alarm_summary_dict[id][1])+"\nType Value: "+type_value
                    yid=scatter_y_list[i]
                    x_offset=-110
                    if i%2==0:
                        y_offset=100
                    else:
                        y_offset =-100



                    self.alarm_annotate[id]=self.daily_prod_plot.axes.annotate(alarm_string,xy=(id,yid),
                                                                               xycoords='data',
                                                                               xytext=(x_offset, y_offset),
                                                                               textcoords='offset points',
                                                                               #x_offset=x_offset, y_offset=y_offset,
                                                                               size=10,bbox=dict(boxstyle="round",fc=(1.0, 0.7, 0.7),ec=(1., .5, .5)),
                                                                               arrowprops=dict(arrowstyle="wedge,tail_width=1.",fc=(1.0, 0.7, 0.7), ec=(1., .5, .5),
                                                                                               patchA=None,patchB=el,relpos=(0.2, 0.8),
                                                                                               connectionstyle="arc3,rad=-0.1")
                                                                               )

                    i+=1

            self.daily_prod_plot.axes.scatter(scatter_x_list, scatter_y_list, picker=5, s=area,
                                          c=['black'] * len(scatter_x_list))


        except :
            pass
        self.daily_comments_scatter_dict = {}
        self.daily_comments_scatter_list=[]

        i = 0
        for id in comments_value.keys():
            try:
                point=self.daily_prod_plot.axes2.scatter(id, comments_prod[i], picker=5, s=area,c=['orange'] * len(scatter_x_list))
                comment_string=str(id).split(' ')[0]+"\n"+comments_value[id]
                annotate = self.daily_prod_plot.axes2.annotate(comment_string, xy=(id, comments_prod[i]),
                                                              xycoords='data',
                                                              xytext=(30, 30),
                                                              textcoords='offset points',
                                                              # x_offset=x_offset, y_offset=y_offset,
                                                              size=10, bbox=dict(boxstyle="round",
                                                                                 fc='orange',
                                                                                 ec='black',
                                                                                 linewidth=2

                                                                                 ),
                                                              arrowprops=dict(
                                                                  arrowstyle="wedge,tail_width=1.",
                                                                  fc='gray', ec='black',
                                                                  patchA=None, patchB=el,
                                                                  relpos=(0.2, 0.8),
                                                                  connectionstyle="arc3,rad=-0.1")
                                                              )
                annotate.set_visible(False)
                self.daily_comments_scatter_list.append((point,annotate))
            except:
                pass
            i += 1

    def  InstProdExtract(self,parameter,inst_par_list,wellid):
        start = time.clock()
        el = Ellipse((2, -1), 0.5, 0.5)
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        pres_time=time.localtime()
        present_date=datetime.datetime(*pres_time[0:6])
        ##print present_date
        month_delta=datetime.timedelta(-1)
        pre_date=present_date+month_delta
        cur_date_string=present_date.strftime('%Y/%m/%d %H:%M:%S')
        prv_date_string=pre_date.strftime('%Y/%m/%d %H:%M:%S')
        ##print 'date scope',cur_date_string,prv_date_string
        inst_prod_cur = db.Sql("select " + parameter + " from raw_inst_data_keep_2day where"
                                                       " wellid=\'" + wellid + "\' order by production_date")
        now_date=datetime.datetime.now()
        last_two_day=now_date-datetime.timedelta(days=2)

        alarm_extract_cur = db.Sql(
            "select * from alarm_2hour_report_table where"
            " wellid='" + wellid + "' and production_date>to_date('"+str(last_two_day).split('.')[0]+"','yyyy/mm/dd hh24:mi:ss') order by production_date")





        self.inst_prod_dict={}
        self.inst_prod_dict[wellid]={}
        self.inst_alarm_summary_dict={}
        for parameter in inst_par_list:

            self.inst_prod_dict[wellid][parameter] = []

        for id in inst_prod_cur.fetchall():
            i = 0
            for par in inst_par_list:
                try:
                    self.inst_prod_dict[wellid][par].append(id[i])
                    i += 1
                except KeyError:
                    pass
                finally:
                    pass


        for id in alarm_extract_cur.fetchall():

            date=id[1]
            self.inst_alarm_summary_dict[date] = []
            i=2
            for x in id[2:]:
                self.inst_alarm_summary_dict[date].append(id[i])
                i+=1


        self.inst_scatter_x_list=[]
        self.inst_scatter_y_list=[]

        for x in self.inst_alarm_summary_dict.keys():
            self.inst_scatter_x_list.append(x)
            if x in self.inst_prod_dict[wellid]['PRODUCTION_DATE']:
                index=self.inst_prod_dict[wellid]['PRODUCTION_DATE'].index(x)
                self.inst_scatter_y_list.append(self.inst_prod_dict[wellid]['INSTANT_PRODUCTION_GAS'][index])

        db.close()

        end = time.clock()

    def HistProdExtract(self,wellid,query_cur,table_name):
        start = time.clock()
        try:
            if table_name == 'AUX_5MIN_DATA_KEEP_15DAY':
                self.hist_prod_plot = PlotDrawing(parent=self, wellid=wellid, parameter_list=self.hist_par_list, cursor=query_cur,
                                        Xaxis='PRODUCTION_DATE', Yaxis_list=self.hist_prod_ylist, Ysec_axis_list=self.hist_prod_ysec_list,
                                        time_data_unit='MINUTE',plot_type='hist')


            elif table_name == 'RAW_DAILY_INST_WH_PRES_HOUR':
                self.hist_prod_plot = PlotDrawing(parent=self, wellid=wellid, parameter_list=self.hist_par_list, cursor=query_cur,
                                        Xaxis='PRODUCTION_DATE', Yaxis_list=self.hist_prod_ylist, Ysec_axis_list=self.hist_prod_ysec_list,
                                        time_data_unit='HOUR',plot_type='hist')

            self.hist_prod_plot.axes.set_ylabel('Cainsg_Pressure Mpa, Pipeline_Temperature Celsius degree\n Pipeline_Pres_Diff Barg,Pipeline_ABS_Pressure Mpa\nWH_PRESSURE Mpa')
            self.hist_prod_plot.axes2.set_ylabel('Instant_Production_Gas km3/d')
            end = time.clock()
        except:
            pass
        ##print 'running time is %f ' % (end - start)

    def InstNewThreadExtract(self,wellid):
        self.new_thread[wellid]=Thread(target=self.InstprodPrepare,args=(wellid,))
        self.new_thread[wellid].start()

    def OnWellSelection(self, event):
        start = time.clock()
        try:
            wellid = self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
        except:
            wellid = self.single_wellid
        self.searched = False
        self.attribute_Daily=False
        self.attribute_Hist=False

        w,h=self.GetSize()

        if 'SN' in wellid or 'SUN003' in wellid:
            self.Panel_dict['Event_Output'].Clear()
            self.wellid = wellid

            if self.pre_center_exist == False:
                self._mgr.DetachPane(self.text3)
                self.text3.Destroy()
                self.inst_plot=False
                try:
                    self.DailyprodPrepare(wellid)

                    self.PiePlotShow(wellid)
                    self.InstNewThreadExtract(wellid)
                except:
                    pass
                ##print 'processing.....', self.daily_prod_canvas
                piesizer=wx.BoxSizer(wx.VERTICAL)
                piesizer1 = wx.BoxSizer(wx.VERTICAL)

                piesizer.Add(self.pie_canvas,1,wx.GROW)
                piesizer1.Add(self.pie_canvas_yesterday, 1, wx.GROW)

                self.pie_toolbar=NavigationToolbar2Wx(self.pie_canvas)
                self.pie_yesterday_toolbar=NavigationToolbar2Wx(self.pie_canvas_yesterday)
                self.pie_toolbar.Realize()
                self.pie_yesterday_toolbar.Realize()
                self.pie_toolbar.update()
                self.pie_yesterday_toolbar.update()
                piesizer.Add(self.pie_toolbar, 0, wx.BOTTOM | wx.GROW)
                piesizer1.Add(self.pie_yesterday_toolbar, 0, wx.BOTTOM | wx.GROW)


                self.Panel_dict['Pie_Plot_Area'].SetSize((200,200))
                self.Panel_dict['Pie_Plot_Area_Yesterday'].SetSize((200,200))

                self.Panel_dict['Pie_Plot_Area'].SetSizer(piesizer)
                self.Panel_dict['Pie_Plot_Area_Yesterday'].SetSizer(piesizer1)


                w,h=self.GetSize()
                '''self._mgr.AddPane(self.Panel_dict['Daily_Plot_Area'], aui.AuiPaneInfo().Name('Daily_Plot').Center().CloseButton(False).MinimizeButton(True))
                pie_pane=self._mgr.AddPane(self.Panel_dict['Pie_Plot_Area'], aui.AuiPaneInfo().Center().
                                           Top().CloseButton(False).MinimizeButton(True))'''
                self._mgr.AddPane(self.Panel_dict['Pie_Plot_Area_Yesterday'], aui.AuiPaneInfo().Center().
                                  Top().CloseButton(False).MinimizeButton(True))
                '''self._mgr.AddPane(self.Panel_dict['Hist_Plot_Area'], aui.AuiPaneInfo().Center().PinButton(True).CloseButton(False).MinimizeButton(True))'''

                self.Panel_dict['Event_Output'].AppendText(EventText(wellid=self.wellid).DBQuery())
                self._mgr.Update()
                self.pre_center_exist = True
                end = time.clock()
                ##print 'running time is %f ' % (end - start)
                ##print self._mgr.GetPaneByName('Daily_Plot')
            else:
                ##print 'pre_center',self.pre_center_exist

                self.daily_plot=False
                self.main_map_nb.DeletePage(2)
                self.main_map_nb.DeletePage(1)
                self.main_map_nb.DeletePage(0)
                self.main_map_nb.Update()
                self.DailyprodPrepare(wellid)

                if self.hist_plot==True:
                    del self.hist_par_list
                    del self.hist_plot_sample
                    del self.hist_prod_canvas
                    del self.hist_prod_plot
                    #self.main_map_nb.DeletePage(1)
                    gc.collect()
                    self.hist_plot=False
                self.Panel_dict['Hist_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Hist Plot Area')
                self.main_map_nb.InsertPage(1, self.Panel_dict['Hist_Plot_Area'], 'Monthly Histrical Prod Plot(5min)')



                if self.inst_plot==True:
                    del self.inst_par_list
                    del self.inst_plot
                    del self.inst_plot_sample
                    del self.inst_prod_canvas
                    #self.main_map_nb.DeletePage(2)
                    gc.collect()
                    self.inst_plot=False
                self.Panel_dict['Inst_Plot_Area'] = wx.Panel(self.main_map_nb, -1, name='Inst Plot Area')
                self.main_map_nb.InsertPage(2, self.Panel_dict['Inst_Plot_Area'], 'Instant prod 2day plot(1min)')


                self._mgr.DetachPane(self.Panel_dict['Pie_Plot_Area'])
                self._mgr.DetachPane(self.Panel_dict['Pie_Plot_Area_Yesterday'])

                try:
                    self.pie_canvas.Destroy()
                    self.pie_canvas_yesterday.Destroy()
                    self.pie_toolbar.Destroy()
                    self.pie_yesterday_toolbar.Destroy()
                except:
                    pass

                if self.inst_plot==True:
                    self._mgr.DetachPane(self.Panel_dict['Inst_Plot_Area'])
                    self.inst_prod_canvas.Destroy()
                    self.inst_toolbar.Destroy()
                    self.inst_plot=False

                for x in self.new_thread:
                    if self.new_thread[x].isAlive():
                        self.new_thread[x]._Thread__stop()
                        try:
                            self.inst_prod_dict.clear()
                        except AttributeError:
                            pass
                try:

                    self.PiePlotShow(wellid)
                    self.InstNewThreadExtract(wellid)
                    ##print 'step1'''
                    piesizer = wx.BoxSizer(wx.VERTICAL)
                    piesizer1 = wx.BoxSizer(wx.VERTICAL)
                    piesizer.Add(self.pie_canvas, 1, wx.GROW)
                    piesizer1.Add(self.pie_canvas_yesterday,1,wx.GROW)
                    self.pie_toolbar = NavigationToolbar2Wx(self.pie_canvas)
                    self.pie_yesterday_toolbar = NavigationToolbar2Wx(self.pie_canvas_yesterday)
                    self.pie_toolbar.Realize()
                    self.pie_yesterday_toolbar.Realize()
                    self.pie_toolbar.update()
                    self.pie_yesterday_toolbar.update()
                    piesizer.Add(self.pie_toolbar, 0, wx.BOTTOM | wx.GROW)
                    piesizer1.Add(self.pie_yesterday_toolbar, 0, wx.BOTTOM | wx.GROW)
                    self.Panel_dict['Pie_Plot_Area'].SetSize((w / 4, h / 4))
                    self.Panel_dict['Pie_Plot_Area_Yesterday'].SetSize((w / 4, h / 4))
                    self.Panel_dict['Pie_Plot_Area'].SetSizer(piesizer)
                    self.Panel_dict['Pie_Plot_Area_Yesterday'].SetSizer(piesizer1)
                    ##print 'step2'

                    self._mgr.AddPane(self.Panel_dict['Pie_Plot_Area'],
                                      aui.AuiPaneInfo().Center().Top().CloseButton(False).MinimizeButton(True))

                    self._mgr.AddPane(self.Panel_dict['Pie_Plot_Area_Yesterday'], aui.AuiPaneInfo().Center().
                                      Top().CloseButton(False).MinimizeButton(True))

                    self.Panel_dict['Event_Output'].AppendText(EventText(wellid=self.wellid).DBQuery())
                    self.main_map_nb.Update()
                    self._mgr.Update()
                except:
                   pass
        try:
            self.GetDefaultPlotValue()
        except AttributeError:
            pass
        ##print'its finished'

    def EventUpdateFrame(self):
        self.notetext = wx.TextCtrl(self.Panel_dict['Event_Update'], -1, value='', style=wx.TE_MULTILINE | wx.TE_RICH2,
                                    name='Event Update')
        year_list = []
        month_list = []
        date_list = []
        for year in range(2010, 2021):
            year_list.append(str(year))
        for month in range(1, 13):
            month_list.append(str(month))
        for date in range(1, 32):
            date_list.append(str(date))
        year = wx.StaticText(self.Panel_dict['Event_Update'], -1, 'Year:')
        month = wx.StaticText(self.Panel_dict['Event_Update'], -1, 'Month:')
        day = wx.StaticText(self.Panel_dict['Event_Update'], -1, 'Day:')
        self.yeartext = wx.ComboBox(self.Panel_dict['Event_Update'], -1, choices=year_list)
        self.monthtext = wx.ComboBox(self.Panel_dict['Event_Update'], -1, choices=month_list)
        self.daytext = wx.ComboBox(self.Panel_dict['Event_Update'], -1, choices=date_list)
        self.today = wx.CheckBox(self.Panel_dict['Event_Update'], -1, 'Present Date')
        self.Bind(wx.EVT_CHECKBOX, self.OnTodayButtonClick, self.today)
        updatebutton = wx.Button(self.Panel_dict['Event_Update'], -1, 'Update')
        self.Bind(wx.EVT_BUTTON, self.OnEventUpdateClick, updatebutton)
        sizer_date = wx.BoxSizer(wx.HORIZONTAL)
        sizer_date.AddSpacer(5)
        sizer_date.Add(year)
        sizer_date.Add(self.yeartext)
        sizer_date.AddSpacer(5)
        sizer_date.Add(month)
        sizer_date.Add(self.monthtext)
        sizer_date.AddSpacer(5)
        sizer_date.Add(day)
        sizer_date.Add(self.daytext)
        sizer_date.AddSpacer(15)
        sizer_date.Add(self.today)
        sizer_date.AddSpacer(25)
        sizer_final = wx.BoxSizer(wx.VERTICAL)
        sizer_final.AddSpacer(15)
        sizer_final.Add(sizer_date)
        sizer_final.Add(updatebutton)
        sizer_final.AddSpacer(15)
        sizer_final.Add(self.notetext, 1, flag=wx.GROW)
        self.Panel_dict['Event_Update'].SetSizer(sizer_final)

    def OnTodayButtonClick(self,event):
        if self.today.IsChecked()==True:
            self.yeartext.Disable()
            self.monthtext.Disable()
            self.daytext.Disable()
            self.prod_date=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        else:
            self.yeartext.Enable()
            self.monthtext.Enable()
            self.daytext.Enable()

    def OnEventUpdateClick(self,event):

        if self.notetext.GetValue()=='':
            alert_box = wx.MessageDialog(self, 'Yo!! stupid girl or boy, Enter Event first!!', style=wx.YES_NO | wx.ICON_WARNING)
        else:
            if self.prod_date=='':
                year=self.yeartext.GetStringSelection()
                month=self.monthtext.GetStringSelection()
                day=self.daytext.GetStringSelection()
                self.prod_date=year+'-'+month+'-'+day+' '+'00:00:00'

            column='wellid,note_date,events'
            tablename='well_event'
            wellid="\'"+self.wellid+"\'"
            prod_date="to_date(\'"+self.prod_date+"\',\'yyyy-mm-dd hh24:mi:ss\') "
            content_text="\'"+self.notetext.GetValue()+"\'"
            content=wellid+','+prod_date+','+content_text
            EventText(self,wellid=self.wellid,tablename=tablename).DBWrite\
                (wellid=self.wellid,tablename=tablename,column=column,content=content)
            self.Panel_dict['Event_Output'].Clear()
            self.Panel_dict['Event_Output'].AppendText(EventText(wellid=self.wellid).DBQuery())

    def AnnotateDraw(self,ax,x,y,text,color,size,x_offset=-80,y_offset=30,arrow=False):
        if arrow==False:
            atext=ax.annotate(text, xy=(x, y), xycoords='data',xytext=(x_offset, 30),
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

    def PiePlotDataExtract(self,wellid):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')

        '''Total Production Statistic'''

        total_days_cur=db.Sql("select production_start_date from well_header where wellid='"+wellid+"'")
        current_date_cur=db.Sql("select max(production_date) from raw_daily_production")
        prod_days_cur=db.Sql("select max(cum_days) from cum_prod_aux where wellid='"+wellid+"'")
        local_time=time.localtime()
        local_year=local_time.tm_year


        for id in current_date_cur.fetchall():
            current_date = id[0]
        for id in total_days_cur.fetchall():
            start_date = id[0]

        for id in prod_days_cur.fetchall():
            prod_days = id[0]
        try:
            total_days = (current_date - start_date).days
            ##print current_date
        except UnboundLocalError:
            pass

        '''# Year Production Statistic'''

        year_start_date=datetime.datetime(year=local_year,month=1,day=1)
        year_end_date=datetime.datetime(year=local_year,month=12,day=31)
        year_total_days=(year_end_date-year_start_date).days
        year_start_str=str(year_start_date)

        year_prod_cur = db.Sql("select count(*) from production_data where "
                               "wellid='" + wellid + "' and "
                                                     "production_date > to_date('"+year_start_str+"','yyyy/mm/dd hh24:mi:ss') and "
                                                                                                  "daily_prod_gas>0")
        year_no_prod_cur=db.Sql("select count(*) from production_data where "
                                "wellid='" + wellid + "' and "
                                                      "production_date > to_date('"+year_start_str+"','yyyy/mm/dd hh24:mi:ss') and "
                                                                                                   "daily_prod_gas=0")


        year_remaining_days=(year_end_date-current_date).days

        for id in year_no_prod_cur.fetchall():
            year_no_prod_count=id[0]


        for id in year_prod_cur.fetchall():
            year_prod_count=id[0]
        ##print wellid, year_remaining_days, year_prod_count, year_no_prod_count, year_total_days

        if year_remaining_days+year_prod_count+year_no_prod_count!=year_total_days:
            year_no_prod_count=year_total_days-year_remaining_days-year_prod_count


        '''Month Production Statistic'''
        local_month = local_time.tm_mon
        month_start_date=datetime.datetime(year=local_year,month=local_month,day=1)
        month_start_str=str(month_start_date)
        month_end_date=datetime.datetime(year=local_year,month=local_month,day=calendar.monthrange(local_year,local_month)[1])
        month_end_str=str(month_end_date)

        month_prod_cur = db.Sql("select count(*) from production_data where "
                               "wellid='" + wellid + "' and "
                                                     "production_date between to_date('" + month_start_str + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                                             "to_date('" + month_end_str + "','yyyy/mm/dd hh24:mi:ss') "
                                                                                                                                           "and daily_prod_gas>0")
        month_no_prod_cur=db.Sql("select count(*) from production_data where "
                               "wellid='" + wellid + "' and "
                                                     "production_date between to_date('" + month_start_str + "','yyyy/mm/dd hh24:mi:ss') and "
                                                                                                             "to_date('" + month_end_str + "','yyyy/mm/dd hh24:mi:ss') "
                                                                                                                                           "and daily_prod_gas=0")
        month_remaining_days=(month_end_date-current_date).days

        for id in month_prod_cur.fetchall():
            month_prod_count=id[0]

        for id in month_no_prod_cur.fetchall():
            month_no_prod_count=id[0]

        '''Yesterday Production Statistic'''

        yesterday_prod_cur=db.Sql("select prod_time,production_date,daily_prod_gas,prod_cum_gas from production_data where "
                                  "wellid=\'"+wellid+"\' and production_date=(select max(production_date) from production_data)")
        for id in yesterday_prod_cur.fetchall():
            yesterday_prod_time=id[0]
            yesterday_prod_date=str(id[1])
            yesterday_prod=str(id[2])
            yesterday_cum_prod=id[3]




        self.pie_data_dict={'total_days':total_days,'prod_days':prod_days,
                            'year_prod_count':year_prod_count,'year_remaining_days':year_remaining_days,'year_total_days':year_total_days,
                            'year_no_prod_count':year_no_prod_count,
                            'month_prod_count':month_prod_count,'month_no_prod_count':month_no_prod_count,'month_remaining_days':month_remaining_days,
                            'local_year':local_year,'local_month':local_month,
                            'yesterday_prod_time':yesterday_prod_time,
                            'yesterday_prod_date':yesterday_prod_date,
                            'yesterday_prod':yesterday_prod,
                            'yesterday_cum_prod':yesterday_cum_prod
                            }


        db.close()
        return self.pie_data_dict

    def PiePlotShow(self,wellid):
        w,h=self.GetSize()
        self.pie_plot = plt.figure()
        self.pie_plot_yesterday=plt.figure()
        self.pie_axes = self.pie_plot.gca()
        self.pie_axes_yesterday=self.pie_plot_yesterday.gca()

        data_dict=self.PiePlotDataExtract(wellid)

        total_colors = ['gold', 'yellowgreen', 'lightskyblue', 'lightcoral']
        # Total Production Statistic
        try:
            total_labels=['prod days:\n'+str(data_dict['prod_days'])+' days','no prod :\n'+str(data_dict['total_days']-data_dict['prod_days'])+' days']
            total_size=[data_dict['prod_days'],data_dict['total_days']-data_dict['prod_days']]
            total_explode=[0.3,0]
            self.pie_axes.pie(total_size, explode=total_explode, colors=total_colors, labels=total_labels,
                              autopct='%1.1f%%', radius=1.3, shadow=True, startangle=90,
                              center=(2.5, 2.5), frame=True
                              )

            # Year Production Statistic
            year_labels=['prod days:\n'+str(data_dict['year_prod_count'])+' days','no prod:\n'+str(data_dict['year_no_prod_count'])+' days',
                         'Remaining:\n'+str(data_dict['year_remaining_days'])+' days']
            year_size=[data_dict['year_prod_count'],data_dict['year_no_prod_count'],data_dict['year_remaining_days']]
            year_explode=[0.3,0,0]
            year_colors = ['lightskyblue', 'lightcoral', 'gray', 'ORCHID']

            self.pie_axes.pie(year_size, explode=year_explode, colors=year_colors, labels=year_labels,
                              autopct='%1.1f%%', radius=1.3, shadow=True, startangle=90,
                              center=(6.5, 2.5), frame=True
                              )

            # Month Production Statistic
            month_labels=['prod days:\n'+str(data_dict['month_prod_count'])+' days','no prod:\n'+str(data_dict['month_no_prod_count'])+' days',
                          'Remaining:\n'+str(data_dict['month_remaining_days'])+' days']
            month_size = [data_dict['month_prod_count'], data_dict['month_no_prod_count'], data_dict['month_remaining_days']]
            month_explode=[0.3,0,0]
            month_colors=[ 'KHAKI', 'ORCHID', 'gray']
            self.pie_axes.pie(month_size, explode=month_explode, colors=month_colors, labels=month_labels,
                              autopct='%1.1f%%', radius=1.3, shadow=True, startangle=10,
                              center=(11.5, 2.5), frame=True
                              )

            # Yesterday Production Statistic
            yesterday_labels=['Prod Hours:\n'+str(data_dict['yesterday_prod_time'])+' Hours','No Prod:\n'+str(24-data_dict['yesterday_prod_time'])+' Hours']
            yesterday_size=[data_dict['yesterday_prod_time'],24-data_dict['yesterday_prod_time']]

            yesterday_explode=[0.3,0]
            yesterday_colors=['cyan','pink']
            self.pie_axes_yesterday.pie(yesterday_size,explode=yesterday_explode,colors=yesterday_colors,labels=yesterday_labels,
                              autopct='%1.1f%%', radius=1.6,center=(2.5,2.5),shadow=True, startangle=90,
                               frame=True)
        except:
            pass


        self.pie_axes.set_xticks(range(50))
        self.pie_axes.set_yticks([5])
        self.pie_axes_yesterday.set_xticks(range(100))
        self.pie_axes_yesterday.set_yticks([5])
        self.pie_axes.set_xticklabels(['','','Total Statistic','','','',' Year '+str(data_dict['local_year'])+' Statistic','','','','','',
                                       ' Month '+str(data_dict['local_month'])+' Statistic','',''])
        self.pie_axes_yesterday.set_xticklabels(['','','Yesterday Prod Status','',''])
        self.pie_axes.set_xlim((0,15))
        self.pie_axes.set_ylim((0, 5))
        self.pie_axes.set_aspect('equal')
        self.pie_axes_yesterday.set_xlim((0, 10))
        self.pie_axes_yesterday.set_ylim((0, 5))
        self.pie_axes_yesterday.set_aspect('equal')



        self.AnnotateDraw(self.pie_axes_yesterday,text=data_dict['yesterday_prod_date'].split(' ')[0],color='black',size=12,x=5,y=3.6,x_offset=0,y_offset=0,arrow=False)

        self.AnnotateDraw(self.pie_axes_yesterday, text='Daily Prod From Report: '+str(data_dict['yesterday_prod'])+' Km3/d', color='blue', size=12, x=5,
                          y=3.0, x_offset=0, y_offset=0, arrow=False)

        self.AnnotateDraw(self.pie_axes_yesterday, text='Cumulative Prod : ' + str(data_dict['yesterday_cum_prod'])+' Mm3',
                          color='brown', size=12, x=5,
                          y=2.5, x_offset=0, y_offset=0, arrow=False)



        if data_dict['yesterday_prod_time']==0.0:
            self.AnnotateDraw(self.pie_axes_yesterday,
                              text='Well Closed', color='red', size=12,
                              x=5,
                              y=2.1, x_offset=0, y_offset=0, arrow=False)
        else:
            self.AnnotateDraw(self.pie_axes_yesterday,
                              text='Well Opened', color='green', size=12,
                              x=5,
                              y=2.1, x_offset=0, y_offset=0, arrow=False)

        self.pie_canvas=FigureCanvas(self.Panel_dict['Pie_Plot_Area'],wx.NewId(),self.pie_plot)
        self.pie_canvas_yesterday = FigureCanvas(self.Panel_dict['Pie_Plot_Area_Yesterday'], wx.NewId(), self.pie_plot_yesterday)

    def OnHistPageChange(self,event):
        #pid=self.main_map_nb.GetPageIndex(self.Panel_dict['Daily_Plot_Area'])
        if 'Hist' in self.main_map_nb.GetPageText(self.main_map_nb.GetSelection()):
            self.HistoricalprodPrepare(wellid=self.single_wellid)
            self.button_area_control['list_combobox'].SetSelection(self.plot_list_name.index('Historical Plot Setting'))
            self.main_map_nb.Update()
            self._mgr.Update()
        elif 'Instant' in self.main_map_nb.GetPageText(self.main_map_nb.GetSelection()):
            self.button_area_control['list_combobox'].SetSelection(self.plot_list_name.index('Instant Plot Setting'))

            self.OnShowInstantButton(event=None)

        elif 'Daily' in self.main_map_nb.GetPageText(self.main_map_nb.GetSelection()):
            self.button_area_control['list_combobox'].SetSelection(self.plot_list_name.index('Daily Plot Setting'))

        self.main_map_nb.Update()
        self._mgr.Update()

    def OnLegendClick(self,event):

        ###print event.artist.get_lines(),self.daily_prod_plot.plot_instance_dict.values()
        '''for x in event.artist.get_lines():
            if x in self.axes_legend.get_lines():
                ##print x,True
            else:
                ##print x,False'''


        legline = event.artist
        #print 'legline clicked',legline
        ###print event.xdata,event.ydata
        if legline in self.daily_prod_legend_dict.keys():
            ##print 'legline filtered legline',legline

            origline = self.daily_prod_legend_dict[legline][0]


            '''##print 'this is corrsponed line',origline
            vis = not origline.get_visible()
            origline.set_visible(vis)
            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)'''
            lw=origline.get_linewidth()
            if lw==1.0:
                origline.set_linewidth(5)
                legline.set_linewidth(5)
            else:
                origline.set_linewidth(1.0)
                legline.set_linewidth(1.0)

        elif legline in self.daily_prod_ax_dict.keys():
            #print 'legline plot legline', legline
            origline = self.daily_prod_ax_dict[legline][0]
            for x in self.daily_prod_legend_dict.keys():
                if origline in self.daily_prod_legend_dict[x]:
                    x.set_linewidth(5)
            lw = origline.get_linewidth()
            if lw == 1.0:
                origline.set_linewidth(5)
                for x in self.daily_prod_legend_dict.keys():
                    if origline in self.daily_prod_legend_dict[x]:
                        x.set_linewidth(5)
            else:
                origline.set_linewidth(1.0)
                for x in self.daily_prod_legend_dict.keys():
                    if origline in self.daily_prod_legend_dict[x]:
                        x.set_linewidth(1)

        self.daily_prod_plot.figure.canvas.draw()

    def OnHistPlotClick(self,event):

        legline = event.artist
        ##print 'legline clicked', legline
        # ##print event.xdata,event.ydata
        if legline in self.hist_prod_legend_dict.keys():
            ##print 'legline filtered legline', legline

            origline = self.hist_prod_legend_dict[legline][0]
            ##print origline
            '''##print 'this is corrsponed line',origline
            vis = not origline.get_visible()
            origline.set_visible(vis)
            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)'''
            lw = origline.get_linewidth()
            if lw == 1.0:
                origline.set_linewidth(5)
                legline.set_linewidth(5)
            else:
                origline.set_linewidth(1.0)
                legline.set_linewidth(1.0)

        elif legline in self.hist_prod_ax_dict.keys():
            ##print 'legline plot legline', legline
            origline = self.hist_prod_ax_dict[legline][0]
            ##print origline
            for x in self.hist_prod_legend_dict.keys():
                if origline in self.hist_prod_legend_dict[x]:
                    x.set_linewidth(5)
            lw = origline.get_linewidth()
            if lw == 1.0:
                origline.set_linewidth(5)
                for x in self.hist_prod_legend_dict.keys():
                    if origline in self.hist_prod_legend_dict[x]:
                        x.set_linewidth(5)
            else:
                origline.set_linewidth(1.0)
                for x in self.hist_prod_legend_dict.keys():
                    if origline in self.hist_prod_legend_dict[x]:
                        x.set_linewidth(1)
        ##print self.hist_prod_plot.plot_instance_dict.keys()
        ##print self.hist_prod_plot.axes2.get_legend_handles_labels()[1]
        self.hist_prod_plot.figure.canvas.draw()

    def OnInstPlotClick(self,event):

        legline = event.artist
        ##print 'legline clicked', legline
        # ##print event.xdata,event.ydata
        if legline in self.inst_prod_legend_dict.keys():
            ##print 'legline filtered legline', legline

            origline = self.inst_prod_legend_dict[legline][0]

            lw = origline.get_linewidth()
            if lw == 1.0:
                origline.set_linewidth(5)
                legline.set_linewidth(5)
            else:
                origline.set_linewidth(1.0)
                legline.set_linewidth(1.0)

        elif legline in self.inst_prod_ax_dict.keys():
            ##print 'legline plot legline', legline
            origline = self.inst_prod_ax_dict[legline][0]
            ##print origline
            for x in self.inst_prod_legend_dict.keys():
                if origline in self.inst_prod_legend_dict[x]:
                    x.set_linewidth(5)
            lw = origline.get_linewidth()
            if lw == 1.0:
                origline.set_linewidth(5)
                for x in self.inst_prod_legend_dict.keys():
                    if origline in self.inst_prod_legend_dict[x]:
                        x.set_linewidth(5)
            else:
                origline.set_linewidth(1.0)
                for x in self.inst_prod_legend_dict.keys():
                    if origline in self.inst_prod_legend_dict[x]:
                        x.set_linewidth(1)
        ##print self.inst_prod_plot.plot_instance_dict.keys()
        ##print self.inst_prod_plot.axes2.get_legend_handles_labels()[1]
        self.inst_prod_plot.figure.canvas.draw()

    def OnPlotRightClick(self, event):
        if event.dblclick==True:
            #print "plot Right Click"
            self.PlotPopupMenu()
        #print event.dblclick

    def PlotPopupMenu(self):
        #if not hasattr(self,'pop_dict'):
        if True:
            self.pop_dict={}
            menu = wx.Menu()
            menu_tuple=('Check Table','Summary Info','Scale Setting')
            for id in menu_tuple:
                self.pop_dict[id]=wx.NewId()
                menu.Append(self.pop_dict[id],id)

            self.Bind(wx.EVT_MENU, self.OnCheckTable, id=self.pop_dict['Check Table'])
            self.PopupMenu(menu)

            #wx.CallAfter(self.PopupMenuAfter, menu)

        #except:
         #   pass

    def PopupMenuAfter(self,menu):
        menu.Destroy()
        del self.pop_dict

    def OnPlotMove(self,event):
        if event.inaxes is not None:
            '''for id in self.daily_comments_scatter_list:
                if id.contains(event)[0]:
                    #print True'''
            visibility_changed = False
            for point, annotation in self.daily_comments_scatter_list:
                should_be_visible = (point.contains(event)[0] == True)
                if should_be_visible != annotation.get_visible():
                    visibility_changed = True
                    annotation.set_visible(should_be_visible)

            self.daily_prod_canvas.draw()

    def OnClose(self,event):
        ##print 'starting close event......'
        self.Restore()
        try:
            del self.daily_prod_canvas
            ##print 'self.daily_prod_canvas'
            del self.daily_prod_plot
            ##print 'self.daily_prod_plot'
            del self.daily_plot_sample
            ##print 'self.daily_plot_sample'
            del self.daily_par_list
            ##print 'self.daily_par_list'
            del self.daily_prod_dict
            del self.daily_prod_ylist
            del self.daily_prod_ysec_list
            del self.daily_toolbar
            del self.hist_prod_canvas
            del self.hist_plot_sample
            del self.hist_prod_plot
            del self.hist_par_list
            del self.hist_prod_ylist
            del self.hist_prod_ysec_list
            del self.hist_toolbar
            del self.Panel_dict
            del self.inst_par_list
            del self.inst_plot_sample
            del self.inst_plot
            del self.inst_prod_canvas
            del self.inst_prod_dict
        except Exception:
            pass
        gc.collect()
        self.Destroy()







'''class PlotMenuPanel(wx.Panel):
    def __init__(self,parent=None):
        wx.Panel.__init__(self,parent,-1)
        bx=wx.BoxSizer(wx.VERTICAL)
        menu.Append'''








