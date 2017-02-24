import os
import sys
import re
import cv2
import signal
import threading
import time
import multiprocessing
from functools import partial

__all__ = [
    'SUPPORT_FORMAT',
    'resize',
]

__FORMAT_ERROR = '[Error] Not support format in file: '
__NOFILE_ERROR = '[Error] No such file: '
__IMREAD_ERROR = '[Error] Can not load file: '

__EXPEND_WARNING = '[Warning] Expend origin image: '

SUPPORT_FORMAT = [
    'bmp', 'dib',
    'jpeg', 'jpg', 'jpe',
    'jp2',
    'png',
    'pbm', 'pgm', 'ppm',
    'sr', 'ras',
    'tiff', 'tif'
]

__MAX_PROCESS = 16


def resize(pathfile, height, width, process_num=1, mode=cv2.IMREAD_COLOR, inter=cv2.INTER_LINEAR, breakpoint=True):
    def __check(pathfile, height, width, mode):
        if not os.path.isfile(pathfile):
            # handle error
            sys.exit()
        if height < 0 or width < 0:
            sys.stderr.write('')
            sys.exit()
        if mode == cv2.IMREAD_UNCHANGED:
            sys.stderr.write('Now not support BGR-D image')
            sys.exit()

    __check(pathfile, height, width, mode)
    pathfiles, process_num = __file_split(pathfile, process_num)

    # signal.signal(signal.SIGINT, __quit)
    process_pool = multiprocessing.Pool(process_num)
    for index, pathfile in enumerate(pathfiles):
        process_pool.apply_async(__resize_process, args=(pathfile, height, width, mode, inter, breakpoint))
    process_pool.close()
    process_pool.join()

    sys.stdout.write('Finish all image resize.\n')


def __resize_process(pathfile, height, width, mode, inter, breakpoint):
    def __quit(signum, frame):
        if breakpoint and len(context):
            with open(pathfile, 'w') as file:
                file.writelines(context)
        else:
            __file_delete(pathfile)
        time.sleep(0.5)
        # http://stackoverflow.com/questions/26578799/python-send-sigint-to-subprocess-using-os-kill-as-if-pressing-ctrlc
        pid = os.getpid()
        os.kill(pid, signal.CTRL_BREAK_EVENT)

    signal.signal(signal.SIGINT, __quit)

    warning_list = []
    error_list = []
    with open(pathfile, 'r') as file:
        context = file.readlines()

    context.reverse()
    for line in reversed(context):
        img_path = line.strip()
        img_name = re.split(r'/|\\', img_path)[-1]
        if img_name.split('.')[-1].lower() not in SUPPORT_FORMAT:
            error_list.append(__FORMAT_ERROR + img_path)
            context.pop()
            continue
        elif not os.path.isfile(img_path):
            error_list.append(__NOFILE_ERROR + img_path)
            context.pop()
            continue

        ori_img = cv2.imread(img_path, mode)
        if ori_img.data is not None:
            if height == ori_img.shape[0] and width == ori_img.shape[1]:
                context.pop()
                continue
            elif height > ori_img.shape[0] or width > ori_img.shape[1]:
                warning_list.append(__EXPEND_WARNING + img_path)
            img = cv2.resize(ori_img, (height, width), inter)
            cv2.imwrite(img_path, img)
            sys.stdout.write('[Process:%d]Finish resize image: %s.\n' % (int(os.getpid()), pathfile))
        else:
            error_list.append(__IMREAD_ERROR + img_path)
        context.pop()

    sys.stdout.write('Finish resize images in file: %s.\n' % pathfile)
    __file_delete(pathfile)


def __file_split(filepath, process_num):
    if process_num <= 1:
        return [filepath], 1
    elif process_num > __MAX_PROCESS:
        process_num = __MAX_PROCESS

    file_list = []
    with open(filepath, 'r') as file:
        context = file.readlines()
    lines = len(context) // process_num

    for num in range(process_num - 1):
        path = filepath + '_tmp' + str(num)
        with open(path, 'w') as file:
            file.writelines(context[lines * num:lines * (num + 1)])
        file_list.append(path)
    path = filepath + '_tmp' + str(num + 1)
    with open(path, 'w') as file:
        file.writelines(context[lines * (num + 1):])
    file_list.append(path)

    return file_list, process_num


def __file_delete(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)


if __name__ == '__main__':
    start_time = time.time()
    resize('C:\\Dataset\\ImageNet_CNTK\\val_map.txt', 224, 224, process_num=8)
    print('total time: %.2f s', float(time.time() - start_time))
