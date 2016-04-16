import sys
sys.path.append('..')
from mfcauto import SimpleClient, FCTYPE, STATE, FCLEVEL, Model

def main():
    if len(sys.argv) != 2:
        print('''
Queries MFC for a specific user's details

    Usage: {0} <username | userid>

    Examples:
        {0} AspenRae
        {0} 3111899
'''.format(sys.argv[0]))
        sys.exit(1)

    idorname = sys.argv[1]
    try:
        # If we were given an integer ID, look up by ID
        idorname = int(idorname)
        lookup = lambda: client.tx_cmd(FCTYPE.USERNAMELOOKUP, 0, 20, idorname, '')
    except ValueError:
        # If we were given a name instead, look up by name
        lookup = lambda: client.tx_cmd(FCTYPE.USERNAMELOOKUP, 0, 20, 0, idorname)

    print()
    print("Querying MFC for {}".format(idorname))
    client = SimpleClient()

    def state_string(uid, state):
        if state != STATE.Private:
            return str(state)
        else:
            # If the model is in private, query her details to determine if it's a true private or not
            m = Model.get_model(uid)
            if m.in_true_private:
                return str(state) + " (True Private)"
            else:
                return str(state) + " (Regular Private)"

    def handler(packet):
        if type(packet.smessage) == dict:
            print("""
          Name: {}
       User ID: {}
     User Type: {}
Current Status: {}
""".format(packet.smessage["nm"], packet.smessage["uid"], FCLEVEL(packet.smessage["lv"]), state_string(int(packet.smessage["uid"]), STATE(packet.smessage["vs"]))))
        else:
            print("\nUser not found\n")
        print("Raw response packet: {}".format(packet))
        print()
        client.disconnect()

    client.on(FCTYPE.USERNAMELOOKUP, handler)
    client.on(FCTYPE.CLIENT_CONNECTED, lookup)

    client.connect(False)

if __name__ == '__main__':
    main()