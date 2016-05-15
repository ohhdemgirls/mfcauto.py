"""Tools for handling network communication with MFC chat servers"""
import sys
import urllib.request
import json
import asyncio
import random
import struct
import traceback
from threading import RLock
from .event_emitter import EventEmitter
from .packet import Packet
from .constants import MAGIC, FCTYPE, FCCHAN
from .model import Model
from .utils import log

__all__ = ['Client', 'SimpleClient']

class MFCProtocol(asyncio.Protocol):
    """asyncio.Protocol handler for MFC"""
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.buffer = b""
    def connection_lost(self, exc):
        self.client._disconnected()
        # if exc is None:
        #     # We lost our connection, but there was no exception.
        #     # Someone called client.disconnect()?
        #     pass
        # else:
        #     # There was an exception for abnormal termination...
        #     pass
    def data_received(self, data):
        self.buffer += data
        while True:
            try:
                pformat = ">iiiiiii"
                packet_size = struct.calcsize(pformat)
                if len(self.buffer) < packet_size:
                    break

                #unpacked_data looks like this: (magic, fctype, nfrom, nto, narg1, narg2, spayload)
                unpacked_data = struct.unpack(pformat, self.buffer[:packet_size])
                assert unpacked_data[0] == MAGIC
                spayload = unpacked_data[6]
                smessage = None
                if spayload > 0:
                    if len(self.buffer) < (packet_size+spayload):
                        break
                    smessage = struct.unpack("{}s".format(spayload), self.buffer[packet_size:packet_size+spayload])
                    smessage = smessage[0].decode('utf-8')
                    try:
                        smessage = json.loads(smessage)
                    except json.decoder.JSONDecodeError:
                        pass

                self.buffer = self.buffer[packet_size+spayload:]
                self.client.packet_received(Packet(*unpacked_data[1:-1], smessage))
            except:
                ex = sys.exc_info()[0]
                log.critical("Unexpected exception: {}\n{}".format(ex, traceback.format_exc()))
                self.loop.stop()
                break

