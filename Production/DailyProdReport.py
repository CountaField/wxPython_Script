__author__ = 'Administrator'
# -*- coding:utf8-*-

import wx
import wx.lib.buttons as buttons
from Oracle_connection import Gsrdb_Conn
from DailyProdPlot import DailyProdMain

class DailyProdReportMainFrame(wx.MDIChildFrame):
    '''
    This is lunched by Single Well Data menu button
    '''

    def __init__(self,parent):
        wx.MDIChildFrame.__init__(self,parent,-1,'Daily Single Well Production Report',size=(3000,3000))
        self.sp = wx.SplitterWindow(self,-1,name='Daily Single Well Data Summary')
        self.wellstree=wx.Panel(self.sp,style=wx.SUNKEN_BORDER)
        self.wells_tree=wx.TreeCtrl(self.wellstree,size=(200,700))
        self.ClusterTreeList()
        self.sp.Initialize(self.wellstree)
        self.SetMinSize((200,750))
        self.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeSelection,self.wells_tree)

    def ClusterTreeList(self):
        tree_root=self.wells_tree.AddRoot("South Sulige Field")
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        vs_wells_summary=self.wells_tree.AppendItem(tree_root,'VS Wells')
        h_wells_summary=self.wells_tree.AppendItem(tree_root,'Horizontal Wells')
        Normal_wells_summary=self.wells_tree.AppendItem(tree_root,'Normal Wells')

        vs_cluster_cur=db.Sql("select clusterid from well_header where wellid in "
                              "(select wellid from allocation_dhc where dhc_type='VS') "
                              "group by clusterid order by clusterid")

        h_cluster_cur=db.Sql("select clusterid from well_header where wellid like '%H%' and clusterid is not null "
                             "group by clusterid order by clusterid")

        Normal_cluster_cur=db.Sql("select clusterid from well_header where wellid not like '%H%' and  wellid not in"
                                  "(select wellid from allocation_dhc where dhc_type='VS') and clusterid is not null "
                                  "group by clusterid order by clusterid")

        self.vs_clusterid_dict={}
        self.h_clusterid_dict = {}
        self.Normal_clusterid_dict = {}
        self.vs_wells_tree_dict={}
        self.h_wells_tree_dict = {}
        self.Normal_wells_tree_dict = {}
        self.wellid_dict={}
        self.wellid_tree_dict={}
        for clusterid in vs_cluster_cur.fetchall():
            if clusterid[0]!=None:
                self.vs_clusterid_dict[clusterid[0]]=[]
                self.vs_wells_tree_dict[clusterid[0]]=self.wells_tree.AppendItem(vs_wells_summary,str(clusterid[0]))

        for clusterid in h_cluster_cur.fetchall():
            if clusterid[0] != None:
                self.h_clusterid_dict[clusterid[0]] = []
                self.h_wells_tree_dict[clusterid[0]] = self.wells_tree.AppendItem(h_wells_summary, str(clusterid[0]))

        for clusterid in Normal_cluster_cur.fetchall():
            if clusterid[0] != None:
                self.Normal_clusterid_dict[clusterid[0]] = []
                self.Normal_wells_tree_dict[clusterid[0]] = self.wells_tree.AppendItem(Normal_wells_summary, str(clusterid[0]))

        for clusterid in self.vs_clusterid_dict:
            vs_wellid_cur=db.Sql("select wellid from well_header where clusterid=\'"+clusterid+"\' and wellid  in "
                                "(select wellid from allocation_dhc where dhc_type='VS') order by wellid")
            for wellid in vs_wellid_cur.fetchall():

                self.vs_clusterid_dict[clusterid].append(wellid[0])
                self.wellid_tree_dict[wellid[0]]=self.wells_tree.AppendItem(self.vs_wells_tree_dict[clusterid],str(wellid[0]))

        for clusterid in self.h_clusterid_dict:
            h_wellid_cur = db.Sql("select wellid from well_header where clusterid=\'" + clusterid + "\' order by wellid")
            for wellid in h_wellid_cur.fetchall():

                self.h_clusterid_dict[clusterid].append(wellid[0])
                self.wellid_tree_dict[wellid[0]] = self.wells_tree.AppendItem(self.h_wells_tree_dict[clusterid],
                                                                              str(wellid[0]))
        for clusterid in self.Normal_clusterid_dict:
            Normal_wellid_cur = db.Sql(
                "select wellid from well_header where clusterid=\'" + clusterid + "\' and wellid not in "
                                                                                  " (select wellid from allocation_dhc where dhc_type='VS') order by wellid")
            for wellid in Normal_wellid_cur.fetchall():

                self.Normal_clusterid_dict[clusterid].append(wellid[0])
                self.wellid_tree_dict[wellid[0]] = self.wells_tree.AppendItem(self.Normal_wells_tree_dict[clusterid],
                                                                              str(wellid[0]))


        db.close()

    def OnTreeSelection(self,event):

        wellid=self.wells_tree.GetItemText(self.wells_tree.GetSelection())

        if 'SN'in wellid or 'SUN003' in wellid:
            if self.sp.GetWindow2() is None:
                Daily_prod_report =DailyProdMain(self.sp,wellid)
                self.sp.SplitVertically(self.wellstree, Daily_prod_report, sashPosition=200)
                self.sp.SetMinimumPaneSize(200)
            else:
                self.sp.Window2.Hide()
                self.sp.Initialize(self.wellstree)
                Daily_prod_report =DailyProdMain(self.sp,wellid)
                self.sp.SplitVertically(self.wellstree, Daily_prod_report, sashPosition=200)
                self.sp.SetMinimumPaneSize(200)
        else:
            pass







