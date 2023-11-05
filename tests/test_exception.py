import unittest

from runrun.models import BaseCommand, Argument
from runrun.exceptions import UnknownArgumentException
from runrun.exceptions import DefaultExceptionHandler

class TestDefaultExceptionHandler(unittest.TestCase):

	def test_get_argument_suggestions_pass(self):
		arg1 = Argument[int](name='argument1')
		arg2 = Argument[str](name='argument2')
		arg3 = Argument[str](name='argument3')
		arg4 = Argument[str](name='argument4')
		arg5 = Argument[int](name='chrono')

		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')
			_arg1 = arg1
			_arg2 = arg2
			_arg3 = arg3
			_arg4 = arg4
			_arg5 = arg5

		command = TCommand()
		default_exception_handler = DefaultExceptionHandler()

		for unknown, expected_matches in [
			('--chr8no', [arg5]),
			('--chrno', [arg5]),
			('--argument', [arg1, arg2, arg3, arg4]),
			('--argumentT', [arg1, arg2, arg3, arg4]),
		]:
			exception = UnknownArgumentException(command=command, unknown_argument=unknown)

			returned_suggestions = default_exception_handler.get_argument_suggestions(exception)

			self.assertListEqual(expected_matches, returned_suggestions)

	def test_get_argument_suggestions_no_match_pass(self):
		arg1 = Argument[int](name='argument1')
		arg2 = Argument[str](name='argument2')
		arg3 = Argument[bool](name='argument3')
		arg4 = Argument[str](name='argument4')

		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')
			_arg1 = arg1
			_arg2 = arg2
			_arg3 = arg3
			_arg4 = arg4

		command = TCommand()

		default_exception_handler = DefaultExceptionHandler()

		exception = UnknownArgumentException(command=command, unknown_argument='--shouldnotmatch')

		returned_suggestions = default_exception_handler.get_argument_suggestions(exception)

		self.assertListEqual([], returned_suggestions)

	def test_get_sub_command_suggestions_pass(self):
		class SubCommand1(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd1')
		cmd1 = SubCommand1()
		class SubCommand2(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd2')
		cmd2 = SubCommand2()
		class SubCommand3(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd3')
		cmd3 = SubCommand3()
		class SubCommand4(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd4')
		cmd4 = SubCommand4()
		class ChronoCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='chrono')
		chronocmd = ChronoCommand()

		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')
			_cmd1 = cmd1
			_cmd2 = cmd2
			_cmd3 = cmd3
			_cmd4 = cmd4
			_cmd5 = chronocmd
			_arg1 = Argument[int](name='argument1')
			_arg2 = Argument[str](name='argument2')
			_arg3 = Argument[str](name='argument3')
			_arg4 = Argument[str](name='argument4')

		command = TCommand()
		default_exception_handler = DefaultExceptionHandler()

		for unknown, expected_matches in [
			('chr8no', [chronocmd]),
			('chron', [chronocmd]),
			('cmd', [cmd1, cmd2, cmd3, cmd4]),
			('cmdT', [cmd1, cmd2, cmd3, cmd4]),
		]:
			exception = UnknownArgumentException(command=command, unknown_argument=unknown)

			returned_suggestions = default_exception_handler.get_sub_command_suggestions(exception)

			self.assertListEqual(expected_matches, returned_suggestions)

	def test_get_sub_command_suggestions_no_match_pass(self):
		class SubCommand1(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd1')
		cmd1 = SubCommand1()
		class SubCommand2(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd2')
		cmd2 = SubCommand2()
		class SubCommand3(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd3')
		cmd3 = SubCommand3()
		class SubCommand4(BaseCommand):
			def __init__(self):
				super().__init__(name='cmd4')
		cmd4 = SubCommand4()

		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')
			_cmd1 = cmd1
			_cmd2 = cmd2
			_cmd3 = cmd3
			_cmd4 = cmd4
			_arg1 = Argument[int](name='argument1')
			_arg2 = Argument[str](name='argument2')
			_arg3 = Argument[str](name='argument3')
			_arg4 = Argument[str](name='argument4')

		command = TCommand()
		default_exception_handler = DefaultExceptionHandler()

		exception = UnknownArgumentException(command=command, unknown_argument='shouldnotmatch')

		returned_suggestions = default_exception_handler.get_sub_command_suggestions(exception)

		self.assertListEqual([], returned_suggestions)