class Client(EventEmitter):
    """An MFC Client object"""
    userQueryLock = RLock()
    userQueryId = 20
    def __init__(self, loop, username='guest', password='guest'):
        self.loop = loop
        self.username = username
        self.password = password
        self.server_config = None
        self.transport = None
        self.protocol = None
        self.session_id = 0
        self.loop = asyncio.get_event_loop()
        self.keepalive = None
        self._completedModels = False
        self._completedFriends = True
        self.uid = None
        self._manual_disconnect = False
        self._logged_in = False
        super().__init__()
    def packet_received(self, packet):
        log.debug(packet)
        self._process_packet(packet)
        self.emit(packet.fctype, packet)
        self.emit(FCTYPE.ANY, packet)
    def _process_packet(self, packet):
        """Merges the given packet into our global state @TODO - Not sure if this should really be a separate function from packet_received"""
        fctype = packet.fctype
        if fctype == FCTYPE.LOGIN:
            if packet.narg1 != 0:
                log.info("Login failed for user '{}' password '{}'".format(self.username, self.password))
                raise Exception("Login failed")
            else:
                self.session_id = packet.nto
                self.uid = packet.narg2
                self.username = packet.smessage
                log.info("Login handshake completed. Logged in as '{}' with sessionId {}".format(self.username, self.session_id))
        elif fctype in (FCTYPE.DETAILS, FCTYPE.ROOMHELPER, FCTYPE.SESSIONSTATE, FCTYPE.ADDFRIEND, FCTYPE.ADDIGNORE, FCTYPE.CMESG, FCTYPE.PMESG, FCTYPE.TXPROFILE, FCTYPE.USERNAMELOOKUP, FCTYPE.MYCAMSTATE, FCTYPE.MYWEBCAM):
            if not ((fctype == FCTYPE.DETAILS and packet.nfrom == FCTYPE.TOKENINC) or (fctype == FCTYPE.ROOMHELPER and packet.narg2 < 100) or (fctype == FCTYPE.JOINCHAN and packet.narg2 == FCCHAN.PART)):
                if type(packet.smessage) == dict:
                    lv = packet.smessage.setdefault("lv",None)
                    uid = packet.smessage.setdefault("uid",None)
                    if uid is None:
                        uid = packet.aboutmodel.uid
                    if uid != None and uid != -1 and (lv != None or lv == 4):
                        possiblemodel = Model.get_model(uid, lv == 4)
                        if possiblemodel != None:
                            possiblemodel.mergepacket(packet)
        elif fctype == FCTYPE.TAGS:
            if type(packet.smessage) == dict:
                #Sometimes TAGS are so long that they're malformed JSON.
                #For now, just ignore those cases.
                for key in packet.smessage:
                    Model.get_model(key).mergepacket(packet)
        elif fctype == FCTYPE.BOOKMARKS:
            #@TODO - Merge this too
            pass
        elif fctype == FCTYPE.METRICS:
            if not (self._completedFriends and self._completedModels):
                if packet.nto == 2:
                    if packet.narg1 != packet.narg2:
                        self._completedFriends = False
                    else:
                        self._completedFriends = True
                if packet.nto == 20 and packet.narg1 == packet.narg2:
                    self._completedModels = True
                if self._completedModels and self._completedFriends:
                    self.emit(FCTYPE.CLIENT_MODELSLOADED)
    def _get_servers(self):
        if self.server_config is None:
            with urllib.request.urlopen('http://www.myfreecams.com/_js/serverconfig.js') as req:
                self.server_config = json.loads(req.read().decode('utf-8'))
    def _ping_loop(self):
        self.tx_cmd(FCTYPE.NULL, 0, 0, 0)
        self.keepalive = self.loop.call_later(120, self._ping_loop)
    async def connect(self, login=True):
        """Connects to an MFC chat server and optionally logs in"""
        self._get_servers()
        selected_server = random.choice(self.server_config['chat_servers'])
        self._logged_in = login
        log.info("Connecting to MyFreeCams chat server {}...".format(selected_server))
        (self.transport, self.protocol) = await self.loop.create_connection(lambda: MFCProtocol(self.loop, self), '{}.myfreecams.com'.format(selected_server), 8100)
        if login:
            self.tx_cmd(FCTYPE.LOGIN, 0, 20071025, 0, "{}:{}".format(self.username, self.password))
            if self.keepalive is None:
                self.keepalive = self.loop.call_later(120, self._ping_loop)
        self.loop.call_soon(self.emit,FCTYPE.CLIENT_CONNECTED)
    def disconnect(self):
        """Disconnects from the MFC chat server and closes the underlying transport"""
        if self.keepalive != None:
            self.keepalive.cancel()
            self.keepalive = None
        self._manual_disconnect = True
        self.transport.close()
    def _disconnected(self):
        """Handles disconnect events from the underlying MFCProtocol instance, reconnecting as needed"""
        if not self._manual_disconnect:
            print("Disconnected from MyFreeCams.  Reconnecting in 30 seconds...")
            self.loop.call_later(30, self.connect, self._logged_in)
        else:
            self.loop.stop()
        self._manual_disconnect = False
        self.emit(FCTYPE.CLIENT_DISCONNECTED)
        Model.reset_all()
    def tx_cmd(self, fctype, nto, narg1, narg2, smsg=''):
        """Transmits a command back to the connected MFC chat server"""
        if type(fctype) != FCTYPE:
            raise Exception("Please provide a valid FCTYPE")
        if smsg is None:
            smsg = ''
        data = struct.pack(">iiiiiii{}s".format(len(smsg)), MAGIC, fctype.value, self.session_id, nto, narg1, narg2, len(smsg), smsg.encode())
        log.debug("TxCmd sending: {}".format(data))
        self.transport.write(data)
    def tx_packet(self, packet):
        self.tx_cmd(packet.fctype, packet.nto, packet.narg1, packet.narg2, packet.smessage)
    @staticmethod
    def touserid(uid):
        if uid > 100000000:
            uid = uid - 100000000
        return uid
    @staticmethod
    def toroomid(the_id):
        if the_id < 100000000:
            the_id = the_id + 100000000
        return the_id
    def sendchat(self, the_id, msg):
        the_id = Client.toroomid(the_id)
        self.tx_cmd(FCTYPE.CMESG, the_id, 0, 0, msg)
        #@TODO - Emote encoding
    def sendpm(self, the_id, msg):
        the_id = Client.touserid(the_id)
        self.tx_cmd(FCTYPE.PMESG, the_id, 0, 0, msg)
        #@TODO - Emote encoding
    def joinroom(self, the_id):
        the_id = Client.toroomid(the_id)
        self.tx_cmd(FCTYPE.JOINCHAN, 0, the_id, FCCHAN.JOIN.value)
    def leaveroom(self, the_id):
        the_id = Client.toroomid(the_id)
        self.tx_cmd(FCTYPE.JOINCHAN, 0, the_id, FCCHAN.PART.value)
    def query_user(self, user): #Untested, @TODO
        with Client.userQueryLock:
            future = asyncio.Future()
            queryId = Client.userQueryId
            Client.userQueryId += 1
            def handler(p):
                if p.narg1 == queryId:
                    self.remove_listener(FCTYPE.USERNAMELOOKUP, handler)
                    if (not hasattr(p, "smessage")) or not isinstance(p.smessage,dict):
                        future.set_result(None) # User doesn't exist
                    else:
                        future.set_result(p.smessage)
            self.on(FCTYPE.USERNAMELOOKUP, handler);
            if isinstance(user, int):
                self.tx_cmd(FCTYPE.USERNAMELOOKUP, 0, queryId, user)
            elif isinstance(user, str):
                self.tx_cmd(FCTYPE.USERNAMELOOKUP, 0, queryId, 0, user)
            else:
                raise Exception("Invalid Argument")
            return future

class SimpleClient(Client):
    """An MFC Client object that maintains its own default event loop"""
    def __init__(self, username='guest', password='guest'):
        super().__init__(asyncio.get_event_loop(), username, password)
    def connect(self, login=True):
        """A blocking call that connects to MFC and begins processing the event loop"""
        self.loop.run_until_complete(super().connect(login))
        self.loop.run_forever()
        self.loop.close()
