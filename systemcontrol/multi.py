import os
import time
from time import sleep
from multiprocessing import Process

def script1():
    os.system('python3 /home/pi/recording.py &')

def script2():
    os.system('python3 /home/pi/netmodule.py &')

if __name__ =='__main__':
    p = Process(target = script1)
    q = Process(target = script2)
    p.start()
    sleep(10)
    q.start()
    p.join()
    q.join()

