### Fill in the following information before submitting
# Group id: 15
# Members: Minh Tan Do, Mark Rodriguez, Colin Damon



from collections import deque

# PID is just an integer, but it is used to make it clear when a integer is expected to be a valid PID.
PID = int

# This class represents the PCB of processes.
# It is only here for your convinience and can be modified however you see fit.
class PCB:
    pid: PID
    priority: int

    def __init__(self, pid: PID, priority: int):
        self.pid = pid
        self.priority = priority


# This class represents the Kernel of the simulation.
# The simulator will create an instance of this object and use it to respond to syscalls and interrupts.
# DO NOT modify the name of this class or remove it.
class Kernel:
    scheduling_algorithm: str
    ready_FCFS_queue: deque[PCB]
    ready_RR_queue: deque[PCB]
    waiting_queue: deque[PCB]
    running: PCB
    idle_pcb: PCB
    running_time: int
    foreground_mode: bool

    # Called before the simulation begins.
    # Use this method to initilize any variables you need throughout the simulation.
    # logger is provided which allows you to include your own print statements in the
    #   output logs. These will not impact grading. This can be done with its .log method
    #   which accepts a string.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def __init__(self, scheduling_algorithm: str, logger):
        self.scheduling_algorithm = scheduling_algorithm
        self.ready_FCFS_queue = deque()
        self.ready_RR_queue = deque()
        self.waiting_queue = deque()
        self.idle_pcb = PCB(0, 0)
        self.running = self.idle_pcb
        self.running_time = 0

    # This method is triggered every time a new process has arrived.
    # new_process is this process's PID.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def new_process_arrived(self, new_process: PID, priority: int, process_type: str) -> PID:
        if self.scheduling_algorithm == "FCFS":
            self.ready_FCFS_queue.append(PCB(new_process, priority))
        elif self.scheduling_algorithm == "RR":
            self.ready_RR_queue.append(PCB(new_process, priority))
        self.choose_next_process()
        return self.running.pid

    # This method is triggered every time the current process performs an exit syscall.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_exit(self) -> PID:
        self.running = self.idle_pcb
        self.running_time = 0
        self.choose_next_process()
        return self.running.pid
    
    # This method is triggered when the currently running process requests to change its priority.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_set_priority(self, new_priority: int) -> PID:
        self.running.priority = new_priority
        self.choose_next_process()
        return self.running.pid


    # This is where you can select the next process to run.
    # This method is not directly called by the simulator and is purely for your convinience.
    # Feel free to modify this method as you see fit.
    # It is not required to actually use this method but it is recommended.
    def choose_next_process(self):
        if self.scheduling_algorithm == "FCFS":
            if len(self.ready_FCFS_queue) == 0:
                return
            if self.running is self.idle_pcb:
                self.running = self.ready_FCFS_queue.popleft()
                self.running_time = 0
        elif self.scheduling_algorithm == "RR":
            if len(self.ready_RR_queue) == 0:
                return
            if self.running is self.idle_pcb:
                self.running = self.ready_RR_queue.popleft()
                self.running_time = 0
        else:
            print("Unknown scheduling algorithm")

    # This method represents the hardware timer interrupt.
    # It is triggered every 10 milliseconds and is the only way our kernel can track passing time.
    # Do not use real time to track how much time has passed as time is simulated.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def timer_interrupt(self) -> PID:
        # If CPU is idle, then do not count up process running time
        if self.running is self.idle_pcb:
            return self.running.pid
        
        self.running_time += 10
        if self.scheduling_algorithm == "RR":
            if self.running_time >= 40:
                self.running_time = 0
                # If there's a process in the ready_queue after the running process's quantum expires,
                # then context switch
                if self.ready_RR_queue:
                    self.ready_RR_queue.append(self.running)
                    self.running = self.ready_RR_queue.popleft()
        return self.running.pid
