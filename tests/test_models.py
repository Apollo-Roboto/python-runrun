import unittest

from arcommander.models import Argument, Command, CommandDetails

class TestCommand(unittest.TestCase):

	def test_equal_simple_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(
				name='a',
				display_name='A',
				description='A test command',
			)

		self.assertEqual(TCommand(), TCommand())

	def test_equal_with_same_arg_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(
				name='a',
				display_name='A',
				description='A test command',
			)

			arg = Argument[str](
				name='arg',
				display_name='Argument',
				description='A test argument',
				required=True,
			)
		
		a = TCommand()
		a.arg.value = 'test'
		b = TCommand()
		b.arg.value = 'test'

		self.assertEqual(a, b)

	def test_equal_with_diff_arg_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(
				name='a',
				display_name='A',
				description='A test command',
			)

			arg = Argument[str](
				name='arg',
				display_name='Argument',
				description='A test argument',
				required=True,
			)
		
		a = TCommand()
		a.arg.value = 'a value'
		b = TCommand()
		b.arg.value = 'a different value'

		self.assertNotEqual(a, b)
