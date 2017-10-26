__author__ = 'Administrator'

import wx
import wx.grid
import cx_Oracle
from GridTable import MarkerTable

class Checkboxes(wx.Frame):
    def __init__(self):

        wx.Frame.__init__( self, None, -1, 'Choice Components test', size=(600, 600))


        self.panel = wx.Panel(self, -1)

        self.count = 0

        self.db = cx_Oracle.connect('gsrdba', 'oracle', 'gsrdb')

        self.cur = self.db.cursor()

        cluster_list = []
        cur_cluster = self.db.cursor().execute("select clusterid from well_header where (wellid like \'SN%\' or wellid like \'SUN003\')group by clusterid order by clusterid")
        for id in cur_cluster.fetchall():
            cluster_list.append(id[0])
        wx.StaticText(self.panel, -1, 'Cluster', (20, 20))
        self.cluster_list_box = wx.ListBox(parent=self.panel, id=-1, pos=(20, 45), choices=cluster_list, name = 'Cluster_List')

        self.Bind(wx.EVT_LISTBOX, self.well_list,self.cluster_list_box)

        self.wellid_radio= wx.RadioBox(parent=self.panel, id=150, label='Cluster Name', pos=(200,20), size=(252,95), choices=['Select Cluster'], majorDimension=3, style=wx.RA_SPECIFY_COLS)

        self.wellid_radio.Disable()


        self.Bind(wx.EVT_RADIOBOX,self.DataQuery,self.wellid_radio)
        self.grid = wx.grid.Grid(self.panel, -1, (20, 250),(400,200))
        self.grid.Disable()



    def MarkerData(self,well_id):
        '''
        :param well_id: input parameter is well id
        :return:  to_markers, tvdss and MD value from markers table in a list type data
        '''
        cur=self.db.cursor()
        cur.execute('select top_marker,marker_tvdss,marker_md from markers where wellid =\''+well_id +'\'')
        formation_list=[]
        tvdss_list = []
        md_list=[]
        self.data={}
        for x in cur.fetchall():
            formation_list.append(x[0])
            tvdss_list.append(x[1])
            md_list.append(x[2])
        col_label=['TOP_MARKERS','TVDSS','MD']

        for raw in range(len(formation_list)):

            for col in range(3):
                self.grid.SetColLabelValue(col,col_label[col])
                if col == 0:
                    self.data[(raw, col)] = formation_list[raw]

                elif col == 1:
                    self.data[(raw, col)] = tvdss_list[raw]
                elif col == 2:
                    self.data[(raw, col)] = md_list[raw]

        return (self.data, len(formation_list))




    def well_list(self,event):
        self.wellid_radio.Enable()

        self.wellid_radio.Destroy()
        well_list = []
        clusterid = self.cluster_list_box.GetStringSelection()
        cur = self.db.cursor()
        cur.execute("select wellid from well_header where clusterid=\'"+clusterid+"\' order by wellid")
        for well_id in cur.fetchall():
            well_list.append(well_id[0])

        self.wellid_radio = wx.RadioBox(parent=self.panel, id=150, label=clusterid, pos=(200,20), size=(252,95), choices=well_list, majorDimension=3, style=wx.RA_SPECIFY_COLS)

    def DataQuery(self,event):
        self.grid.Enable()
        self.grid.Destroy()
        well_id=self.wellid_radio.GetStringSelection()
        self.grid = wx.grid.Grid(self.panel, -1, (20, 250),(400,200))
        col_labels=['TOP_MARKERS','TVDSS','MD']
        table = MakerTable(data=self.MarkerData(well_id)[0],col_label=col_labels,row_count=self.MarkerData(well_id)[1])
        self.grid.SetTable(table, True)

if  __name__  ==  '__main__':
    app = wx.PySimpleApp()
    frame = Checkboxes()
    frame.Show()
    app.MainLoop()




