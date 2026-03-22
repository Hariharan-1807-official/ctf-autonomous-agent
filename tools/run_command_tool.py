from tools.base_tool import BaseTool


class RunCommandTool(BaseTool):
    name = "run_command"
    description = "Execute any Linux shell command directly. Use this when other tools are insufficient. Examples: 'grep -r password /etc', 'find / -user bandit7 -group bandit6 -size 33c 2>/dev/null', 'strings file.bin', 'base64 -d file', 'xxd file | head'"

    def __init__(self, runner):
        self.runner = runner

    def run(self, command="ls"):
        command = command.strip().strip('"').strip("'")
        return self.runner.run(command)