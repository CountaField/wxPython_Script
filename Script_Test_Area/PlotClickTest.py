import wx

import matplotlib

from matplotlib.figure import Figure

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class PlotClick:
    def __init__(self,rect=None,fig=None):
        self.rect=rect
        self.fig=fig
        self.pick_dict={}

    def connect(self):
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        #self.cidrelease = self.rect.figure.canvas.mpl_connect(
         #   'button_release_event', self.on_release)
        self.cidpick=self.rect.figure.canvas.mpl_connect(
            'pick_event', self.on_pick)
        #elf.cidpick = self.fig.mpl_connect(
         #   'pick_event', self.on_pick)

    def on_press(self,event):
        self.rect.set_hatch('o')
        self.rect.set_linestyle(':')
        self.rect.set_edgecolor('pink')
        print event.xdata,event.ydata


    def on_pick(self,event):
        if event.artist not in self.pick_dict:
            if self.pick_dict.keys()!=[]:
                for id in self.pick_dict.keys():
                    self.pick_dict[id].set_hatch('')
                    self.pick_dict.pop(id)
                self.pick_dict[event.artist] = event.artist
                self.pick_dict[event.artist].set_hatch('o')
                self.pick_dict[event.artist].figure.canvas.draw()
            else:
                self.pick_dict[event.artist]=event.artist
                self.pick_dict[event.artist].set_hatch('o')
                self.pick_dict[event.artist].figure.canvas.draw()




    def on_release(self,event):
        self.rect.figure.canvas.draw()
        print 'release button'









