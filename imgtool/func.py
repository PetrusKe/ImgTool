import os, sys, signal, re, shutil
import cv2, logging, multiprocessing
from PIL import Image
from . import util
from .constant import *

__all__ = [
    'resize',
]


def resize(pathfile, outpath, height, width, process_num=1, mode=cv2.IMREAD_COLOR,
           inter=cv2.INTER_LINEAR, breakpoint=True, islog=True):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    if not os.path.isfile(pathfile):
        sys.stderr.write('')
        sys.exit()
    if height < 0 or width < 0:
        sys.stderr.write('')
        sys.exit()
    if mode == cv2.IMREAD_UNCHANGED:
        logging.warning('')
        sys.stderr.write('Now not support BGR-D image')
        sys.exit()

    tmp_folder = os.path.split(pathfile)[0] + '\\' + TMP_FOLDER
    parallel_args = util.file_split(pathfile, process_num, breakpoint)

    if parallel_args[1] > 0:
        print('start...')
        process_pool = multiprocessing.Pool(parallel_args[1])
        for index, file in enumerate(parallel_args[0]):
            args = (file, tmp_folder, outpath, height, width, mode, inter, breakpoint)
            process_pool.apply_async(__resize_process, args=args)
        process_pool.close()
        process_pool.join()

    if not [files for roots, dirs, files in os.walk(tmp_folder)][0]:
        shutil.rmtree(tmp_folder, ignore_errors=True)  # fixme: handle errors?
        sys.stdout.write('Finish all images resize.\n')


def __resize_process(pathfile, tmp_folder, output, height, width, mode, inter, breakpoint):
    def __quit(signum, frame):
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

    img_folder = tmp_folder + '\\' + TMP_IMG_FOLDER
    if not os.path.isdir(img_folder):
        os.makedirs(img_folder)

    warning_list = []
    error_list = []
    with open(pathfile, 'r') as file:
        context = file.readlines()
    context.reverse()

    for line in reversed(context):
        img_path = line.strip()
        img_name = re.split(r'/|\\', img_path)[-1]
        if img_name.split('.')[-1].lower() not in SUPPORT_FORMAT:
            error_list.append(ERROR['format_error'] + img_path)
            context.pop()
            continue
        elif not os.path.isfile(img_path):
            error_list.append(ERROR['nofile_error'] + img_path)
            context.pop()
            continue

        tmp_img = img_folder + '\\' + img_name + TMP_FOLDER
        try:
            Image.open(img_path).verify()
        except:
            if os.path.isfile(tmp_img):
                shutil.copy2(tmp_img, img_path)
            else:
                print(pathfile + ': Err!' + img_path)
                continue

        ori_img = cv2.imread(img_path, mode)
        if ori_img.data is not None:
            if height == ori_img.shape[0] and width == ori_img.shape[1]:
                util.file_delete(tmp_img)
                context.pop()
                continue
            elif height > ori_img.shape[0] or width > ori_img.shape[1]:
                warning_list.append(WARNING['expend_warning'] + img_path)
            img = cv2.resize(ori_img, (height, width), inter)
            cv2.imwrite(tmp_img, img)
            shutil.copy2(tmp_img, img_path)
            util.file_delete(tmp_img)
        else:
            error_list.append(ERROR['imread_error'] + img_path)
        context.pop()

    sys.stdout.write('Finish resize images in file: %s.\n' % pathfile)
    util.file_delete(pathfile)
