from datetime import datetime
import os
import logging
from time import sleep
from rich.logging import RichHandler

from queue import Queue
from tempfile import _TemporaryFileWrapper

WavTimeSizeQueue = Queue[tuple[_TemporaryFileWrapper, datetime, int]]
CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")

if __name__ == "__main__":
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
    log.log(25, "This is a custom at level 25")
    sleep(1)
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
