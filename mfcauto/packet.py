import re
import html
from urllib.parse import unquote
from .constants import FCTYPE
from .model import Model

__all__ = ["Packet"]

emote_pattern = re.compile(r"#~(e|c|u|ue),(\w+)(\.?)(jpeg|jpg|gif|png)?,([\w\-\:\);\(\]\=\$\?\*]{0,48}),?(\d*),?(\d*)~#")

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
        self._pmessage = -1
        self._chat_string = -1
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
    def _parse_emotes(self, text):
        text = unquote(text)
        text = html.unescape(text)
        return emote_pattern.sub(r':\5',text)
    @property
    def pmessage(self):
        if self._pmessage == -1:
            if type(self.smessage) == dict and self.fctype in (FCTYPE.CMESG, FCTYPE.PMESG, FCTYPE.TOKENINC) and "msg" in self.smessage:
                self._pmessage = self._parse_emotes(self.smessage["msg"])
            else:
                self._pmessage = None
        return self._pmessage
    @property
    def chat_string(self):
        if self._chat_string == -1:
            if type(self.smessage) == dict:
                if self.fctype in (FCTYPE.CMESG, FCTYPE.PMESG):
                    self._chat_string = "{}: {}".format(self.smessage["nm"], self.pmessage)
                elif self.fctype == FCTYPE.TOKENINC:
                    self._chat_string = "{} has tipped {} {} tokens{}".format(self.smessage["u"][2], self.smessage["m"][2], self.smessage["tokens"], "." if self.pmessage is None else (": '" + self.pmessage + "'"))
            else:
                self._chat_string = None
        return self._chat_string
    def __repr__(self):
        return '{{"fctype": {}, "nfrom": {}, "nto": {}, "narg1": {}, "narg2": {}, "smessage": {}}}'.format(str(self.fctype)[7:], self.nfrom, self.nto, self.narg1, self.narg2, self.smessage)
    def __str__(self):
        return self.__repr__()
