
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import math
import matplotlib.image as img
import numpy as np
from Oracle_connection import Gsrdb_Conn
from matplotlib.backends.backend_wx import  NavigationToolbar2Wx,wxc
import wx
import wx.lib.agw.aui as aui
from collections import OrderedDict
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from TidyUpStackPlotprodDate import  TidyUpStackPlotProdDate as tspd
import matplotlib.text
import wx.lib.scrolledpanel as ScrolledPanel
from AuiFrameTemple import  AuiTemple
from PolygonPlot3D import PolygonPlot3D as pp3
import datetime
from SingleWellProdReport import SingleWellProdReport as spr
import gc
import threading
from EventText import  EventText
from DailyProdTable import DailyProdTable
from BB9Frame import BB9Frame
import wx.aui
from PltReadImage import PltReadImage as pr
import time
if wx.Platform == '__WXMSW__':
    from wx.lib.flashwin import FlashWindow

class StatisticPlot:
    def __init__(self,parent=None):
        self.canvas,self.figure=self.BaseStatisticPlot(parent)





    def BaseStatisticPlot(self,parent):
        with plt.xkcd():
            fig=plt.figure()
            axes=fig.add_subplot(111)
            data_dict = self.BaseDataPrepare()
            cur_year=datetime.datetime.now().year
            years=cur_year-2011
            drill_data_list=[]
            year_labels_list=[]
            bar_width=0.15
            ind=np.arange(years)
            for year in data_dict.keys():
                drill_data_list.append(data_dict[year]['drilling'])
                year_labels_list.append(str(year))

            bar_test=axes.bar(ind,drill_data_list,bar_width,color='r')

            canvas=FigureCanvas(parent,wx.NewId(),fig)

            return canvas,fig



    def BaseDataPrepare(self):
        db=Gsrdb_Conn()
        cur_year=datetime.datetime.now().year
        data_dict = OrderedDict()

        for year in range(2011,cur_year+1):
            data_dict[year]={'drilling':0,'prod':0,'vs':0,'frac':0}

        base_info_cur=db.Sql("select drilling_program,production_start_date from well_header where "
                             "(wellid like 'SN%' ) AND production_start_date is not null order by production_start_date")

        frac_info_cur=db.Sql('select frac_year from fracture where frac_year is not null order by frac_year')

        vs_info_cur=db.Sql("select dhc_set_date from allocation_dhc where dhc_type='VS' and dhc_set_date is not null order by dhc_set_date")
        for id in base_info_cur.fetchall():
            data_dict[id[0]]['drilling']+=1
            year=id[1].year
            data_dict[year]['prod']+=1

        for id in frac_info_cur.fetchall():
            data_dict[id[0]]['frac']+=1

        for id in vs_info_cur.fetchall():
            data_dict[id[0].year]['vs']+=1

        print data_dict


        db.close()


if __name__=='__main__':
    test=StatisticPlot()















