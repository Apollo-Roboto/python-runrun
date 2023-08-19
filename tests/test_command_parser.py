import unittest

from arcommander.models import Argument, Command, CommandDetails
from arcommander.command_parser import CommandParser

class TestCommand(Command):
	command_details = CommandDetails(
		name='test',
		display_name='Test',
		description='Meant to be for testing'
	)

	name = Argument[str](
		name='name',
		display_name='Name',
		description='',
		required=False,
		value=''
	)

	count = Argument[int](
		name='count',
		display_name='Count',
		description='',
		required=False,
		value=0
	)

class RootCommand(Command):
	command_details = CommandDetails(
		name='root',
		display_name='Root',
		description='Meant to be for testing'
	)

	test = TestCommand

class TestCommandParser(unittest.TestCase):

	def test_parse_subcommand_no_arg_pass(self):
		returned_command = CommandParser(RootCommand).parse(['test'])
		expected_command = TestCommand()

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcommand_with_string_arg_pass(self):
		returned_command = CommandParser(RootCommand).parse(['test', '--name', 'a test value'])
		expected_command = TestCommand()
		expected_command.name.value = 'a test value'

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcommand_with_int_arg_pass(self):
		returned_command = CommandParser(RootCommand).parse(['test', '--count', '5545'])
		expected_command = TestCommand()
		expected_command.count.value = 5545

		self.assertEqual(returned_command, expected_command)
