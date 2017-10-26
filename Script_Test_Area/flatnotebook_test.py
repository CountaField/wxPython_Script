import wx
import wx.lib
import wx.lib.flatnotebook as FNB
from popupmenu import Popmenu
class TestFrame(wx.Frame):
    def __init__(self,parent=None):
        wx.Frame.__init__(self,parent,-1,size=(1000,1000))
        self.panel=wx.Panel(self,-1,size=(1000,1000))
        self.flatnotebook=MyFlatNotebook(self)

class MyFlatNotebook(FNB.FlatNotebook):
  def __init__(self, parent):
    mystyle = FNB.FNB_DROPDOWN_TABS_LIST|\
              FNB.FNB_FF2|\
              FNB.FNB_SMART_TABS|\
              FNB.FNB_X_ON_TAB
    super(MyFlatNotebook, self).__init__(parent,style=mystyle)
    self.text_test=wx.TextCtrl(self,-1,'this is a test')
    self.AddPage(self.text_test,'test')
    # Attributes
    '''self._imglst = wx.ImageList(16, 16)
    # Setup
    bmp = wx.Bitmap("text-x-generic.png")
    self._imglst.Add(bmp)
    bmp = wx.Bitmap("text-html.png")
    self._imglst.Add(bmp)
    self.SetImageList(self._imglst)
    # Event Handlers'''
    self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING,
    self.OnClosing)
  def OnClosing(self, event):
    """Called when a tab is closing"""
    page = self.GetCurrentPage()
    if page and hasattr(page, "IsModified"):
      if page.IsModified():
        r = wx.MessageBox("Warning unsaved changes"
                          " will be lost",
                          "Close Warning",
                          wx.ICON_WARNING|\
                          wx.OK|wx.CANCEL)
        if r == wx.CANCEL:
          event.Veto()

if __name__=='__main__':
  app=wx.PySimpleApp()
  frm=TestFrame()
  frm.Show()
  app.MainLoop()
