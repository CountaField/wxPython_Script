__author__ = 'Administrator'

import wx
import os
import sys
import string
import wx.lib.buttons as buttons

#sys.path.append(r'c:\test\wx')
#sys.path.append(r'W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process')
from TVD_MD_excel_format import excel_process



class TvdMdDataImport(wx.Frame):
    def __init__(self, parent, id=-1):
        wx.Frame.__init__(self, parent, id, 'MD & TVD Data Import',size=(700,550))
        self.SetBackgroundColour('light gray')
        self.wildcard="xlsx files (*.xlsx)|*.xlsx"
        self.filename = ''
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menuOpen = menu.Append(-1, "&Open")
        menuClose = menu.Append(-1, "&Exit....")
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.onOpen,menuOpen)
        self.Bind(wx.EVT_MENU, self.OnClose, menuClose)
        self.panel = wx.Panel(self)
        self.button_format = wx.Button(self.panel, label='Format',pos=(450, 20), size=(70,60))
        self.button_format.Disable()
        self.Bind(wx.EVT_BUTTON, self.Transfer, self.button_format)
        self.button_load=wx.Button(self.panel, label='Load', pos=(550, 20), size=(70, 60))
        self.button_load.Disable()
        self.Bind(wx.EVT_BUTTON, self.DataLoad, self.button_load)
        self.text_pos_long = 60  # To Set default text dialog position
        self.text_pos_width = 60  # To set
        self.close_button = buttons.GenButton(parent=self.panel, id=-1, label='Finish\n', pos=(450, 100), size=(100,100))
        self.close_button.SetToolTipString('Closing\n Windows')
        self.close_button.SetBackgroundColour('sky blue')
        self.close_button.SetForegroundColour('white')
        self.close_button.SetBezelWidth(8)
        self.close_button.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        self.Bind(wx.EVT_BUTTON,self.OnClose,self.close_button)
        self.font = wx.Font(9,wx.SCRIPT,wx.NORMAL,wx.BOLD)

        if self.filename == '':
            # Set two TextCtrl dialog which will display Format information and Data load information, and both of them used multiline attribute of TextCtrl
            multiLabel=wx.StaticText(parent=self.panel, id=-1, label='Formation:',pos=(60,60))
            self.multiText = wx.TextCtrl(parent=self.panel, id=-1, value='', size=(350, 200), style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY)
            loadLabel = wx.StaticText(parent=self.panel, id=-1, label='Data Load')
            self.loadText = wx.TextCtrl(parent=self.panel, id=-1, value='', size=(350, 200), style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY)
        # Using FlexGridSizer to format above TextCtrl automatically
        sizer = wx.FlexGridSizer(cols=2,vgap=10,hgap=10)
        sizer.AddMany([multiLabel, self.multiText, loadLabel, self.loadText])
        self.panel.SetSizer(sizer)





    def OnClose(self,event):
        self.Close(True)


    def onOpen(self,event):
        self.text_pos_width += 30
        dlg = wx.FileDialog(self, message="Open Input File...", defaultDir=r'W:\GSR\060000-Operations',
                           style=wx.OPEN, wildcard=self.wildcard
                          )

        if dlg.ShowModal() == wx.ID_OK:
            if self.filename == '':
                self.multiText.Clear()
                self.filename = dlg.GetPath()
            else:
                self.multiText.Clear()
                self.filename = dlg.GetPath()
        dlg.Destroy()
        if self.filename is not '':
            self.multiText.AppendText(self.filename+'\n')
            end_point=self.multiText.GetInsertionPoint()
            self.multiText.SetStyle(0, end_point, wx.TextAttr('blue'))
            self.multiText.AppendText('File Load Successful ! Now you Can Format Data !!!\n')
            #print(self.multiText.GetInsertionPoint())

            self.button_format.Enable()
        else:
            self.multiText.AppendText('Error: you did not select import file')
            end_point=self.multiText.GetInsertionPoint()
            self.multiText.SetInsertionPoint(0)
            self.multiText.SetStyle(0, int(end_point), wx.TextAttr('red'))



    def Transfer(self, event):

        excel_process.__init__(self,self.filename, r'W:\GSR\050000-GeoInformation\052300-Projects\Geoscience database\Input files\Markers\\')
        if self.rel_file != '':
            self.button_load.Enable(True)
            self.multiText.AppendText('File Transfered Successful ! The file saved in :\n')
            start_point = self.multiText.GetInsertionPoint()
            self.multiText.AppendText(self.rel_file+'\n')
            end_point = self.multiText.GetInsertionPoint()
            self.multiText.SetStyle(start_point, end_point, wx.TextAttr('brown'))
            self.multiText.AppendText('Now you Can load Data\n')
        else:
            self.multiText.Clear()
            self.multiText.AppendText( 'Error: Please Format your file first!!!')
            end_point = self.multiText.GetInsertionPoint()
            self.multiText.SetStyle(0,end_point,wx.TextAttr('red'))

    def DataLoad(self, event):
        if 'MD' in self.rel_file:
            inputfile = open(r"W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process\Control_Files\md_sample.ctl", 'r')
            #print(self.rel_file+' used md')
        elif 'TVD' in self.rel_file:
            #print(self.rel_file+' used tvd')
            inputfile = open(r'W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process\Control_Files\tvd_sample.ctl', 'r')
        outputfile = open(r'W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process\Control_Files\input.ctl', 'w')

        try:
            astring = inputfile.read()
            outputfile.write(astring.replace('$input', self.rel_file))
        finally:
            inputfile.close()
            outputfile.close()
        logfile = r'W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process\Control_Files\input.log'
        os.system(r'W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process\Control_Files\import_execute.bat')
        self.report(logfile)
        self.report1(logfile)

        if string.atof(self.report(logfile))>1:
            self.loadText.Clear()
            load_error = 'Yo! ! The Data Load Failed, you may already loaded Data, please check your input file !'
            self.loadText.AppendText(load_error)
            end_point=self.loadText.GetInsertionPoint()
            self.loadText.SetStyle(0, end_point, wx.TextAttr('red'))

        elif string.atof(self.report1(logfile)) == 0:
            load_error = 'Yo! ! the data load failed, Maybe you Did Not correctly setup input file!'
            self.loadText.Clear()
            self.loadText.AppendText(load_error)
            end_point=self.loadText.GetInsertionPoint()
            self.loadText.SetStyle(0,end_point,wx.TextAttr('red'))


        else:
            self.loadText.Clear()
            self.loadText.AppendText('Data Load Successfully!\n')


    def report(self,filename):
        bstring = 'Total logical records rejected:'
        astring = open(filename)
        astring.seek(0)
        try:
                for line in astring.readlines():
                        if  bstring in line:
                                return line.split()[-1]
        finally:
                astring.close()

    def report1(self, filename):
        bstring = 'Total logical records read:'
        astring = open(filename)
        astring.seek(0)
        try:
                for line in astring.readlines():
                        if bstring in line:
                                return line.split()[-1]
        finally:
                astring.close()







if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = TvdMdDataImport(parent=None, id=-1)
    frame.Show()
    app.MainLoop()










