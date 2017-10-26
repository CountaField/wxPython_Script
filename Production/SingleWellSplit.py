__author__ = 'Administrator'
import wx
import wx.lib.buttons as buttons
from DailyAlarmReport import AlarmMain
from DailyProdReport import  DailyProdReportMainFrame as DPR
from HistoricalProddataReview import HistoricalProddataReview as hpr
from DesandingReport import DesandingMain as dm
from SingleWellProdReport import SingleWellProdReport as spr
import threading
import time


class SingleWellMainFrame(wx.MDIChildFrame):

    def __init__(self,parent):

        self.parent=parent
        wx.MDIChildFrame.__init__(self,parent,-1,'Single Well Data Summary',size=(3000,3000))
        self.sp = wx.SplitterWindow(self,-1,name='Main Menu')
        self.menu_panel1=wx.Panel(self.sp,style=wx.SUNKEN_BORDER)
        self.menu_panel1.SetBackgroundColour('light gray')
        self.Alarm_button=buttons.GenButton(self.menu_panel1,-1,'Daily Production Alarm Report')
        self.Alarm_button.SetBackgroundColour('sky blue')
        self.Daily_Prod_Report_button=buttons.GenButton(self.menu_panel1,-1,'Daily Production Report')
        self.Daily_Prod_Report_button.SetBackgroundColour('green yellow')
        self.Desand_Report_button=buttons.GenButton(self.menu_panel1,-1,'Desanding Report')
        self.Desand_Report_button.SetBackgroundColour('wheat')
        self.menu_panel1.SetSizer(self.MakeStaticBoxSizer('Menu'))
        self.sp.Initialize(self.menu_panel1)
        self.Bind(wx.EVT_BUTTON,self.OnAlarmShow,self.Alarm_button)
        self.Bind(wx.EVT_BUTTON,self.OnDailyProdShow,self.Daily_Prod_Report_button)
        self.Bind(wx.EVT_BUTTON,self.OnDesandClick,self.Desand_Report_button)


    def MakeStaticBoxSizer(self,boxlabel):
        box=wx.StaticBox(self.menu_panel1, -1, boxlabel)
        sizer=wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(self.Daily_Prod_Report_button,0,flag=wx.EXPAND)
        sizer.Add(self.Alarm_button,0,flag=wx.EXPAND)
        sizer.Add(self.Desand_Report_button,0,flag=wx.EXPAND)

        return sizer

    def OnAlarmShow(self,event):
        if self.sp.GetWindow2() is None:
            marker = AlarmMain(self.sp)
            self.sp.SplitVertically(self.menu_panel1,marker,sashPosition=100)

            self.sp.SetMinimumPaneSize(200)
        else:
            alert_box=wx.MessageDialog(self.sp.Window2,'Clear Window ?',style=wx.YES_NO | wx.ICON_WARNING)
            reply_box=alert_box.ShowModal()
            if reply_box == wx.ID_YES:
                self.sp.Window2.Hide()
                self.sp.Initialize(self.menu_panel1)
                marker = AlarmMain(self.sp)
                self.sp.SplitVertically(self.menu_panel1,marker,sashPosition=100)
                self.sp.SetMinimumPaneSize(100)
            elif reply_box == wx.ID_NO:
                pass


    def OnDailyProdShow(self,event):
        frm = spr(self.parent)
        frm.SetSize((800, 600))
        new_thread=threading.Thread(target=self.DailyProdShow,args=(frm,))
        new_thread.start()



    def DailyProdShow(self,frm):
        frm.Show()



    def OnDesandClick(self,event):
        if self.sp.GetWindow2() is None:
            marker = dm(self.sp)
            self.sp.SplitVertically(self.menu_panel1, marker, sashPosition=100)

            self.sp.SetMinimumPaneSize(200)
        else:
            alert_box = wx.MessageDialog(self.sp.Window2, 'Clear Window ?', style=wx.YES_NO | wx.ICON_WARNING)
            reply_box = alert_box.ShowModal()
            if reply_box == wx.ID_YES:
                self.sp.Window2.Hide()
                self.sp.Initialize(self.menu_panel1)
                marker = dm(self.sp)
                self.sp.SplitVertically(self.menu_panel1, marker, sashPosition=100)
                self.sp.SetMinimumPaneSize(100)
            elif reply_box == wx.ID_NO:
                pass