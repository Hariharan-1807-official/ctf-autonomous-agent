from tools.ls_tool import ListDirectoryTool
from tools.cat_tool import ReadFileTool
from tools.find_tool import FindFileTool
from tools.file_type_tool import FileTypeTool


class ToolRegistry:
    def __init__(self, runner):
        self.tools = {
            "list_directory": ListDirectoryTool(runner),
            "read_file": ReadFileTool(runner),
            "find_files": FindFileTool(runner),
            "check_file_type": FileTypeTool(runner),
        }

    def get(self, name):
        return self.tools.get(name)