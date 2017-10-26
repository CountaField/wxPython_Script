__author__ = 'Administrator'
import wx
import wx.lib.buttons as buttons

from MarkerMain import SubsurfaceMain
from PaySummary import PaySummaryMain
from DataImport import TvdMdDataImport


class GeologyFrame(wx.MDIChildFrame):
    def __init__(self,parent):
        wx.MDIChildFrame.__init__(self,parent,-1,'Subsurface OverView Frame',size=(3000,3000))
        self.sp = wx.SplitterWindow(self,-1,name='Main Menu')
        self.menu_panel1=wx.Panel(self.sp,style=wx.SUNKEN_BORDER)
        self.menu_panel1.SetBackgroundColour('light gray')
        self.button_marker = buttons.GenButton(self.menu_panel1,-1,'Marker')
        self.button_marker.SetBackgroundColour('green yellow')
        self.button_paysummary = buttons.GenButton(self.menu_panel1,-1,'Pay Summary')
        self.button_paysummary.SetBackgroundColour('sky blue')
        self.button_tvd_md_import = buttons.GenButton(self.menu_panel1, -1, 'MD & TVD Data Import')
        self.button_tvd_md_import.SetBackgroundColour('wheat')
        self.menu_panel1.SetSizer(self.MakeStaticBoxSizer('Menu'))
        self.sp.Initialize(self.menu_panel1)
        self.Bind(wx.EVT_BUTTON,self.OnMarkerShow,self.button_marker)
        self.Bind(wx.EVT_BUTTON,self.OnPaysummaryShow,self.button_paysummary)
        self.Bind(wx.EVT_BUTTON,self.OnTvdMdDataImportShow,self.button_tvd_md_import)



    def MakeStaticBoxSizer(self,boxlabel):
        box=wx.StaticBox(self.menu_panel1, -1, boxlabel)
        sizer=wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(self.button_marker,0,flag=wx.EXPAND)
        sizer.Add(self.button_paysummary,0,flag=wx.EXPAND)
        sizer.Add(self.button_tvd_md_import,0,flag=wx.EXPAND)
        return sizer



    def OnMarkerShow(self,event):
        if self.sp.GetWindow2() is None:
            marker = SubsurfaceMain(self.sp)
            self.sp.SplitVertically(self.menu_panel1,marker,sashPosition=100)
            self.sp.SetMinimumPaneSize(100)
        else:
            alert_box=wx.MessageDialog(self.sp.Window2,'Clear Window ?',style=wx.YES_NO | wx.ICON_WARNING)
            reply_box=alert_box.ShowModal()
            if reply_box == wx.ID_YES:
                self.sp.Window2.Hide()
                self.sp.Initialize(self.menu_panel1)
                marker = SubsurfaceMain(self.sp)
                self.sp.SplitVertically(self.menu_panel1,marker,sashPosition=100)
                self.sp.SetMinimumPaneSize(100)
            elif reply_box == wx.ID_NO:
                pass

    def OnPaysummaryShow(self,event):
            if self.sp.GetWindow2() is None:
                paysummary = PaySummaryMain(self.sp)
                self.sp.SplitVertically(self.menu_panel1,paysummary,sashPosition=100)
                self.sp.SetMinimumPaneSize(100)
            else:
                alert_box=wx.MessageDialog(self.sp.Window2,'Clear Window ?',style=wx.YES_NO | wx.ICON_WARNING)
                reply_box=alert_box.ShowModal()
                if reply_box == wx.ID_YES:
                    self.sp.Window2.Hide()
                    self.sp.Initialize(self.menu_panel1)
                    paysummary = PaySummaryMain(self.sp)
                    self.sp.SplitVertically(self.menu_panel1,paysummary,sashPosition=100)
                    self.sp.SetMinimumPaneSize(100)
                elif reply_box == wx.ID_NO:
                    pass

    def OnTvdMdDataImportShow(self,event):
        self.frm=TvdMdDataImport(self)
        self.frm.Show()
















