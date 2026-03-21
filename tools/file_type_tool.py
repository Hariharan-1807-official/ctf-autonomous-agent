from tools.base_tool import BaseTool


class FileTypeTool(BaseTool):
    name = "check_file_type"
    description = "Check file types in a directory to identify which files contain ASCII text vs binary data. Pass a directory path."

    def __init__(self, runner):
        self.runner = runner

    def run(self, path="."):
        path = path.strip().strip('"').strip("'")
        # Run file command on all files in the directory using find + xargs
        return self.runner.run(
            f'find "{path}" -maxdepth 1 -type f | xargs file 2>/dev/null'
        )