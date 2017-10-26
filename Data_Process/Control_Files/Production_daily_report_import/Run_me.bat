@echo off

sqlldr gsrdba/oracle@gsrdb control="'W:\EXCHANGE\GSR_DATABASE_APPLICATION\Prod_data_import.CTL'",log="'W:\EXCHANGE\GSR_DATABASE_APPLICATION\Prod_data_import.log'"


sqlplus gsrdba/oracle@gsrdb @"W:\GSR\050000-GeoInformation\052300-Projects\User_Interface\wxPython_Script\Data_Process\Control_Files\Production_daily_report_import\cum_prod_aux.sql"
 