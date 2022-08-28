import queue


class MessageQueue:
    def __init__(self):
        self.queue = queue.Queue()

    def get(self, block=True):
        return self.queue.get(block)

    def put(self, mes):
        self.queue.put(mes)

    def task_done(self):
        self.queue.task_done()

    def num_of_mes(self):
        return self.queue.qsize()

    def join(self):
        self.queue.join()
