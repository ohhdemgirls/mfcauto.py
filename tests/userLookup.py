import sys
sys.path.append('..')
from mfcauto import Client, STATE, FCLEVEL, Model
import asyncio

async def main(loop):
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
    except ValueError:
        pass

    print()
    print("Querying MFC for {}".format(idorname))
    client = Client(loop)
    await client.connect(False)
    msg = await client.query_user(idorname)
    client.disconnect()

    if msg == None:
        print("User not found")
    else:
        state_string = str(STATE(msg["vs"]))
        if msg["vs"] == STATE.Private.value:
            # If the model is in private, query her details to determine if it's a true private or not
            m = Model.get_model(msg["uid"])
            if m.in_true_private:
                state_string += " (True Private)"
            else:
                state_string += " (Regular Private)"

        print("""
          Name: {}
       User ID: {}
     User Type: {}
Current Status: {}
""".format(msg["nm"], msg["uid"], FCLEVEL(msg["lv"]), state_string))

        print("Raw response packet: {}".format(msg))
        print()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()