from tools.ls_tool import ListDirectoryTool
from tools.cat_tool import ReadFileTool


class ToolRegistry:

    def __init__(self, runner):

        self.tools = {
            "list_directory": ListDirectoryTool(runner),
            "read_file": ReadFileTool(runner)
        }

    def get(self, tool_name):

        return self.tools.get(tool_name)