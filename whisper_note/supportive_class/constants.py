from datetime import datetime
import os
import logging
from time import sleep
from rich.logging import RichHandler

from queue import Queue
from tempfile import _TemporaryFileWrapper

WavTimeSizeQueue = Queue[tuple[_TemporaryFileWrapper, datetime, int]]

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
LOG = logging.getLogger("rich")

if __name__ == "__main__":
    LOG.debug("This is a debug message")
    LOG.info("This is an info message")
    LOG.warning("This is a warning message")
    LOG.error("This is an error message")
    LOG.critical("This is a critical message")
    LOG.log(25, "This is a custom at level 25")
    sleep(1)
    LOG.info("This is an info message")
    LOG.warning("This is a warning message")
    LOG.error("This is an error message")
