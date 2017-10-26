
import wx
import wx.lib.buttons as buttons
from Oracle_connection import Gsrdb_Conn
from DailyProdPlot import DailyProdMain
import wx.lib.agw.aui as aui
from PlotSample import PlotSample
import wx.grid
from PlotDraw import PlotDrawing
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DailyProdTable import DailyProdTable
from EventText import  EventText
import datetime
import time

class HistoricalProddataReview(wx.MDIChildFrame,PlotSample):
    def __init__(self, parent):
        wx.MDIChildFrame.__init__(self, parent, -1, 'Historical Production Data Review', size=(4000, 4000))
        self.LineWidthInitial=False
        self._mgr=aui.AuiManager(self,aui.AUI_MGR_DEFAULT | aui.AUI_MGR_TRANSPARENT_DRAG | aui.AUI_MGR_ALLOW_ACTIVE_PANE |
                                   aui.AUI_MGR_LIVE_RESIZE | aui.AUI_MGR_TRANSPARENT_HINT | aui.AUI_MGR_SMOOTH_DOCKING)

        self.pre_center_exist=False
        self.wellselected=None
        self.text3 = wx.TextCtrl(self, -1, "Main content window",
                        wx.DefaultPosition, wx.Size(200, 150),
                        wx.NO_BORDER | wx.TE_MULTILINE)
        self.InitialToolPanel()
        self.MenuCreation()
        self.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnWellSelection,self.wells_tree_list)

    def InitialToolPanel(self):
        self.Panel_dict={}
        self.Panel_dict['Plot_Area']=wx.Panel(self,-1,name='Plot Area')
        self.Panel_dict['well_tree']=wx.Panel(self,-1,name='Well Tree Selection',size=(150,750))
        self.Panel_dict["Y_Axis_Selection"] = wx.Panel(self, -1, name='Y Axis Selection',size=(300,250))
        self.Panel_dict["Y_Sec_Axis_Selection"] = wx.Panel(self, -1, name='Y Sec Axis Selection',size=(280,80))
        self.Panel_dict["Line_Type_Selection"] = wx.Panel(self, -1, name='Line Type Selection',size=(290,280))
        self.Panel_dict["Line_Scale_Selection"] = wx.Panel(self, -1, name='Line Scale Selection',size=(380,400))
        self.Panel_dict["Extra_Tool_Bar"] = wx.Panel(self, -1, name='Common Tool Bar',size=(280,250))
        self.Panel_dict["Event_Output"] = wx.TextCtrl(self,-1,value='',
                                                      style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY,name='Event Text')
        self.Panel_dict["Event_Update"]=wx.Panel(self, -1, name='Event Update',size=(380,400))
        self._mgr.AddPane(self.text3, aui.AuiPaneInfo().CenterPane())
        self.DefineToolControl()
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.wells_tree_list)
        self.Panel_dict['well_tree'].SetSizer(sizer)

        for id in self.Panel_dict:
            if id=='well_tree':
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Left().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))

            elif id=="Line_Type_Selection":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Bottom().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            elif id=="Event_Output":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Bottom().MinimizeButton(True).CloseButton(False).Resizable(resizable=True))
            elif id=='Event_Update':
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Bottom().MinimizeButton(True).CloseButton(True).Resizable(resizable=True).Hide())
            else:
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  Right().MinimizeButton(True).CloseButton(False))

        self._mgr.Update()
        self._mgr.DoFrameLayout()

    def Setsizer(self):
        self.Panel_dict["Y_Axis_Selection"].SetSizer(self.par_box_sizer)
        self.Panel_dict["Y_Sec_Axis_Selection"].SetSizer(self.ysec_box_sizer)
        self.Panel_dict["Line_Type_Selection"].SetSizer(self.linestyle_box_sizer)
        self.Panel_dict["Line_Scale_Selection"].SetSizer(self.Sc_Box_Sizer)
        self.CommonToolBarSetting()
        self.Panel_dict["Extra_Tool_Bar"].SetSizer(self.extra_tool_sizer)

    def CommonToolBarSetting(self):
        self.extra_tool_sizer = wx.BoxSizer(wx.VERTICAL)
        self.replotButton = wx.Button(self.Panel_dict["Extra_Tool_Bar"], -1, 'Refresh Plotting')
        self.tablebutton = wx.Button(self.Panel_dict["Extra_Tool_Bar"], -1, 'Checking Table')
        self.Bind(wx.EVT_BUTTON,self.OnWellSelection,self.replotButton)

        self.extra_tool_sizer.AddSpacer(5)
        self.extra_tool_sizer.Add(self.replotButton)
        self.extra_tool_sizer.AddSpacer(5)
        self.extra_tool_sizer.Add(self.tablebutton)
        self.extra_tool_sizer.AddSpacer(5)
        self.extra_tool_sizer.Add(self.gridshow)
        self.Bind(wx.EVT_BUTTON, self.OnCheckTable, self.tablebutton)


    def DefineToolControl(self):
        self.wells_tree_list = wx.TreeCtrl(self.Panel_dict['well_tree'],size=self.Panel_dict['well_tree'].GetSize())
        self.ClusterTreeList()
        self.LineTypeInitializing() # From parent class PlotSample
        self.gridshow = wx.CheckBox(self.Panel_dict['Extra_Tool_Bar'], -1, label='Grid Show')


    def VSwells_list(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        vs_wells_list = []
        vs_wells_cur=db.Sql('SELECT WELLID FROM ALLOCATION_DHC WHERE DHC_TYPE=\'VS\' GROUP BY WELLID ORDER BY WELLID')
        for id in vs_wells_cur.fetchall():
            vs_wells_list.append(id[0])
        db.close()
        return vs_wells_list

    def CenterPlot(self,wellid,mindate=None,maxdate=None):
        vs_well_list=self.VSwells_list()

        if wellid in vs_well_list:

            self.vs_well=True
            table_name='AUX_5MIN_DATA_KEEP_15DAY'
            query_cur = self.PlotCursor(wellid, table_name)[0]
            self.parameter_list = self.PlotCursor(wellid, table_name)[1]
        else:
            self.vs_well=False

            table_name='RAW_DAILY_INST_WH_PRES_HOUR'
            query_cur = self.PlotCursor(wellid, table_name)[0]
            self.parameter_list = self.PlotCursor(wellid, table_name)[1]


        if self.wellselected!=self.vs_well:
            if self.pre_center_exist==True:
                self.linestyle_par_box.Destroy()
                self.ysec_par_box.Destroy()
                self.par_box.Destroy()
                self.ScStaticBox.Destroy()

            if table_name=='AUX_5MIN_DATA_KEEP_15DAY':
                self.X_Y_sec_Axis_list(self.parameter_list, ysec_list=['INSTANT_PRODUCTION_GAS'])

            elif table_name=='RAW_DAILY_INST_WH_PRES_HOUR':
                self.X_Y_sec_Axis_list(self.parameter_list, ysec_list=['INSTANT_PRODUCTION_GAS_HOUR'])
            self.LineStyleCBCreate(self.Panel_dict['Line_Type_Selection'], self.parameter_list)
            self.ParametersCheckbox(self.Panel_dict['Y_Axis_Selection'], self.parameter_list)
            self.SecondYaxis(self.Panel_dict['Y_Sec_Axis_Selection'], self.parameter_list)
            self.YaxisStepSpinCtrl(self.Panel_dict["Line_Scale_Selection"])
            self.wellselected=self.vs_well

        if table_name == 'AUX_5MIN_DATA_KEEP_15DAY':
            self.plot = PlotDrawing(parent=self, wellid=wellid, parameter_list=self.parameter_list, cursor=query_cur,
                                    Xaxis='PRODUCTION_DATE', Yaxis_list=self.y_list, Ysec_axis_list=self.ysec_list,
                                    solid_list=self.solid_list, dashed_list=self.dashed_list,
                                    dotted_list=self.dotted_list, width_dict=self.LineWidth(),
                                    y_grid_show=self.gridshow.IsChecked(), x_grid_show=self.gridshow.IsChecked(),
                                    time_data_unit='MINUTE')

        elif table_name == 'RAW_DAILY_INST_WH_PRES_HOUR':
            self.plot = PlotDrawing(parent=self, wellid=wellid, parameter_list=self.parameter_list, cursor=query_cur,
                                    Xaxis='PRODUCTION_DATE', Yaxis_list=self.y_list, Ysec_axis_list=self.ysec_list,
                                    solid_list=self.solid_list, dashed_list=self.dashed_list,
                                    dotted_list=self.dotted_list, width_dict=self.LineWidth(),
                                    y_grid_show=self.gridshow.IsChecked(), x_grid_show=self.gridshow.IsChecked(),
                                    time_data_unit='HOUR')

        self.canvas = FigureCanvas(self.Panel_dict['Plot_Area'], wx.NewId(), self.plot.ReturnObject())
        self.Setsizer()
        self.table_name=table_name
        return self.canvas

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


    def OnWellSelection(self,event):
        wellid = self.wells_tree_list.GetItemText(self.wells_tree_list.GetSelection())
        self.searched = False
        if  'SN'in wellid or 'SUN003' in wellid:
            self.Panel_dict['Event_Output'].Clear()
            self.wellid = wellid

            if self.pre_center_exist==False:
                self._mgr.DetachPane(self.text3)
                self.text3.Destroy()
                plotsizer=wx.BoxSizer(wx.VERTICAL)
                plotsizer.Add(self.CenterPlot(wellid),1,wx.GROW)
                self.add_toolbar(self.canvas)
                plotsizer.Add(self.toolbar,0,wx.BOTTOM | wx.GROW)
                self.Panel_dict['Plot_Area'].SetSizer(plotsizer)
                self._mgr.AddPane(self.Panel_dict['Plot_Area'], aui.AuiPaneInfo().CenterPane())
                self.Panel_dict['Event_Output'].AppendText(EventText(wellid=self.wellid).DBQuery())
                self._mgr.Update()
                self.pre_center_exist=True

            else:

                self.canvas.Destroy()
                self.toolbar.Destroy()
                plotsizer = wx.BoxSizer(wx.VERTICAL)
                plotsizer.Add(self.CenterPlot(wellid), 1, wx.GROW)
                self.add_toolbar(self.canvas)
                plotsizer.Add(self.toolbar, 0, wx.BOTTOM | wx.GROW)
                self.Panel_dict['Plot_Area'].SetSizer(plotsizer)
                self._mgr.AddPane(self.Panel_dict['Plot_Area'], aui.AuiPaneInfo().CenterPane())
                self.Panel_dict['Event_Output'].AppendText(EventText(wellid=self.wellid).DBQuery())
                self._mgr.Update()

    def MenuCreation(self):
        '''
        it's not real menu bar, just still using aui ToolBar frame to display like a menu bar
        :return:
        '''
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cur=db.Sql("select production_date from production_data group by production_date order by production_date"
                   " desc")
        prod_date_list=[]
        for id in cur.fetchall():
            prod_date_list.append(str(id[0]))
        self.FrameDisplay=aui.AuiToolBar(self)
        self.startdate_combox = wx.ComboBox(self.FrameDisplay, -1, choices=prod_date_list)
        self.enddate_combox = wx.ComboBox(self.FrameDisplay, -1, choices=prod_date_list)
        start_text=wx.StaticText(self.FrameDisplay,-1,'Start Date: ')
        end_text=wx.StaticText(self.FrameDisplay,-1,'      End Date:')
        searchbutton=wx.Button(self.FrameDisplay,-1,'Search')
        NoteBookhbutton = wx.Button(self.FrameDisplay, -1, 'Event Notebook')
        self.FrameDisplay.AddControl(start_text,'StartDate')
        self.FrameDisplay.AddControl(self.startdate_combox,'StartDateList')
        self.FrameDisplay.AddControl(end_text, 'EndDate')
        self.FrameDisplay.AddControl(self.enddate_combox, 'StartDateList')
        self.FrameDisplay.AddSpacer(10)
        self.FrameDisplay.AddControl(searchbutton)
        self.FrameDisplay.AddSpacer(10)
        self.FrameDisplay.AddControl(NoteBookhbutton)
        self.FrameDisplay.Realize()
        self.Bind(wx.EVT_BUTTON,self.OnNotebookClick,NoteBookhbutton)
        self.Bind(wx.EVT_BUTTON,self.OnMenuSearchButton,searchbutton)
        self._mgr.AddPane(self.FrameDisplay, aui.AuiPaneInfo().
                          Top().MinimizeButton(False).CloseButton(False).CaptionVisible(visible=False))
        self._mgr.Update()
        db.close()

    def OnMenuSearchButton(self,event):
        if self.pre_center_exist==True:
            self.min_date=self.startdate_combox.GetStringSelection()
            self.max_date=self.enddate_combox.GetStringSelection()
            if self.min_date!='' and  self.max_date!='':
                cur=self.PlotCursor(self.wellid,self.table_name,min_date=self.min_date,max_date=self.max_date)[0]
                self.plot = PlotDrawing(parent=self, wellid=self.wellid, parameter_list=self.parameter_list, cursor=cur,
                                Xaxis='PRODUCTION_DATE', Yaxis_list=self.y_list, Ysec_axis_list=self.ysec_list,
                                solid_list=self.solid_list, dashed_list=self.dashed_list,
                                dotted_list=self.dotted_list, width_dict=self.LineWidth(),
                                y_grid_show=self.gridshow.IsChecked(), x_grid_show=self.gridshow.IsChecked(),
                                time_data_unit='HOUR')
                self.canvas.Destroy()
                self.toolbar.Destroy()
                plotsizer = wx.BoxSizer(wx.VERTICAL)
                self.canvas = FigureCanvas(self.Panel_dict['Plot_Area'], wx.NewId(), self.plot.ReturnObject())
                plotsizer.Add(self.canvas, 1, wx.GROW)
                self.add_toolbar(self.canvas)
                plotsizer.Add(self.toolbar, 0, wx.BOTTOM | wx.GROW)
                self.Panel_dict['Plot_Area'].SetSizer(plotsizer)
                self._mgr.AddPane(self.Panel_dict['Plot_Area'], aui.AuiPaneInfo().CenterPane())
                self._mgr.Update()
                self.pre_center_exist = True
                self.searched = True


    def OnCheckTable(self,event):
        if self.searched==True:
            frm=DailyProdTable(self,self.wellid,self.table_name,self.min_date,self.max_date)
            frm.Show()
        else:
            frm = DailyProdTable(self, self.wellid, table_name=self.table_name)
            frm.Show()


    def EventUpdateFrame(self):
        self.notetext=wx.TextCtrl(self.Panel_dict['Event_Update'],-1,value='',style=wx.TE_MULTILINE | wx.TE_RICH2,
                                  name='Event Update')
        year_list=[]
        month_list=[]
        date_list=[]
        for year in range(2010,2021):
            year_list.append(str(year))
        for month in range(1,13):
            month_list.append(str(month))
        for date in range(1,32):
            date_list.append(str(date))
        year=wx.StaticText(self.Panel_dict['Event_Update'],-1,'Year:')
        month=wx.StaticText(self.Panel_dict['Event_Update'],-1,'Month:')
        day=wx.StaticText(self.Panel_dict['Event_Update'],-1,'Day:')
        self.yeartext = wx.ComboBox(self.Panel_dict['Event_Update'], -1, choices=year_list)
        self.monthtext = wx.ComboBox(self.Panel_dict['Event_Update'], -1, choices=month_list)
        self.daytext = wx.ComboBox(self.Panel_dict['Event_Update'],-1,choices=date_list)
        self.today=wx.CheckBox(self.Panel_dict['Event_Update'],-1,'Present Date')
        self.Bind(wx.EVT_CHECKBOX,self.OnTodayButtonClick,self.today)
        updatebutton=wx.Button(self.Panel_dict['Event_Update'],-1,'Update')
        self.Bind(wx.EVT_BUTTON,self.OnEventUpdateClick,updatebutton)
        sizer_date=wx.BoxSizer(wx.HORIZONTAL)
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
        sizer_date.Add(updatebutton)
        sizer_final=wx.BoxSizer(wx.VERTICAL)
        sizer_final.AddSpacer(15)
        sizer_final.Add(sizer_date)
        sizer_final.AddSpacer(15)
        sizer_final.Add(self.notetext,1,flag=wx.GROW)
        self.Panel_dict['Event_Update'].SetSizer(sizer_final)

    def OnNotebookClick(self,event):
        self.prod_date=''
        self._mgr.DetachPane(self.Panel_dict['Event_Update'])
        self.Panel_dict['Event_Update'].Destroy()
        self.Panel_dict["Event_Update"] = wx.Panel(self, -1, name='Event Update', size=(380, 400))
        self.EventUpdateFrame()
        self._mgr.AddPane(self.Panel_dict['Event_Update'],
                          aui.AuiPaneInfo().Caption(self.Panel_dict['Event_Update'].GetName()).
                          Bottom().MinimizeButton(True).CloseButton(True).Resizable(resizable=True))
        self._mgr.Update()

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



    def OnClose(self, event):
        # de-initialize the frame manager
        self._mgr.UnInit()
        self.Destroy()
        event.Skip()
