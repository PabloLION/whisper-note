from datetime import datetime
from queue import Queue

TimedSampleQueue = Queue[tuple[datetime, bytes]]
