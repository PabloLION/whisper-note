from datetime import datetime
import os

from queue import Queue
from tempfile import _TemporaryFileWrapper

WavTimeSizeQueue = Queue[tuple[_TemporaryFileWrapper, datetime, int]]
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"
