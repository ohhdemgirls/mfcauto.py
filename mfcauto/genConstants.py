import re
from urllib.request import urlopen
url = "http://www.myfreecams.com/_js/mfccore.js"
# Maybe it's wrong to merge in the w. stuff?  Is that all just for the UI?
constantRe = re.compile(r'(\s|;?|,)(FCS|w)\.([A-Z0-9]+)_([A-Z0-9_]+)\s+?=\s+?([0-9]+);')
constantMap = dict()

header = """#Various constants and enums used by MFC.  Most of these values can be seen here:
#http:#www.myfreecams.com/_js/mfccore.js
from enum import Enum
MAGIC = -2027771214;

#STATE is essentially the same as FCVIDEO but has friendly names
#for better log messages and code readability
class STATE(Enum):
    FreeChat = 0            #TX_IDLE
    #TX_RESET = 1           #Unused?
    Away = 2                #TX_AWAY
    #TX_CONFIRMING = 11     #Unused?
    Private = 12            #TX_PVT
    GroupShow = 13          #TX_GRP
    #TX_RESERVED = 14       #Unused?
    #TX_KILLMODEL = 15      #Unused?
    #C2C_ON = 20            #Unused?
    #C2C_OFF = 21           #Unused?
    Online = 90             #RX_IDLE
    #RX_PVT = 91            #Unused?
    #RX_VOY = 92            #Unused?
    #RX_GRP = 93            #Unused?
    #NULL = 126             #Unused?
    Offline = 127           #OFFLINE
"""

#Add our own constants...
constantMap.setdefault("FCTYPE", dict())["CLIENT_MODELSLOADED"] = -4
constantMap.setdefault("FCTYPE", dict())["CLIENT_CONNECTED"] = -3
constantMap.setdefault("FCTYPE", dict())["ANY"] = -2
constantMap.setdefault("FCTYPE", dict())["UNKNOWN"] = -1

with urlopen(url) as data:
    scriptText = data.read().decode('utf-8')

    result = constantRe.findall(scriptText)
    for (prefix1, prefix2, fctype, subtype, num) in result:
        constantMap.setdefault(fctype, dict())[subtype] = num

    with open("constants.py", "w") as f:
        f.write(header)
        for fctype in sorted(constantMap):
            f.write("\nclass {}(Enum):\n".format(fctype))
            for subtype, value in sorted(constantMap[fctype].items(), key=lambda x: int(x[1])):
                f.write("    {} = {}\n".format(subtype.replace("60DAY","SIXTYDAY"), value))
            #f.write("\n")
        f.write("\n")

print("Done")