from loguru import logger
from conf.config import LOG_PATH

logger.add(LOG_PATH,
           level='INFO',
           # format='{level} - {file} - {line} -> {message}',
           format='{message}',
           rotation="10 MB",
           encoding='utf-8')


def log(output_item):
    logger.info(output_item)
