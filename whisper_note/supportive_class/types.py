from datetime import datetime
from queue import Queue
from tempfile import _TemporaryFileWrapper

WavTimeSizeQueue = Queue[tuple[_TemporaryFileWrapper, datetime, int]]
