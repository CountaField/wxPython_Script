from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plot
import numpy as np
import datetime
import matplotlib.dates as dates
import matplotlib.ticker as ticker
from collections import OrderedDict
from PolygonPlot3D import PolygonPlot3D

class BarPlot:
    def __init__(self,xaxis_list,yaxis_list,three_d=False,color=None):

        if three_d==False:
            self.fig = plot.figure()
            self.ax=self.fig.add_subplot(111)
            self.Initial2DAxis(xaxis_list,yaxis_list,color)

    def Initial2DAxis(self,xaxis_list,yaxis_list,color):
        self.plot=self.ax.stackplot(xaxis_list,yaxis_list,colors=color,baseline='zero')




    def ReturnFigure(self):
        return self.fig,self.ax,self.plot






