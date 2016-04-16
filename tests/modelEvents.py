import sys
sys.path.append('..')
from mfcauto import SimpleClient, Model, FCTYPE, STATE

def main():
    def do_stuff():
        # Get every model in free chat now, sorted by most popular room to least popular
        list = Model.find_models(lambda m: m.bestsession["vs"] == STATE.FreeChat.value)
        list.sort(key=lambda m: m.bestsession["rc"] if "rc" in m.bestsession else 0, reverse=True)
        print("Found {} online models".format(len(list)))
        #client.disconnect()

    client = SimpleClient()
    Model.All.on("vs", lambda m,before,after: print("{} is now in {}".format(m.nm, STATE(after))))

    client.on(FCTYPE.CLIENT_MODELSLOADED, do_stuff)

    client.connect()

if __name__ == '__main__':
    main()