import cv2
import argparse
import numpy
import matplotlib
import imgtool
import time

INTER_POLICY = {
    'nearest': cv2.INTER_NEAREST,
    'linear': cv2.INTER_LINEAR,
    'area': cv2.INTER_AREA,
    'cubic': cv2.INTER_CUBIC,
    'lanczos4': cv2.INTER_LANCZOS4
}

READ_MODE = {
    'color': cv2.IMREAD_COLOR,
    'gray': cv2.IMREAD_GRAYSCALE,
    'unchanged': cv2.IMREAD_UNCHANGED
}

SUPPORT_SUFFIX = {

}

OPES = {
    'resize': imgtool.resize,
}


def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--operation', required=True, type=str, help='')
    parser.add_argument('-p', '--pathfile', required=True, type=str,
                        help='path for files which store all images path')
    parser.add_argument('-h', '--height', required=True, type=int, help='height for resized image')
    parser.add_argument('-w', '--width', required=True, type=int, help='width for resized image')
    parser.add_argument('-m', '--mode', required=False, type=str, default='color',
                        choices=list(READ_MODE.keys()),
                        help='mode of images')
    parser.add_argument('-t', '--thread', required=False, type=int, default=1, help='thread num')
    return parser


if __name__ == '__main__':
    # parser = init_parser()
    # args = vars(parser.parse_args())
    s = time.time()
    OPES['resize']('C:\\Users\\kezha\\Pictures\\test\\out.txt', 256, 256, process_num=2)
    print('total time: ', time.time() - s)
