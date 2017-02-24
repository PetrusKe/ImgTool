import os
import re
filepath = 'D:\\Share\\'
infilepath = filepath + 'val_map.txt'
outfilepath = filepath + 'out.txt'

outfile = open(outfilepath, 'w')

with open(infilepath, 'r') as infile:
    for line in infile.readlines():
        outfile.write(str(line).split()[0]+'\n')


outfile.close()