from utils.logger import logger
from typing import Any


class BaseTool:

    name = "base_tool"
    description = "Base tool"

    def run(self, *args, **kwargs) -> str:

        logger.error(f"Tool {self.name} not implemented")

        raise NotImplementedError(f"{self.name}.run() not implemented")