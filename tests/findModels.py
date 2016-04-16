import sys
sys.path.append('..')
from mfcauto import SimpleClient, Model, FCTYPE

def main():
    def query():
        list = Model.find_models(lambda m: "age" in m.bestsession and m.bestsession["age"] < 24)
        print("Found {} models claiming to be under 24 years old".format(len(list)))
        client.disconnect()

    client = SimpleClient()
    client.on(FCTYPE.CLIENT_MODELSLOADED, query)

    client.connect()

if __name__ == '__main__':
    main()