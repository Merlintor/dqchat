import logging


log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("dqchat.log")
fileHandler.setFormatter(log_formatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter("%(message)s"))
consoleHandler.setLevel(logging.INFO)
logger.addHandler(consoleHandler)
