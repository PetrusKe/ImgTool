import os
import sys
import re
import cv2
import signal
import threading
import time
import multiprocessing

# TODO: subprocess?

__all__ = [
    'SUPPORT_FORMAT',
    'resize',
]

__FORMAT_ERROR = '[Error] Not support format in file: '
__NOFILE_ERROR = '[Error] No such file: '
__IMREAD_ERROR = '[Error] Can not load file: '

__EXPEND_WARnING = '[Warning] Expend origin image: '

SUPPORT_FORMAT = [
    'bmp', 'dib',
    'jpeg', 'jpg', 'jpe',
    'jp2',
    'png',
    'pbm', 'pgm', 'ppm',
    'sr', 'ras',
    'tiff', 'tif'
]

__MAX_PROCESS = 8


def resize(pathfile, height, width, process_num=1, mode=cv2.IMREAD_COLOR, inter=cv2.INTER_LINEAR):
    __resize_check(pathfile, height, width, mode)
    pathfiles, process_num = __file_split(pathfile, process_num)

    signal.signal(signal.SIGINT, __quit)
    process_pool = multiprocessing.Pool(process_num)
    for index, pathfile in enumerate(pathfiles):
        process_pool.apply_async(__resize_process, args=(pathfile, height, width, mode, inter))
    process_pool.close()
    process_pool.join()

    sys.stdout.write('Finish all image resize.\n')


def __resize_process(pathfile, height, width, mode, inter):
    signal.signal(signal.SIGINT, __quit)

    warning_list = []
    error_list = []

    file = open(pathfile, 'r')
    context = file.readlines()

    for img_path in context:
        img_path = img_path.strip()
        img_name = re.split(r'/|\\', img_path)[-1]
        if img_name.split('.')[-1].lower() not in SUPPORT_FORMAT:
            error_list.append(__FORMAT_ERROR + img_path)
            continue
        if not os.path.isfile(img_path):
            error_list.append(__NOFILE_ERROR + img_path)
            continue

        ori_img = cv2.imread(img_path, mode)
        if ori_img.data is not None:
            if height == ori_img.shape[0] and width == ori_img.shape[1]:
                continue
            elif height > ori_img.shape[0] or width > ori_img.shape[1]:
                warning_list.append(__EXPEND_WARnING + img_path)

            img = cv2.resize(ori_img, (height, width), inter)
            cv2.imwrite(img_path, img)
            sys.stdout.write('[Process:%d]Finish resize image: %s.\n' % (int(os.getpid()), pathfile))
        else:
            error_list.append(__IMREAD_ERROR + img_path)

    sys.stdout.write('Finish resize images in file: %s.\n' % pathfile)


def __file_split(pathfile, process_num):
    if process_num <= 1:
        return [pathfile], 1
    elif process_num > __MAX_PROCESS:
        process_num = __MAX_PROCESS

    file_list = []
    with open(pathfile, 'r') as file:
        context = file.readlines()
    lines = len(context) // process_num

    for num in range(process_num - 1):
        path = pathfile + '_' + str(num)
        with open(path, 'a') as file:
            file.writelines(context[lines * num:lines * (num + 1)])
        file_list.append(path)
    path = pathfile + '_' + str(num + 1)
    with open(path, 'a') as file:
        file.writelines(context[lines * (num + 1):])
    file_list.append(path)

    return file_list, process_num


def __resize_check(pathfile, height, width, mode):
    if not os.path.isfile(pathfile):
        # handle error
        sys.exit()
    if height < 0 or width < 0:
        sys.stderr.write('')
        sys.exit()
    if mode == cv2.IMREAD_UNCHANGED:
        sys.stderr.write('Now not support BGR-D image')
        sys.exit()


def __quit(signum, frame):
    # http://stackoverflow.com/questions/26578799/python-send-sigint-to-subprocess-using-os-kill-as-if-pressing-ctrlc
    pid = os.getpid()
    os.kill(pid, signal.CTRL_BREAK_EVENT)


if __name__ == '__main__':
    start_time = time.time()
    resize('C:\\Dataset\\ImageNet_CNTK\\val_map.txt', 256, 256, process_num=8)
    print('total time: %.2f s', float(time.time() - start_time))

