import logging
import sys
from datetime import datetime, timezone

class CustomFormatter(logging.Formatter):
    """
    Custom log formatter that produces clean, readable log lines.
   
    Log levels explained:
    - DEBUG:    Detailed info for diagnosing problems
    - INFO:     Confirmation that things are working
    - WARNING:  Something unexpected, but the app still works
    - ERROR:    Something failed, a specific operation didn't complete
    - CRITICAL: The app itself might be broken
    """

    def format(self, record):
        #add timestamp in UTC
        record.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return super().format(record)
    
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # format: timestamp | level | module | message
        formatter = CustomFormatter(
            "%(timestamp)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler("app.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger