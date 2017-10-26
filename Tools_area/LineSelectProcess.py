import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines

class LineSelected(object):
    def __init__(self, figure):
        self.fig=figure
        self.fig.canvas.mpl_connect('button_press_event',self.on_click)


    def on_click(self):
        print 'line selected'

