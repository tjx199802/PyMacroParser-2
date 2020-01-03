import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test/log.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s\n%(message)s', datefmt='%Y-%m-%d %H:%M')
handler.setFormatter(formatter)
logger.addHandler(handler)
