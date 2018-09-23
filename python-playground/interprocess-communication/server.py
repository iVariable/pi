from multiprocessing.connection import Listener
import threading
import os
import time

address = "/tmp/socket_test.s"

try:
    os.unlink(address)
except OSError:
    if os.path.exists(address):
        raise


def heartbeat(conn, timer):
    try:
        while True:
            print("...sending heartbeat")
            conn.send("hello from server")
            time.sleep(timer)
    except Exception as e:
        print("Got exception...")
        print(e)
        print("...closing connection")
        conn.close()


listener = Listener(address)
try:

    print("Start listening for connections")
    while True:
        conn = listener.accept()
        print("Accepted new connection...")
        timer = int(conn.recv())
        threading.Thread(target=heartbeat, args=(conn, timer)).start()

except KeyboardInterrupt:
    listener.close()
    print("Done")
