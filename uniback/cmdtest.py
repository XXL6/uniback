import subprocess
import time
import functools
import os
from uniback.tools.progress_tools import Progress
#from pywin32 import O_NONBLOCK, F_GETFL, F_SETFL
#import pywin32
def execute():
    start = time.clock()
    server = subprocess.Popen(
            ['robocopy', 'C:\\Users\\topst\\Downloads\\test', 'D:\\Temp'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    progress = Progress()
    progress.set_regex(('(?<=\r ).*(?=%)'))
    while server.poll() is None:
        #print(os.read(server.stdout.fileno(), 128))
        #time.sleep(0.1)
        #i += 1
        print(progress.parse_progress(os.read(server.stdout.fileno(), 64).decode('utf-8')))
        print(progress.get_current_progress())
        #print(server.stdout.read())
    print(time.clock() - start)
    #flags = pywin32(server.stdout, pywin32.F_GETFL)
    #pywin32(server.stdout, pywin32.F_SETFL, flags | pywin32.O_NONBLOCK)
    #while True:
    #    print(os.read(server.stdout.fileno(), 1024))
    # flags = functools(out.stdout, functools.F_GETFL)
    # functools(out.stdout, functools.F_SETFL, flags | os.O_NONBLOCK)
    # while out.poll() is None:
    #    print(os.read(out.stdout.fileno(), 1024))
#    for stdout in iter(server.stdout.read, b''):
#        if b"C:\\Users\\tops" in stdout:
#            print("entered if statement")
#        print(stdout)
