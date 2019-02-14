import json
import logging
from queue import Queue
from threading import Thread


class AdWriter(Thread):
    logger = logging.getLogger(__name__)

    def __init__(self, outfile, queue: Queue):
        # TODO: Check whether file exists, create or clear if needed
        super().__init__()
        self.__outfile = outfile
        self.__queue = queue

    @property
    def queue(self):
        return self.__queue

    def run(self):
        while True:
            item = self.__queue.get()
            if item is None:
                break
            self.logger.debug("Item written: %s", json.dumps(item, default=str))
            with open(self.__outfile, 'a') as of:
                json.dump(item, of, default=str)
                of.write('\n')
            self.__queue.task_done()

