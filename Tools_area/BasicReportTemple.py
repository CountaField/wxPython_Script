from Oracle_connection import Gsrdb_Conn
import wx
from GridTable import MarkerTable
import wx.grid
from GridEdit import PyWXGridEditMixin
import wx.lib.scrolledpanel as ScrolledPanel
import wx.lib.buttons as buttons




class BasicReportTemple(ScrolledPanel.ScrolledPanel):
    def __init__(self,parent,table_name,checkbox_dict):
        pass


    def GridInitial(self,parent,cur):
        if PyWXGridEditMixin not in wx.grid.Grid.__bases__:  # import copy paste cut etc. function from external module
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)  # put these action be attribute into original function of grid table
            self.grid = wx.grid.Grid(self, -1, pos=(400, 20), size=(600, 600), style=wx.BORDER_SUNKEN)



    def CheckBoxInitial(self,parent,checkbox_dict):
        db=Gsrdb_Conn('gsrdba','oracle','gsrdb')
        self.checkbox_list={}
        for id in checkbox_dict:
            data_list=[]
            query_cur=checkbox_dict[id]
            cur=db.Sql(query_cur)
            for col in cur.fetchall():
                data_list.append(col[0])
            self.checkbox_list[id]=wx.CheckListBox(parent,-1,choices=data_list)
        db.close()


    def comboboxInitial(self,parent,combobox_dict):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.combobox_list = {}
        for id in combobox_dict:
            data_list = []
            query_cur = combobox_dict[id]
            cur = db.Sql(query_cur)
            for col in cur.fetchall():
                data_list.append(col[0])
            self.checkbox_list[id] = wx.CheckListBox(parent, -1, choices=data_list)
        db.close()
        return self.checkbox_list


    def buttonInitial(self,parent,button_list):
        self.button_dict={}
        for name in button_list:
            self.button_dict[name]=wx.Button(parent,-1,str(name))
        return self.button_dict





