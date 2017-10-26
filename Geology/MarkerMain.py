__author__ = 'Administrator'


from Oracle_connection import Gsrdb_Conn
import wx
from GridTable import MarkerTable
import wx.grid
from GridEdit import PyWXGridEditMixin
import wx.lib.scrolledpanel as ScrolledPanel
import wx.lib.buttons as buttons
import wx.lib.flatnotebook as FNB

class SubsurfaceMain(FNB.FlatNotebook):
    def __init__(self,parent):
        '''FNB.FNB_DROPDOWN_TABS_LIST | \
                  FNB.FNB_FANCY_TABS | \
                  FNB.FNB_SMART_TABS | \
                  FNB.FNB_X_ON_TAB | \''''
        mystyle = FNB.FNB_DCLICK_CLOSES_TABS | \
                  FNB.FNB_ALLOW_FOREIGN_DND | \
                  FNB.FNB_BACKGROUND_GRADIENT | \
                  FNB.FNB_BOTTOM

        super(SubsurfaceMain,self).__init__(parent,-1,style=FNB.FNB_BOTTOM)
        marker_tab=MarkerMain(self)
        md_tab=MdFrame(self)
        self.AddPage(marker_tab,'Marker Frame')
        self.AddPage(md_tab,'MD Frame')


class MdFrame(ScrolledPanel.ScrolledPanel):

    def __init__(self,parent):

        super(MdFrame,self).__init__(parent)
        '''
        1. initial all sizers in this fraem
        '''
        self.x=0
        frame_sizer=wx.BoxSizer(wx.VERTICAL)
        self.grid_sizer=wx.BoxSizer(wx.VERTICAL)
        cluster_sizer=wx.BoxSizer(wx.VERTICAL)
        self.well_sizer=wx.BoxSizer(wx.VERTICAL)
        box_sizer=wx.BoxSizer(wx.VERTICAL)
        box_in_sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.box_all_sizer=wx.BoxSizer(wx.VERTICAL)
        self.final_sizer=wx.BoxSizer(wx.HORIZONTAL)
        '''
        2.initial database connection
        '''
        db=Gsrdb_Conn('gsrdba','oracle','gsrdb')

        '''
        3.initial cluster id ,well id and formation list
        '''

        cluster_text=wx.StaticText(self,-1,'Cluster Id')
        well_text=wx.StaticText(self,-1,'Well ID')
        self.formation_text=wx.StaticText(self,-1,'Formation Selection',pos=(20,200))
        cluster_cur=db.Sql("select clusterid from well_header where (WELLID like \'SN%\' "
                           "or wellid like \'SUN003\') group by clusterid order by clusterid ")
        cluster_list=[]
        for id in cluster_cur.fetchall():
            cluster_list.append(id[0])
        self.cluster_combox=wx.ComboBox(self,-1,choices=cluster_list)
        self.well_combobox=wx.ComboBox(self,-1,choices=[])
        self.well_combobox.SetLabel('Well Name')
        self.formation_filter_list=wx.ComboBox(self,-1,choices=[])
        self.formation_filter_list.SetLabel('Select Marker')
        self.Bind(wx.EVT_COMBOBOX,self.OnClusterClick,self.cluster_combox)
        self.Bind(wx.EVT_COMBOBOX,self.OnWellidClick,self.well_combobox)

        '''
        4.initial static box area in frame
        '''
        self.box=wx.StaticBox(self,-1,'Filter Parameters',size=(150,600))
        self.tvd_md_rbox=wx.RadioBox(self.box,-1,'TVD or MD',pos=(20,40),choices=['MD','TVD'])
        self.tvd_md_rbox.Disable()
        self.Bind(wx.EVT_RADIOBOX,self.OnTvdmdrboxClick,self.tvd_md_rbox)

        '''
        5.initial grid table in frame
        '''
        if PyWXGridEditMixin not in wx.grid.Grid.__bases__: #import copy paste cut etc. function from external module
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)  # put these action be attribute into original function of grid table
        self.SetBackgroundColour('light gray') # set background color for this frame
        self.grid=wx.grid.Grid(self,-1,pos=(400,20),size=(600,600),style=wx.BORDER_SUNKEN)
        self.checkbox_list=[] # initializing Filter column list
        #self.MdData()

        '''
        6.setup sizer to each controls in frame
        '''
        cluster_sizer.Add(cluster_text)
        cluster_sizer.AddSpacer(5)
        cluster_sizer.Add(self.cluster_combox)
        self.well_sizer.Add(well_text)
        self.well_sizer.AddSpacer(10)
        self.well_sizer.Add(self.well_combobox)
        self.well_sizer.AddSpacer(123)
        self.well_sizer.Add(self.formation_text)
        self.well_sizer.AddSpacer(6)
        self.well_sizer.AddSpacer(self.formation_filter_list)
        frame_sizer.Add(cluster_sizer)
        frame_sizer.AddSpacer(100)
        frame_sizer.Add(self.well_sizer)
        box_sizer.Add(self.box)
        self.grid_sizer.Add(self.grid)
        self.final_sizer.AddSpacer(20)
        self.final_sizer.Add(frame_sizer)
        self.final_sizer.AddSpacer(15)
        self.final_sizer.Add(box_sizer)
        self.final_sizer.AddSpacer(30)
        self.final_sizer.Add(self.grid_sizer)
        self.SetSizer(self.final_sizer)
        '''
        7.initial scrolling bar for frame
        '''
        self.Bind(wx.EVT_SIZE,self.Resize)
        self.SetupScrolling()

        '''
        8.initial CheckBox by Creating  self.controller dictionary
        '''
        self.controller={}
        self.FilterButton=buttons.GenButton(self.box,-1,'Filter Column',pos=(10,500))
        self.Bind(wx.EVT_BUTTON,self.OnFilterButtonClick,self.FilterButton)
        '''
        end initial
        '''
        db.close()
    def OnClusterClick(self,event):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.well_combobox.Destroy()
        well_list=[]
        cluster_id=self.cluster_combox.GetStringSelection()

        cur=db.Sql("select wellid from well_header where clusterid=\'"+cluster_id+"\' order by wellid")
        for id in cur.fetchall():
            well_list.append(id[0])

        self.well_combobox=wx.ComboBox(self,-1,choices=well_list,style=wx.CB_SIMPLE,pos=(20,160))
        self.Bind(wx.EVT_COMBOBOX,self.OnWellidClick,self.well_combobox)
        db.close()

    def OnWellidClick(self,event):

        self.tvd_md_rbox.Enable()
        self.MdData()
        self.Resize(self)
        self.FilterList()
        self.FormaitonFilter()


    def OnTvdmdrboxClick(self,event):
        self.checkbox_list=[]
        self.FilterList()



    def MdData(self):
        self.data={}
        well_id=self.well_combobox.GetStringSelection()
        tvd_md=self.tvd_md_rbox.GetStringSelection()
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.col_name=[]
        if tvd_md=='MD':
            self.cur=db.Sql("select column_name from user_tab_cols where table_name=\'RAW_MD\' "
                            "and (column_name not like \'%MIN\' and column_name not like \'%MAX\')")
        else:
            self.cur=db.Sql("select column_name from user_tab_cols where table_name=\'RAW_TVD\' "
                            "and (column_name not like \'%MIN\' and column_name not like \'%MAX\')")
        for id in self.cur.fetchall():
            self.col_name.append(id[0])
        par_dict={}
        par_col=""
        length_list=[]
        if self.checkbox_list!=[]:
            self.final_col=self.checkbox_list
        else:
            self.final_col=self.col_name

        for list_name in self.final_col:
            exec('par_dict[list_name]=[]')
            par_col=par_col + list_name + ' , '
        par = par_col[:-2]
        if tvd_md=='MD':
            if self.formation_filter_list.GetStringSelection()!='':
                formation=self.formation_filter_list.GetStringSelection()
                cur2=db.Sql("select "+par+" from raw_md where wellid=\'" + well_id +
                            "\' and layer_number in (select layer_number from paysummary_depth where wellid=\'"+well_id+
                            "\' and formation=\'"+formation+"\')")
                length_test_cur= db.Sql("select layer_number from paysummary_depth where wellid=\'"+well_id+"\' and formation=\'"+formation+"\'")
            else:
                cur2 = db.Sql("select "+par+" from raw_md where wellid=\'" + well_id + "\'")
                length_test_cur= db.Sql("select LAYER_NUMBER from raw_md where wellid=\'" + well_id + "\'")
        else:
             if self.formation_filter_list.GetStringSelection()!='':
                formation=self.formation_filter_list.GetStringSelection()
                cur2=db.Sql("select "+par+" from raw_tvd where wellid=\'" + well_id +
                            "\' and layer_number in (select layer_number from paysummary_depth where wellid=\'"
                            +well_id+"\' and formation=\'"+formation+"\')")
                length_test_cur= db.Sql("select layer_number from paysummary_depth where wellid=\'"+well_id+"\' and formation=\'"+formation+"\'")
             else:
                cur2 = db.Sql("select "+par+" from raw_tvd where wellid=\'" + well_id + "\'")
                length_test_cur= db.Sql("select LAYER_NUMBER from raw_tvd where wellid=\'" + well_id + "\'")

        for i in length_test_cur.fetchall():
            if i[0] is not None:
                length_list.append(i[0])


        for id in cur2.fetchall():
            i=0

            for list_name in self.final_col:
                par_dict[list_name].append(id[i])
                i+=1

        if length_list:
            for row in range(len( length_list)):
                i=row
                for col in range(len(self.final_col)):
                    self.grid.SetColLabelValue(col,self.final_col[col])
                    self.data[(row,col)]=par_dict[self.final_col[col]][i]
        self.grid.Enable()
        self.grid.__init_mixin__()
        table=MarkerTable(data=self.data,col_label=self.final_col,row_count=len( length_list))
        self.grid.SetTable(table,True)
        self.grid.EnableDragColMove()
        self.grid.EnableDragGridSize()
        self.grid.EnableGridLines()
        for col in range(len(self.final_col)):
            self.grid.AutoSizeColLabelSize(col)
        self.Refresh()
        db.close()

    def FilterList(self):
        '''
        List all filter parameter, the name of filter parameters is column name in RAW_MD and RAW_TVD
        :return: None
        '''
        i=10
        if self.controller=={}:
            self.MdData()
            for list_name in self.col_name:
                c_name=list_name
                self.controller[list_name]=wx.CheckBox(self.box,wx.NewId(),list_name,pos=(10,100+i),name=list_name+'cb')
                self.Bind(wx.EVT_CHECKBOX,lambda event,list_name1=list_name:
                self.OnCheckBoxClick(event,list_name1),self.controller[list_name])
                i+=20
        else:
             for list_name in self.col_name:
                   self.controller[list_name].Destroy()
             self.controller={}
             self.MdData()
             self.FilterList()



    def OnCheckBoxClick(self,event,list_name):
        '''
        :param event: filter column by click check widgets in Filter Parameter box
        :param list_name: delivery list_name to self.controller dictionary to find checkbox object
        :return:checkbox object
        '''
        if list_name not in self.checkbox_list:
            self.checkbox_list.append(list_name)
        else:
            self.checkbox_list.remove(list_name)


    def OnFilterButtonClick(self,event):
        '''
        :param event: self.grid will re-display according selected checkbox
        :return: None
        '''
        if self.checkbox_list!=[]:
            if 'WELLID' in self.checkbox_list:
                self.checkbox_list.remove('WELLID')
                self.checkbox_list=['WELLID']+self.checkbox_list[:]
        self.MdData()

    def FormaitonFilter(self):
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        well_id=self.well_combobox.GetStringSelection()
        formation_list=[]
        cur=db.Sql("select formation from paysummary_depth where wellid=\'"+well_id+"\' group by formation order by formation")
        for id in cur.fetchall():
            formation_list.append(id[0].rstrip())

        pos=self.formation_filter_list.GetPosition()
        self.formation_filter_list.Destroy()
        self.formation_filter_list=wx.ComboBox(self,-1,choices=formation_list,pos=pos)
        self.Bind(wx.EVT_COMBOBOX,self.OnFormationClick,self.formation_filter_list)
        db.close()

    def OnFormationClick(self,event):
        self.MdData()
        self.Resize(self)



    def Resize(self,event):
        self.grid.Destroy()
        f_x=self.GetVirtualSize()[0]
        f_y=self.GetVirtualSize()[1]
        self.grid=wx.grid.Grid(self,-1,pos=(400,20),size=(0.7*f_x,0.85*f_y),style=wx.BORDER_SUNKEN)
        self.grid.Refresh()
        self.Refresh()
        self.MdData()
        self.grid.AutoSize()
        self.grid_sizer.Add(self.grid)
        self.formation_text.SetPosition((20,320))



