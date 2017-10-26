

import wx
import wx.lib.buttons as buttons



class GuideFrame(wx.MDIChildFrame):
    def __init__(self, parent,frame_label):
        self.parent = parent
        self.frame_label=frame_label
        wx.MDIChildFrame.__init__(self, parent, -1, frame_label, size=(3000, 3000))
        self.sp = wx.SplitterWindow(self, -1, name='Main Menu')
        self.menu_panel1 = wx.Panel(self.sp, style=wx.SUNKEN_BORDER)
        self.menu_panel1.SetBackgroundColour('light gray')



    def GuideButton(self,button_list):
        self.button_dict={}
        i=0
        button_color_list=['sky blue','green yellow','wheat','pink']
        for id in button_list:
            self.button_dict[id]=buttons.GenButton(self.menu_panel1,-1,id)
            if i<=3:
                self.button_dict[id].SetBackgroundColour(button_color_list[i])
            i+=1


    def FrameSizer(self,boxlabel):
        box = wx.StaticBox(self.menu_panel1, -1, boxlabel)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        for id in self.button_dict:
            sizer.Add(self.button_dict[id],0,flag=wx.EXPAND)
        return sizer



    def SetFrameSizer(self):
        self.menu_panel1.SetSizer(self.FrameSizer(self.frame_label))
        self.sp.Initialize(self.menu_panel1)
