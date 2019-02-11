from multiprocessing import Process, current_process
import os

# os.getpid() for the process id 

class ProcessManager:

    process_list = []

    def __init__(self):
        pass

    def add_process(self, input_process):
        argument = "test"
        process = Process(target=input_process, args=(argument,))
        process_list.append(process)
        # processes are spawned by creating a Process object and 
        # then calling its start() method
        process.start()
