__author__ = 'Administrator'
import matplotlib.dates as mdates
from Oracle_connection import Gsrdb_Conn
import wx
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import Tkinter
import FileDialog
from CommonTool import FloatRange as fltrange
import os
import matplotlib.lines as lines


class PlotDrawing:
    def __init__(self,parent,wellid,parameter_list,cursor,Xaxis,Yaxis_list,Ysec_axis_list=[],solid_list=[],
                 dashed_list=[],dotted_list=[],width_dict={},y_grid_show=True,x_grid_show=True,time_data_unit='DAY',prod_data_dict=None,plot_type=None):
        '''
        :param parameter_list:  The column which will be Queried from GSR Database
        :param cursor: using cursor to extract well data into dictionary data_dict
        :param xaxis: defining which data of column will be used as X axis
        :param Yaxis: Y axis should be a list.
        :return:
        '''

        '''
         1. Initializing data_dict and parameter list, extracting data from database into data_dict
        '''
        self.plot_y_select_dict={}
        self.plot_y_line_dict={}
        self.plot_ysec_line_dict={}
        self.time_unit=time_data_unit
        self.plot_instance_dict={}
        self.plot_type=plot_type
        par_list=parameter_list
        Y_list=Yaxis_list
        if prod_data_dict is None:
            self.data_dict={}
            for parameter in parameter_list:
                self.data_dict[parameter]=[]
            for id in cursor.fetchall():

                i = 0
                #print(id[i])
                for par in par_list:
                    self.data_dict[par].append(id[i])
                    i += 1
        else:
           self.data_dict=prod_data_dict

        '''

            2. Create second Y axis data
        '''
        self.ysec_list=Ysec_axis_list

        '''
            Initializing Line Color and Style
        '''
        self.solid_list=solid_list
        self.dashed_list=dashed_list
        self.dotted_list=dotted_list
        '''
        3. Initializing Figure object
        '''
        self.wellid=wellid
        self.figure=plt.figure()
        self.axes=self.figure.add_subplot(111)
        if self.data_dict[Xaxis]!=[]:
            xlist=self.X_Y_axsi(Xaxis,Y_list)[0]
            self.x_list=xlist
            ydict=self.X_Y_axsi(Xaxis,Y_list)[1]
            ydict_sec=self.Y_Axis_Sec()
            self.DrawPlot(xlist,ydict,ydict_sec,self.solid_list,
            self.dashed_list,self.dotted_list,width_dict,y_grid_show,x_grid_show,plot_type=plot_type)
            self.figure.autofmt_xdate()
        else:
            self.axes.set_title(str(self.wellid)+' Not Produce')
        self.axes.grid(y_grid_show)




    def OnPlotPress(self,event):
        print 'clicked button'

    def ArtistRemove(self):
        for id in self.plot_instance_dict.keys():
            print id
            try:
                self.plot_instance_dict[id].remove(self)
            except:
                pass
        #self.figure.draw(self)


    def LineTypeSelection(self,solid_list,dashed_list,dotted_list):
        self.solid_list=solid_list
        self.dashed_list=dashed_list
        self.dotted_list=dotted_list



    def ReturnObject(self):
        return self.figure

    def ChangingPlot(self,xlist,ydict,ydict_sec,solid_list,dashed_list,dotted_list,width_dict,y_grid_show,x_grid_show):
        self.axes.clear()
        #self.axes2.clear()
        self.DrawPlot(xlist,ydict,ydict_sec,solid_list,dashed_list,dotted_list,width_dict,y_grid_show,x_grid_show)
        self.figure.autofmt_xdate()
        self.xlist_s=xlist
        self.ydict_s=ydict
        self.ydict_sec_s=ydict_sec
        self.solid_list_s=solid_list
        self.dashed_list_s=dashed_list
        self.dotted_list_s=dotted_list
        self.width_dict_s=width_dict
        self.axes.grid(y_grid_show)
        #self.axes2.grid(x_grid_show,which='minor')


    def ReturnChangedPlotParameter(self):
        return self.xlist_s,self.ydict_s,self.ydict_sec_s,self.solid_list_s,self.dashed_list_s,self.dotted_list_s,self.width_dict_s


    def DrawPlot(self,X_axis,Y_axis,Y_sec_axis,solid_list,dashed_list,dotted_list,width_dict,y_grid_show,x_grid_show,plot_type):
        '''
        Spicifying Line Style,width And Color
        :param X_axis:
        :param Y_axis:
        :param Y_sec_axis:6
        :param solid_list:
        :param dashed_list:
        :param dotted_list:
        :param width:
        :return:
        '''

        if Y_sec_axis!=[]:
            self.axes2=self.axes.twinx()



        for col in Y_axis:
            print 'this is col',col

            '''
             Customize primary Y axis Color of Line
            '''
            color = 'white'
            if col == 'daily_prod_gas'.upper() \
                    or col == 'INSTANT_PRODUCTION_GAS' \
                    or col == 'INSTANT_PRODUCTION_GAS_HOUR' \
                    or col == 'DAILY_CUM_PROD':
                color = 'red'
            if col == 'well_head_pressure'.upper() or col == 'WH_PRESSURE' or col == 'well_header_pressure'.upper() :
                color = 'DIMGREY'
            if col == 'casing_pressure'.upper():
                color = 'navy'
            if col == 'well_head_temperature'.upper() or col == 'PIPELINE_TEMPERATURE':
                color = 'gold'
            if col == 'prod_cum_gas'.upper() or col == 'CLUSTER_CUM_PROD':
                color = 'brown'
            if col == 'raw_daily_prod_gas'.upper():
                color = 'forestgreen'
            if col == 'pipeline_pres_diff'.upper():
                color = 'lightblue'
            if col == 'bhp_barg'.upper():
                color = 'orange'
            if col == 'bhp_degc'.upper() or col == 'PIPELINE_ABS_PRESSURE':
                color = 'black'

            '''
                Customize the primary Y axis line type
            '''

            if col in self.solid_list:
                line_style='solid'
            elif col in self.dashed_list:
                line_style='dashed'
            elif col in self.dotted_list:
                line_style='dotted'
            else:
                 line_style='solid'

            '''
                Customize primary Y axis line width
            '''

            if width_dict!={}:
                if width_dict[col] is not None:
                    width_y = width_dict[col]
                    self.plot_instance_dict[col]=self.axes.plot(X_axis,Y_axis[col],label=col,linestyle=line_style,color=color,lw=width_y,picker=5)
                else:
                    pass
            else:
                self.plot_instance_dict[col]=self.axes.plot(X_axis,Y_axis[col],color=color,label=col,picker=5)

        for col in Y_sec_axis:
            
            # Customize Second Y axis Color of Line
            
            seccolor = 'white'
            if col == 'daily_prod_gas'.upper() \
                    or col == 'INSTANT_PRODUCTION_GAS' \
                    or col == 'INSTANT_PRODUCTION_GAS_HOUR' \
                    or col == 'DAILY_CUM_PROD':
                seccolor = 'red'
            if col == 'well_head_pressure'.upper() or col=='WH_PRESSURE':
                seccolor = 'DIMGREY'
            if col == 'casing_pressure'.upper() or col == 'CLUSTER_CUM_PROD':
                seccolor = 'blue'
            if col == 'well_head_temperature'.upper() or col=='PIPELINE_TEMPERATURE':
                seccolor = 'gold'
            if col == 'prod_cum_gas'.upper() :
                seccolor = 'brown'
            if col == 'raw_daily_prod_gas'.upper():
                seccolor = 'forestgreen'
            if col == 'pipeline_pres_diff'.upper():
                seccolor = 'sienna'
            if col == 'bhp_barg'.upper():
                seccolor = 'orange'
            if col == 'bhp_degc'.upper():
                seccolor = 'Wheat'
            if col=='PIPELINE_ABS_PRESSURE':
                seccolor='black'
            
                #Customize the second Y axis line type
            

            if col in self.solid_list:
                sec_line_style='solid'

            elif col in self.dashed_list:
                sec_line_style='dashed'

            elif col in self.dotted_list:
                sec_line_style='dotted'

            else:
                sec_line_style='solid'
            if width_dict != {}:
                if width_dict[col] is not None:
                        width_ysec = width_dict[col]
                        self.plot_instance_dict[col]=self.axes2.plot(X_axis, Y_sec_axis[col], label=col, linestyle=sec_line_style, color=seccolor,lw=width_ysec)

                else:
                    pass
            else:
                self.plot_instance_dict[col]=self.axes2.plot(X_axis, Y_sec_axis[col], color=seccolor,label=col)



        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d %H:%M:%S'))
        #self.axes.set_ylabel('Daily_Prod km3/d,Annulas Pressure Mpa,\nWHP Bara,'
                             #' Cumulative prod Mm3')
        #self.axes2.set_ylabel('Daily_Prod km3/d,Annulas Pressure Mpa,\nWHP Bara, Cumulative prod Mm3')
        if plot_type=='daily':
            self.axes.set_title(str(self.wellid)+' Daily Production Plot')
        elif plot_type=='hist':
            self.axes.set_title(str(self.wellid) + ' Historical Production Plot')
        elif plot_type=='inst':
            self.axes.set_title(str(self.wellid) + ' Instant Production Plot')





        i=0
        for yid in Y_axis:
            self.plot_y_line_dict[yid]=self.axes.lines[i]
            i+=1


        isec=0
        for ysecid in Y_sec_axis:
            self.plot_y_line_dict[ysecid]=self.axes2.lines[isec]
            isec+=1

        for x in self.plot_instance_dict.keys():
            if 'CASING' not in x or 'PROD' not in x or 'INSTANT' not in x or 'DAILY_PROD_GAS' not in x:
                self.plot_instance_dict[x][0].remove()
                self.axes2.add_line(self.plot_instance_dict[x][0])
                self.plot_instance_dict[x][0].set_picker(5)
        h1, l1 = self.axes.get_legend_handles_labels()
        final_h, final_l = self.axes2.get_legend_handles_labels()


        '''if plot_type=='daily':
            h1.insert(1, h2.pop(2))
            l1.insert(1, l2.pop(2))
            final_h = h1 + h2
            final_l = l1 + l2
        else:'''
        final_h,final_l=self.axes2.get_legend_handles_labels()
        print 'final_h,final_l',final_l


        self.plot_legend = self.axes2.legend(final_h, final_l, loc=2, framealpha=98, fontsize=11)




    def X_Y_axsi(self,Xaxis,Yaxis):
        '''
        :param Xaxis: preparing data for X axis, column was defined in Xaxis
        :param Yaxis: Preparing data for Y axis, columns wre defined in Yaxis, it's a list
        :return:
        '''
        '''
        1.Iniitalizing X axis
        '''
        xaxis_list=[]
        for x in self.data_dict[Xaxis]:
                xaxis_list.append(x)
        '''
        2.Initializing Y axis
        '''
        y_dict={}
        for col in Yaxis:
            if  col not in self.ysec_list:
                y_dict[col]=self.data_dict[col]
        return(xaxis_list,y_dict)


    def Y_Axis_Sec(self):
        ysec_dict={}
        for col in self.ysec_list:
            ysec_dict[col]=self.data_dict[col]
        return(ysec_dict)


    def ScaleSetting(self,step_y,step_ysec,step_X):
        min_ticker,max_ticker=self.axes.get_ylim()
        #min_tick_sec,max_tick_sec=self.axes2.get_ylim()
        if step_y!=0:
            self.axes.set_yticks(fltrange(min_ticker,max_ticker,step_y))
        #if step_ysec!=0:
         #   self.axes2.set_yticks(fltrange(min_tick_sec,max_tick_sec,step_ysec))
        if step_X!=0:
            if self.time_unit=='DAY':
                self.axes.xaxis.set_major_locator(mdates.DayLocator(interval=step_X))
            elif self.time_unit=='MINUTE':
                self.axes.xaxis.set_major_locator(mdates.MinuteLocator(interval=step_X))
            elif self.time_unit=='HOUR':
                self.axes.xaxis.set_major_locator(mdates.HourLocator(interval=step_X))


    def GridShow(self,judge):
        self.axes.grid(judge)


class Workaround(object):
    def __init__(self, artists):
        self.artists = artists
        artists[0].figure.canvas.mpl_connect('button_press_event', self)
        print 'print artist in workaround',self.artists

    def __call__(self, event):
        for artist in self.artists:
            artist.pick(event)