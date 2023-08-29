import unittest

from arcommander.models import Argument, Command, CommandDetails

class TestCommand(unittest.TestCase):

	def test_equal_simple_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='a', display_name='A', description='A test command')

		self.assertEqual(TCommand(), TCommand())

	def test_equal_with_same_arg_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='a', display_name='A', description='A test command')
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument', required=True)
		
		a = TCommand()
		a.arg.value = 'test'
		b = TCommand()
		b.arg.value = 'test'

		self.assertEqual(a, b)

	def test_equal_with_diff_arg_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='a',display_name='A',description='A test command',)
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument', required=True)
		
		a = TCommand()
		a.arg.value = 'a value'
		b = TCommand()
		b.arg.value = 'a different value'

		self.assertNotEqual(a, b)

	def test_get_arguments_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='a',display_name='A',description='A test command')
			arg1 = Argument[str](name='arg1', display_name='Argument 1', description='A test argument', required=True)
			arg2 = Argument[int](name='arg2', display_name='Argument 2', description='A test argument', required=False, value=5)
			arg3 = Argument[float]( name='arg3',display_name='Argument 3',description='A test argument',required=True)
		
		returned_arguments = TCommand().get_arguments()
		expected_arguments = [
			Argument[str](name='arg1', display_name='Argument 1', description='A test argument', required=True),
			Argument[int](name='arg2', display_name='Argument 2', description='A test argument', required=False, value=5),
			Argument[float]( name='arg3',display_name='Argument 3',description='A test argument',required=True),
		]

		self.assertEqual(returned_arguments, expected_arguments)

	def test_get_sub_commands_pass(self):
		class Sub_command_1(Command):
			command_details = CommandDetails(name='a',display_name='A',description='A test command')
		class Sub_command_2(Command):
			command_details = CommandDetails(name='b',display_name='B',description='B test command')
		class Sub_command_3(Command):
			command_details = CommandDetails(name='c',display_name='C',description='C test command')
		class TCommand(Command):
			command_details = CommandDetails(name='test',display_name='Test',description='The test command')
			cmd1 = Sub_command_1()
			cmd2 = Sub_command_2()
			cmd3 = Sub_command_3()

		returned_commands = TCommand().get_sub_commands()
		expected_commands = [
			Sub_command_1(),
			Sub_command_2(),
			Sub_command_3(),
		]

		self.assertEqual(returned_commands, expected_commands)
