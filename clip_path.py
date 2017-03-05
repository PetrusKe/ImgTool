import os
import re

filepath = 'C:\\Users\\kezha\\Pictures\\test\\'
infilepath = filepath + 'val_map.txt'
outfilepath = filepath + '\\277.jpg'

print(os.path.split(outfilepath))

print(os.path.pardir)
# if os.path.isdir(filepath):
#     filenames = os.listdir(filepath)
#     for filename in filenames:
#         outfile.write(filepath + '\\' + filename + '\n')
#
#     outfile.close()


import shutil
print(os.path.isdir(outfilepath))
if os.path.isdir(filepath):
    shutil.rmtree(filepath)
