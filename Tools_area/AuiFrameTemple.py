
import wx
import wx.lib.buttons as buttons
from Oracle_connection import Gsrdb_Conn

import wx.lib.agw.aui as aui
from PlotSample import PlotSample
import wx.grid
from PlotDraw import PlotDrawing
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from DailyProdTable import DailyProdTable
from EventText import  EventText
import datetime
import time
import wx.lib.scrolledpanel as ScrolledPanel



class AuiTemple(wx.MDIChildFrame,PlotSample):
    def __init__(self,parent,title='Historical Production Data Review'):
        wx.MDIChildFrame.__init__(self, parent, -1, title, size=(800, 600))
        self._mgr=aui.AuiManager(self,aui.AUI_MGR_DEFAULT | aui.AUI_MGR_TRANSPARENT_DRAG | aui.AUI_MGR_ALLOW_ACTIVE_PANE |
                                   aui.AUI_MGR_LIVE_RESIZE | aui.AUI_MGR_TRANSPARENT_HINT | aui.AUI_MGR_SMOOTH_DOCKING)
        self._toolbar=aui.AuiToolBar(self)
        self.Panel_dict = {}
        self.StaticBox_dict={}
        self.aui_parent=parent
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CustomPanel(self,panel_name,size=wx.DefaultSize,staticbox=False):

        self.Panel_dict[panel_name]=wx.Panel(self,-1,name=str(panel_name),size=size)
        self.staticbox=staticbox
        if staticbox==True:

            self.StaticBox_dict[panel_name]=wx.StaticBox(self.Panel_dict[panel_name],-1,panel_name)
            self.staticbox_sizer = wx.StaticBoxSizer(self.StaticBox_dict[panel_name],wx.VERTICAL)
        else:
            self.StaticBox_dict[panel_name]=None
        return self.Panel_dict[panel_name],self.StaticBox_dict[panel_name]

    def CustomAuiToolBar(self,toolbar_name,controlslist):

        for control in controlslist:
           self._toolbar.AddControl(control,control.GetName())

        self._toolbar.Realize()
        self._mgr.AddPane(self._toolbar,aui.AuiPaneInfo().
                          Top().MinimizeButton(False).CloseButton(False).CaptionVisible(visible=False))


    def CustomLayout(self,panel_name1,position):
            panel_name=panel_name1
            position1=position[0].upper()+position[1:]+"()"

            execute_string="self._mgr.AddPane(panel_name,aui.AuiPaneInfo().Caption(panel_name.GetName())."+position1+".MinimizeButton(True).CloseButton(False).Resizable(resizable=True))"

            exec(execute_string)


    def SetStaticBoxSizer(self,controllslist):
        if self.staticbox==True:
            for control in controllslist:
                self.staticbox_sizer.Add(control)
                self.staticbox_sizer.AddSpacer(15)
        else:
            pass
        return self.staticbox_sizer

    def OnClose(self,event):
        self.Restore()
        self.Destroy()










