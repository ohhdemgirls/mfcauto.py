"""mfcauto - Communicates with MFC chat servers"""
from .client import Client, SimpleClient
from .model import Model
from .packet import Packet
from .constants import *
from .utils import createLogger, log
__version__ = '0.1.0'
__author__ = 'ZombieAlex <zombiealex69@gmail.com>'
__all__ = ["Client", "SimpleClient", "Model", "Packet", "constants"]