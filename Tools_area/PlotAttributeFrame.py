import wx
import wx.lib.agw.aui as aui
import os
from mpldatacursor import datacursor
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot as plt
from collections import OrderedDict


class PlotAttributeFrame(wx.Frame,):
    def __init__(self, parent,  id,plot,canvas,plot_sample_instance,par_list,title='', pos=wx.DefaultPosition,
                 size=(1000, 600), style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP,datacursor_dict={}):
        wx.Frame.__init__(self,parent,id,title,pos,size,style)
        print "Atribute Setting processing %d" %os.getpid()

        self.canvas=canvas
        self.plot=plot
        self.datacursor_dict=datacursor_dict
        self.plot_sample_instance=plot_sample_instance
        '''self._mgr=aui.AuiManager(agwFlags=aui.AUI_MGR_DEFAULT | aui.AUI_MGR_TRANSPARENT_DRAG | aui.AUI_MGR_ALLOW_ACTIVE_PANE |
                                   aui.AUI_MGR_LIVE_RESIZE | aui.AUI_MGR_VENETIAN_BLINDS_HINT |aui.AUI_MGR_SMOOTH_DOCKING |
                                            aui.AUI_MGR_WHIDBEY_DOCKING_GUIDES)'''
        self._mgr = aui.AuiManager(
            agwFlags=aui.AUI_MGR_DEFAULT | aui.AUI_MGR_TRANSPARENT_DRAG | aui.AUI_MGR_ALLOW_ACTIVE_PANE |
                     aui.AUI_MGR_VENETIAN_BLINDS_HINT | aui.AUI_MGR_SMOOTH_DOCKING |
                     aui.AUI_MGR_WHIDBEY_DOCKING_GUIDES)
        self._mgr.SetManagedWindow(self)
        self.InitialToolPanel(plot_sample_instance)
        self.Setsizer(self.plot_sample_instance,par_list)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_BUTTON,self.OnConfirmButton,self.plot_sample_instance.confirm_button)


    def InitialToolPanel(self,plot_sample_instance):
        self.Panel_dict = {}
        self.Panel_dict["Y_Axis_Selection"] = wx.Panel(self, -1, name='Y Axis Selection', size=(300, 250))
        self.Panel_dict["Y_Sec_Axis_Selection"] = wx.Panel(self, -1, name='Y Sec Axis Selection', size=(280, 80))
        self.Panel_dict["Line_Type_Selection"] = wx.Panel(self, -1, name='Line Type Selection', size=(290, 280))
        self.Panel_dict["Line_Scale_Selection"] = wx.Panel(self, -1, name='Line Scale Selection', size=(380, 400))
        #plot_sample_instance.LineTypeInitializing()
        for id in self.Panel_dict:
            print id,self.Panel_dict[id]
            if id=="Line_Type_Selection":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                 CenterPane().MinimizeButton(False).CloseButton(False).Resizable(resizable=True))
            elif id=="Y_Axis_Selection":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  CenterPane().Left().MinimizeButton(False).CloseButton(False).Resizable(resizable=True))
            elif id=="Y_Sec_Axis_Selection":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  CenterPane().Left().MinimizeButton(False).CloseButton(False).Resizable(resizable=True))
            elif id=="Line_Scale_Selection":
                self._mgr.AddPane(self.Panel_dict[id], aui.AuiPaneInfo().Caption(self.Panel_dict[id].GetName()).
                                  CenterPane().Right().MinimizeButton(False).CloseButton(False).Resizable(resizable=True))

        self._mgr.Update()
        self._mgr.DoFrameLayout()

    def Setsizer(self,plot_sample_instance,par_list):
        plot_sample_instance.ParametersCheckbox(self.Panel_dict['Y_Axis_Selection'],par_list) #call this function here because of
                                                            #need to provide parent class
        plot_sample_instance.SecondYaxis(self.Panel_dict['Y_Sec_Axis_Selection'],par_list)
        plot_sample_instance.LineStyleCBCreate(self.Panel_dict['Line_Type_Selection'],par_list)
        plot_sample_instance.YaxisStepSpinCtrl(self.Panel_dict["Line_Scale_Selection"])
        self.Panel_dict["Y_Axis_Selection"].SetSizer(plot_sample_instance.par_box_sizer)
        self.Panel_dict["Y_Sec_Axis_Selection"].SetSizer(plot_sample_instance.ysec_box_sizer)
        self.Panel_dict["Line_Type_Selection"].SetSizer(plot_sample_instance.linestyle_box_sizer)
        self.Panel_dict["Line_Scale_Selection"].SetSizer(plot_sample_instance.Sc_Box_Sizer)



    def OnConfirmButton(self,event):

        for id in self.plot_sample_instance.linestyle_dict:
            if self.plot_sample_instance.linestyle_dict[id].GetStringSelection()=="Solid":
                self.plot_sample_instance.solid_list.append(id)
            elif self.plot_sample_instance.linestyle_dict[id].GetStringSelection()=="Dashed":
                self.plot_sample_instance.dashed_list.append(id)
            elif self.plot_sample_instance.linestyle_dict[id].GetStringSelection()=="Dotted":
                self.plot_sample_instance.dotted_list.append(id)

        for id in self.plot_sample_instance.solid_list:
            try:
                self.plot.plot_y_line_dict[id].set_linestyle('solid')
            except KeyError:
                pass
        for id in self.plot_sample_instance.dashed_list:
            try:
                self.plot.plot_y_line_dict[id].set_linestyle('dashed')
            except KeyError:
                pass
        for id in self.plot_sample_instance.dotted_list:
            try:
                self.plot.plot_y_line_dict[id].set_linestyle('dotted')
            except KeyError:
                pass
        self.plot_sample_instance.LineWidth()

        for id in self.plot_sample_instance.linewidth_final_dict:
            try:
                self.plot.plot_y_line_dict[id].set_linewidth(self.plot_sample_instance.linewidth_final_dict[id])

            except KeyError:
                pass

        for id in self.plot_sample_instance.par_dict:
            if self.plot_sample_instance.par_dict[id].IsChecked()==True:

                self.plot.plot_y_line_dict[id].set_visible(True)
            else:

                self.plot.plot_y_line_dict[id].set_visible(False)


        for id in self.plot_sample_instance.ysec_dict:
            if self.plot_sample_instance.ysec_dict[id].IsChecked()==True:
                self.plot.plot_y_line_dict[id].set_visible(True)
            else:
                self.plot.plot_y_line_dict[id].set_visible(False)


        step_y = self.plot_sample_instance.YaxisSc.GetValue()
        step_ysec = self.plot_sample_instance.minorYaxisSc.GetValue()
        step_x = self.plot_sample_instance.XaxisSc.GetValue()
        self.plot.axes.legend(loc='upper left', framealpha=98.9, fontsize=10)
        self.plot.axes2.legend(loc='upper right', framealpha=98.9, fontsize=10)
        if  self.datacursor_dict!={}:
            for x in self.plot.axes.get_lines():
                if x.get_visible()==False:
                    self.datacursor_dict[x].disable()
                else:
                    pass
            for x in self.plot.axes2.get_lines():
                if x.get_visible() == False:
                    self.datacursor_dict[x].disable()
                else:
                    pass

        self.canvas.draw()


    def OnClose(self,event):
        self.Hide()

