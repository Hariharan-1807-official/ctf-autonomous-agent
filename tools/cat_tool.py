from tools.base_tool import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read file contents. Pass the full path if file is inside a subdirectory e.g. inhere/...Hiding-From-You"

    def __init__(self, runner):
        self.runner = runner

    def run(self, filename):
        filename = filename.strip().strip('"').strip("'")

        # Only prepend ./ if it's a plain filename with no path separator
        if not filename.startswith("/") and not filename.startswith("./") and "/" not in filename:
            filename = f"./{filename}"

        return self.runner.run(f'cat "{filename}"')