import os
import sys
import shutil
import multiprocessing
from .constant import *


def file_split(filepath, process_num, breakpoint):
    tmp_folder = os.path.split(filepath)[0] + '\\' + TMP_FOLDER
    if breakpoint:
        if os.path.isdir(tmp_folder) and os.listdir(tmp_folder):
            # TODO: breakpoint load need test
            tmp_files = [files for roots, dirs, files in os.walk(tmp_folder)][0]
            file_list = []
            for file in tmp_files:
                path = tmp_folder + '\\' + file
                if os.path.getsize(path) == 0:
                    os.remove(path)
                file_list.append(path)

            process_num = len(file_list)
            return (file_list, process_num)

    if os.path.isdir(tmp_folder):
        shutil.rmtree(tmp_folder)
    os.makedirs(tmp_folder)

    if process_num <= 1:
        process_num = 1
        path = tmp_folder + '\\' + TMP_FOLDER + str(process_num)
        try:
            shutil.copyfile(filepath, path)
        except shutil.SameFileError:
            sys.stderr.write(ERROR['tmpfile_error'] + filepath)
        return ([path], process_num)

    elif process_num > MAX_PROCESS:
        process_num = MAX_PROCESS

    file_list = []
    with open(filepath, 'r') as file:
        context = file.readlines()
    lines = len(context) // process_num

    for num in range(1, process_num):
        path = tmp_folder + '\\' + TMP_FOLDER + str(num)
        with open(path, 'w') as file:
            file.writelines(context[lines * (num - 1):lines * num])
        file_list.append(path)

    assert (num + 1) == process_num
    path = tmp_folder + '\\' + TMP_FOLDER + str(process_num)
    with open(path, 'w') as file:
        file.writelines(context[lines * num:])
    file_list.append(path)

    return (file_list, process_num)


def file_delete(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)

# def parallel_handle(parallel_args, func, func_args):
#     # TODO: need test
#     process_pool = multiprocessing.Pool(parallel_args[1])
#     for index, file in enumerate(parallel_args[0]):
#         process_pool.apply_async(func, args=func_args)
#     process_pool.close()
#     process_pool.join()
