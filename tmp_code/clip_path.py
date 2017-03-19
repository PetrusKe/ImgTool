import os
import re
#
# infile = 'C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\train_map.txt'
# outfile = 'C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\train_map1.txt'
#
# out = []
# with open(infile, 'r') as f:
#     lines = f.readlines()
#     with open(outfile, 'w') as of:
#         for line in lines:
#             of.write(line[:-3] + '\n')

# path = 'C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\test\\'
# for file in os.listdir(path):
#     if os.path.isfile(os.path.join(path, file)):
#         newname = file.split('.')[0] + '.jpg'
#         os.rename(os.path.join(path, file), os.path.join(path, newname))


import cv2

folder = 'C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\test\\'
l = os.listdir(folder)
index = 0
error = 0
errors = []
for i in l:
    s = cv2.imread(folder + i)
    if s is False or s is None:
        print(False)
        error += 1
        errors.append(folder + i)
    else:
        index += 1
        print(s.shape)

print(index)
print(error)
print(errors)