class ClusterOrderChange(wx.Frame):
    def __init__(self,parent,id,plotid,plot_axes,plot,plot_canvas,data_dict,date_list,cluster_list,colors,colors_list,title,
                 checked_dict=None,mgr=None,
                 pos=wx.DefaultPosition,size=(400, 400),style=wx.CLOSE_BOX | wx.FRAME_FLOAT_ON_PARENT|wx.CAPTION|wx.SYSTEM_MENU):
        wx.Frame.__init__(self, parent, id,title, pos, size, style)
        self.SetBackgroundColour('light grey')
        self.parent=parent
        self.plot_axes=plot_axes
        self.plot=plot
        self.plot_canvas=plot_canvas
        self.date_list=date_list
        self.data_dict=data_dict
        self.cluster_list=cluster_list
        self.mgr=mgr
        self.colors=colors
        self.colors_list=colors_list
        self.plotid=plotid
        self.panel_define=checked_dict
        self.InitalToolPanel(cluster_list)



    def InitalToolPanel(self,cluster_list):
        self.controls_dict={}
        original_order=wx.StaticText(self,-1,'Original Order:')
        new_order=wx.StaticText(self,-1,'New Order:')
        self.controls_dict['old_wells_cluster_list']=wx.ListBox(self,-1,choices=cluster_list,size=(120,250),style=wx.LB_ALWAYS_SB|wx.BORDER_SUNKEN)

        self.controls_dict['new_wells_cluster_list'] = wx.ListBox(self, -1, choices=[], size=(120, 250))
        self.controls_dict['left_arrow_bmp'],self.controls_dict['right_arrow_bmp']=self.ArrowBitmap()
        self.controls_dict['confirm_button']=wx.Button(self,-1,'Confirm')
        self.Bind(wx.EVT_BUTTON,self.OnLeftArrow,self.controls_dict['left_arrow_bmp'])
        self.Bind(wx.EVT_BUTTON, self.OnRightArrow, self.controls_dict['right_arrow_bmp'])
        self.Bind(wx.EVT_BUTTON,self.OnConfirm,self.controls_dict['confirm_button'])
        left_sizer=wx.BoxSizer(wx.VERTICAL)
        left_sizer.AddSpacer(5)
        left_sizer.Add(original_order)
        left_sizer.AddSpacer(5)
        left_sizer.Add(self.controls_dict['old_wells_cluster_list'])
        mid_sizer=wx.BoxSizer(wx.VERTICAL)
        mid_sizer.AddSpacer(45)
        mid_sizer.Add(self.controls_dict['right_arrow_bmp'])
        mid_sizer.AddSpacer(15)
        mid_sizer.Add(self.controls_dict['left_arrow_bmp'])
        right_sizer=wx.BoxSizer(wx.VERTICAL)
        right_sizer.AddSpacer(5)
        right_sizer.Add(new_order)
        right_sizer.AddSpacer(5)
        right_sizer.Add(self.controls_dict['new_wells_cluster_list'])
        right_sizer.AddSpacer(15)
        right_sizer.Add(self.controls_dict['confirm_button'])
        final_sizer=wx.BoxSizer(wx.HORIZONTAL)
        final_sizer.AddSpacer(25)
        final_sizer.Add(left_sizer)
        final_sizer.AddSpacer(15)
        final_sizer.Add(mid_sizer)
        final_sizer.AddSpacer(15)
        final_sizer.Add(right_sizer)
        self.SetSizer(final_sizer)

    def OnLeftArrow(self,event):
        cluster_select=self.controls_dict['new_wells_cluster_list'].GetStringSelection()
        old_cluster_list = self.controls_dict['old_wells_cluster_list'].GetItems()
        new_cluster_list = self.controls_dict['new_wells_cluster_list'].GetItems()
        ind = new_cluster_list.index(cluster_select)
        print old_cluster_list
        self.controls_dict['old_wells_cluster_list'].Append(cluster_select)
        old_cluster_list.append(cluster_select)
        self.controls_dict['new_wells_cluster_list'].Delete(ind)
        new_cluster_list.remove(cluster_select)

    def OnRightArrow(self,event):
        cluster_select=self.controls_dict['old_wells_cluster_list'].GetStringSelection()
        old_cluster_list = self.controls_dict['old_wells_cluster_list'].GetItems()
        new_cluster_list=self.controls_dict['new_wells_cluster_list'].GetItems()
        ind=old_cluster_list.index(cluster_select)
        print old_cluster_list
        self.controls_dict['new_wells_cluster_list'].Append(cluster_select)
        new_cluster_list.append(cluster_select)
        self.controls_dict['old_wells_cluster_list'].Delete(ind)
        old_cluster_list.remove(cluster_select)

    def OnConfirm(self,event):
        query_clusters_data=''
        old_cluster_list= self.controls_dict['old_wells_cluster_list'].GetItems()
        new_cluster_list=self.controls_dict['new_wells_cluster_list'].GetItems()

        for id in new_cluster_list:
            query_clusters_data += 'self.data_dict[\'' + id + '\'],'

        excute_string = "self.plot_axes.stackplot(self.date_list," + query_clusters_data[ :-1] + ",colors=[" + self.colors + "] )"
        exec(excute_string)
        well_list = []
        color_dict = OrderedDict()

        i = 0
        for id in new_cluster_list:
            color_dict[id] = plt.Rectangle((i, 0), 1, 1, angle=90.0, fc=self.colors_list[i])
            well_list.append(color_dict[id])
            i += 1
        legend=self.plot_axes.legend(well_list, color_dict.keys(), loc='upper center', ncol=9, fontsize=10)
        legend.draggable()
        self.cluster_list=new_cluster_list
        self.plot_canvas.draw()
        self.mgr.Update()


    def ArrowBitmap(self):
        arrow_ico_path=r"W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\images\arrow"
        left_arrow=arrow_ico_path+r"\left_arrow.bmp"
        right_arrow = arrow_ico_path + r"\right_arrow.bmp"
        left_image=wx.Image(left_arrow,type=wx.BITMAP_TYPE_BMP)
        left_image=left_image.Scale(left_image.GetWidth()/2,left_image.GetHeight()/2)
        right_image=wx.Image(right_arrow,type=wx.BITMAP_TYPE_BMP)
        right_image=right_image.Scale(right_image.GetWidth()/2,right_image.GetHeight()/2)
        print left_image.GetWidth(),left_image.GetHeight()
        left_arrow_bmp=wx.BitmapFromImage(left_image)
        right_arrow_bmp=wx.BitmapFromImage(right_image)
        left_arrow_button=wx.BitmapButton(self,-1,bitmap=left_arrow_bmp)
        right_arrow_button=wx.BitmapButton(self,-1,bitmap=right_arrow_bmp)
        return left_arrow_button,right_arrow_button





























































