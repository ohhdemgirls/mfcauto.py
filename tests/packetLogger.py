"""
Connects to MFC as a guest, joins the two most popular rooms
and logs every received message to the console.
"""

# If you get a strange 'charmap' error on Windows...
# Run 'chcp 65001' to change the console code page to print everything
# 437 was the default when I first ran it.  See here for more info:
# https://stackoverflow.com/questions/14284269/why-doesnt-python-recognize-my-utf-8-encoded-source-file/14284404#14284404

import sys
sys.path.append("..")
from mfcauto import SimpleClient, FCTYPE, Model, STATE

if __name__ == "__main__":
    c = SimpleClient()

    def on_connected():
        models = Model.find_models(lambda m: m.bestsession["vs"] == STATE.FreeChat.value)
        models.sort(key=lambda m: m.bestsession["rc"], reverse=True)
        for model in models[:2]:
            print("Joining {}'s room".format(model.nm))
            c.joinroom(model.uid)

    c.on(FCTYPE.ANY, lambda p: print(p))
    c.on(FCTYPE.CLIENT_MODELSLOADED, on_connected)
    c.connect()
