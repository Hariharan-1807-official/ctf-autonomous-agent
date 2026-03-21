from tools.base_tool import BaseTool


class FindFileTool(BaseTool):
    name = "find_files"
    description = "Find all files including hidden ones in a directory. Use this when ls shows a directory to explore inside it."

    def __init__(self, runner):
        self.runner = runner

    def run(self, path="."):
        path = path.strip().strip('"').strip("'")
        return self.runner.run(f'find "{path}" -type f 2>/dev/null')