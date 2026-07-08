import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers.clear()

current_dir = os.path.dirname(__file__)
log_dir = os.path.abspath(os.path.join(current_dir, '..', 'logs'))
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'logs.log')
handler = logging.FileHandler(filename=log_file,
                              mode="a",
                              encoding='utf-8'
                              )
handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)
logger.addHandler(handler)