
import wx
import wx.grid
from GridEdit import PyWXGridEditMixin
from GridTable import MarkerTable
import wx.lib.scrolledpanel as ScrolledPanel
from Oracle_connection import Gsrdb_Conn
from CreateGrid import CreateGrid
from threading import Thread
from  collections import OrderedDict
from AuiFrameTemple import AuiTemple
import wx.lib.agw.aui as aui
import datetime

class DailyProdTable(AuiTemple):
    def __init__(self,parent,wellid,table_name,min_date=None,max_date=None,cluster=False,table_title=''):

        AuiTemple.__init__(self, parent, wellid+' Data Table')
        print 'Table Initializing'
        self.table_name=table_name
        '''
        Database Connection Initializing
        '''

        self.wellid=wellid
        self.min_date=min_date
        self.max_date=max_date
        self.cluster=cluster
        self.current_date_dict={}
        self.slide_id=1
        self.current_slide=1
        self.max_slide=0
        '''
        Initializing Sizer Configuration
        '''
        self.grid_sizer=wx.BoxSizer(wx.VERTICAL)

        '''
        Initializing grid
        '''
        if PyWXGridEditMixin not in wx.grid.Grid.__bases__:  # import copy paste cut etc. function from external module
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)  # put these action be attribute into original function of grid table
        self.grid=wx.grid.Grid(self,-1,size=(600,600),style=wx.BORDER_SUNKEN)
        self.grid.__init_mixin__()
        #self.ShowGridData(wellid,min_date,max_date,cluster)
        self.MenuInitial(wellid,table_name)
        self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Center().MinimizeButton(True).CloseButton(False))
        self._mgr.Update()
        self.ShowGridData(wellid,min_date,max_date,cluster)

        '''
        Setup Sizer
        '''

    def MenuInitial(self,wellid,table_name):
        self.date_list=[]
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        date_cur=db.Sql('select production_date from production_data where wellid=\''+wellid+'\' order by production_date')
        col_cur=db.Sql("select column_name from user_tab_cols where table_name=\'"+table_name+"\' AND colum"
                                                                                              "n_name!='WELLID'")
        col_list=[]
        for id in col_cur.fetchall():
            col_list.append(id[0])

        cond_list=['greater than','less than','equal']
        date_list=[]
        for id in date_cur.fetchall():
            date_list.append(id[0])
            self.date_list.append(str(id[0]))
        self.org_min_date=date_list[0]
        self.org_max_date=date_list[-1]
        self.menu_dict = OrderedDict()



        #elf.menu_dict['confirm']=wx.Button(self._toolbar,-1,'Confirm')
        self.menu_dict['prv_button'] = wx.Button(self._toolbar, -1, 'Prv 500 Rows <<<')
        self.menu_dict['next_button'] = wx.Button(self._toolbar, -1, 'Next 500 Rows >>>')
        #self.menu_dict['showall_button'] = wx.Button(self._toolbar, -1, 'Show All Data')

        self.Bind(wx.EVT_BUTTON,self.OnNextSlide,self.menu_dict['next_button'])
        self.Bind(wx.EVT_BUTTON, self.OnPrvSlide, self.menu_dict['prv_button'])

        self.menu_dict['prv_button'].Disable()



        control_list=[]
        for id in self.menu_dict.keys():
            control_list.append(self.menu_dict[id])
        self.CustomAuiToolBar('Menu Bar',control_list)
        self._mgr.Update()
        del date_list
        db.close()


    def OnConfirmClick(self,event):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        col_select=self.menu_dict['column_list'].GetStringSelection()
        cond_select=self.menu_dict['cond_value_list'].GetStringSelection()
        if col_select=='PRODUCTION_DATE':
            value=self.menu_dict['cond_value_list'].GetStringSelection()
            if cond_select=='less than':
                cur=db.Sql("select * from (select * from "+self.table_name+" where wellid=\'"+self.wellid+"\' and production_date"
                                                                                                          " <to_date(\'" + str(
                        value) + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE desc)  "
                                             "where rownum<=500")
            if cond_select=='greater than':
                cur=db.Sql("select * from (select * from "+self.table_name+" where wellid=\'"+self.wellid+"\' and production_date"
                                                                                                          " >to_date(\'" + str(
                        value) + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE desc)  "
                                             "where rownum<=500")
            else:
                cur = db.Sql(
                    "select * from (select * from " + self.table_name + " where wellid=\'" + self.wellid + "\' and production_date"
                                                                                                           " =to_date(\'" + str(
                        value) + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE desc)  "
                                 "where rownum<=500")
        else:
            col_select=self.menu_dict['cond_list'].GetStringSelection()
            value=self.menu_dict['cond_value_list'].GetValue()
            try:
                par_value=int(value)
            except ValueError:
                par_vlaue=str(value)
            if cond_select=='less than':
                cur = db.Sql("select * from " + self.table_name + " where "
                                                                        "wellid=\'" + self.wellid + "\' and "+col_select+"<"+value+" order by PRODUCTION_DATE desc")
            elif cond_select=='greater than':
                cur = db.Sql("select * from " + self.table_name + " where "
                                                                  "wellid=\'" + self.wellid + "\' and " + col_select + ">" + value + " order by PRODUCTION_DATE desc")
            elif cond_select=='equal':
                cur = db.Sql("select * from " + self.table_name + " where "
                                                                  "wellid=\'" + self.wellid + "\' and " + col_select + "=" + value + " order by PRODUCTION_DATE desc")



        cur_name = db.Sql("select column_name from user_tab_cols where table_name=\'" + self.table_name + "\' ")
        col_list = []
        for col_name in cur_name.fetchall():
            col_list.append(col_name[0])

        data, self.row_count = CreateGrid(col_list, cur, 'WELLID').ReturnDictionary()

        db.close()
        self.ShowGridData(wellid=self.wellid,data_return=(data,col_list))


        #new_thread = Thread(target=self.ShowGridData, args=(self.wellid, self.min_date, self.max_date, self.cluster))
        #new_thread.start()


    def OnColumnSelect(self,event):
        col_select=self.menu_dict['column_list'].GetStringSelection()
        if col_select=='PRODUCTION_DATE':
            self.menu_dict['cond_value_list'].SetItems(self.date_list)

        else:
            self.menu_dict['cond_value_list'].Clear()
        self.menu_dict['cond_list'].Enable()

    def OnCondSelect(self,event):
        col_select = self.menu_dict['column_list'].GetStringSelection()
        if col_select is not None:
            self.menu_dict['cond_value_list'].Enable()
            self.menu_dict['confirm'].Enable()






    def OnNextSlide(self,event):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        if self.current_slide!=self.max_slide:
            self.current_slide += 1
            try:
                self.current_date_dict[self.current_slide]
            except KeyError:
                self.current_date=self.current_date_dict[self.current_slide-1]
                date_cur = db.Sql("select production_date "
                                  " from (select * from " + self.table_name + " where wellid=\'" + self.wellid + "\' and production_date"
                                                                                                  " <to_date(\'" + str(
                    self.current_date) + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE desc) "
                                         "where rownum<=500")
                date_list = []

                for id in date_cur.fetchall():
                    date_list.append(id[0])

                self.current_date_dict[self.current_slide] = date_list[-1]
                self.row_length = len(date_list)

                if self.row_length < 500:
                    self.menu_dict['next_button'].Disable()
                    self.max_slide=self.current_slide
                del date_list
            except IndexError:
                pass
            self.current_date = self.current_date_dict[self.current_slide - 1]
            self.ShowGridData(self.wellid,self.current_date,None,self.cluster,next=True)
            print self.current_date, ' next current date'
            self.menu_dict['prv_button'].Enable()
            print 'current slide',self.current_slide
        elif self.max_slide != 0 and self.current_slide == self.max_slide:
            self.menu_dict['next_button'].Disable()

    def OnPrvSlide(self,event):


        if self.current_slide > 2 and self.current_slide-1>0:
            self.current_slide -= 1
            self.current_date = self.current_date_dict[self.current_slide - 1]
        elif self.current_slide ==2:
            self.current_slide -= 1
            self.current_date = self.current_date_dict[0]
            self.menu_dict['prv_button'].Disable()
        elif self.current_slide ==1:
            self.menu_dict['prv_button'].Disable()
            self.current_date = self.current_date_dict[self.current_slide - 1]

        self.ShowGridData(self.wellid, self.current_date, None, self.cluster, prv=True)
        self.menu_dict['next_button'].Enable()
        print self.current_date, ' prv current date'
        print 'current slide', self.current_slide

    def GetWellData(self,wellid,min_date,max_date,cluster,next=False,prv=False):
        print 'table Geting well Data'
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        if cluster==False:
            if min_date is not None and max_date is not None:
                cur = db.Sql("select * "
                                " from " + self.table_name + " where wellid=\'" + wellid + "\' and production_date"
                                " between to_date(\'" + min_date + "\',\'yyyy-mm-dd hh24:mi:ss\') and "
                                "to_date(\'" + max_date + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE")


            elif min_date is not None and max_date is None and next is True:


                cur = db.Sql("select * "
                             " from (select * from " + self.table_name + " where wellid=\'" + self.wellid + "\' and production_date"
                                                                                             " <to_date(\'" + str(
                    self.current_date) + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE desc)  "
                                         "where rownum<=500")


            elif min_date is not None and max_date is None and prv is True:
                cur = db.Sql("select * "
                             " from (select * from " + self.table_name + " where wellid=\'" + self.wellid + "\' and production_date"
                                                                                             " <to_date(\'" + str(
                    self.current_date) + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE desc) "
                                         "where rownum<=500  ")
            else:
                date_list=[]
                date_cur=db.Sql("select PRODUCTION_DATE   from ( select * from "+self.table_name+" where wellid=\'"+wellid+"\' order by production_date desc) "
                                                                                                                           "where rownum<=500")
                for id in date_cur.fetchall():
                    date_list.append(id[0])
                try:
                    self.current_date_dict[self.current_slide] = date_list[-1]
                    self.current_date_dict[0]=date_list[0]

                except IndexError:
                    pass
                self.row_length = len(date_list)
                del date_list
                if self.row_length < 500:
                    self.menu_dict['next_button'].Disable()
                cur=db.Sql("select * from ( select * from "+self.table_name+" where wellid=\'"+wellid+"\' order by production_date desc)"
                                                                                                      " where rownum<=500 ")
                print self.current_slide


            cur_name=db.Sql("select column_name from user_tab_cols where table_name=\'"+self.table_name+"\' ")
            col_list=[]
            for col_name in cur_name.fetchall():
                if col_name[0]!='WELLID':
                    col_list.append(col_name[0])
                else:
                    col_list.insert(0,'WELLID')

            self.data,self.row_count=CreateGrid(col_list,cur,'WELLID').ReturnDictionary()
            db.close()
            return(self.data,col_list)
        else:
            if min_date is not None and max_date is not None:

                cur = db.Sql("select * "
                             " from " + self.table_name + " where clusterid=\'" + wellid + "\' and production_date"
                             " between to_date(\'" + min_date + "\',\'yyyy-mm-dd hh24:mi:ss\') and "
                             "to_date(\'" + max_date + "\',\'yyyy-mm-dd hh24:mi:ss\') order by PRODUCTION_DATE")


            else:
                cur = db.Sql("select * from " + self.table_name + " where clusterid=\'" + wellid + "\' and rownum<=500 order by production_date desc")
            cur_name = db.Sql("select column_name from user_tab_cols where table_name=\'" + self.table_name + "\' ")
            col_list = []
            for col_name in cur_name.fetchall():
                col_list.append(col_name[0])

            self.data, self.row_count = CreateGrid(col_list, cur, 'CLUSTERID').ReturnDictionary()
            db.close()

            return (self.data, col_list)




    def ShowGridData(self,wellid=None,min_date=None,max_date=None,cluster=False,next=False,prv=False,data_return=()):
        self._mgr.DetachPane(self.grid)
        self.grid.Destroy()
        self.grid = wx.grid.Grid(self, -1, size=(600, 600), style=wx.BORDER_SUNKEN)
        self.grid.__init_mixin__()
        if data_return!=():
            data_dict, col_label=data_return
            print data_dict
        else:
            data_dict,col_label=self.GetWellData(wellid,min_date,max_date,cluster,next=next,prv=prv)
        table=MarkerTable(data=data_dict,col_label=col_label,row_count=self.row_count)
        self.grid.SetTable(table,True)
        self.grid.EnableDragColMove()
        self.grid.EnableDragGridSize()
        self.grid.EnableGridLines()
        self.grid.AutoSize()
        self.Refresh()
        self._mgr.AddPane(self.grid, aui.AuiPaneInfo().Center().MinimizeButton(True).CloseButton(False))
        self._mgr.Update()