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


def TypeValueInsert(wellid):
        db=Gsrdb_Conn()
        pre_date = str(datetime.datetime.now()-datetime.timedelta(days=1)).split('.')[0]

        daily_alarm_check_cur=db.Sql("select alarm_message from alarm_summary_table where "
                               "wellid='"+wellid+"' ")

        for id_m in daily_alarm_check_cur.fetchall():
            data_filter_list = []
            sql_string="select type_value from alarm_2hour_report_table where" \
                       " alarm_message='"+id_m[0]+"' and wellid='"+wellid+"'  and type_value is not null and production_date>to_date('"+pre_date+"','yyyy/mm/dd hh24:mi:ss') " \
                                                                                                                    "order by  type_value"

            min_string = ''
            unit_string = ' '
            hour_alarm_cur = db.Sql(sql_string)
            for id in hour_alarm_cur.fetchall():
                if id[0] is not None:
                    data_filter_list.append(float(id[0].split(': ')[1].split(' ')[0]))
                    min_string = str(id[0].split(': ')[0])
                    if str(id[0].split(': ')[1].split(' ')[1]) != 'max_whp':
                        unit_string = str(id[0].split(': ')[1].split(' ')[1])
                    else:
                        unit_string = str(id[0].split('\n')[1])

            print id_m[0], data_filter_list
            if data_filter_list != []:
                insert_value = min_string + ": " + str(min(data_filter_list)) + unit_string
                update_string = "update alarm_summary_table set type_value='" + insert_value + "' where wellid='" + wellid + "' and alarm_message='" + \
                                id_m[0] + "'"
                print update_string
        db.close()
TypeValueInsert('SN0012-05')