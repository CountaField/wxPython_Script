from Oracle_connection import Gsrdb_Conn
import wx
from GridTable import MarkerTable
import wx.grid
from GridEdit import PyWXGridEditMixin
import wx.lib.scrolledpanel as ScrolledPanel
import wx.lib.buttons as buttons




class HourAlarmReport(ScrolledPanel.ScrolledPanel):
    def __init__(self,parent):
        super(HourAlarmReport,self).__init__(parent)

        if PyWXGridEditMixin not in wx.grid.Grid.__bases__:  # import copy paste cut etc. function from external module
            wx.grid.Grid.__bases__ += (
            PyWXGridEditMixin,)  # put these action be attribute into original function of grid table
        self.SetBackgroundColour('light gray')  # set background color for this frame
        self.grid = wx.grid.Grid(self, -1, pos=(400, 20), size=(600, 600), style=wx.BORDER_SUNKEN)
        self.Sizers()
        self.ClusterWellInit()
        self.StaticBoxInitial()
        self.SetSizerInit()
        self.ScrollingInit()


    def Sizers(self):

        '''
            1. initial all sizers in this frame
        '''
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.grid_sizer = wx.BoxSizer(wx.VERTICAL)
        self.prod_date_sizer = wx.BoxSizer(wx.VERTICAL)
        self.well_sizer = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.box_all_sizer = wx.BoxSizer(wx.VERTICAL)
        self.final_sizer = wx.BoxSizer(wx.HORIZONTAL)


        '''
        2.initial database connection
        '''
    def ClusterWellInit(self):

        '''
            3.initial cluster id ,well id and formation list
        '''
        db=Gsrdb_Conn('gsrdba','oracle','gsrdb')

        self.prod_date_text = wx.StaticText(self, -1, 'Production Date')
        self.well_text = wx.StaticText(self, -1, 'Well ID')
        prod_date_cur = db.Sql(
            "select production_date from vw_alarm_2h_report group by production_date order by production_date desc ")
        proddate_list = []
        for id in prod_date_cur.fetchall():
            proddate_list.append(str(id[0]))
        wellid_cur = db.Sql("select wellid from vw_alarm_2h_report group by wellid order by wellid ")
        self.wellid_list = []
        for id in wellid_cur.fetchall():
            self.wellid_list.append(str(id[0]))
        self.prod_date_combox = wx.ComboBox(self, -1, choices=proddate_list)
        self.well_combobox = wx.CheckListBox(self, -1, choices=self.wellid_list)
        self.wellid_select_all = wx.Button(self, -1, 'Select All')
        self.wellid_select_clear = wx.Button(self, -1, 'Clean All')
        self.well_combobox.SetLabel('Well Name')
        self.well_query_button = wx.Button(self, -1, 'Search')
        self.Bind(wx.EVT_COMBOBOX, self.OnClusterClick, self.prod_date_combox)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnWellidClick, self.well_combobox)
        self.Bind(wx.EVT_BUTTON, self.OnWellSelectAll, self.wellid_select_all)
        self.Bind(wx.EVT_BUTTON, self.OnWellCleanAll, self.wellid_select_clear)
        self.Bind(wx.EVT_BUTTON, self.OnSearchClick, self.well_query_button)
        db.close()



    def StaticBoxInitial(self):


        '''
        4.initial static box area in frame

        '''
        self.filter_parameter_staticbox = wx.StaticBox(self, -1, label='Advanced Options', size=(250, 200))
        self.alert_message_1 = wx.CheckBox(self.filter_parameter_staticbox, -1, 'Data Anomailes ')
        self.alert_message_2 = wx.CheckBox(self.filter_parameter_staticbox, -1, 'Liquid Loading Effect ')
        self.alert_message_3 = wx.CheckBox(self.filter_parameter_staticbox, -1, 'BHP Out of Rnage ')
        Query_button = buttons.GenButton(self.filter_parameter_staticbox, -1, 'Re-Query')

        self.box_in_sizer = wx.StaticBoxSizer(self.filter_parameter_staticbox, wx.VERTICAL)
        self.box_in_sizer.AddSpacer(7)
        self.box_in_sizer.Add(self.alert_message_1)
        self.box_in_sizer.AddSpacer(7)
        self.box_in_sizer.Add(self.alert_message_2)
        self.box_in_sizer.AddSpacer(7)
        self.box_in_sizer.Add(self.alert_message_3)
        self.box_in_sizer.AddSpacer(17)
        self.box_in_sizer.Add(Query_button)
        self.box_in_sizer.AddSpacer(10)



        '''
            5.initial grid table in frame
        '''



    def SetSizerInit(self):
        '''
        6.setup sizer to each controls in frame
        '''
        self.prod_date_sizer.Add(self.prod_date_text)
        self.prod_date_sizer.AddSpacer(5)
        self.prod_date_sizer.Add(self.prod_date_combox)
        self.well_sizer.Add(self.well_text)
        self.well_sizer.AddSpacer(10)
        self.well_sizer.Add(self.well_combobox)
        self.well_sizer.AddSpacer(7)
        self.well_sizer.Add(self.wellid_select_all)
        self.well_sizer.AddSpacer(7)
        self.well_sizer.Add(self.wellid_select_clear)
        self.well_sizer.AddSpacer(7)
        self.well_sizer.Add(self.well_query_button)
        self.well_sizer.AddSpacer(123)
        self.frame_sizer.Add(self.prod_date_sizer)
        self.frame_sizer.AddSpacer(100)
        self.frame_sizer.Add(self.well_sizer)
        self.frame_sizer.AddSpacer(10)
        self.frame_sizer.Add(self.box_in_sizer)
        self.grid_sizer.Add(self.grid)
        self.final_sizer.AddSpacer(20)
        self.final_sizer.Add(self.frame_sizer)
        self.final_sizer.AddSpacer(15)
        self.final_sizer.Add(self.box_sizer)
        self.final_sizer.AddSpacer(30)
        self.final_sizer.Add(self.grid_sizer)
        self.SetSizer(self.final_sizer)

        '''
        7.initial scrolling bar and Re-size event for frame
        '''

    def AlarmGrid(self):
        self.par_string = "wellid,production_date,alarm_message,exceed_percent,BHP,ACT_2HOUR_PROD_AVG,RIGHT_PROD,LEFT_PROD "
        self.col_list = self.par_string.upper().split(',')
        self.grid.Enable()
        self.grid.__init_mixin__()
        table = MarkerTable(data=self.AlarmData()[0], col_label=self.col_list, row_count=self.AlarmData()[1])
        self.grid.SetTable(table, True)
        self.grid.EnableDragColMove()
        self.grid.EnableDragGridSize()
        self.grid.EnableGridLines()
        for col in range(len(self.col_list)):
            self.grid.AutoSizeColLabelSize(col)
        self.Refresh()


    def ScrollingInit(self):

        '''
            8.initial CheckBox by Creating  self.controller dictionary
        '''

        self.Bind(wx.EVT_SIZE,self.Resize)
        self.SetupScrolling()
        self.AlarmGrid()
        self.AlarmDataProcess()


        '''
        end initial
        '''

    def AlarmData(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.data = {}
        '''
            Get prod_date and wellid value which will be used in SQL sentence
        '''
        well_id = ''
        well_id1 = self.well_combobox.GetCheckedStrings()
        well_id_list = []
        for id in well_id1:
            well_id_list.append(id.encode("utf-8"))

        for id in well_id_list:
            well_id += "\'" + id + "\',"

        well_id = well_id[:-1]
        prod_date = str(self.prod_date_combox.GetStringSelection())
        '''
            Initializing Data dictionary which will use to generate grid data, there is NOT COLUMN FILTER function here.
        '''
        for list_name in self.col_list:  # Create list for each col in grid
            self.data[list_name] = []

        '''
            Querying data according well_id and prod_data from database
        '''
        if well_id != '':

            if prod_date != '':

                cur = db.Sql(
                    "select " + self.par_string + "from vw_alarm_2h_report where wellid in (" + well_id + ") and production_date=to_date(\'" + prod_date + "\',\'yyyy-mm-dd hh24:mi:ss\')")
                for id in cur.fetchall():
                    i = 0
                    for list_name in self.col_list:
                        self.data[list_name].append(id[i])
                        i += 1
            else:  # if prod date not select

                cur = db.Sql(
                    "select " + self.par_string + "from vw_alarm_2h_report where wellid in (" + well_id + ") order by production_date desc")
                for id in cur.fetchall():
                    i = 0
                    for list_name in self.col_list:
                        self.data[list_name].append(id[i])
                        i += 1
        else:  # if well_id not select

            if prod_date != '':

                cur = db.Sql(
                    "select " + self.par_string + "from vw_alarm_2h_report where production_date=to_date(\'" + prod_date + "\',\'yyyy-mm-dd hh24:mi:ss\')")
                for id in cur.fetchall():
                    i = 0
                    for list_name in self.col_list:
                        self.data[list_name].append(id[i])
                        i += 1
            else:  # if prod date not select

                cur = db.Sql(
                    "select " + self.par_string + "from vw_alarm_2h_report order by production_date desc")
                for id in cur.fetchall():
                    i = 0
                    for list_name in self.col_list:
                        self.data[list_name].append(id[i])
                        i += 1
        self.result_data = {}
        for row in range(len(self.data['WELLID'])):
            i = row
            for col in range(len(self.col_list)):
                self.grid.SetColLabelValue(col, self.col_list[col])
                self.result_data[(row, col)] = self.data[self.col_list[col]][i]
        return (self.result_data, len(self.data['WELLID']))

    def AlarmDataProcess(self):
        attr = wx.grid.GridCellAttr()
        attr.SetBackgroundColour("pink")
        attr_liquid = wx.grid.GridCellAttr()
        attr_liquid.SetBackgroundColour('YELLOW')
        attr_data_tr=wx.grid.GridCellAttr()
        attr_data_tr.SetBackgroundColour('sky blue')

        for row in range(len(self.data['WELLID'])):
            for col in range(len(self.col_list)):
                if 'Anomalies' in self.grid.GetCellValue(row, col):
                    self.grid.SetAttr(row, col, attr)
                elif 'BHP out of Range' in self.grid.GetCellValue(row, col):
                    self.grid.SetAttr(row, col, attr)
                elif 'PBU' in self.grid.GetCellValue(row, col):
                    self.grid.SetAttr(row, col, attr)
                elif 'Liquid Loading Effect' in self.grid.GetCellValue(row, col):
                    self.grid.SetAttr(row, col, attr_liquid)
                elif 'Data Transfer problem' in self.grid.GetCellValue(row, col):
                    self.grid.SetAttr(row, col, attr_data_tr)
                else:
                    pass

    def OnClusterClick(self, event):
        self.AlarmData()
        self.Resize(self)

    def OnWellidClick(self, event):
        print(self.well_combobox.GetCheckedStrings())

    def OnWellSelectAll(self, event):
        self.well_combobox.SetCheckedStrings(self.wellid_list)

    def OnWellCleanAll(self, event):
        self.well_combobox.SetCheckedStrings('')

    def OnSearchClick(self, event):
        self.AlarmData()
        self.Resize(self)

    def Resize(self, event):
        self.grid.Destroy()
        f_x = self.GetVirtualSize()[0]
        f_y = self.GetVirtualSize()[1]
        self.grid = wx.grid.Grid(self, -1, pos=(315, 0), size=(0.7 * f_x, 0.85 * f_y), style=wx.BORDER_SUNKEN)
        self.grid_sizer.Add(self.grid)
        self.AlarmGrid()
        self.grid.AutoSize()
        self.AlarmDataProcess()


