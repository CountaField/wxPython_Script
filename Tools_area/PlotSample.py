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
#from DailyProdTable import DailyProdTable
import wx.lib.flatnotebook as FNB
from CreateGrid import CreateGrid
from AddTab import AddNewGridTab,NewGridTab,AddNewFrame





class PlotSample(ScrolledPanel.ScrolledPanel):
        def __init__(self,parent,wellid,table_name):
            super(PlotSample,self).__init__(parent)
            self.SetBackgroundColour('light gray')
            self.table_name=table_name
            self.wellid = wellid
            self.LineWidthInitial=False
            '''
            Plot Area Initializing
            '''


            '''
            Parameter Adjust Area Initializing
            '''


            '''
            Grid Area Initializing
            '''

        def PlotCursor(self,wellid,table_name,min_date=None,max_date=None):
            db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
            par_cur=db.Sql("select column_name from user_tab_cols where table_name=\'"+table_name+"\'")
            exclude_list=['WELLID','VALVE_STATUS']
            par_list=[]
            for id in par_cur.fetchall():
                if id[0] not in exclude_list:
                    par_list.append(id[0])
            parameter=''

            for id in par_list:
                if table_name=="AUX_5MIN_DATA_KEEP_15DAY" or table_name=="RAW_INST_DATA_KEEP_2DAY" or table_name=='RAW_DAILY_INST_WH_PRES_HOUR':
                    if id=="INSTANT_PRODUCTION_GAS":
                        parameter+='INSTANT_PRODUCTION_GAS*24/1000 AS INSTANT_PRODUCTION_GAS,'
                    elif id=='INSTANT_PRODUCTION_GAS_HOUR':
                        parameter += 'INSTANT_PRODUCTION_GAS_HOUR*24/1000 AS INSTANT_PRODUCTION_GAS_HOUR,'
                    else:
                        parameter += id + ','
                else:
                    parameter += id + ','



            #print('this is parameter',parameter)
            if min_date is not None and max_date is not None:
                cursor = db.Sql("select " + parameter[:-1] +
                                " from " + table_name + " where wellid=\'" + wellid + "\' and production_date"
                                " between to_date(\'"+min_date+"\',\'yyyy-mm-dd hh24:mi:ss\') and "
                                "to_date(\'"+max_date+"\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE")
            else:
                #print 'inst parameter',parameter
                cursor=db.Sql("select "+parameter[:-1]+" from "+table_name+ " where wellid=\'"+wellid+"\' order by PRODUCTION_DATE")
            #db.close()
            return cursor,par_list,db

        def X_Y_sec_Axis_list(self, parameter_list,Xaxis='PRODUCTION_DATE',ysec_list=[]):
            self.x_list = Xaxis
            self.y_list = parameter_list[:]
            self.y_list.remove(Xaxis)
            self.ysec_list=ysec_list
            if self.ysec_list!=[]:
                for id in self.ysec_list:
                    self.y_list.remove(id)
            return self.y_list[:],self.ysec_list[:]

        def ParametersCheckbox(self, parent,par_list):
            self.par_dict = {}
            self.par_box = wx.StaticBox(parent, -1, label='Y Axis')
            self.par_box_sizer = wx.StaticBoxSizer(self.par_box, wx.VERTICAL)
            for par in self.y_list:
                if par!='PRODUCTION_DATE':
                    self.par_dict[par] = wx.CheckBox(self.par_box, id=wx.NewId(), label=par)
                    self.par_box_sizer.Add(self.par_dict[par])
                    self.Bind(wx.EVT_CHECKBOX, lambda event, list_name=par: self.OnYaxisCBClick(event, list_name),
                              self.par_dict[par])
                    self.par_dict[par].SetValue(True)
                self.par_box.Refresh()
            #for id in self.ysec_list:
             #   self.par_dict[id].SetValue(False)

        def OnYaxisCBClick(self, event, list_name):
            print 'Check Box Trigger EVENT'
            if list_name not in self.y_list:
                self.y_list.append(list_name)
            else:
                self.y_list.remove(list_name)

            self.CleanDataSelection()

        def SecondYaxis(self, parent,par_list):
            self.ysec_dict = {}
            self.ysec_par_box = wx.StaticBox(parent, -1, label='Second Y Axis')
            self.ysec_box_sizer = wx.StaticBoxSizer(self.ysec_par_box, wx.VERTICAL)
            for par in self.ysec_list:
                if par!='PRODUCTION_DATE':
                    self.ysec_dict[par] = wx.CheckBox(self.ysec_par_box, id=wx.NewId(), label=par)
                    self.ysec_box_sizer.Add(self.ysec_dict[par])
                    self.Bind(wx.EVT_CHECKBOX, lambda event, list_name=par: self.OnSecYaxisCBClick(event, list_name),
                              self.ysec_dict[par])
            for id in self.ysec_list:
                self.ysec_dict[id].SetValue(True)

        def OnSecYaxisCBClick(self, event, list_name):
            if list_name not in self.ysec_list:
                self.ysec_list.append(list_name)
            else:
                self.ysec_list.remove(list_name)
            self.CleanDataSelection()

        def CleanDataSelection(self):
            for par in self.par_dict:
                if self.ysec_dict[par].IsChecked() == True:
                    self.par_dict[par].Disable()
                else:
                    self.par_dict[par].Enable()

            for par in self.ysec_dict:
                if self.par_dict[par].IsChecked() == True:
                    self.ysec_dict[par].Disable()
                else:
                    self.ysec_dict[par].Enable()

        def LineStyleCBCreate(self, parent,par_list):
            linestyle_list = ['Solid', 'Dashed', 'Dotted']
            self.linestyle_dict = {}
            self.linewidth_dict = {}
            label_sizer_dict = {}
            self.linestyle_par_box = wx.StaticBox(parent, -1, label='Line Style Choose')
            self.linestyle_box_sizer = wx.StaticBoxSizer(self.linestyle_par_box, wx.VERTICAL)
            for par in par_list:
                if par != 'PRODUCTION_DATE':
                    label_sizer_dict[par] = wx.BoxSizer(wx.HORIZONTAL)
                    self.linestyle_dict[par] = wx.ComboBox(self.linestyle_par_box, id=wx.NewId(), choices=linestyle_list)
                    self.Bind(wx.EVT_COMBOBOX, lambda event, list_name=par: self.OnLineStyleSelected(event, list_name),
                              self.linestyle_dict[par])

                    self.linewidth_dict[par] = wx.SpinCtrl(self.linestyle_par_box, -1, min=1, max=20, size=(40, 20))
                    self.linestyle_dict[par].SetEditable(False)
                    label_sizer_dict[par].Add(wx.StaticText(self.linestyle_par_box, -1, par + ' (Style and Width)'))
                    label_sizer_dict[par].AddSpacer(8)
                    label_sizer_dict[par].Add(self.linestyle_dict[par])
                    label_sizer_dict[par].AddSpacer(8)
                    label_sizer_dict[par].Add(self.linewidth_dict[par])
                    self.linestyle_box_sizer.Add(label_sizer_dict[par])
                    self.linestyle_box_sizer.AddSpacer(5)
                self.LineWidth()


        def LineWidth(self):
            self.LineWidthInitial=True
            self.linewidth_final_dict = {}
            for par in self.linewidth_dict:
                self.linewidth_final_dict[par] = (self.linewidth_dict[par].GetValue())
            return self.linewidth_final_dict



        def LineTypeInitializing(self):
            self.solid_list = []
            self.dashed_list = []
            self.dotted_list = []


        def OnLineStyleSelected(self, event, par_name):
            style = self.linestyle_dict[par_name].GetStringSelection()
            print 'this is style',style
            if style == 'Solid':
                if par_name not in self.solid_list:
                    self.solid_list.append(par_name)
                if par_name in self.dashed_list:
                    self.dashed_list.remove(par_name)
                if par_name in self.dotted_list:
                    self.dotted_list.remove(par_name)
            elif style == 'Dashed':
                if par_name not in self.dashed_list:
                    self.dashed_list.append(par_name)
                if par_name in self.solid_list:
                    self.solid_list.remove(par_name)
                if par_name in self.dotted_list:
                    self.dotted_list.remove(par_name)
            elif style == 'Dotted':
                if par_name not in self.dotted_list:
                    self.dotted_list.append(par_name)
                if par_name in self.dashed_list:
                    self.dashed_list.remove(par_name)
                if par_name in self.solid_list:
                    self.solid_list.remove(par_name)

        def YaxisStepSpinCtrl(self,parent):
            '''
            using for adjust scale of X and Y axis
            '''
            self.ScStaticBox = wx.StaticBox(parent, -1, label='Scale Modification')
            self.Sc_Box_Sizer = wx.StaticBoxSizer(self.ScStaticBox, wx.VERTICAL)

            YAxisSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.YaxisText = wx.StaticText(self.ScStaticBox, -1, 'Y Axis Scale Interval :   ')
            self.YaxisSc = fs.FloatSpin(self.ScStaticBox, -1, min_val=0, max_val=10000)
            self.YaxisSc.SetFormat("%f")
            self.YaxisSc.SetDigits(2)
            YAxisSizer.Add(self.YaxisText)
            YAxisSizer.Add(self.YaxisSc)
            self.Sc_Box_Sizer.Add(YAxisSizer)
            self.Sc_Box_Sizer.AddSpacer(15)

            minorYaxisSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.minorYaxisText = wx.StaticText(self.ScStaticBox, -1, 'Y secA Scale Interval :  ')
            self.minorYaxisSc = fs.FloatSpin(self.ScStaticBox, -1, min_val=0, max_val=10000)
            self.minorYaxisSc.SetFormat("%f")
            self.minorYaxisSc.SetDigits(2)
            minorYaxisSizer.Add(self.minorYaxisText)
            minorYaxisSizer.Add(self.minorYaxisSc)
            self.Sc_Box_Sizer.Add(minorYaxisSizer)
            self.Sc_Box_Sizer.AddSpacer(15)

            XaxisSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.XaxisText = wx.StaticText(self.ScStaticBox, -1, 'X Axis Scale Interval : \n (Interval Minute/Days)  ')
            self.XaxisSc = wx.SpinCtrl(self.ScStaticBox, -1, min=0, max=9999)
            XaxisSizer.Add(self.XaxisText)
            XaxisSizer.Add(self.XaxisSc)
            self.Sc_Box_Sizer.Add(XaxisSizer)
            self.Sc_Box_Sizer.AddSpacer(15)
            self.confirm_button = wx.Button(self.ScStaticBox, -1, 'Confirm')
            self.Bind(wx.EVT_BUTTON, self.OnScaleConfirmButtonClick, self.confirm_button)
            self.Sc_Box_Sizer.Add(self.confirm_button)

        def OnScaleConfirmButtonClick(self, event):
            step_y = self.YaxisSc.GetValue()
            step_ysec = self.minorYaxisSc.GetValue()
            step_x = self.XaxisSc.GetValue()
            self.plot.ScaleSetting(step_y, step_ysec, step_x)
            self.canvas.draw()


        def add_toolbar(self,canvas):
            """Copied verbatim from embedding_wx2.py"""
            self.toolbar = NavigationToolbar2Wx(canvas)
            self.toolbar.Realize()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # update the axes menu on the toolbar
            self.toolbar.update()
            return self.toolbar

        #def ShowDataTable(self, event):
         #   frm = DailyProdTable(self, self.wellid, table_name=self.table_name)
          #  frm.Show()

