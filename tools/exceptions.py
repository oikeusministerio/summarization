
import os

class TextTooLong(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

class SummarySizeTooSmall(ValueError):
    def __init__(self, *args, **kwargs):
        ValueError.__init__(self, *args, **kwargs)

class CommandLineError(Exception):
    """Errors when communicating with commandline
    """
    def render(self, msg):
        return msg % vars(self)

class ShellError(CommandLineError):
    """This error is raised when a shell.run returns a non-zero exit code
    (meaning the command failed).
    """
    def __init__(self, command, exit_code, stdout, stderr):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.executable = self.command.split()[0]

    def is_not_installed(self):
        return os.name == 'posix' and self.exit_code == 127

    def not_installed_message(self):
        return (
            "The command `%(command)s` failed because the executable\n"
            "`%(executable)s` is not installed on your system. Please make\n"
            "sure the appropriate dependencies are installed before using\n"
        ) % vars(self)

    def failed_message(self):
        return (
            "The command `%(command)s` failed with exit code %(exit_code)d\n"
            "------------- stdout -------------\n"
            "%(stdout)s"
            "------------- stderr -------------\n"
            "%(stderr)s"
        ) % vars(self)

    def __str__(self):
        if self.is_not_installed():
            return self.not_installed_message()
        else:
            return self.failed_message()