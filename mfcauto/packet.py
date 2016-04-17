from .constants import FCTYPE
from .model import Model

__all__ = ["Packet"]

class Packet:
    def __init__(self, fctype, nfrom, nto, narg1, narg2, smessage = None):
        self.fctype = FCTYPE(fctype)
        self.nfrom = nfrom
        self.nto = nto
        self.narg1 = narg1
        self.narg2 = narg2
        self.smessage = smessage
        self._flatdict = None
        self._aboutModel = None
    @property
    def aboutmodel(self):
        if self._aboutModel == None:
            mid = -1
            if self.fctype in (FCTYPE.ADDFRIEND, FCTYPE.ADDIGNORE, FCTYPE.JOINCHAN, FCTYPE.STATUS, FCTYPE.CHATFLASH, FCTYPE.BROADCASTPROFILE):
                mid = self.narg1
            elif self.fctype in (FCTYPE.SESSIONSTATE, FCTYPE.LISTCHAN):
                mid = self.narg2
            elif self.fctype in (FCTYPE.USERNAMELOOKUP, FCTYPE.NEWSITEM, FCTYPE.PMESG):
                mid = self.nfrom
            elif self.fctype in (FCTYPE.GUESTCOUNT, FCTYPE.TOKENINC, FCTYPE.CMESG):
                mid = self.nto
            elif self.fctype == FCTYPE.ROOMDATA:
                if type(self.smessage) == dict and "model" in self.smessage:
                    mid = self.smessage["model"]
            elif self.fctype in (FCTYPE.LOGIN, FCTYPE.MODELGROUP, FCTYPE.PRIVACY, FCTYPE.DETAILS, FCTYPE.METRICS, FCTYPE.UEOPT, FCTYPE.SLAVEVSHARE, FCTYPE.INBOX, FCTYPE.EXTDATA, FCTYPE.MYWEBCAM, FCTYPE.TAGS, FCTYPE.NULL):
                mid = -1
            if mid > 100000000:
                mid = mid - 100000000
            self._aboutModel = Model.get_model(mid)
        return self._aboutModel
    #@TODO - chatstring and all that other stuff that Packet.js does...
    def __repr__(self):
        return '{{"fctype": {}, "nfrom": {}, "nto": {}, "narg1": {}, "narg2": {}, "smessage": {}}}'.format(str(self.fctype)[7:], self.nfrom, self.nto, self.narg1, self.narg2, self.smessage)
    def __str__(self):
        return self.__repr__()
