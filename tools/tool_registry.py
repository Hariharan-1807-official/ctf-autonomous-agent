from tools.ls_tool import ListDirectoryTool
from tools.cat_tool import ReadFileTool
from tools.find_tool import FindFileTool


class ToolRegistry:
    def __init__(self, runner):
        self.tools = {
            "list_directory": ListDirectoryTool(runner),
            "read_file": ReadFileTool(runner),
            "find_files": FindFileTool(runner),
        }

    def get(self, name):
        return self.tools.get(name)