class MarkerMain(ScrolledPanel.ScrolledPanel):

    def __init__(self,parent):
        self.x=0
        super(MarkerMain,self).__init__(parent)
        '''
        initial sizer
        '''
        self.choosesizer=wx.BoxSizer(wx.VERTICAL)
        self.gridsizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer=wx.BoxSizer(wx.HORIZONTAL)
        ''' Connect to gsrdb database reference input username,password and DSN name'''

        db=Gsrdb_Conn('gsrdba','oracle','gsrdb')
        '''
        specify Cluster list box function which well list box will be enabled for using after cluster is selected
        '''
        Cluster_list=[]
        Cluster_cur=db.Sql("select clusterid from well_header where (wellid like \'SN%\' "
                           "or wellid like \'SUN003\')group by clusterid order by clusterid")
        self.Refresh()
        for id in Cluster_cur.fetchall():
            Cluster_list.append(id[0])
        cluster_text=wx.StaticText(self,-1,'Cluster Name')
        self.Cluster_list_box=wx.ComboBox(self,-1,choices=Cluster_list)
        self.Cluster_list_box.SetLabel('Cluster id')
        self.SetBackgroundColour('white')
        self.Bind(wx.EVT_COMBOBOX,self.OnClickCluster,self.Cluster_list_box)

        '''

        after select well id , grid table will be created

        '''
        well_text=wx.StaticText(self,-1,'Well Name')
        self.well_list_box=wx.ComboBox(self,-1,choices=['well id '])
        self.well_list_box.SetLabel('Well Id')
        self.well_list_box.Show()
        '''

        Initialize Grid table

        '''

        if PyWXGridEditMixin not in wx.grid.Grid.__bases__:
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)
        self.grid = wx.grid.Grid(self, -1,size=(400,400),style=wx.BORDER_SUNKEN)

        self.col_size=0
        self.SetBackgroundColour('light gray')
        self.DataQuery()
        '''
        Setup Sizer
        '''
        self.choosesizer.AddStretchSpacer()
        self.choosesizer.AddMany([(cluster_text),(10,10),(self.Cluster_list_box),(40,40),(well_text),(self.well_list_box)])
        self.gridsizer.Add(self.grid)
        self.sizer.AddSpacer(20)
        self.sizer.AddMany([(self.choosesizer),(100,100),(self.gridsizer)])
        self.SetSizer(self.sizer)
        self.Bind(wx.EVT_SIZE,self.Resize)
        self.SetupScrolling()
        db.close()

    def OnClickCluster(self,event):
        '''
        :param event: cluster select
        :return: well id
        '''
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        self.well_list_box.Enable()
        self.well_list_box.Destroy()
        well_list=[]
        Cluster_id=self.Cluster_list_box.GetStringSelection()
        Well_Cur=db.Sql("select wellid from well_header where clusterid =\'"+ Cluster_id +"\' order by wellid ")
        for id in Well_Cur.fetchall():
            well_list.append(id[0])

        #elf.well_list_box=wx.ComboBox(self,-1,choices=well_list,style=wx.CB_SIMPLE,pos=(20,200)
        self.well_list_box=wx.ComboBox(self,-1,choices=well_list,style=wx.CB_SIMPLE,pos=(20,100))
        self.Bind(wx.EVT_COMBOBOX,self.OnClickWellid,self.well_list_box)
        db.close()
    def MarkerData(self,well_id):
        '''
        :param well_id: input parameter is well id
        :return:  to_markers, tvdss and MD value from markers table in a list type data
        '''
        db = Gsrdb_Conn('gsrdba', 'oracle', 'gsrdb')
        cur=db.Sql("select top_marker,marker_easting_bj54,marker_northing_bj54,marker_tvdss,marker_md "
                   "from markers where wellid =\'"+well_id +"\' and top_marker like \'Top%\' order by marker_md")
        formation_list = []
        tvdss_list = []
        md_list = []
        easting_list=[]
        northing_list=[]
        self.data={}
        for x in cur.fetchall():
            formation_list.append(x[0])
            easting_list.append(x[1])
            northing_list.append(x[2])
            tvdss_list.append(x[3])
            md_list.append(x[4])
        col_label = ['TOP_MARKERS', 'EASTING_BJ54','NORTHING_BJ54','TVDSS', 'MD']
        for raw in range(len(formation_list)):

            for col in range(5):
                self.grid.SetColLabelValue(col,col_label[col])
                if col == 0:
                    self.data[(raw, col)] = formation_list[raw]
                    if self.LengthDefine(formation_list[raw]) > self.col_size:
                        self.col_size = self.LengthDefine(formation_list[raw])
                elif col == 1:
                    self.data[(raw, col)] = easting_list[raw]
                elif col == 2:
                    self.data[(raw, col)] =northing_list[raw]
                elif col==3:
                    self.data[(raw, col)] =tvdss_list[raw]
                elif col==4:
                    self.data[(raw, col)] =md_list[raw]
        db.close()
        return (self.data, len(formation_list))


    def DataQuery(self):
        '''
        :param event: input wellid then generate one table
        :return: marker table
        '''


        well_id=self.well_list_box.GetStringSelection()


        self.grid.__init_mixin__()
        col_labels=['MARKERS','EASTING_BJ54','NORTHING_BJ54','TVDSS','MD']
        table = MarkerTable(data=self.MarkerData(well_id)[0],col_label=col_labels,row_count=self.MarkerData(well_id)[1])
        self.grid.SetTable(table, True)
        self.grid.SetColSize(0,self.col_size)
        self.grid.EnableDragColMove()
        self.grid.EnableDragGridSize()
        self.grid.EnableGridLines()
        for col in range(len(col_labels)):
            self.grid.AutoSizeColLabelSize(col)


    def OnClickWellid(self,event):
        self.DataQuery()
        self.Resize(self)


    def LengthDefine(self,text):
        f=self.grid.GetFont()
        self.grid.SetFont(f)
        width,height=self.grid.GetTextExtent(text)
        return width

    def Resize(self,event):
        self.grid.Destroy()
        f_x=self.GetVirtualSize()[0]
        f_y=self.GetVirtualSize()[1]
        self.grid=wx.grid.Grid(self,-1,pos=(200,0),size=(0.7*f_x,0.7*f_y),style=wx.BORDER_SUNKEN)
        self.DataQuery()
        self.grid.AutoSize()
        self.gridsizer.Add(self.grid)
