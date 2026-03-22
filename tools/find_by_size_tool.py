from tools.base_tool import BaseTool


class FindBySizeTool(BaseTool):
    name = "find_by_properties"
    description = "Find files matching specific properties like size. Use when you need to filter files by size (in bytes or kilobytes), type, or permissions. Example args: 'inhere -size 1033c' finds files exactly 1033 bytes."

    def __init__(self, runner):
        self.runner = runner

    def run(self, args="."):
        args = args.strip().strip('"').strip("'")
        return self.runner.run(f'find {args} -type f 2>/dev/null')