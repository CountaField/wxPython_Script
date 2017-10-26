# -*- coding:utf-8 -*-

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
import datetime
from PlotAttributeFrame import  ClusterOrderChange as coc

class BB9Frame(AuiTemple,tspd,pp3):
    def __init__(self,parent):
        AuiTemple.__init__(self,parent)
        tspd.__init__(self, '')
        self.BB9TreeList()
        self.text3 = wx.TextCtrl(self, -1, "Main content window",
                                 wx.DefaultPosition, wx.Size(200, 150),
                                 wx.NO_BORDER | wx.TE_MULTILINE)
        self.parent=parent
        self.plot_setting_control_dict=OrderedDict()
        self.compare_cluster_data_dict={}
        self.cluster_wells_date_crc= {}
        self.global_plot={}
        self.global_plt={}
        self.plot_exist = []
        self.global_axes={}
        self.compare_cluster_date_dict={}
        self.compare_wells_data_dict={}
        self.compare_wells_list_dict={}
        self.wells_stack_dict={}
        self.global_canvas={}
        self.cluster_wells_date_dict={}
        self.cluster_summary_date_dict={}
        self.plot_default_value_dict={}
        self._mgr.AddPane(self.text3, aui.AuiPaneInfo().CenterPane())
        self.clusterwellsselection()
        self.PlotSetting()
        self._mgr.Update()
        self.MenuPane()
        self.final_query_wells_data = {}
        self.prod_data_cluster_dict = {}
        self.checked_dict = {}
        self.text3_exist=True
        self.well_select=False
        self.cluster_compare=False
        self.cluster_compare_3d=False
        self.cluster3d_plot_list=[]
        self.cluster_stack_list=[]
        self.cluster_summary_list=[]
        self.checked_cluster_table={}
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.colors = " 'gold','yellowgreen', 'lightskyblue', 'lightcoral', 'KHAKI', 'ORCHID', 'PALEGREEN', 'pink','cyan','PLUM','cadetblue','gold','wheat','green','seagreen'"
        self.color_list = [ 'gold','yellowgreen', 'lightskyblue', 'lightcoral', 'KHAKI', 'ORCHID', 'PALEGREEN', 'pink','cyan','PLUM','cadetblue','gold','wheat','green','seagreen']


    def BB9TreeList(self):

        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        parent_panel=self.CustomPanel('BB9 Tree List',(150,700))[0]
        self.bb9_tree_list=ct.CustomTreeCtrl(parent_panel,size=parent_panel.GetSize(),agwStyle=wx.TR_DEFAULT_STYLE)
        tree_root =self.bb9_tree_list.AddRoot("South Sulige Field")
        self.bb9_tree_list.SetBackgroundColour('white')
        self.bb9_dict={}
        self.bb9_cluster_list = {}
        bb9_cur=db.Sql("select BB9 FROM well_cluster group by bb9 order by bb9")
        for id in bb9_cur.fetchall():
            if id[0]!=None:
                self.bb9_dict[id[0]]=self.bb9_tree_list.AppendItem(tree_root,id[0],ct_type=0)
                bb9_cur_str="select clusterid from well_cluster where bb9=\'" + id[0].replace("'","''")+\
                            "\' order by clusterid"

                bb9_cluster_cur = db.Sql(bb9_cur_str)
                for clusterid in bb9_cluster_cur.fetchall():
                    self.bb9_cluster_list[clusterid[0]]=self.bb9_tree_list.AppendItem(self.bb9_dict[id[0]],clusterid[0],ct_type=1)
        db.close()
        self.CustomLayout(parent_panel,'left')
        self._mgr.Update()

    def MenuPane(self):
        plot3d_button=wx.Button(self._toolbar, -1,'Cluster Wells 3D Plot')
        TreeListQuery_button=wx.Button(self._toolbar, -1,'Cluster Wells Stack Plot')
        cluster_compare_3d_button=wx.Button(self._toolbar,-1,'Cluster Compare 3d Plot')
        ClusterSummary_button=wx.Button(self._toolbar,-1,'Cluster Summary')
        cluster_compare_button=wx.Button(self._toolbar,-1,'Cluster Compare')
        control_list=[]
        control_list.append(plot3d_button)
        control_list.append(TreeListQuery_button)
        control_list.append(ClusterSummary_button)
        control_list.append(cluster_compare_button)
        control_list.append(cluster_compare_3d_button)
        FrameDisplay = self.CustomAuiToolBar('Menu Bar',control_list)
        self._mgr.Update()
        self.Bind(wx.EVT_BUTTON,self.ongetcheckeditemintreelist,TreeListQuery_button)
        self.Bind(wx.EVT_BUTTON,self.onCluster3DplotClick,plot3d_button)
        self.Bind(wx.EVT_BUTTON, self.onClusterSummaryClick,ClusterSummary_button)
        self.Bind(wx.EVT_BUTTON,self.OnClusterCompareClick,cluster_compare_button)
        self.Bind(wx.EVT_BUTTON,self.OnClusterCompare3Dplot,cluster_compare_3d_button)

    def Polygon3Dplot(self,clusterid):
        canvas_panel = self.CustomPanel("Cluster "+clusterid+ " 3D Plot")[0]
        self.WellidInCluster(clusterid,[])
        self.MinProdDateWells(clusterid,[])
        self.MaxProdDateWells(clusterid,[])
        self.CompareProdDateDiff()
        self.DefineProdDateStander(clusterid)
        self.TidyUpProdData(clusterid)
        prod_data=self.prod_data_dict
        well_list=self.wellid_list
        prod_date = self.final_date_dict[clusterid]
        pp3.__init__(self)
        self.canvas3d=FigureCanvas(canvas_panel,wx.NewId(),self.figure3d)
        self.axis_create(prod_date,prod_data,well_list,clusterid)
        self.CustomLayout(canvas_panel,'Center')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas3d, 2, flag=wx.GROW)
        canvas_panel.SetSizer(sizer)
        self._mgr.Update()
        return (canvas_panel)

    def WellsInClusterDataPrepare(self,clusterid,wellid_list=[],final_date_dict=None,prod_data_dict=None):
         db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
         #print('wellid_list',wellid_list)
         print clusterid
         self.global_plot[clusterid+' Stack Plot']=self.CustomPanel(" Cluster "+clusterid+" Stack Plot")[0]
         plotid=clusterid+' Stack Plot'

         self.exist_plot_combobox.Set(self.plot_exist)
         query_wells_data = ''
         if wellid_list==[]:
            for wellid in self.wellid_list: # self.prod_data_dict is a dictionary which from tspd (super class)
                 if wellid in self.prod_data_dict and self.prod_data_dict[wellid]!=[]:
                    query_wells_data+='self.prod_data_dict[\''+wellid+'\'],'
            self.compare_wells_list_dict[plotid] = self.wellid_list
         else:

             for wellid in wellid_list:  # self.prod_data_dict is a dictionary which from tspd (super class)
                # print(wellid)2
                 if wellid in self.prod_data_cluster_dict[clusterid].keys() and self.prod_data_cluster_dict[clusterid][wellid] != []:
                   #  print(wellid)
                     query_wells_data += 'self.prod_data_cluster_dict[\''+clusterid+'\'][\'' + wellid + '\'],'
             self.compare_wells_list_dict[plotid] = wellid_list
         self.final_query_wells_data[clusterid]=query_wells_data[:-1]
         if plotid in self.cluster_wells_date_crc.keys():
            if self.cluster_wells_date_crc[plotid]!=[]:
                 self.cluster_wells_date_dict[plotid]=self.cluster_wells_date_crc[plotid]
            else:
                 self.cluster_wells_date_dict[plotid]=self.final_date_dict[clusterid][:]
         else:
             self.cluster_wells_date_dict[plotid] = self.final_date_dict[clusterid][:]
         self.compare_wells_data_dict[plotid]=self.prod_data_dict
         del self.final_date_dict[clusterid]

         figure = plt.figure()
         self.global_axes[plotid] = figure.add_subplot(111)
         self.global_axes[plotid].xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
         self.global_axes[plotid].set_title('Cluster '+str(clusterid) + ' Wells Stack Plot\n')

         self.global_axes[plotid].set_ylabel(u'Km3/d ',size=20)
         excute_string="self.wells_stack_dict[plotid]=self.global_axes[plotid]." \
                       "stackplot(self.cluster_wells_date_dict[plotid],"+self.final_query_wells_data[clusterid]+",color='black',colors=["+self.colors+"],alpha=0.9)"
         exec(excute_string)
         figure.autofmt_xdate()
         self.global_canvas[plotid]=FigureCanvas(self.global_plot[plotid],wx.NewId(),figure)
         toolbar=add_toolbar(self.global_canvas[plotid])
         self.CustomLayout(self.global_plot[plotid],'Center')
         sizer=wx.BoxSizer(wx.VERTICAL)
         sizer.Add(self.global_canvas[plotid],5,flag=wx.GROW)
         sizer.Add(toolbar,1,wx.BOTTOM)
         self.global_plot[plotid].SetSizer(sizer)
         wellid_cur=db.Sql("select wellid from production_data where wellid in ( select wellid from well_header "
                           "where Clusterid=\'"+clusterid+"\') group by wellid order by wellid")
         well_list=[]
         color_dict = OrderedDict()
         i=0
         if wellid_list==[]:
            for id in wellid_cur.fetchall():
                color_dict[id[0]]=plt.Rectangle((i, 0), 1, 1, angle=90.0,fc=self.color_list[i])
                well_list.append(color_dict[id[0]])
                i+=1
         else:
             for id in wellid_list:
                 color_dict[id] = plt.Rectangle((i, 0), 1, 1, angle=90.0,fc=self.color_list[i])
                 well_list.append(color_dict[id])
                 i += 1
         plt.legend(well_list,color_dict.keys(),loc='upper center',ncol=9,fontsize=10)
         self._mgr.Update()
         db.close()
         return(self.global_plot[plotid])

    def ongetcheckeditemintreelist(self,event):
        if self.text3_exist==True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist=False
        self.prod_datadict={}
        self.final_date_dict={}
        for id in self.bb9_cluster_list:
            if self.bb9_cluster_list[id].IsChecked():
                if id not in self.checked_dict.keys():
                    if id not in self.cluster_stack_list:
                        self.cluster_stack_list.append(id)
                        clusterid=id
                        if id in self.final_date_dict:
                            pass
                        else:
                            self.WellidInCluster(clusterid,[],[])
                            self.MinProdDateWells(clusterid, [],[])
                            self.MaxProdDateWells(clusterid, [],[])
                            try:
                                self.DefineProdDateStander(clusterid,[])
                            except TypeError:
                                wx.MessageDialog(self.parent, 'Soryy,'+clusterid+' is not producing', style=wx.OK | wx.ICON_ERROR)
                            self.CompareProdDateDiff()
                            self.TidyUpProdData(clusterid,[])
                            self.prod_data_cluster_dict[clusterid] = self.prod_data_dict
                        self.checked_dict[id]=self.WellsInClusterDataPrepare(clusterid)
                else:
                    if id not in self.cluster_stack_list:
                        self.cluster_stack_list.append(id)
                        clusterid = id
                        if id in self.final_date_dict:
                            pass
                        else:
                            self.WellidInCluster(clusterid, [])
                            self.MinProdDateWells(clusterid, [])
                            self.MaxProdDateWells(clusterid, [])
                            self.DefineProdDateStander(clusterid)
                            self.CompareProdDateDiff()
                            self.TidyUpProdData(clusterid)
                            self.prod_data_cluster_dict[clusterid] = self.prod_data_dict
                        self.checked_dict[id] = self.WellsInClusterDataPrepare(clusterid)
                if id + ' Stack Plot' not in self.plot_exist:
                    self.plot_exist.append(id + ' Stack Plot')
            else:
                if id in self.checked_dict:
                    self._mgr.DetachPane(self.checked_dict[id])
                    try:
                        self.checked_dict[id].Destroy()
                    except AttributeError:
                        pass
                    self.checked_dict.pop(id)
                    if id in self.cluster_summary_list:
                        self.cluster_summary_list.remove(id)
                    if id in self.cluster3d_plot_list:
                        self.cluster3d_plot_list.remove(id)
                    if id in self.cluster_stack_list:
                        self.cluster_stack_list.remove(id)
                if id + ' Stack Plot'  in self.plot_exist:
                    self.plot_exist.remove(id + ' Stack Plot')
        if self.well_select == False:
            self.well_select = True
        self.exist_plot_combobox.Set(self.plot_exist)
        self._mgr.Update()

    def onCluster3DplotClick(self,event):
        if self.text3_exist == True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist = False
        if self.well_select == False:
            #self.clusterwellsselection()
            self.well_select = True
            self.prod_data_dict = {}
            self.final_date_dict = {}
        for id in self.bb9_cluster_list:
            if self.bb9_cluster_list[id].IsChecked():
                if id not in self.checked_dict:
                    if id not in self.cluster3d_plot_list:
                        self.cluster3d_plot_list.append(id)
                        clusterid = id
                        self.checked_dict[id] = self.Polygon3Dplot(clusterid)
                else:
                    if id not in self.cluster3d_plot_list:
                        self.cluster3d_plot_list.append(id)
                        clusterid = id
                        self.checked_dict[id] = self.Polygon3Dplot(clusterid)
            else:
                if id in self.checked_dict:
                    self._mgr.DetachPane(self.checked_dict[id])
                    self.checked_dict[id].Destroy()
                    self.checked_dict.pop(id)
                    if id in self.cluster_summary_list:
                        self.cluster_summary_list.remove(id)
                    if id in self.cluster3d_plot_list:
                        self.cluster3d_plot_list.remove(id)
                    if id in self.cluster_stack_list:
                        self.cluster_stack_list.remove(id)
        self._mgr.Update()

    def onClusterSummaryClick(self,event):
        if self.text3_exist == True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist = False
        if self.well_select == False:
            self.well_select = True
            self.prod_data_dict={}
            self.final_date_dict={}
        for id in self.bb9_cluster_list:
            if self.bb9_cluster_list[id].IsChecked():
                if id not in self.checked_dict.keys():
                    if id not in self.cluster_summary_list:
                        self.cluster_summary_list.append(id)
                        clusterid = id
                        tspd.__init__(self, clusterid)
                        self.checked_dict[id] = self.ClusterSummaryPlot(clusterid)
                else:
                    if id not in self.cluster_summary_list:
                        self.cluster_summary_list.append(id)
                        clusterid = id
                        tspd.__init__(self, clusterid)
                        self.checked_dict[id] = self.ClusterSummaryPlot(clusterid)
                if id+' summary plot' not in self.plot_exist:
                    self.plot_exist.append(id+' summary plot')
            else:
                if id in self.checked_dict:
                    self._mgr.DetachPane(self.checked_dict[id])
                    self.checked_dict[id].Destroy()
                    self.checked_dict.pop(id)
                    if id in self.cluster_summary_list:
                        self.cluster_summary_list.remove(id)
                    if id in self.cluster3d_plot_list:
                        self.cluster3d_plot_list.remove(id)
                    if id in self.cluster_stack_list:
                        self.cluster_stack_list.remove(id)
                if id + ' summary plot' in self.plot_exist:
                    self.plot_exist.remove(id + ' summary plot')

        self.exist_plot_combobox.Set(self.plot_exist)
        self._mgr.Update()

    def clusterwellsselection(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cluster_cur = db.Sql("select clusterid from vw_cluster_summary group by Clusterid order by clusterid")
        cluster_list = []
        for id in cluster_cur.fetchall():
            cluster_list.append(id[0])
        parent_panel,self.cluster_to_well_staticbox=self.CustomPanel('Advance Setting',size=(200,200),staticbox=True)
        cluster_label=wx.StaticText(self.cluster_to_well_staticbox,-1,'Please Choose Cluster:')
        wellid_label=wx.StaticText(self.cluster_to_well_staticbox,-1,'Please Choose Wellid:')
        plot_refresh_button = wx.Button(self.cluster_to_well_staticbox, -1, 'Plot Refresh')
        cluster_data_button= wx.Button(self.cluster_to_well_staticbox, -1, 'Check Data')

        self.Bind(wx.EVT_BUTTON,self.OnClusterDataShow,cluster_data_button)
        self.cluster_select=wx.ComboBox(self.cluster_to_well_staticbox,-1,choices=cluster_list)
        self.well_combobox = wx.CheckListBox(self.cluster_to_well_staticbox, -1, choices=[])
        self.Bind(wx.EVT_COMBOBOX,self.onClusterSelect,self.cluster_select)
        self.Bind(wx.EVT_BUTTON,self.OnReplotButton,plot_refresh_button)
        controlslist=[]
        controlslist.append(cluster_label)
        controlslist.append(self.cluster_select)
        controlslist.append(wellid_label)
        controlslist.append(self.well_combobox)
        controlslist.append(plot_refresh_button)
        controlslist.append(cluster_data_button)
        static_sizer=self.SetStaticBoxSizer(controlslist)
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(static_sizer)
        parent_panel.SetSizer(static_sizer)
        self.CustomLayout(parent_panel,'Right')
        self._mgr.Update()
        db.close()

    def PlotSetting(self):
        parent_panel, self.plot_setting_frame = self.CustomPanel('Plot Setting', size=(200, 200),
                                                                  staticbox=True)
        controlslist = []
        promopt_text=wx.StaticText(self.plot_setting_frame,-1,'Please Choose Plot:')
        self.exist_plot_combobox = wx.ComboBox(self.plot_setting_frame, -1, choices=self.plot_exist)
        self.plot_setting_control_dict['yaxis_min_text']=wx.StaticText(self.plot_setting_frame,-1,'Y Axis Min:')
        self.plot_setting_control_dict['yaxis_min_ctrltext']=wx.TextCtrl(self.plot_setting_frame,-1)
        self.plot_setting_control_dict['yaxis_max_text'] = wx.StaticText(self.plot_setting_frame, -1, 'Y Axis Max:')
        self.plot_setting_control_dict['yaxis_max_ctrltext']=wx.TextCtrl(self.plot_setting_frame,-1)
        self.plot_setting_control_dict['xaxis_min_text'] = wx.StaticText(self.plot_setting_frame, -1, 'Start Date:')
        self.plot_setting_control_dict['xaxis_min_combobox']=wx.ComboBox(self.plot_setting_frame,-1,choices=[])
        self.plot_setting_control_dict['xaxis_max_text'] = wx.StaticText(self.plot_setting_frame, -1, 'End Date:')
        self.plot_setting_control_dict['xaxis_max_combobox'] = wx.ComboBox(self.plot_setting_frame, -1, choices=[])
        self.plot_setting_control_dict['confirm_button'] = wx.Button(self.plot_setting_frame, -1, 'Confirm')
        self.plot_setting_control_dict['restore_button'] = wx.Button(self.plot_setting_frame, -1, 'Plot Restore')
        self.plot_setting_control_dict['order_change_button'] = wx.Button(self.plot_setting_frame, -1, 'Order Change')
        controlslist.append(promopt_text)
        controlslist.append(self.exist_plot_combobox)
        for x in self.plot_setting_control_dict.keys():
            controlslist.append(self.plot_setting_control_dict[x])
        static_sizer=self.SetStaticBoxSizer(controlslist)
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(static_sizer)
        parent_panel.SetSizer(static_sizer)
        self.CustomLayout(parent_panel,'Right')
        self.Bind(wx.EVT_COMBOBOX,self.OnPlotSelect,self.exist_plot_combobox)
        self.Bind(wx.EVT_BUTTON,self.OnPlotSettingConfirm,self.plot_setting_control_dict['confirm_button'])
        self.Bind(wx.EVT_BUTTON,self.OnPlotRestore,self.plot_setting_control_dict['restore_button'])
        self.Bind(wx.EVT_BUTTON, self.OnOrderchangeClick, self.plot_setting_control_dict['order_change_button'])
        self._mgr.Update()



    def OnPlotRestore(self,event):
        plot_select = self.exist_plot_combobox.GetStringSelection()
        self.global_axes[plot_select].set_xlim(self.plot_default_value_dict[plot_select + 'x_min'],
                                               self.plot_default_value_dict[plot_select + 'x_max'])
        self.global_axes[plot_select].set_ylim(self.plot_default_value_dict[plot_select + 'y_min'],
                                               self.plot_default_value_dict[plot_select + 'y_max'])
        self.global_canvas[plot_select].draw()


    def OnOrderchangeClick(self,event):
        plot_select = self.exist_plot_combobox.GetStringSelection()
        if 'Compare' in plot_select:
            order_frm=coc(self.parent,-1,plot_select,
                          checked_dict=self.checked_dict[self.cluster_compare_string],
                          plot_axes=self.global_axes[plot_select],
                          plot=self.global_plot[plot_select],
                          plot_canvas=self.global_canvas[plot_select],
                          colors=self.colors,
                          colors_list=self.color_list,
                          data_dict=self.compare_cluster_data_dict[plot_select],
                          date_list=self.compare_cluster_date_dict[plot_select],
                          cluster_list=self.cluster_compare_list,
                          mgr=self._mgr,
                          title=plot_select+' Order Change')
            order_frm.Show()
        elif 'Stack' in plot_select:
            order_frm = coc(self.parent, -1, plot_select,
                            plot_axes=self.global_axes[plot_select],
                            plot=self.global_plot[plot_select],
                            plot_canvas=self.global_canvas[plot_select],
                            colors=self.colors,
                            colors_list=self.color_list,
                            data_dict=self.compare_wells_data_dict[plot_select],
                            date_list=self.cluster_wells_date_dict[plot_select],
                            cluster_list=self.compare_wells_list_dict[plot_select],
                            mgr=self._mgr,
                            title=plot_select + ' Order Change')

            order_frm.Show()

    def OnPlotSelect(self,event):
        plot_select=self.exist_plot_combobox.GetStringSelection()
        #print plot_select
        date_list=[]
        if 'Compare' in plot_select:
            for x in self.compare_cluster_date_dict[plot_select]:
                date_list.append(str(x))

        elif 'Stack' in plot_select:
            for x in self.cluster_wells_date_dict[plot_select]:
                date_list.append(str(x))

        elif 'summary' in plot_select:
            for x in self.cluster_summary_date_dict[plot_select]:
                date_list.append(str(x))

        self.plot_default_value_dict[plot_select + 'y_min'],self.plot_default_value_dict[plot_select + 'y_max']=self.global_axes[plot_select].get_ylim()
        self.plot_default_value_dict[plot_select + 'x_min'] = date_list[0]
        self.plot_default_value_dict[plot_select + 'x_max'] = date_list[-1]
        self.plot_setting_control_dict['xaxis_min_combobox'].Set(date_list)
        self.plot_setting_control_dict['xaxis_max_combobox'].Set(date_list)

    def OnPlotSettingConfirm(self,event):
        if self.plot_setting_control_dict['yaxis_max_ctrltext'].GetValue() is not unicode(''):
            y_max=float(self.plot_setting_control_dict['yaxis_max_ctrltext'].GetValue())
        else:
            y_max=None
        if self.plot_setting_control_dict['yaxis_min_ctrltext'].GetValue() is not unicode(''):
            y_min = float(self.plot_setting_control_dict['yaxis_min_ctrltext'].GetValue())
        else:
            y_min = None
        if self.plot_setting_control_dict['xaxis_min_combobox'].GetStringSelection() is not unicode(''):
            start_date=datetime.datetime.strptime(self.plot_setting_control_dict['xaxis_min_combobox'].GetStringSelection(),'%Y-%m-%d %H:%M:%S')
        else:
            start_date=None
        if self.plot_setting_control_dict['xaxis_max_combobox'].GetStringSelection() is not unicode(''):
            end_date=datetime.datetime.strptime(self.plot_setting_control_dict['xaxis_max_combobox'].GetStringSelection(),'%Y-%m-%d %H:%M:%S')
        else:
            end_date=None
        plot_select=self.exist_plot_combobox.GetStringSelection()
        if start_date is not None and end_date is not None:
            self.global_axes[plot_select].set_xlim(start_date,end_date)
        if y_min is not None and y_max is not None:
            self.global_axes[plot_select].set_ylim(y_min,y_max)
        self.global_canvas[plot_select].draw()


    def ClusterSummaryPlot(self,clusterid):
        plotid=clusterid+' summary plot'
        self.global_plot[plotid] = self.CustomPanel(" Cluster "+clusterid+" Summary Plot")[0]
        #self.plot_exist.append(plotid)
        self.exist_plot_combobox.Set(self.plot_exist)
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cluster_summary_cur=db.Sql("select production_date,sum_daily_prod_gas,sum_prod_cum_gas/1000 "
                                   "from vw_cluster_summary where "
                                   "clusterid=\'"+clusterid+"\' order by production_date")
        parameter_list=['PRODUCTION_DATE','DAILY_CUM_PROD','CLUSTER_CUM_PROD']
        plot=PlotDrawing(parent=self,wellid=clusterid,parameter_list=parameter_list,cursor=cluster_summary_cur,
                         Xaxis='PRODUCTION_DATE',Yaxis_list=['DAILY_CUM_PROD'],Ysec_axis_list=['CLUSTER_CUM_PROD'])
        self.global_axes[plotid]=plot.axes
        plot.axes.set_ylabel('Km3/d',size=20)
        plot.axes2.set_ylabel('Bcm',size=20)
        self.cluster_summary_date_dict[plotid]=plot.x_list
        self.global_canvas[plotid]=FigureCanvas(self.global_plot[plotid],wx.NewId(),plot.figure)
        toolbar = add_toolbar(self.global_canvas[plotid])
        self.CustomLayout(self.global_plot[plotid], 'Center')
        db.close()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.global_canvas[plotid], 1, flag=wx.GROW)
        sizer.Add(toolbar, 1, wx.BOTTOM)
        self.global_plot[plotid].SetSizer(sizer)
        self._mgr.Update()
        return self.global_plot[plotid]

    def OnClusterDataShow(self,event):
        Clusterid =self.cluster_select.GetStringSelection()
        print('CLUSTERID IS :',Clusterid)
        self.checked_cluster_table[Clusterid] = DailyProdTable(parent=self.parent, wellid=Clusterid, table_name='VW_CLUSTER_SUMMARY',cluster=True)
        self.checked_cluster_table[Clusterid].Show()


    def OnClose(self,event):
        self.Restore()
        self.checked_cluster_table.clear()
        self.Destroy()


    def onClusterSelect(self,event):
        self.well_combobox.Clear()
        clusterid=self.cluster_select.GetStringSelection()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        wellid_cur = db.Sql("select wellid from production_data where wellid in ( select wellid from well_header "
                            "where Clusterid=\'" + clusterid + "\') group by wellid order by wellid")
        well_list=[]
        for id in wellid_cur.fetchall():
            well_list.append(id[0])
        self.well_combobox.InsertItems(well_list,0)
        db.close()


    def OnReplotButton(self,event):
        clusterid=self.cluster_select.GetStringSelection()
        well_list=self.well_combobox.GetCheckedStrings()
        #print(well_list)
        plotid=clusterid+' Stack Plot'
        if well_list!=[]:
            self._mgr.DetachPane(self.checked_dict[clusterid])
            self.cluster_wells_date_crc[plotid]=self.cluster_wells_date_dict[plotid][:]
            self.checked_dict[clusterid].Destroy()
            self.WellidInCluster(clusterid, well_list)
            self.MinProdDateWells(clusterid, well_list,[])
            self.MaxProdDateWells(clusterid, well_list,[])
            self.CompareProdDateDiff()
            self.TidyUpProdData(clusterid)
            self.checked_dict[clusterid] = self.WellsInClusterDataPrepare(clusterid,well_list)
        else:
            pass


    def CompareClusterPlot(self,clu_final_date_list,prod_data_cluster_dict,cluster_list):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cluster_string=''
        for id in cluster_list:
            cluster_string=cluster_string+','+id
        cluster_string=cluster_string[1:]
        clusterid=cluster_string+' Compare Plot'
        self.global_plot[clusterid] = self.CustomPanel(" Clusters " + cluster_string + " Compare Plot")[0]
        for x in self.plot_exist:
            if 'Compare Plot' in x:
                self.plot_exist.remove(x)
        self.plot_exist.append(clusterid)
        self.exist_plot_combobox.Set(self.plot_exist)
        self.compare_cluster_date_dict[clusterid]=clu_final_date_list[cluster_list[0]]
        self.compare_cluster_data_dict[clusterid]=self.prod_data_dict
        query_clusters_data = ''
        for cluster in cluster_list:
            if cluster in prod_data_cluster_dict and prod_data_cluster_dict[cluster]!=[]:
                query_clusters_data += 'self.compare_cluster_data_dict[clusterid][\'' + cluster + '\'],'
        self.cluster_compare_list=cluster_list #self.cluster_compare_list is using for order change
        figure=plt.figure()
        self.global_axes[clusterid]=figure.add_subplot(111)
        self.global_axes[clusterid].xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        self.global_axes[clusterid].set_title('Cluster ' +  cluster_string[1:] + ' Compare Plot\n')
        self.global_axes[clusterid].legend(loc='upper right', framealpha=98.9, fontsize=10)
        self.global_axes[clusterid].set_ylabel('Km3/d',size=20)
        excute_string = "self.global_axes[clusterid].stackplot(self.compare_cluster_date_dict[clusterid]," +query_clusters_data[:-1] +",color=["+self.colors+"],colors=["+self.colors+"],alpha=0.6)"
        exec(excute_string)
        figure.autofmt_xdate()
        self.global_canvas[clusterid] = FigureCanvas(self.global_plot[clusterid], wx.NewId(), figure)
        toolbar = add_toolbar(self.global_canvas[clusterid])
        self.CustomLayout(self.global_plot[clusterid], 'Center')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.global_canvas[clusterid], 5, flag=wx.GROW)
        sizer.Add(toolbar, 1, wx.BOTTOM)
        self.global_plot[clusterid].SetSizer(sizer)
        '''
        Color Define did not config
        '''
        well_list = []
        color_dict = OrderedDict()
        i = 0
        for id in cluster_list:
            color_dict[id] = plt.Rectangle((i, 0), 1, 1, angle=90.0, fc=self.color_list[i])
            well_list.append(color_dict[id])
            i += 1

        legend=self.global_axes[clusterid].legend(well_list, color_dict.keys(), loc='upper center', ncol=9, fontsize=10)
        legend.draggable(state=True)

        print legend.get_title()
        self._mgr.Update()
        db.close()
        for x in self.global_axes[clusterid].get_xlim():
            print x

        return (self.global_plot[clusterid])

    def OnClusterCompareClick(self,event):
        if self.text3_exist == True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist = False
        if self.cluster_compare == False:
            self.cluster_compare = True
        else:
            self._mgr.DetachPane(self.checked_dict[self.cluster_compare_string])
            self.checked_dict[self.cluster_compare_string].Destroy()
            self.cluster_compare_string=''
        cluster_list=[]
        for id in self.bb9_cluster_list:
            if self.bb9_cluster_list[id].IsChecked():
               cluster_list.append(id)
        self.WellidInCluster(cluster_list=cluster_list)
        self.MinProdDateWells(cluster_list=cluster_list)
        self.MaxProdDateWells(cluster_list=cluster_list)
        self.DefineProdDateStander(cluster_list=cluster_list)
        self.CompareProdDateDiff(cluster_list=cluster_list)
        self.TidyUpProdData(cluster_list=cluster_list)
        prod_data_cluster_dict = self.prod_data_dict
        clu_final_date_list=self.final_date_dict
        self.cluster_compare_string=''

        for id in cluster_list:
            self.cluster_compare_string=self.cluster_compare_string+','+id
        self.checked_dict[self.cluster_compare_string] = self.CompareClusterPlot(clu_final_date_list,prod_data_cluster_dict,cluster_list)
        print self.cluster_compare_string

        self._mgr.Update()

    def OnClusterCompare3Dplot(self,event):
        cluster_list=[]
        if self.text3_exist == True:
            self._mgr.DetachPane(self.text3)
            self.text3.Destroy()
            self.text3_exist = False
        if self.cluster_compare_3d==False:
            self.cluster_compare_3d=True
        else:
            self._mgr.DetachPane(self.checked_dict[self.cluster_compare_string])
            self.checked_dict[self.cluster_compare_string].Destroy()
            self.cluster_compare_string = ''
        for id in self.bb9_cluster_list:
            if self.bb9_cluster_list[id].IsChecked():
                cluster_list.append(id)
        self.WellidInCluster(cluster_list=cluster_list)
        self.MinProdDateWells(cluster_list=cluster_list)
        self.MaxProdDateWells(cluster_list=cluster_list)
        self.DefineProdDateStander(cluster_list=cluster_list)
        self.CompareProdDateDiff(cluster_list=cluster_list)
        self.TidyUpProdData(cluster_list=cluster_list)
        self.cluster_compare_string = ''
        for id in cluster_list:
            self.cluster_compare_string=self.cluster_compare_string+','+id
        self.checked_dict[self.cluster_compare_string]=self.ClusterCompare3Dplot(cluster_list,self.cluster_compare_string)
        self._mgr.Update()

    def ClusterCompare3Dplot(self,cluster_list,cluster_string):
        prod_data_cluster_dict = self.prod_data_dict
        clu_final_date_list = self.final_date_dict
        canvas_panel = self.CustomPanel("Cluster " + cluster_string[1:]+ " 3D Plot")[0]
        pp3.__init__(self)
        canvas3d = FigureCanvas(canvas_panel, wx.NewId(), self.figure3d)
        for id in clu_final_date_list:
            if clu_final_date_list[id]!=[]:
                clusterid=id

        self.axis_create(clu_final_date_list[clusterid], prod_data_cluster_dict, cluster_list, cluster_string,cluster=True)
        self.CustomLayout(canvas_panel, 'Center')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas3d, 2, flag=wx.GROW)
        canvas_panel.SetSizer(sizer)
        self._mgr.Update()

        return (canvas_panel)