import os
import sys
import re
import cv2
import signal
import time
import shutil
import multiprocessing

__all__ = [
    'SUPPORT_FORMAT',
    'MAX_PROCESS',
    'resize',

]

MAX_PROCESS = 16

SUPPORT_FORMAT = [
    'bmp', 'dib',
    'jpeg', 'jpg', 'jpe',
    'jp2',
    'png',
    'pbm', 'pgm', 'ppm',
    'sr', 'ras',
    'tiff', 'tif'
]

__FORMAT_ERROR = '[Error] Not support format in file: '
__NOFILE_ERROR = '[Error] No such file: '
__IMREAD_ERROR = '[Error] Can not load file: '
__TMPFILE_ERROR = '[Error] Fail to copy tmp file: '
__EXPEND_WARNING = '[Warning] Expend origin image: '

__TMP_SUFFIX = '_tmp'


def resize(pathfile, height, width, process_num=1, mode=cv2.IMREAD_COLOR, inter=cv2.INTER_LINEAR, breakpoint=True):
    if not os.path.isfile(pathfile):
        # handle error
        sys.exit()
    if height < 0 or width < 0:
        sys.stderr.write('')
        sys.exit()
    if mode == cv2.IMREAD_UNCHANGED:
        sys.stderr.write('Now not support BGR-D image')
        sys.exit()

    parallel_args = __file_split(pathfile, process_num, breakpoint)
    __parallel_handle(parallel_args, __resize_process, (pathfile, height, width, mode, inter, breakpoint))

    tmp_folder = os.path.split(pathfile)[0] + '\\' + __TMP_SUFFIX
    if os.listdir(tmp_folder):
        sys.stdout.write('Stop images resize.\n')
        return

    shutil.rmtree(tmp_folder, ignore_errors=True)  # fixme: handle errors?
    sys.stdout.write('Finish all images resize.\n')

    # signal.signal(signal.SIGINT, __quit)
    # process_pool = multiprocessing.Pool(process_num)
    # for index, pathfile in enumerate(pathfiles):
    #     process_pool.apply_async(__resize_process, args=(pathfile, height, width, mode, inter, breakpoint))
    # process_pool.close()
    # process_pool.join()


def __resize_process(pathfile, height, width, mode, inter, breakpoint):
    def __quit(signum, frame):
        if breakpoint and len(context):
            with open(pathfile, 'w') as file:
                file.writelines(context)
        else:
            __file_delete(pathfile)
        time.sleep(0.5)
        # reference:
        # http://stackoverflow.com/questions/26578799
        # /python-send-sigint-to-subprocess-using-os-kill-as-if-pressing-ctrlc
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


def __file_split(filepath, process_num, breakpoint):
    tmp_folder = os.path.split(filepath)[0] + '\\' + __TMP_SUFFIX
    if breakpoint:
        if os.path.isdir(tmp_folder) and os.listdir(tmp_folder):
            # TODO: breakpoint load need test
            tmp_files = [files for roots, dirs, files in os.walk(tmp_folder)][0]
            process_num = len(tmp_files)
            file_list = []
            for file in tmp_files:
                path = tmp_folder + '\\' + file
                file_list.append(path)
            assert len(file_list) == process_num
            return (file_list, process_num)

    if os.path.isdir(tmp_folder):
        shutil.rmtree(tmp_folder)
    os.makedirs(tmp_folder)

    if process_num <= 1:
        process_num = 1
        path = tmp_folder + '\\' + __TMP_SUFFIX + str(process_num)
        try:
            shutil.copyfile(filepath, path)
        except shutil.SameFileError:
            sys.stderr.write(__TMPFILE_ERROR + filepath)
        return ([path], process_num)

    elif process_num > MAX_PROCESS:
        process_num = MAX_PROCESS

    file_list = []
    with open(filepath, 'r') as file:
        context = file.readlines()
    lines = len(context) // process_num

    for num in range(1, process_num):
        path = tmp_folder + '\\' + __TMP_SUFFIX + str(num)
        with open(path, 'w') as file:
            file.writelines(context[lines * num:lines * num])
        file_list.append(path)
    assert (num + 1) == process_num
    path = tmp_folder + '\\' + __TMP_SUFFIX + str(process_num)
    with open(path, 'w') as file:
        file.writelines(context[lines * process_num:])
    file_list.append(path)

    return (file_list, process_num)


def __file_delete(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)


def __parallel_handle(parallel_args, func, func_args):
    # TODO: need test
    process_pool = multiprocessing.Pool(parallel_args[1])
    for index, pathfile in enumerate(parallel_args[0]):
        process_pool.apply_async(func, args=func_args)
    process_pool.close()
    process_pool.join()


if __name__ == '__main__':
    start_time = time.time()
    resize('C:\\Dataset\\ImageNet_CNTK\\val_map.txt', 224, 224, process_num=8)
    print('total time: %.2f s', float(time.time() - start_time))
