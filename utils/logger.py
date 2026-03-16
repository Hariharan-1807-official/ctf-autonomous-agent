import logging
from rich.logging import RichHandler


def get_logger():

    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        handlers=[RichHandler()]
    )

    return logging.getLogger("ctf-agent")


logger = get_logger()