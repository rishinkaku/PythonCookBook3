# Code to execute in an independent thread
# IO heavy work
import time


def countdown(n):
    while n > 0:
        print('T-minus', n)
        n -= 1
        time.sleep(5)


# Create and launch a thread
from threading import Thread

t = Thread(target=countdown, args=(10,))
t.start()

if t.is_alive():
    print('Still running')
else:
    print('Completed')


# t.join()
# wait until t ends

# can't send signal to end t
class CountdownTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, n):
        while self._running and n > 0:
            print('T-minus', n)
            n -= 1
            time.sleep(5)

    c = CountdownTask()
    t = Thread(target=c.run, args=(10,))
    t.start()
    c.terminate()  # Signal termination
    t.join()  # Wait for actual termination (if needed)


class IOTask:
    def terminate(self):
        self._running = False

    def run(self, sock):
        # sock is a socket
        sock.settimeout(5)  # Set timeout period
        while self._running:
            # Perform a blocking I/O operation w/ timeout
            try:
                data = sock.recv(8192)
                break
            except socket.timeout:
                continue
        # Continued processing
        # Terminated
        return


# for threading
from threading import Thread


class CountdownThread(Thread):
    def __init__(self, n):
        super().__init__()
        self.n = 0

    def run(self):
        while self.n > 0:
            print('T-minus', self.n)
            self.n -= 1
            time.sleep(5)


c = CountdownThread(5)
c.start()

import multiprocessing

c = CountdownTask()
p = multiprocessing.Process(target=c.run)
p.start()
