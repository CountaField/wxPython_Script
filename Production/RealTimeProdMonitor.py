

from PlotSample import PlotSample
import wx
import wx.grid
from PlotDraw import PlotDrawing
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from DailyProdTable import DailyProdTable


class RealTimeProdMonitor(PlotSample):
    def __init__(self,parent,wellid,table_name):
        super(RealTimeProdMonitor,self).__init__(parent,wellid,table_name)
        self.table_name=table_name
        self.wellid=wellid
        self.canvas1_exist=False
        self.figure_sizer = wx.BoxSizer(wx.VERTICAL)
        self.par_box_all_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.par_box_all_sizer.AddSpacer(100)
        self.LineTypeInitializing()
        self.gridshow = wx.CheckBox(self, -1, label='Grid Show')
        self.parameter_list = self.PlotCursor(self.wellid, self.table_name)[1]
        self.X_Y_sec_Axis_list(self.parameter_list,ysec_list=['INSTANT_PRODUCTION_GAS'])
        self.LineStyleCBCreate(self,self.parameter_list)
        self.ParametersCheckbox(self,self.parameter_list)
        self.SecondYaxis(self,self.parameter_list)
        self.drawplot_button=wx.Button(self,-1,'Show Plot')
        self.Bind(wx.EVT_BUTTON,self.OnShowPlot,self.drawplot_button)

        '''
            button initializing
        '''

        self.CleanDataSelection()
        self.figure_sizer.AddSpacer(15)
        self.replotButton = wx.Button(self, -1, 'Refresh Plotting')
        self.Bind(wx.EVT_BUTTON, self.OnShowPlot,self.replotButton)
        self.tablebutton = wx.Button(self, -1, 'Checking Table')
        self.Bind(wx.EVT_BUTTON, self.ShowDataTable, self.tablebutton)
        self.YaxisStepSpinCtrl(self)
        '''
            3.Plot Grid Show By Grid Show checkbox
        '''



        '''
            Setup Sizer to each controls in frame
        '''


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
        self.SetSizer(self.figure_sizer)
        self.SetupScrolling()
        self.Fit()

    def ButtonSizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.drawplot_button)
        sizer.AddSpacer(10)
        sizer.Add(self.replotButton)
        sizer.AddSpacer(10)
        sizer.Add(self.tablebutton)
        sizer.AddSpacer(10)
        sizer.Add(self.gridshow)
        return sizer

    def OnShowPlot(self,event):
        if self.canvas1_exist==True:
            self.canvas.Destroy()
            self.toolbar.Destroy()
        else:
            self.canvas1_exist=True
        self.query_cur= self.PlotCursor(self.wellid, self.table_name)[0]
        self.plot = PlotDrawing(parent=self, wellid=self.wellid, parameter_list=self.parameter_list, cursor=self.query_cur,
                                 Xaxis='PRODUCTION_DATE', Yaxis_list=self.y_list, Ysec_axis_list=self.ysec_list,
                                 solid_list=self.solid_list, dashed_list=self.dashed_list,
                                 dotted_list=self.dotted_list, width_dict=self.LineWidth(),
                                 y_grid_show=self.gridshow.IsChecked(), x_grid_show=self.gridshow.IsChecked(),
                                 time_data_unit='MINUTE')
        self.canvas = FigureCanvas(self, wx.NewId(), self.plot.ReturnObject())
        self.add_toolbar(self.canvas)
        self.figure_sizer.Add(self.canvas, 1, wx.LEFT | wx.CENTER | wx.GROW)
        self.figure_sizer.Add(self.toolbar, 0, wx.BOTTOM | wx.EXPAND)
        self.SetSizer(self.figure_sizer)
        self.Fit()
        self.Refresh()
        self.Resize(self)



    def Resize(self,event):
        f_x = self.GetVirtualSize()[0]
        f_y = self.GetVirtualSize()[1]
        self.SetInitialSize((f_x,f_y))

