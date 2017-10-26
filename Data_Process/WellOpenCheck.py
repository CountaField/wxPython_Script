# !/usr/bin/python
# -*- coding:utf8-*-
import string
from Oracle_connection import Gsrdb_Conn
import datetime
import time
import os
import pandas as pd


class OpenWellCheck:
    def __init__(self):
        db = Gsrdb_Conn()
        close_well_list=[]
        close_cur=db.Sql("select wellid from aux_prod_shut_wells ")
        for id in close_cur.fetchall():
            close_well_list.append(id[0])

        for id in close_well_list:
            well_check_cur=db.Sql("select count(*) from raw_")



        db.close()



if __name__=='__main__':
    test=OpenWellCheck()