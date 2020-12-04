import logging
import logging.handlers
import os.path
import sys
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from types import TracebackType
from typing import Union, Tuple, Optional

CWD = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(CWD, 'bot.log')

LOG_FILE_FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
MAX_BYTES = 10 * 1024 * 1024
LOG_CONSOLE_FORMAT = '%(asctime)s - [%(levelname)s] %(message)s'

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter(LOG_CONSOLE_FORMAT)
console_handler.setFormatter(console_formatter)

file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=2)
file_formatter = logging.Formatter(LOG_FILE_FORMAT)
file_handler.setFormatter(file_formatter)

_logger.addHandler(console_handler)
_logger.addHandler(file_handler)


@dataclass
class Log:
    level: int
    message: str
    exc_info: Union[None, bool, Tuple[type, BaseException, Optional[TracebackType]]]


class Logger(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.logs = Queue()
        self._running = True

    def run(self):
        while self._running or not self.logs.empty():
            self._process_logs()

    def join(self, timeout=None):
        self._running = False

    def info(self, message):
        self._log(logging.INFO, message)

    def warning(self, message):
        self._log(logging.WARNING, message)

    def exception(self, message, exc_info):
        self._log(logging.ERROR, message, exc_info)

    def fatal(self, message, exc_info):
        self._log(logging.FATAL, message, exc_info)

    def _log(self, level, message, exc_info=None):
        log = Log(level, message, exc_info)
        self.logs.put(log)

    def _process_logs(self, timeout=2.0):
        try:
            log = self.logs.get(block=True, timeout=timeout)
            _logger.log(log.level, log.message, exc_info=log.exc_info)
        except:
            return
