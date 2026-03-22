from tools.ls_tool import ListDirectoryTool
from tools.cat_tool import ReadFileTool
from tools.find_tool import FindFileTool
from tools.file_type_tool import FileTypeTool
from tools.find_by_size_tool import FindBySizeTool
from tools.run_command_tool import RunCommandTool


class ToolRegistry:
    def __init__(self, runner):
        self.tools = {
            "list_directory": ListDirectoryTool(runner),
            "read_file": ReadFileTool(runner),
            "find_files": FindFileTool(runner),
            "check_file_type": FileTypeTool(runner),
            "find_by_properties": FindBySizeTool(runner),
            "run_command": RunCommandTool(runner),
        }

    def get(self, name):
        return self.tools.get(name)