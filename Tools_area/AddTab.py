import wx
import wx.lib.scrolledpanel as ScrolledPanel
from GridEdit import PyWXGridEditMixin
import wx.grid

class AddNewGridTab(wx.Notebook):
    def __init__(self,parent):
        super(AddNewGridTab,self).__init__(parent,-1,style=wx.NB_BOTTOM)

class AddNewFrame(wx.Frame):
    def __init__(self,title):
        wx.Frame.__init__(self,None,-1,title)

class NewGridTab(ScrolledPanel.ScrolledPanel):
    def __init__(self,parent,table):
        super(NewGridTab,self).__init__(parent)
        self.grid_sizer=wx.BoxSizer(wx.VERTICAL)
        if PyWXGridEditMixin not in wx.grid.Grid.__bases__:  # import copy paste cut etc. function from external module
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)  # put these action be attribute into original function of grid table
        self.grid=wx.grid.Grid(self,-1,size=(600,600),style=wx.BORDER_SUNKEN)
        self.grid.__init_mixin__()
        self.grid.SetTable(table)
        self.grid.EnableDragColMove()
        self.grid.EnableDragGridSize()
        self.grid.EnableGridLines()
        self.grid.AutoSize()
        self.Refresh()
        self.grid_sizer.Add(self.grid,flag=wx.EXPAND)
        self.SetSizer(self.grid_sizer)


