import imgtool
import os
import cv2

if __name__ == '__main__':
    size = 30
    imgtool.resize('C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\index.txt',
                   'C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\out\\',
                   size, size, process_num=8,
                   breakpoint=True)

    print('eval...')

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
            if s.shape[0] != size or s.shape[1] != size:
                error += 1
                errors.append(folder + i)
            else:
                index += 1

    print(index)
    print(error)
    print(errors)
