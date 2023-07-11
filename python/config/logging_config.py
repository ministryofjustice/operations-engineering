import os
import logging

LOGGING_LEVEL = ""

if (LOGGING_LEVEL := os.getenv('LOGGING_LEVEL')) not in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']:
    LOGGING_LEVEL = "INFO"

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=LOGGING_LEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
)
