# !/usr/bin/python
# -*- coding:gbk -*-


def CVSformat(inputfile):
    import csv
    from pyexcel_xls import get_data
    data = get_data(inputfile)
    rel_file = inputfile[:inputfile.find('.xls')] + '.csv'
    csv_file = open(rel_file, 'wb')
    cformat = csv.writer(csv_file)
    for row in data:
        #print row
        cformat.writerow(row)
    return rel_file
