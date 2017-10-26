from GuideFrame import GuideFrame
from BB9Frame import BB9Frame
import wx
from GGSProdReport import GGSFrame
from DashBoardFrame import DashboardFrame

class FiledGuide(GuideFrame):
    def __init__(self,parent,frame_label):
        GuideFrame.__init__(self,parent,frame_label)
        self.parent=parent
        button_list=['GGS Data Summary','Cluster Data Summary','Dashboard']
        self.GuideButton(button_list=button_list)
        self.SetFrameSizer()
        self.Bind(wx.EVT_BUTTON,self.OnBB9Query,self.button_dict['Cluster Data Summary'])
        self.Bind(wx.EVT_BUTTON, self.OnGGSQuery, self.button_dict['GGS Data Summary'])
        self.Bind(wx.EVT_BUTTON, self.OnDashboard, self.button_dict['Dashboard'])

    def OnBB9Query(self,event):
        frm=BB9Frame(self.parent)
        frm.SetSize((1000, 700))
        frm.Show()


    def OnGGSQuery(self,event):
        frm=GGSFrame(self.parent)
        frm.SetSize((1000,700))
        frm.Show()


    def OnDashboard(self,event):
        dash_board_frm = DashboardFrame(self.parent)
        dash_board_frm.SetSize((1024, 768))
        dash_board_frm.Show()

