import os
from loguru import logger
# from notifiers.logging import NotificationHandler
# from dotenv import load_dotenv

from config import BOT_TOKEN


path_to_logs = fr"/root/BIK_monitoring/logs"
# path_to_logs = rf"C:\Users\User\PycharmProjects\BIK_monitoring\logs"

logger.add(f'{path_to_logs}/log.log', rotation='20 mb', level="DEBUG")
logger.add(f'{path_to_logs}/info.log', rotation='20 mb', level="INFO")
logger.add(f'{path_to_logs}/warning.log', rotation='10 mb', level="WARNING")
logger.add(f'{path_to_logs}/errors.log', rotation='10 mb', level="ERROR")
logger.add(f'{path_to_logs}/critical.log', rotation='10 mb', level="CRITICAL")


# load_dotenv()

params = {
    "token": BOT_TOKEN,
    "chat_id": 674796107,
}

# tg_handler = NotificationHandler(provider='telegram', defaults=params)
# logger.add(tg_handler, level='INFO')


if __name__ == "__main__":
    logger.debug("Уровень Debug")
    logger.info("Уровень Info")
    logger.warning("Уровень Warning")
    logger.error("Уровень Error")
    logger.critical("Уровень Critical Error")


