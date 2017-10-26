__author__ = 'Administrator'

from Oracle_connection import Gsrdb_Conn
import wx
from GridTable import MarkerTable
import wx.grid
from GridEdit import PyWXGridEditMixin
import wx.lib.scrolledpanel as ScrolledPanel
import wx.lib.buttons as buttons
from PlotDraw import PlotDrawing
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import  NavigationToolbar2Wx,wxc
import wx.lib.agw.floatspin as fs
import Tkinter
import FileDialog
from DailyProdTable import DailyProdTable
import wx.lib.flatnotebook as FNB
from CreateGrid import CreateGrid
from AddTab import AddNewGridTab,NewGridTab,AddNewFrame
from RealTimeProdMonitor import RealTimeProdMonitor


class DailyProdMain(FNB.FlatNotebook):
    def __init__(self,parent,wellid):

        mystyle = FNB.FNB_DROPDOWN_TABS_LIST | \
                  FNB.FNB_FANCY_TABS | \
                  FNB.FNB_SMART_TABS | \
                  FNB.FNB_X_ON_TAB | \
                  FNB.FNB_DCLICK_CLOSES_TABS | \
                  FNB.FNB_ALLOW_FOREIGN_DND | \
                  FNB.FNB_BACKGROUND_GRADIENT | \
                  FNB.FNB_BOTTOM

        super(DailyProdMain,self).__init__(parent,-1,style=mystyle)
        daily_prod_plot=DailyProdPlot(self,wellid)
        SingleWellSummary=SingleWellSummaryFrame(self,wellid)
        ProdDataQuery5min=RealTimeProdMonitor(self,wellid,'VW_RAW_DAILY_INST_WH_PRES_1MIN')
        self.AddPage(daily_prod_plot,'Daily Production Report')
        self.AddPage(SingleWellSummary,wellid+' Single Well Summary ')
        self.AddPage(ProdDataQuery5min,wellid+' Production Real Time Monitor')





