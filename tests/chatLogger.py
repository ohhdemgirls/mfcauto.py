"""
Joins the two most popular rooms and logs only
chat and tip messages to the console.
"""

import sys
sys.path.append("..")
from mfcauto import SimpleClient, FCTYPE, Model, STATE, createLogger

def main():
    c = SimpleClient()

    loggers = dict()
    def on_connected():
        models = Model.find_models(lambda m: m.bestsession["vs"] == STATE.FreeChat.value)
        models.sort(key=lambda m: m.bestsession["rc"], reverse=True)
        for model in models[:2]:
            loggers[model.nm] = createLogger(model.nm)
            print("Joining {}'s room".format(model.nm))
            c.joinroom(model.uid)

    def on_chat(packet):
        if packet.chat_string != None:
            loggers[packet.aboutmodel.nm].info(packet.chat_string)

    c.on(FCTYPE.CMESG, on_chat)
    c.on(FCTYPE.TOKENINC, on_chat)
    c.on(FCTYPE.CLIENT_MODELSLOADED, on_connected)
    c.connect()

if __name__ == "__main__":
    main()