import os,exceptions,sys,string
sys.path.append(r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script')
#import report

#choice=raw_input('Data Load please enter "Y" for help please enter \'?\': ')
#if choice ==('Y' or 'y'):
y=raw_input('please enter year: ')
m=raw_input('please enter month: ')
d=raw_input('please enter day: ')
#else:
        #print 'what is this?'
''' Declare variable for this script, main target is get date which user want to import into database. three variable people need to enter:
        1.Year----format: YYYY, for example 2014
        2.Month----format: MM, for example 01,02,10,11
        3.Day----format: DD, for example 01,02,20,31'''


years=['2012','2013','2014','2015','2016']
inputfile_dir=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\01_Daily inputs\\'
text=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script\Prod_data_sample.CTL'
text2=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script\Prod_data_import.CTL'
filename=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script\Prod_data_import.log'

''' Declare constant for script, main target are Oracle database SQL*Loader control file(text,text2),
   log file(filename) and daily input file(inputfile_dir) path'''


if len(y)!=4:
	raise Exception( 'please enter correct year from 2012 to 2014')
elif y not in years:
	raise Exception('Entered year must be from 2012 to 2014')
else:
	pass

if len(m)!=2:
	raise Exception('please enter correct Month,for example: Jan=01,Feb=02...Dec=12')
'''elif m not in range(00,12):
                raise Exception('Welcome to earth, in this world, we only have month from 01 to 12')'''
if len(d)!=2:
	raise Exception( 'please enter correct Day,from 01-31')


def fulldate(y,m,d):
 	fulldate=y+'-'+m+'-'+d
	return fulldate



def checkfile(path1):
        import os
        filename=os.path.join(path1,fulldate(y,m,d)+'.csv')
        if os.path.isfile(filename):
                return True
        else:
                return False
        
def replace(stext,rtext):
        inputfile=open(stext,'r')
        outputfile=open(rtext,'w')
        try:            
                astring=inputfile.read()
                outputfile.write(astring.replace('$input',fulldate(y,m,d)+'x'))
        finally:
                inputfile.close()
                outputfile.close()

if checkfile(inputfile_dir):
        replace(text,text2)
else:
        raise Exception('yo man ! you DID NOT setup inputfile!')

#if string.atof(report.report(filename))>1:
       # print 'hi belle! the data load failed, please check your input file or contact Mr.Benoit !'
        #os.system(r'notepad W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\02_Production Data Update Script\Prod_data_import.log')
#elif string.atof(report.report1(filename))==0:
        #print 'Hi belle! the data load failed, Mybe you Did Not correctly setup inputfile!'
#else:
        #print 'Data Load Successfully!'
apath=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\01_Daily inputs\\'+fulldate(y,m,d)+'.csv'
bpath=r'W:\GSR\040000-Reservoir_Studies\040300-RE_Summary and Templates\01_Database\02_Production Data Update\01_Daily inputs\\'+fulldate(y,m,d)+'x.csv'
afile=open(apath)
bfile=open(bpath,'w')

def dataproc1(afile):
        import re
        rs=re.compile(r'\w|\s|[\.,-:]|\)|\(')
        alist=[]
        astring=''
        bstring=''
        for x in afile:
                if x[:2]=='WE':
                        continue
                elif x[:2]=='SN' or x[:2]=='SU':
                        alist.append(x)
                else:
                        alist[len(alist)-1]=alist[len(alist)-1][:-1]+x
  
        
        for z in alist:
                for y in z:
                        if rs.match(y):
                                astring+=y
        bstring=astring.replace('_x000D_','')
        return bstring

bfile.write(dataproc1(afile))
bfile.close()
afile.close()