class DailyProdPlot(ScrolledPanel.ScrolledPanel):
        def __init__(self,parent,wellid):
            super(DailyProdPlot,self).__init__(parent)
            self.SetBackgroundColour('light gray')
            db=Gsrdb_Conn('gsrdba','oracle','gsrdb')
            self.wellid=wellid
            '''
                1. initial all sizers in this frame
            '''
            self.figure_sizer=wx.BoxSizer(wx.VERTICAL)
            self.par_box_all_sizer=wx.BoxSizer(wx.HORIZONTAL)
            self.par_box_all_sizer.AddSpacer(100)

            '''
                2.Creating Figure by pass parameters into Class PlotDrawing
            '''
            self.solid_list=[]
            self.dashed_list=[]
            self.dotted_list=[]
            self.gridshow = wx.CheckBox(self, -1, label='Grid Show')
            parameter="PRODUCTION_DATE,daily_prod_gas,well_head_pressure,casing_pressure," \
                      "well_head_temperature,prod_cum_gas,raw_daily_prod_gas,pipeline_pres_diff,bhp_barg,bht_degc".upper()
            self.par_list=parameter.split(",")
            self.wellid_cur=db.Sql("select "+parameter+" from vw_prod_all_ssoc where wellid=\'"+wellid+"\'")
            self.y_list=self.par_list[:]
            self.y_list.remove('PRODUCTION_DATE')
            self.y_list.remove('prod_cum_gas'.upper())
            self.y_list.remove('casing_pressure'.upper())
            self.ysec_list=['prod_cum_gas'.upper(),'casing_pressure'.upper()]
            self.LineStyleCBCreate(self.par_list)
            self.plot=PlotDrawing(parent=self,wellid=wellid,parameter_list=self.par_list,cursor=self.wellid_cur,Xaxis='PRODUCTION_DATE',
                                  Yaxis_list=self.y_list,Ysec_axis_list=self.ysec_list,solid_list=self.solid_list,dashed_list=self.dashed_list,
                                  dotted_list=self.dotted_list,width_dict=self.LineWidth(),y_grid_show=self.gridshow.IsChecked(),
                                  x_grid_show=self.gridshow.IsChecked(),time_data_unit='DAY')
            self.canvas=FigureCanvas(self,wx.NewId(),self.plot.ReturnObject())
            self.ParametersCheckbox(self.par_list)
            self.SecondYaxis(self.par_list)

            '''
            button initializing
            '''
            self.CleanDataSelection()
            self.figure_sizer.AddSpacer(15)
            self.add_toolbar()
            self.replotButton=wx.Button(self,-1,'Refresh Plotting')
            self.Bind(wx.EVT_BUTTON,self.OnrePlotbuttonClick,self.replotButton)
            self.tablebutton=wx.Button(self,-1,'Checking Table')
            self.Bind(wx.EVT_BUTTON,self.ShowDataTable,self.tablebutton)
            self.eventbutton=wx.Button(self,-1,'Show Production Log')
            self.Bind(wx.EVT_BUTTON,self.OnShowEventTable,self.eventbutton)
            self.YaxisStepSpinCtrl()
            '''
                3.Plot Grid Show By Grid Show checkbox
            '''

            self.Bind(wx.EVT_CHECKBOX,self.OnGridShow,self.gridshow)

            '''
                Setup Sizer to each controls in frame
            '''

            self.figure_sizer.Add(self.canvas, 1, wx.LEFT | wx.CENTER | wx.GROW)
            self.par_box_all_sizer.Add(self.par_box_sizer)
            self.par_box_all_sizer.AddSpacer(20)
            self.par_box_all_sizer.Add(self.ysec_box_sizer)
            self.par_box_all_sizer.AddSpacer(20)
            self.par_box_all_sizer.Add(self.linestyle_box_sizer)
            self.par_box_all_sizer.AddSpacer(20)
            self.par_box_all_sizer.Add(self.Sc_Box_Sizer)
            self.par_box_all_sizer.AddSpacer(20)
            self.par_box_all_sizer.Add(self.ButtonSizer())
            self.figure_sizer.Add(self.par_box_all_sizer)
            self.figure_sizer.AddSpacer(50)
            self.figure_sizer.Add(self.toolbar,0,wx.BOTTOM | wx.EXPAND)
            self.SetSizer(self.figure_sizer)
            self.SetupScrolling()
            self.Fit()
            db.close()

        def ButtonSizer(self):
            sizer=wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.replotButton)
            sizer.AddSpacer(10)
            sizer.Add(self.tablebutton)
            sizer.AddSpacer(10)
            sizer.Add(self.eventbutton)
            sizer.AddSpacer(10)
            sizer.Add(self.gridshow)
            return sizer


        def add_toolbar(self):
            """Copied verbatim from embedding_wx2.py"""
            self.toolbar =NavigationToolbar2Wx(self.canvas)
            self.toolbar.Realize()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # update the axes menu on the toolbar
            self.toolbar.update()


        def CleanDataSelection(self):
            for par in self.par_dict:
                if self.ysec_dict[par].IsChecked()==True:
                    self.par_dict[par].Disable()
                else:
                    self.par_dict[par].Enable()

            for par in self.ysec_dict:
                if self.par_dict[par].IsChecked()==True:
                    self.ysec_dict[par].Disable()
                else:
                    self.ysec_dict[par].Enable()


        def ParametersCheckbox(self,par_list):
            self.par_dict={}
            self.par_box=wx.StaticBox(self,-1,label='Y Axis')
            self.par_box_sizer=wx.StaticBoxSizer(self.par_box,wx.VERTICAL)
            for par in par_list[1:]:
                self.par_dict[par]=wx.CheckBox(self.par_box,id=wx.NewId(),label=par)
                self.par_box_sizer.Add(self.par_dict[par])
                self.Bind(wx.EVT_CHECKBOX,lambda event,list_name=par:self.OnYaxisCBClick(event,list_name),self.par_dict[par])
                self.par_dict[par].SetValue(True)
            self.par_dict['prod_cum_gas'.upper()].SetValue(False)
            self.par_dict['casing_pressure'.upper()].SetValue(False)
            self.par_box.Refresh()


        def SecondYaxis(self,par_list):
            self.ysec_dict={}
            self.ysec_par_box=wx.StaticBox(self,-1,label='Second Y Axis')
            self.ysec_box_sizer=wx.StaticBoxSizer(self.ysec_par_box,wx.VERTICAL)
            for par in par_list[1:]:
                self.ysec_dict[par]=wx.CheckBox(self.ysec_par_box,id=wx.NewId(),label=par)
                self.ysec_box_sizer.Add(self.ysec_dict[par])
                self.Bind(wx.EVT_CHECKBOX,lambda event,list_name=par:self.OnSecYaxisCBClick(event,list_name),self.ysec_dict[par])
            self.ysec_dict['prod_cum_gas'.upper()].SetValue(True)
            self.ysec_dict['casing_pressure'.upper()].SetValue(True)


        def OnYaxisCBClick(self,event,list_name):
            if list_name not in self.y_list:
                self.y_list.append(list_name)
            else:
                self.y_list.remove(list_name)

            self.CleanDataSelection()

        def OnSecYaxisCBClick(self,event,list_name):
            if list_name not in self.ysec_list:
                self.ysec_list.append(list_name)
            else:
                self.ysec_list.remove(list_name)
            self.CleanDataSelection()


        def OnrePlotbuttonClick(self,event):
            x_list=self.plot.X_Y_axsi('PRODUCTION_DATE',self.y_list)[0]
            ydict=self.plot.X_Y_axsi('PRODUCTION_DATE',self.y_list)[1]
            ydict_sec=self.plot.Y_Axis_Sec()
            width_dict=self.LineWidth()
            self.plot.ChangingPlot(x_list,ydict,ydict_sec,self.solid_list,self.dashed_list,self.dotted_list,width_dict,self.gridshow.IsChecked(),self.gridshow.IsChecked())
            step_y=self.YaxisSc.GetValue()
            step_ysec=self.minorYaxisSc.GetValue()
            step_x=self.XaxisSc.GetValue()
            self.plot.ScaleSetting(step_y,step_ysec,step_x)
            self.canvas.draw()

        def LineStyleCBCreate(self,par_list):
            linestyle_list=['solid','dashed','dotted']
            self.linestyle_dict={}
            self.linewidth_dict={}
            label_sizer_dict={}
            self.linestyle_par_box=wx.StaticBox(self,-1,label='Line Style Choose')
            self.linestyle_box_sizer=wx.StaticBoxSizer(self.linestyle_par_box,wx.VERTICAL)
            for par in par_list[1:]:
                label_sizer_dict[par]=wx.BoxSizer(wx.HORIZONTAL)
                self.linestyle_dict[par]=wx.ComboBox(self.linestyle_par_box,id=wx.NewId(),choices=linestyle_list)
                self.Bind(wx.EVT_COMBOBOX,lambda event,list_name=par: self.OnLineStyleSelected(event,list_name),self.linestyle_dict[par])
                self.linewidth_dict[par]=wx.SpinCtrl(self.linestyle_par_box,-1,min=1,max=20,size=(40,20))
                self.linestyle_dict[par].SetEditable(False)
                label_sizer_dict[par].Add(wx.StaticText(self.linestyle_par_box,-1,par+' (Style and Width)'))
                label_sizer_dict[par].AddSpacer(8)
                label_sizer_dict[par].Add(self.linestyle_dict[par])
                label_sizer_dict[par].AddSpacer(8)
                label_sizer_dict[par].Add(self.linewidth_dict[par])
                self.linestyle_box_sizer.Add(label_sizer_dict[par])
                self.linestyle_box_sizer.AddSpacer(5)
            self.LineWidth()


        def LineWidth(self):
            self.linewidth_final_dict={}
            for par in self.linewidth_dict:
                self.linewidth_final_dict[par]=(self.linewidth_dict[par].GetValue())
            return self.linewidth_final_dict



        def OnLineStyleSelected(self,event,par_name):
            style=self.linestyle_dict[par_name].GetStringSelection()
            if style=='solid':
                if par_name not in self.solid_list:
                    self.solid_list.append(par_name)
                if par_name in self.dashed_list:
                    self.dashed_list.remove(par_name)
                if par_name in self.dotted_list:
                    self.dotted_list.remove(par_name)
            elif style=='dashed':
                if par_name not in self.dashed_list:
                    self.dashed_list.append(par_name)
                if par_name in self.solid_list:
                    self.solid_list.remove(par_name)
                if par_name in self.dotted_list:
                    self.dotted_list.remove(par_name)
            elif style=='dotted':
                if par_name not in self.dotted_list:
                    self.dotted_list.append(par_name)
                if par_name in self.dashed_list:
                    self.dashed_list.remove(par_name)
                if par_name in self.solid_list:
                    self.solid_list.remove(par_name)

        def YaxisStepSpinCtrl(self):
            '''
            using for adjust scale of X and Y axis
            '''
            self.ScStaticBox=wx.StaticBox(self,-1,label='Scale Modification')
            self.Sc_Box_Sizer=wx.StaticBoxSizer(self.ScStaticBox,wx.VERTICAL)

            YAxisSizer=wx.BoxSizer(wx.HORIZONTAL)
            self.YaxisText=wx.StaticText(self.ScStaticBox,-1,'Y Axis Scale Interval :   ')
            self.YaxisSc=fs.FloatSpin(self.ScStaticBox,-1,min_val=0,max_val=100)
            self.YaxisSc.SetFormat("%f")
            self.YaxisSc.SetDigits(2)
            YAxisSizer.Add(self.YaxisText)
            YAxisSizer.Add(self.YaxisSc)
            self.Sc_Box_Sizer.Add(YAxisSizer)
            self.Sc_Box_Sizer.AddSpacer(15)

            minorYaxisSizer=wx.BoxSizer(wx.HORIZONTAL)
            self.minorYaxisText=wx.StaticText(self.ScStaticBox,-1,'Y secA Scale Interval :  ')
            self.minorYaxisSc=fs.FloatSpin(self.ScStaticBox,-1,min_val=0,max_val=100)
            self.minorYaxisSc.SetFormat("%f")
            self.minorYaxisSc.SetDigits(2)
            minorYaxisSizer.Add(self.minorYaxisText)
            minorYaxisSizer.Add(self.minorYaxisSc)
            self.Sc_Box_Sizer.Add(minorYaxisSizer)
            self.Sc_Box_Sizer.AddSpacer(15)

            XaxisSizer=wx.BoxSizer(wx.HORIZONTAL)
            self.XaxisText=wx.StaticText(self.ScStaticBox,-1,'X Axis Scale Interval : \n (Interval Days)  ')
            self.XaxisSc=wx.SpinCtrl(self.ScStaticBox,-1,min=0,max=365)
            XaxisSizer.Add(self.XaxisText)
            XaxisSizer.Add(self.XaxisSc)
            self.Sc_Box_Sizer.Add(XaxisSizer)
            self.Sc_Box_Sizer.AddSpacer(15)
            confirm_button=wx.Button(self.ScStaticBox,-1,'Confirm')
            self.Bind(wx.EVT_BUTTON,self.OnScaleConfirmButtonClick,confirm_button)
            self.Sc_Box_Sizer.Add(confirm_button)


        def OnScaleConfirmButtonClick(self,event):
            step_y=self.YaxisSc.GetValue()
            step_ysec=self.minorYaxisSc.GetValue()
            step_x=self.XaxisSc.GetValue()
            self.plot.ScaleSetting(step_y,step_ysec,step_x)
            self.canvas.draw()

        def ShowDataTable(self,event):
            frm=DailyProdTable(self,self.wellid,table_name='VW_PROD_ALL_SSOC')
            frm.Show()


        def OnGridShow(self,event):
            if self.gridshow.IsChecked():
                return True
            else:
                return False

        def OnShowEventTable(self,event):
            event_col_list=[]
            db=Gsrdb_Conn('gsrdba','oracle','gsrdb')
            event_cursor=db.Sql("select column_name from user_tab_cols where table_name=\'VW_PRODCOMMENT_WITH_EVENTS\'")
            for col in event_cursor.fetchall():
                event_col_list.append(col[0])
            event_data_cursor=db.Sql("select * from VW_PRODCOMMENT_WITH_EVENTS where wellid=\'"+self.wellid+
                                          "\' order by production_date desc")
            event_data_dict, event_row_count = CreateGrid(event_col_list, event_data_cursor, 'WELLID').ReturnDictionary()
            event_table = MarkerTable(event_data_dict, event_col_list, event_row_count)
            event_frm=AddNewFrame(self.wellid+' Production Log')
            event_grid=NewGridTab(event_frm,event_table)
            event_frm.Show()
            db.close()




