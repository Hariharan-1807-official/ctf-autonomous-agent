from core.controller import Controller
from utils.logger import logger


def main():
    logger.info("Starting CTF Autonomous Agent")

    controller = Controller()
    controller.run()


if __name__ == "__main__":
    main()