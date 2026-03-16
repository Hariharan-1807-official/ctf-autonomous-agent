from tools.base_tool import BaseTool


class ListDirectoryTool(BaseTool):

    name = "list_directory"
    description = "List all files and directories in the specified path (default: current directory). Shows permissions, owner and file size."

    def __init__(self, runner):
        self.runner = runner

    def run(self, path="."):

        command = f"ls -la {path}"

        return self.runner.run(command)