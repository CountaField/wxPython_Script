from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plot
import numpy as np
import datetime
import matplotlib.dates as dates
import matplotlib.ticker as ticker
from collections import OrderedDict



class PolygonPlot3D:
    def __init__(self):
        self.figure3d = plot.figure()


    def axis_create(self,prod_date,prod_data,well_list,clusterid='',cluster=False):
        self.axes = self.figure3d.gca(projection='3d')
        self.prod_date = prod_date
        self.verts = []
        self.well_list3d = well_list
        self.well_number_process(self.well_list3d)
        self.wells_colors()
        self.date_list = self.date_to_number(prod_date)
        self.prod_data_func(prod_data)
        self.poly = PolyCollection(self.verts, facecolors=self.facecolor_list)
        self.poly.set_alpha(0.8)
        self.axes.add_collection3d(self.poly, zs=self.well_count, zdir='y')
        self.isCluster=cluster
        self.Axis_Setting(clusterid)



    def Axis_Setting(self,clusterid):
        self.axes.set_autoscale_on(True)
        self.axes.set_xlim3d(self.date_list[0], self.date_list[-1],auto=True)
        self.axes.xaxis.set_major_locator(ticker.FixedLocator(self.date_list))  # I want all the dates on my xaxis
        self.axes.xaxis.set_major_locator(dates.DayLocator(interval=30))
        self.axes.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        for tl in self.axes.xaxis.get_ticklabels():  # re-create what autofmt_xdate but with w_xaxis
            tl.set_ha('right')
            tl.set_rotation(30)
        self.axes.set_ylim3d(self.well_count[0],self.well_count[-1], self.well_number_process(self.well_list3d))
        plot.yticks(self.well_count,self.well_list3d)
        self.axes.set_zlabel('Production Data')
        if self.isCluster==False:
            self.axes.set_zlim3d(0, 120)
        else:
            self.axes.set_zlim3d(0, 600)
        self.axes.set_title('Cluster '+str(clusterid) + ' Wells 3D Polygon Plot')
        self.figure3d.autofmt_xdate()

    def well_number_process(self,well_list):
        well_count=[]
        i=0
        for x in well_list:
            well_count.append(i)
            i+=1
        self.well_count=well_count[:]


    def prod_data_func(self,prod_data):
        self.prod_data=prod_data
        for wellid in self.well_list3d:
            if wellid!='SN0002-06':
                self.prod_data[wellid][0],self.prod_data[wellid][-1]=0,0
                self.verts.append(list(zip(self.date_list,self.prod_data[wellid])))

    def cc(self,arg):
        return colorConverter.to_rgba(arg, alpha=0.6)

    def wells_colors(self):
        self.color_list=['red', 'green', 'blue', 'grey', 'orange', 'yellow', 'pink', 'skyblue', 'maroon','cyan','brown','cadetblue','gold','wheat','violet','seagreen']
        i=0
        self.facecolor_list=[]
        for well in self.well_list3d:
             self.facecolor_list.append(self.cc(self.color_list[i]))
             i+=1


    def date_to_number(self,prod_date):
        date_number_list=[]
        #('prod date is',prod_date)
        for d in prod_date:
            date_number_list.append(dates.date2num(d))
        #print('date number list',date_number_list)
        return date_number_list


    def format_date(self,x, pos=None):
        return dates.num2date(x).strftime('%Y-%m-%d')





