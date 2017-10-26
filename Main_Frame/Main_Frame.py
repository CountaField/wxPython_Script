__author__ = 'Administrator'

import wx
from SplitterWin import GeologyFrame
from SingleWellSplit import SingleWellMainFrame as SWFrame
from ProdDailyDataImport import ProdDataImport
from FiledGuideFrame import FiledGuide
from Oracle_connection import Gsrdb_Conn
import socket
import getpass
from ClientScoket import  echo_client
import os
from multiprocessing import Process
import time
from ggsdataimport import GGSImport
from  GGSProdReport import GGSFrame
import sys
import threading
from ArcGisMapLoad import ArcGisMapLoad


class MDIMainFrame(wx.MDIParentFrame):
    def __init__(self):
        start=time.clock()
        print ("the pid is: ",os.getpid())
        print sys.version
        osusername=getpass.getuser()
        hostname=socket.gethostname()
        ipaddress=socket.gethostbyname(hostname)
        self.user_dict={'user':osusername,'host':hostname,'ip':ipaddress}
        try:
            echo_client(osusername,hostname,ipaddress)
        except socket.error:
            pass
        finally:
            pass
        print(osusername,' ',hostname,' ',ipaddress)
        image_path=r'W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\images\\'

        size_x,size_y=wx.DisplaySize()
        wx.MDIParentFrame.__init__(self, None, -1, 'GSR CORE DATABASE',size=(size_x*0.7,size_y*0.7))
        menu=wx.Menu()
        menu.Append(5000,"&GSRDB")
        menu.Append(5003,"&GSRBK")
        menu.AppendSeparator()
        menu.Append(5001,"&EXIT")
        menu_splt=wx.Menu()
        menu_splt.Append(5002,"&SubSerface")
        menubar=wx.MenuBar()
        menubar.Append(menu,"&Connect")
        menubar.Append(self.IgeoMenuInitial(),'IGEO')
        menubar.Append(menu_splt,"Geology")
        menubar.SetBackgroundColour('black')
        self.submenu_prod=wx.Menu()
        self.submenu_igeo=wx.Menu()
        self.Bind(wx.EVT_MENU,self.OnExit,id=5001)
        self.Bind(wx.EVT_LEFT_DCLICK,self.OnClick)
        self.Bind(wx.EVT_MENU,self.OnSplit,id=5002)
        menubar.Append(self.ProdMenuInitial(),'Production')
        self.Bind(wx.EVT_MENU,self.OnSingleWellMenu,self.MenuDict['Single Well Data'])
        self.Bind(wx.EVT_MENU,self.OnDailyProdImportClick,id=5005)
        self.Bind(wx.EVT_MENU,self.OnFieldSummaryClick,self.MenuDict['Filed Summary'])
        self.Bind(wx.EVT_MENU,self.OnGGSimportClick,id=5006)
        self.SetMenuBar(menubar)
        end=time.clock()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.image_path=image_path
        ArcGisMapLoad(self,image_path)
        print "Program Lunching time is %f seconds" % (end-start)

    def IgeoMenuInitial(self):
        igeo_list=['Well Header','Drilling Map','SSOC ArcGis Hyper Link','ArcGis Maps']
        self.IGeoMenuDict={}
        self.igeomenu=wx.Menu()

        for menu_list in igeo_list:
            self.IGeoMenuDict[menu_list]=self.igeomenu.Append(-1,menu_list)

        self.Bind(wx.EVT_MENU,self.OnWHMapClick,self.IGeoMenuDict['Well Header'])
        return self.igeomenu


    def ProdMenuInitial(self):
       prod_list=['Single Well Data','Filed Summary']
       self.MenuDict={}
       self.Prodmenu=wx.Menu()
       for menu_list in prod_list:
           self.MenuDict[menu_list]=self.submenu_prod.Append(-1,menu_list)
       self.Prodmenu.AppendMenu(-1,'Reservoir',self.submenu_prod)
       self.Prodmenu.Append(5005,'Daily Production Data Import')
       self.Prodmenu.Append(5006, 'GGS Production Data Import')
       return self.Prodmenu

    def OnClick(self,evt):
        return None

    def OnExit(self,evt):
        self.Close(True)


    def OnSplit(self,evt):
        self.frm = GeologyFrame(self)
        self.frm.SetSize((1000,700))
        self.frm.Show()

    def OnSingleWellMenu(self,event):
        print("single well pid: %d" %os.getpid())
        frm=SWFrame(self)
        frm.SetSize((1000,700))


    def OnDailyProdImportClick(self,event):
        self.frm=ProdDataImport(self)
        self.frm.Show()

    def OnFieldSummaryClick(self,event):
        frm=FiledGuide(self,'Filed Summary Frame')
        frm.SetSize((1000, 700))
        frm.Show()

    def OnGGSimportClick(self,event):
        dlg=GGSImport(self)

    def GGSDisplay(self):
        ggs_frame = GGSFrame(self)
        ggs_frame.TreeListQuery_button.BitmapPressed(True)


    def OnWHMapClick(self,event):
        ArcGisMapLoad(self, self.image_path)


    def OnClose(self,event):
        osusername = getpass.getuser()
        hostname = socket.gethostname()
        ipaddress = socket.gethostbyname(hostname)
        try:
            echo_client(osusername,hostname,ipaddress,close=True)
        except socket.error:
            pass
        finally:
            pass
        self.Destroy()



if __name__=='__main__':
    #app=wx.PySimpleApp()
    app=wx.App()
    frame=MDIMainFrame()
    frame.Show()
    app.MainLoop()

