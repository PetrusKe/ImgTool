__all__ = [
    'MAX_PROCESS',
    'SUPPORT_FORMAT',
    'TMP_SUFFIX',
    'ERROR',
    'WARNING',
]

MAX_PROCESS = 16

SUPPORT_FORMAT = [
    'bmp', 'dib',
    'jpeg', 'jpg', 'jpe',
    'jp2',
    'png',
    'pbm', 'pgm', 'ppm',
    'sr', 'ras',
    'tiff', 'tif',
]

TMP_SUFFIX = '_tmp'

ERROR = {
    'format_error': '[Error] Not support format in file: ',
    'nofile_error': '[Error] No such file: ',
    'imread_error': '[Error] Can not load file: ',
    'tmpfile_error': '[Error] Fail to copy tmp file: ',
}

WARNING = {
    'expend_warning': '[Warning] Expend origin image: ',
}
