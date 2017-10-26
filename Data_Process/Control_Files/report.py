import os,string

#filename=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script\Prod_data_import.log'
def report(filename):
        bstring='Total logical records rejected:'
        astring=open(filename)
        astring.seek(0)
        try:
                for line in astring.readlines():
                        if  bstring in line:
                                return line.split()[-1]
        finally:
                astring.close()
def report1(filename):
        bstring='Total logical records read:'
        astring=open(filename)
        astring.seek(0)
        try:
                for line in astring.readlines():
                        if  bstring in line:
                                return line.split()[-1]
        finally:
                astring.close()

#if string.atof(report(filename))>1:
     # print 'Yo! ! the data load failed, please check your input file or contact Mr.Benoit !'
      #os.system(r'notepad W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script\Prod_data_import.log')
#elif string.atof(report1(filename))==0:
        #print 'Yo! ! the data load failed, Maybe you Did Not correctly setup inputfile!'
#else:
       #print 'Data Load Successfully!'

