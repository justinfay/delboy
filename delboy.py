from collections import namedtuple
from functools import partial
import urllib.request
import sched
import time


Ad = namedtuple('Ad', 'url title price')


def get_body(url, ignore_exceptions=True):
    """
    Return the content of a web request.
    """
    try:
        return urllib.request.urlopen(url).read()
    except Exception as e:
        if ignore_exceptions:
            return None
        raise e


class Scheduler:
    """
    A wrapper around a scheduler class providing
    a simple API for recurring events.
    """

    def __init__(self, scheduler=None):
        if scheduler is None:
            scheduler = sched.scheduler(time.time, time.sleep)
        self._scheduler = scheduler
        self._recurring = dict()

    def schedule(self, delay, func, recurring=False):
        """
        Schedule a callable to be executed after `delay`.
        If recurring is `True` the event is repeated.
        To pass arguments to `func` use `functools.partial`.
        """
        if recurring:
            schedule = partial(
                self.schedule, delay, func, recurring=True)
            event = self._scheduler.enter(delay, 1, schedule)
            self._recurring[event.action] = event
        self._scheduler.enter(delay, 1, func)

    def stop(self):
        """
        Cancel any recurring events.
        """
        while self._recurring:
            try:
                self._scheduler.cancel(self._recurring.popitem()[1])
            except ValueError:
                # Event has already executed.
                continue

    def start(self):
        """
        Start scheduled event execution.
        """
        self._scheduler.run(blocking=True)


if __name__ == "__main__":
    ss = Scheduler()
    ss.schedule(1, partial(print, 'foo'), recurring=True)
    try:
        ss.start()
    except KeyboardInterrupt:
        ss.stop()
