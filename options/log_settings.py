import logging
import logging.handlers
import os
import sys


def create_file_handler(file_full_name, level, formatter):
    if os.path.dirname(file_full_name):
        os.makedirs(os.path.dirname(file_full_name), exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(file_full_name,
                                                        maxBytes=10 * 1000 * 1000, backupCount=1000,
                                                        delay=True, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    return file_handler


def setup_logging(console_level, debug_file_path="debug.log", info_file_path="info.log") -> None:
    logging_format = '%(asctime)s %(levelname)5s %(name)s - %(message)s'

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(logging_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    root_logger.addHandler(create_file_handler(debug_file_path, logging.DEBUG, formatter))
    root_logger.addHandler(create_file_handler(info_file_path, logging.INFO, formatter))
