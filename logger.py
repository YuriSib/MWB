import logging


logging.basicConfig(level=logging.DEBUG, filename='my_logging.log',
                    format='%(levelname)s - (%(asctime)s) - %(message)s (Line: %(lineno)d) - [%(filename)s]',
                    datefmt="%d/%m/%Y %I:%M:%S", encoding="utf-8", filemode="w")

logging.debug("Debug")
logging.info("Info")
logging.warning("Warning")
logging.error("Error")
logging.critical("Critical")

try:
    10/1
except Exception as E:
    logging.exception(E)

logger = logging.getLogger("test")
handler = logging.FileHandler('../test.log', encoding='utf-8')
formatter = logging.Formatter('%(levelname)s - (%(asctime)s) - %(message)s (Line: %(lineno)d) - [%(filename)s]')
handler.setFormatter(formatter)
logger.addHandler(handler)

cycle_logger = logging.getLogger('cycle')
cycle_handler = logging.FileHandler('../история циклов.log', encoding='utf-8')
cycle_formatter = logging.Formatter('%(levelname)s - (%(asctime)s) - %(message)s (Line: %(lineno)d)')
cycle_handler.setFormatter(cycle_formatter)
cycle_logger.addHandler(cycle_handler)

product_logger = logging.getLogger('product')
product_handler = logging.FileHandler('../product.log', encoding='utf-8')
product_formatter = logging.Formatter('%(levelname)s - (%(asctime)s) - %(message)s')
product_handler.setFormatter(product_formatter)
product_logger.addHandler(product_handler)

user_logger = logging.getLogger('users')
user_handler = logging.FileHandler('../product.log', encoding='utf-8')
user_formatter = logging.Formatter('%(levelname)s - (%(asctime)s) - %(message)s')
user_handler.setFormatter(user_formatter)
user_logger.addHandler(user_handler)
