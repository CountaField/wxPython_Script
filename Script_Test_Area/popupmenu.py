__author__ = 'Administrator'

import wx

class Popmenu(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self,parent,size=(500,500))
        self.panel=wx.Panel(self)
        self.popupmenu=wx.Menu()
        item=self.popupmenu.Append(-1,'Copy')
        self.panel.Bind(wx.EVT_CONTEXT_MENU,self.OnShowPopup)



    def OnShowPopup(self,event):
        pos=event.GetPosition()
        pos=self.panel.ScreenToClient(pos)
        self.panel.PopupMenu(self.popupmenu,pos)

    #def OnPopupItemSelected(self,event):


if __name__=='__main__':
    app=wx.PySimpleApp()
    frame=Popmenu(None)
    frame.Show()
    app.MainLoop()