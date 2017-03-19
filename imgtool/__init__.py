from . import func
from .constant import *

__all__ = [
    'resize',

]


def resize(pathfile, outpath, height, width, process_num=1, mode=func.cv2.IMREAD_COLOR,
           inter=func.cv2.INTER_LINEAR, breakpoint=True, islog=True):
    return func.resize(pathfile, outpath, height, width, process_num, mode, inter, breakpoint, islog)
