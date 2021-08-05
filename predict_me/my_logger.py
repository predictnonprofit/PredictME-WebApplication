import logging
import sys
import traceback
from pathlib import Path


def setup_logging_to_file(log_type):
    '''
    Setup and initializes the logging file
    :return: logger
    '''
    logger_folder = Path(__file__).parent / "logs"
    if log_type == 'errors':
        logger = logging.getLogger(
            "errors_log")  # make names for logger to avoid mixed logs in errors and info log files
        logging_level = logging.ERROR
        logger_file = logger_folder / "errors.log"
        logger.setLevel(logging.DEBUG)  # set the logger level
        formatter = logging.Formatter(
            '%(asctime)s, %(levelname)-4s [%(filename)s:%(lineno)d] %(funcName)s %(module)s --> %(message)s',
            '%d-%m-%Y:%H:%M:%S')  # set log format
    elif log_type == 'info':
        logger = logging.getLogger('info_log')  # make names for logger to avoid mixed logs in errors and info log files
        logging_level = logging.INFO
        logger_file = logger_folder / "info.log"
        logger.setLevel(logging.INFO)  # set the logger level
        formatter = logging.Formatter(
            '%(asctime)s, %(levelname)-4s %(funcName)s %(module)s --> %(message)s',
            '%d-%m-%Y:%H:%M:%S')  # set log format
    file_handler = logging.FileHandler(logger_file.as_posix())  # set the log file
    file_handler.setLevel(logging_level)  # set the level for file handler
    file_handler.setFormatter(formatter)  # set the formatter for file handler
    logger.addHandler(file_handler)
    return logger


def log_exception(exp):
    # create logger obj
    logger = setup_logging_to_file('errors')
    # first Extracts failing function name from Traceback
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][3]
    exc_type, exc_obj, exc_tb = sys.exc_info()
    # logger.error("{} {} {} ".format(exc_type, fname, exc_tb.tb_lineno))
    logger.error(f"{exp}", exc_info=True)
    # sys.stderr.errors("{} {} {} ".format(exc_type, fname, exc_tb.tb_lineno))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    # error_msg = str(exp) + " " + str(exc_tb.tb_lineno) + " " + str(fname)
    error_msg = str(exp)
    # sys.stderr.write(error_msg)
    # return error_msg


def log_info(msg):
    logger = setup_logging_to_file('info')
    logger.info(msg)
