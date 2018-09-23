import argparse
from multiprocessing.connection import Client

address = "/tmp/socket_test.s"


parser = argparse.ArgumentParser()
parser.add_argument('timer')
args = parser.parse_args()

client = Client(address)

try:
    client.send(args.timer)
    while True:
        data = client.recv()
        print(data)

except KeyboardInterrupt:
    client.close()
    print("Done")
