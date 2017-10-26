# encoding:utf-8
from multiprocessing import Process,Queue,JoinableQueue,Manager
import os, time, random
from Oracle_connection import Gsrdb_Conn
from PlotDraw import PlotDrawing

import wx
import threading

# 线程启动后实际执行的代码块
class multiprocctest:

    def __init__(self):
        start=time.clock()
        print "process id is %d" % os.getpid()
        self.blist = Manager().dict()
        self.alist = [1,2,3,4,5,6,7,8,9,10]
        self.clist = [1,2,3,4,5,6,7,8,9,10]
        self.prod_dict=[]

        #self.alist = []
        #wellid_list = ['SN0002-01','SN0138-04']
        self.CreateThread()
        #self.CreateProcess()
        for x in self.clist:
            self.prod_dict.append(x)
        print 'prod dict is ',self.prod_dict
        #print 'the prod data dict is ', self.prod_dict['SN0138-04']

        end=time.clock()
        print 'main process running time is %f ' % (end - start)

    def CreateThread(self):

        t=threading.Thread(target=self.DataProcess,args=(self.blist,self.alist))
        t.start()
        #t.join()
        time.sleep(6)
        if t.isAlive():
            t._Thread__stop()




    def CreateProcess(self):

        #self.DataProcess(wellid,self.alist)
        process = Process(target=self.DataProcess, args=(self.blist,self.alist))
        process.start()
        process.join()





    def DataProcess(self, blist,prod_date_list):
        print "starting create new process......", os.getpid()
        start = time.clock()
        time.sleep(5)
        for x in prod_date_list:
            blist[x]=[1]
        print blist
        end = time.clock()
        print 'sub threading running time is %f ' % (end - start)

    def PordDataPrepare(self):
        pass

if __name__ == "__main__":
    test=multiprocctest()
