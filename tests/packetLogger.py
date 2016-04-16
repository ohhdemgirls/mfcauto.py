"""
Connects to MFC as a guest and logs every received
message to the console.
"""

# If you get a strange 'charmap' error on Windows...
# Run 'chcp 65001' to change the console code page to print everything
# 437 was the default when I first ran it.  See here for more info:
# https://stackoverflow.com/questions/14284269/why-doesnt-python-recognize-my-utf-8-encoded-source-file/14284404#14284404

import sys
sys.path.append("..")
from mfcauto import SimpleClient, FCTYPE

if __name__ == "__main__":
    c = SimpleClient()
    c.on(FCTYPE.ANY, lambda p: print(p))
    c.connect()
