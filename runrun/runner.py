import sys
import asyncio
import inspect

from runrun.models import BaseCommand
from runrun.command_parser import CommandParser
from runrun.exceptions import (
    CLIException,
    DefaultExceptionHandler,
    BaseExceptionHandler,
)


class Runner:
    def __init__(
        self,
        command: BaseCommand,
        exception_handler: BaseExceptionHandler = DefaultExceptionHandler(),
    ):
        self.command = command
        self.exception_handler = exception_handler

    def run(self, args: list[str] | None = None):
        if args is None:
            args = sys.argv[1:]

        try:
            cmd = CommandParser(self.command).parse(args)

            is_async = inspect.iscoroutinefunction(cmd.run)

            if is_async:
                asyncio.run(cmd.run())  # type: ignore
            else:
                cmd.run()

        except CLIException as e:
            self.exception_handler.handle_exception(e)
