__author__ = 'Administrator'

import wx
import wx.grid


class MarkerTable(wx.grid.PyGridTableBase):

    def __init__(self, data,col_label,row_count):
        wx.grid.PyGridTableBase.__init__(self)

        '''self.odd=wx.grid.GridCellAttr()
        self.odd.SetBackgroundColour('white')
        self.odd.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.even = wx.grid.GridCellAttr()
        self.even.SetBackgroundColour('white')
        self.even.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))'''
        self.data = data
        self.colLabels=col_label
        self.rowCounts=row_count

    def GetNumberRows(self):
        return self.rowCounts

    def GetNumberCols(self):
        return len(self.colLabels)

    def IsEmpty(self,row,col):
        return self.data.get((row, col)) is not None

    def GetValue(self,row,col):
        value = self.data.get((row,col))
        if value is not None:
            return value
        else:
            return ''

    def GetColLabelValue(self,col):
        return self.colLabels[col]

    def Clear(self):
        del self.data



    def SetValue(self,row,col,value):
        self.data[(row,col)]=value

    '''def GetAttr(self,row,col,kind):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr'''


