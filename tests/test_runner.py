import unittest

from runrun.models import BaseCommand
from runrun.runner import Runner


class TestRunner(unittest.TestCase):

    def test_runner_calls_run(self):

        class TCommand(BaseCommand):
            def __init__(self):
                super().__init__(name="a")
                self.called = False

            def run(self):
                self.called = True

        cmd = TCommand()
        Runner(cmd).run([])

        self.assertTrue(cmd.called)

    def test_runner_calls_async_run(self):
        class TCommand(BaseCommand):
            def __init__(self):
                super().__init__(name="a")
                self.called = False

            async def run(self):
                self.called = True

        cmd = TCommand()
        Runner(cmd).run([])

        self.assertTrue(cmd.called)
