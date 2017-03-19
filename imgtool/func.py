import os, sys, time, signal, re, shutil
import cv2, logging, multiprocessing
from copy import deepcopy
from PIL import Image, ImageFile
import imghdr
from . import util
from .constant import *

__all__ = [
    'resize',
]


def resize(pathfile, outpath, height, width, process_num=1, mode=cv2.IMREAD_COLOR,
           inter=cv2.INTER_LINEAR, breakpoint=True, islog=True):
    def a(signum, frame):
        process_pool.join()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    if not os.path.isfile(pathfile):
        # handle error
        sys.exit()
    if height < 0 or width < 0:
        sys.stderr.write('')
        sys.exit()
    if mode == cv2.IMREAD_UNCHANGED:
        logging.warning('')
        sys.stderr.write('Now not support BGR-D image')
        sys.exit()

    parallel_args = util.file_split(pathfile, process_num, breakpoint)

    if parallel_args[1] > 0:
        process_pool = multiprocessing.Pool(parallel_args[1])

        for index, file in enumerate(parallel_args[0]):
            process_pool.apply_async(__resize_process, args=(file, outpath, height, width, mode, inter, breakpoint))
        process_pool.close()
        process_pool.join()

    tmp_folder = os.path.split(pathfile)[0] + '\\' + TMP_SUFFIX
    if not os.listdir(tmp_folder):
        shutil.rmtree(tmp_folder, ignore_errors=True)  # fixme: handle errors?
        sys.stdout.write('Finish all images resize.\n')


def __resize_process(pathfile, output, height, width, mode, inter, breakpoint):
    def __quit(signum, frame):
        # if not breakup and ori_img is not None:
        #     print('!!!', img_path + TMP_SUFFIX, '--', img_path)
        #     cv2.imwrite(img_path, ori_img)
        #
        # util.file_delete('C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\_img\\' + img_name)

        if backup['tag']:
            context = backup['cur_context']
            cv2.imwrite(backup['cur_img_path'], backup['cur_img'])
        util.file_delete(backup['cur_img_path'] + TMP_SUFFIX)

        if breakpoint and len(context):
            context.reverse()
            with open(pathfile, 'w') as file:
                file.writelines(context)
        else:
            util.file_delete(pathfile)
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

    _img = 'C:\\Users\\Zhanghan Ke\\Downloads\\imgtool_test\\_img'

    backup = {
        'cur_context': None,
        'cur_img_path': None,
        'cur_img': None,
        'tag': False,
    }

    context.reverse()
    for line in reversed(context):
        backup['tag'] = False
        backup['cur_context'] = deepcopy(context)

        img_path = line.strip()
        backup['cur_img_path'] = deepcopy(img_path)
        img_name = re.split(r'/|\\', img_path)[-1]
        if img_name.split('.')[-1].lower() not in SUPPORT_FORMAT:
            error_list.append(ERROR['format_error'] + img_path)
            context.pop()
            continue
        elif not os.path.isfile(img_path):
            error_list.append(ERROR['nofile_error'] + img_path)
            context.pop()
            continue

        ori_img = cv2.imread(img_path, mode)

        backup['cur_img'] = deepcopy(ori_img)
        backup['tag'] = True
        if ori_img.data is not None:
            if height == ori_img.shape[0] and width == ori_img.shape[1]:
                context.pop()
                continue
            elif height > ori_img.shape[0] or width > ori_img.shape[1]:
                warning_list.append(WARNING['expend_warning'] + img_path)

            img = cv2.resize(ori_img, (height, width), inter)

            cv2.imwrite(img_path + TMP_SUFFIX, img)

            shutil.copy2(img_path + TMP_SUFFIX, img_path)
            util.file_delete(img_path + TMP_SUFFIX)

            # sys.stdout.write('[Process:%d]Finish resize image: %s.\n' % (int(os.getpid()), pathfile))
        else:
            error_list.append(ERROR['imread_error'] + img_path)
        context.pop()

    sys.stdout.write('Finish resize images in file: %s.\n' % pathfile)
    util.file_delete(pathfile)
