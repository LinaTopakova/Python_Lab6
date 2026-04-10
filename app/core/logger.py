import logging
import sys

def setup_logger(name: str = "app") -> logging.Logger:
    """Настройка и возврат логгера."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Обработчик для вывода в консоль
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(handler)
    return logger

logger = setup_logger()