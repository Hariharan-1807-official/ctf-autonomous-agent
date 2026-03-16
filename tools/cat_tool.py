from tools.base_tool import BaseTool


class ReadFileTool(BaseTool):

    name = "read_file"
    description = "Read and display the contents of a file."

    def __init__(self, runner):
        self.runner = runner

    def run(self, filename):

        command = f"cat {filename}"

        return self.runner.run(command)