class SingleWellSummaryFrame(wx.MDIChildFrame):

    def __init__(self, parent, wellid):
        #super(SingleWellSummaryFrame, self).__init__(parent)
        wx.MDIChildFrame.__init__(self, parent, -1,wellid+' Sumamry Information' , size=(1000, 800))
        self.wellid=wellid


        '''
            Initializng well summary grid

        '''
        '''
         Initializing Widgets Initializing
        '''
        self.info_box = wx.StaticBox(self, -1, label='Well Summary')
        self.SizerInitial()
        self.Box_Tab = AddNewGridTab(self.info_box)
        self.wellsummary_tab = NewGridTab(self.Box_Tab, self.GridInitial(self.wellid))
        self.aof_tab=NewGridTab(self.Box_Tab,self.AofDataQuery(self.wellid))
        self.dhc_tab=NewGridTab(self.Box_Tab,self.DHCDataQuery(self.wellid))
        self.event_tab=NewGridTab(self.Box_Tab,self.EventDataQuery(self.wellid))
        self.Box_Tab.AddPage(self.wellsummary_tab,'Well Summary')
        self.Box_Tab.AddPage(self.aof_tab,'AOF Summary')
        self.Box_Tab.AddPage(self.dhc_tab,'DHC Summary')
        self.Box_Tab.AddPage(self.event_tab,'Event Summary')
        self.grid_sizer.Add(self.Box_Tab,flag=wx.EXPAND)
        self.SetSizer(self.grid_sizer)

    def SizerInitial(self):
        self.grid_sizer=wx.StaticBoxSizer(self.info_box,wx.VERTICAL)


    def GridInitial(self,wellid):

        self.info_dict={}
        self.info_data_dict={}
        self.info_text={}
        info_list = ['Wellid', 'Easting_at_TD', 'Northing_at_TD', 'GGS','Clusterid', 'Slotid', 'Velocity_String', 'RTE',
                     'Orifice_Plate']
        self.WellSummarydata,self.ws_row_count = CreateGrid(info_list,self.DataSourConfig(wellid,info_list),'Wellid').ReturnDictionary()
        wellsummary_table=MarkerTable(self.WellSummarydata,info_list,self.ws_row_count)
        return wellsummary_table


    def DataSourConfig(self,wellid,par_list):
        parameter=''
        for id in par_list:
            parameter+=id+','
        db = Gsrdb_Conn(user='gsrdba', password='oracle', dsn='gsrdb')
        cursor=db.Sql("select "+ parameter[:-1]+" from well_header where wellid=\'"+wellid+"\'")
        return cursor

    def AofDataQuery(self,wellid):
        aof_col_list=[]
        db = Gsrdb_Conn(user='gsrdba', password='oracle', dsn='gsrdb')
        col_cursor=db.Sql("select column_name from user_tab_cols where table_name=\'AOF\' ")
        for col in col_cursor.fetchall():
            aof_col_list.append(col[0])

        aof_data_cursor=db.Sql("select * from AOF where wellid=\'"+wellid+"\'")
        aof_data_dict,aof_row_count=CreateGrid(aof_col_list,aof_data_cursor,'WELLID').ReturnDictionary()
        aof_table=MarkerTable(aof_data_dict,aof_col_list,aof_row_count)
        return aof_table

    def DHCDataQuery(self,wellid):
        dhc_col_list=[]
        db = Gsrdb_Conn(user='gsrdba', password='oracle', dsn='gsrdb')
        col_cursor=db.Sql("select column_name from user_tab_cols where table_name=\'ALLOCATION_DHC\' ")
        for col in col_cursor.fetchall():
            dhc_col_list.append(col[0])
        dhc_data_cursor=db.Sql("select * from ALLOCATION_DHC where wellid=\'"+wellid+"\'")
        dhc_data_dict,dhc_row_count=CreateGrid(dhc_col_list,dhc_data_cursor,'WELLID').ReturnDictionary()
        dhc_table=MarkerTable(dhc_data_dict,dhc_col_list,dhc_row_count)
        return dhc_table

    def EventDataQuery(self,wellid):
        event_col_list = []
        db = Gsrdb_Conn(user='gsrdba', password='oracle', dsn='gsrdb')
        event_cursor = db.Sql("select column_name from user_tab_cols where table_name=\'VW_PRODCOMMENT_WITH_EVENTS\'")
        for col in event_cursor.fetchall():
            event_col_list.append(col[0])
        event_data_cursor = db.Sql("select * from VW_PRODCOMMENT_WITH_EVENTS where wellid=\'" + self.wellid +
                                        "\' order by production_date desc")
        event_data_dict, event_row_count = CreateGrid(event_col_list, event_data_cursor, 'WELLID').ReturnDictionary()
        event_table = MarkerTable(event_data_dict, event_col_list, event_row_count)
        return event_table






