__author__ = 'Administrator'


def FloatRange(min,max,step,precision=10 ):
    '''
    This is a fuction for ranging float data,which just enter min value, max vlua and step,then it will return you a list
    :param min:
    :param max:
    :param step:
    :return:
    '''
    prec="%0."+str(precision)+"f"
    print(prec)
    alist=[]
    while min<max:
        alist.append(float(prec %  min))
        min+=step
    return alist

