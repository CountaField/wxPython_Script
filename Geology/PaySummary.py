__author__ = 'Administrator'
from Oracle_connection import Gsrdb_Conn
import wx
from GridTable import MarkerTable
import wx.grid
from GridEdit import PyWXGridEditMixin
import wx.lib.scrolledpanel as ScrolledPanel
import wx.lib.buttons as buttons

class PaySummaryMain(wx.Notebook):
    def __init__(self,parent):
        wx.Notebook.__init__(self,parent,-1,style=wx.NB_BOTTOM)
        paysummary_tab=PaySummaryFrame(self)
        self.AddPage(paysummary_tab,'Pay Summary')


class PaySummaryFrame(ScrolledPanel.ScrolledPanel):
     def __init__(self,parent):
         super(PaySummaryFrame,self).__init__(parent)
         #elf.SetBackgroundColour('light gray') # set background color for this frame
         '''
            1. initial all sizers in this frame
         '''
         self.SizerInitial()


         '''
            2.initial database connection
         '''
         self.db=Gsrdb_Conn('gsrdba','oracle','gsrdb')

         '''
            3.initial cluster id ,well id and formation list
         '''
         self.cluster_text=wx.StaticText(self,-1,'Cluster Id')
         self.well_text=wx.StaticText(self,-1,'Well ID')
         cluster_cur=self.db.Sql("select clusterid from well_header where (WELLID like \'SN%\' or wellid like \'SUN003\') group by clusterid order by clusterid ")
         cluster_list=[]
         for id in cluster_cur.fetchall():
            cluster_list.append(id[0])
         self.cluster_combox=wx.ComboBox(self,-1,choices=cluster_list,style=wx.BORDER_SUNKEN)
         self.well_combobox=wx.ComboBox(self,-1,choices=[],style=wx.BORDER_RAISED)
         self.well_combobox.SetLabel('Well Name')
         self.Bind(wx.EVT_COMBOBOX,self.OnClusterClick,self.cluster_combox)
         self.Bind(wx.EVT_COMBOBOX,self.OnWellidClick,self.well_combobox)
         '''
            4.initial static box area in frame
         '''
         self.checkbox_list=[]
         self.box=wx.StaticBox(self,-1,'Formation Selection')
         self.box_in_sizer=wx.StaticBoxSizer(self.box,wx.VERTICAL)
         self.FilterList()
         self.FilterButton=buttons.GenButton(self.box,-1,'Query')
         self.box_in_sizer.Add(self.FilterButton)
         self.box_in_sizer.AddSpacer(30)
         self.box_list={}
         self.summary_dict={}
         self.sand_dict={}
         self.formation_text_dict={}
         self.sand_text_dict={}



         '''
            5. initializing grid table in formation box
         '''
         if PyWXGridEditMixin not in wx.grid.Grid.__bases__: #import copy past cut etc. function from external module
            wx.grid.Grid.__bases__ += (PyWXGridEditMixin,)  # put these action be attribute into original function of grid table

         '''
         6.setup sizer to each controls in frame
         '''
         self.SizerConfig()
         self.Bind(wx.EVT_BUTTON,self.OnQueryClick,self.FilterButton)

         '''
         7.initial scrolling bar for frame
         '''
         self.SetupScrolling()
         '''
         8. initial filter list in Filter Parameter box

         '''

     def SizerInitial(self):
         self.frame_sizer=wx.BoxSizer(wx.VERTICAL)
         self.grid_sizer=wx.BoxSizer(wx.VERTICAL)
         self.cluster_sizer=wx.BoxSizer(wx.VERTICAL)
         self.well_sizer=wx.BoxSizer(wx.VERTICAL)
         self.box_sizer=wx.BoxSizer(wx.VERTICAL)
         self.summary_sizer=wx.BoxSizer(wx.HORIZONTAL)
         self.box_all_sizer=wx.BoxSizer(wx.VERTICAL)
         self.final_sizer=wx.BoxSizer(wx.HORIZONTAL)
         self.summary_all_sizer=wx.BoxSizer(wx.HORIZONTAL)



     def SizerConfig(self):
         self.cluster_sizer.Add(self.cluster_text)
         self.cluster_sizer.AddSpacer(5)
         self.cluster_sizer.Add(self.cluster_combox)
         self.well_sizer.Add(self.well_text)
         self.well_sizer.AddSpacer(10)
         self.well_sizer.Add(self.well_combobox)
         self.well_sizer.AddSpacer(123)
         self.frame_sizer.Add(self.cluster_sizer)
         self.frame_sizer.AddSpacer(100)
         self.frame_sizer.Add(self.well_sizer)
         self.box_sizer.Add(self.box_in_sizer)
         self.box_sizer.AddSpacer(25)
         #self.box_sizer.Add(self.sand_box_sizer)
         self.final_sizer.AddSpacer(20)
         self.final_sizer.Add(self.frame_sizer)
         self.final_sizer.AddSpacer(15)
         self.final_sizer.Add(self.box_sizer)
         self.final_sizer.AddSpacer(30)
         self.SetSizer(self.final_sizer)

     def FilterList(self):
        '''
        initializing check box in Formation static box
        :return:
        '''
        self.box_in_sizer.AddSpacer(40)
        self.controller={}
        cur=self.db.Sql("select formation from paysummary group by formation order by formation")
        filter_list=[]
        for id in cur.fetchall():
            filter_list.append(id[0].rstrip())
        for list_name in filter_list:
            self.controller[list_name]=wx.CheckBox(self.box,wx.NewId(),list_name,name=list_name+'cb')
            self.Bind(wx.EVT_CHECKBOX,lambda event,list_name1=list_name:self.OnCheckboxClick(event,list_name1),self.controller[list_name])
            self.box_in_sizer.Add(self.controller[list_name],0,wx.EXPAND)
            self.box_in_sizer.AddSpacer(15)


     def SummaryGrid(self,f_name):
        '''
        initializing summary grid and sand level grid
        :param f_name:(this is parent static box in frame)
        :return: None
        '''
        formation_key=f_name.GetLabel()
        self.summary_sizer=wx.BoxSizer(wx.VERTICAL)
        self.col_list=['MD_Top','MD_Bottom','TVD_Top','TVD_Bottom','TVDSS_Top','TVDSS_Bottom','Thickness','PHI_AVG','H*PHI','H*PHI*SG']
        self.sand_list=['LAYER_NUMBER', 'MD_SAND_TOP', 'MD_SAND_BOTTOM', 'TVDSS_SAND_TOP', 'TVDSS_SAND_BOTTOM', 'TVD_SAND_TOP', 'TVD_SAND_BOTTOM', 'THICKNESS', 'VCL_AVG', 'PHI_AVG', 'SOG_AVG', 'PERM_AVG']
        '''
        Creating summary grid
        '''
        self.summary_dict[formation_key]=wx.grid.Grid(f_name,-1,size=(890,55),style=wx.BORDER_SUNKEN)
        for col in range(len(self.col_list)):
            self.summary_dict[formation_key].SetColLabelValue(col,self.col_list[col])
        table=MarkerTable(data={},col_label=self.col_list,row_count=10)
        self.formation_text_dict[formation_key]=wx.StaticText(f_name,-1,'Formation Level Statistic')
        self.summary_dict[formation_key].SetTable(table,True)
        '''
        Creating Sand Level grid
        '''

        self.sand_text_dict[formation_key]=wx.StaticText(f_name,-1,'Sand Level Statistic')
        self.sand_dict[formation_key]=wx.grid.Grid(f_name,-1,size=(1060,200),style=wx.BORDER_SUNKEN)
        for col in range(len(self.sand_list)):
             self.sand_dict[formation_key].SetColLabelValue(col,self.sand_list[col])
        sand_table=MarkerTable(data={},col_label=self.sand_list,row_count=2)
        self.sand_dict[formation_key].SetTable(sand_table,True)

        '''
        Put summary grid and sand level grid into sizer
        This sizer just manage the layout in the static box
        '''
        sizer=wx.StaticBoxSizer(f_name,wx.VERTICAL)
        sizer.Add(self.formation_text_dict[formation_key])
        sizer.Add(self.summary_dict[formation_key])

        sizer.AddSpacer(15)
        sizer.Add(self.sand_text_dict[formation_key])
        sizer.Add(self.sand_dict[formation_key])
        '''
        Add sizer into static boxes sizer

        '''
        self.summary_sizer.Add(sizer)

     def SummaryGridData(self):
             '''
             Generating data of summary grid and sand level data
             :return:
             '''
             well_id=self.well_combobox.GetStringSelection()
             par="MD_FORMAT_top,md_format_bottom ,tvd_format_top,tvd_format_bottom,tvdss_format_top,tvdss_format_bottom "
             par2="thickness,phi_avg,h_phi,h_phi_sg"
             col_list=list(par.split(","))
             col_list2=list(par2.split(","))
             data_dict={}
             data_dict2={}
             for col_name in col_list:
                 exec("data_dict[col_name]=[]")
             for col_name in col_list2:
                 exec("data_dict2[col_name]=[]")

             for for_name in self.checkbox_list:
                cur_depth=self.db.Sql("select "+par+" from paysummary_depth where wellid=\'"+well_id+"\' and formation=\'"+for_name+"\' group by ("+par+")")
                cur_summary=self.db.Sql("select "+par2+" from paysummary where wellid=\'"+well_id+"\' and formation=\'"+for_name+"\'")
                data={}
                for id in cur_depth.fetchall():
                    for i in range(len(id)) :
                        data_dict[col_list[i]].append(id[i])
                        data[(0,i)]=id[i]
                for id in cur_summary.fetchall():
                    for i in range(len(id)):
                        data_dict2[col_list2[i]].append(id[i])
                        data[0,i+6]=id[i]

                table=MarkerTable(data=data,col_label=self.col_list,row_count=1)
                self.summary_dict[for_name+' Summary'].__init_mixin__()
                self.summary_dict[for_name+' Summary'].SetTable(table,True)
                self.summary_dict[for_name+' Summary'].EnableDragColMove()
                self.summary_dict[for_name+' Summary'].EnableDragGridSize()
                self.summary_dict[for_name+' Summary'].EnableGridLines()

             par_sand=''
             for col_name in self.sand_list[:-5]:
                par_sand=par_sand+col_name+", "
                data_sand_dict={}

             for for_name in self.checkbox_list:
                exec("data_sand_dict[for_name]={}")
                for col_name in self.sand_list:
                    exec("data_sand_dict[for_name][col_name]=[]")



             for for_name in self.checkbox_list:
                    data_sand_table={}
                    data_sand_table[for_name]={}
                    print(data_sand_table[for_name])
                    cur_sand_depth=self.db.Sql("select "+par_sand[:-2]+" from paysummary_depth where wellid=\'"+well_id+"\' and formation=\'"+for_name+"\'")

                    for id in cur_sand_depth.fetchall():
                        i=0
                        print(id)
                        for col in self.sand_list[:-5]:
                            data_sand_dict[for_name][col].append(id[i])
                            i+=1
                    for row in range(len(data_sand_dict[for_name]['LAYER_NUMBER'])):
                            i=row
                            for col in range(len(self.sand_list[:-5])):
                                data_sand_table[for_name][(row,col)]=data_sand_dict[for_name][self.sand_list[col]][i]

                    par_sand_summary=r"thickness,vcl_avg,phi_avg,sog_avg,perm_avg"
                    for ln in data_sand_dict[for_name]['LAYER_NUMBER']:
                        if ln is not None:
                            cur_sand_summary=self.db.Sql("select "+par_sand_summary+" from raw_tvd where wellid=\'"+well_id+"\' and layer_number=\'"+str(ln)+"\'")
                            i=0
                            for id in cur_sand_summary.fetchall():
                                for col in self.sand_list[7:]:
                                    data_sand_dict[for_name][col].append(id[i])
                                    i+=1

                    for row in range(len(data_sand_dict[for_name]['LAYER_NUMBER'])):
                        if data_sand_dict[for_name]['LAYER_NUMBER'][0] is not None:
                            print(data_sand_dict[for_name]['LAYER_NUMBER'])
                            i=row
                            for col in range(len(self.sand_list[7:])):
                                print('this is col %s ' % str(col))
                                data_sand_table[for_name][(row,col+7)]=data_sand_dict[for_name][self.sand_list[col+7]][i]

                    table_sand=MarkerTable(data=data_sand_table[for_name],col_label=self.sand_list,row_count=len(data_sand_dict[for_name]['LAYER_NUMBER']))
                    self.sand_dict[for_name+' Summary'].__init_mixin__()
                    self.sand_dict[for_name+' Summary'].SetTable(table_sand,True)
                    self.sand_dict[for_name+' Summary'].EnableDragColMove()
                    self.sand_dict[for_name+' Summary'].EnableDragGridSize()
                    self.sand_dict[for_name+' Summary'].EnableGridLines()
             self.Resize()

     def Resize(self):
        f_x=self.GetVirtualSize()[0]
        f_y=self.GetVirtualSize()[1]
        self.SetSize((f_x+1,f_y+1))
        self.SetSize((f_x-11,f_y-1))

     def OnCheckboxClick(self,event,list_name):

         if list_name not in self.checkbox_list:
            self.checkbox_list.append(list_name)
         else:
            self.checkbox_list.remove(list_name)

     def OnQueryClick(self,event):
        '''
        Generating grids for summary and sand level table
        According the formation layer which user selected
        :param event: Click Query Button
        :return:
        '''
        check_list=[]
        '''
        Detecting which formation layer was selected
        '''
        for for_name in self.summary_dict:
            check_list.append(for_name)
        '''
        Erasing previous widgets which generated at last time query button procedure

        '''
        for for_name in check_list:
            if for_name  not in self.checkbox_list:
                del_summary=self.summary_dict[for_name]
                del_sand=self.sand_dict[for_name]
                del_for=self.formation_text_dict[for_name]
                del_sand_text=self.sand_text_dict[for_name]
                self.summary_dict.pop(for_name)
                print(self.summary_dict)
                del_summary.Destroy()
                del_sand.Destroy()
                del_for.Destroy()
                del_sand_text.Destroy()
        '''
        Clear sizer and re-layout widgets
        '''
        self.summary_all_sizer.Clear()
        self.summary_all_sizer=wx.BoxSizer(wx.VERTICAL)
        for list_name in self.checkbox_list:
            self.box_list[list_name]=wx.StaticBox(self,-1,list_name+' Summary',style=wx.BORDER_RAISED)
            self.SummaryGrid(self.box_list[list_name])
            self.summary_all_sizer.Add(self.summary_sizer)
            self.summary_all_sizer.AddSpacer(20)
        self.final_sizer.AddSizer(self.summary_all_sizer)
        self.SetSizer(self.final_sizer,deleteOld=True)
        '''
        Generating grid data
        '''

        self.SummaryGridData()
        self.Resize()

     def OnClusterClick(self,event):
        self.well_combobox.Destroy()
        well_list=[]
        cluster_id=self.cluster_combox.GetStringSelection()
        cur=self.db.Sql("select wellid from well_header where clusterid=\'"+cluster_id+"\' order by wellid")
        for id in cur.fetchall():
            well_list.append(id[0])
        self.well_combobox=wx.ComboBox(self,-1,choices=well_list,style=wx.CB_SIMPLE,pos=(20,160))
        self.Bind(wx.EVT_COMBOBOX,self.OnWellidClick,self.well_combobox)


     def OnWellidClick(self,event):
            self.sand_list=[]
            self.OnQueryClick(self)















