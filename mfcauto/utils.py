import sys
import logging

def createLogger(name, *, stdout=True, file=False):
    """Helper to create loggers from the logging
    module with some common predefines"""
    name = name.upper()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    #formatter = logging.Formatter('[%(asctime)s  %(name)s  %(levelname)s] %(message)s')
    if name == "MFCAUTO":
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
    else:
        formatter = logging.Formatter('[%(asctime)s, %(name)s] %(message)s')

    if stdout:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if file:
        fh = logging.FileHandler(name + ".log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

log = createLogger('mfcauto')

__all__ = ["createLogger", "log"]
