import logging
import threading
import uuid

from ajenti.api import *


@interface
class Task (object):
    name = '---'
    ui = None

    def __init__(self, **kwargs):
        self.params = kwargs

    def init(self):
        self._progress = 0
        self._progress_max = 1
        self.running = False
        self.complete = False
        self.aborted = False

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        logging.info('Starting task %s' % self.__class__.__name__)
        self.running = True
        self.run()
        self.running = False
        self.complete = True 
        logging.info('Task %s complete' % self.__class__.__name__)

    def run():
        pass

    def abort(self):
        if not self.running:
            return
        self.aborted = True
        self.thread.join()
        
    def set_progress(self, current, max):
        self._progress, self._progress_max = current, max

    def get_progress(self):
        return self._progress, self._progress_max


class TaskDefinition (object):
    def __init__(self, j={}, task_class=None):
        self.name = j.get('name', 'unnamed')
        self.task_class = j.get('task_class', task_class)
        self.params = j.get('params', self.get_class().default_params if self.get_class() else {})
        self.id = j.get('id', str(uuid.uuid4()))

    def get_class(self):
        for task in Task.get_classes():
            if task.classname == self.task_class:
                return task

    def save(self):
        return {
            'name': self.name,
            'task_class': self.task_class,
            'params': self.params,
            'id': self.id,
        }


class JobDefinition (object):
    def __init__(self, j={}):
        self.name = j.get('name', 'unnamed')
        self.task_id = j.get('task_id', None)
        self.id = j.get('id', str(uuid.uuid4()))
        self.schedule_special = j.get('schedule_special', None)
        self.schedule_minute = j.get('schedule_minute', '0')
        for _ in ['hour', 'day_of_month', 'month', 'day_of_week']:
            setattr(self, 'schedule_' + _, j.get('schedule_' + _, '*'))

    def save(self):
        return {
            'name': self.name,
            'task_id': self.task_id,
            'id': self.id,
            'schedule_special': self.schedule_special,
            'schedule_minute': self.schedule_minute,
            'schedule_hour': self.schedule_hour,
            'schedule_day_of_month': self.schedule_day_of_month,
            'schedule_month': self.schedule_month,
            'schedule_day_of_week': self.schedule_day_of_week,
        }
