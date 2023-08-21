import unittest
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

from arcommander.models import Argument, Command, CommandDetails
from arcommander.command_parser import CommandParser

BLANK_DETAILS = CommandDetails(name='', display_name='', description='')

class TestCommandParser(unittest.TestCase):

	def test_parse_cmd_with_two_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg1 = Argument[str](name='arg1', display_name='Argument 1', description='', required=False)
			arg2 = Argument[str](name='arg2', display_name='Argument 2', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg1', 'aaa', '--arg2', 'bbb'])
		expected_command = RootCommand()
		expected_command.arg1.value = 'aaa'
		expected_command.arg2.value = 'bbb'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_int_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[int](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', '1515'])
		expected_command = RootCommand()
		expected_command.arg.value = 1515

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_true_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[bool](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'true'])
		expected_command = RootCommand()
		expected_command.arg.value = True

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_false_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[bool](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'false'])
		expected_command = RootCommand()
		expected_command.arg.value = False

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_int_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[int](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', '1515'])
		expected_command = RootCommand()
		expected_command.arg.value = 1515

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_float_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[float](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', '1515.5'])
		expected_command = RootCommand()
		expected_command.arg.value = 1515.5

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_enum_arg_pass(self):
		class TestEnum(Enum):
			A = 1
			B = 2
			C = 3

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[TestEnum](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'B'])
		expected_command = RootCommand()
		expected_command.arg.value = TestEnum.B

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_no_value_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[bool](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg'])
		expected_command = RootCommand()
		expected_command.arg.value = True

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_different_values_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg1 = Argument[bool](name='arg1', display_name='Argument 1', description='', required=False)
			arg2 = Argument[bool](name='arg2', display_name='Argument 2', description='', required=False)
			arg3 = Argument[bool](name='arg3', display_name='Argument 3', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg1', '--arg2', 'true', '--arg3', 'false'])
		expected_command = RootCommand()
		expected_command.arg1.value = True
		expected_command.arg2.value = True
		expected_command.arg3.value = False

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_special_value_true_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[bool](name='arg', display_name='Argument', description='', required=False)

		for true_value in ['true', 'yes', 'yup', '👍', ':)', '😊', '1', 'positive', 'OK']:

			returned_command = CommandParser(RootCommand).parse(['--arg', true_value])
			expected_command = RootCommand()
			expected_command.arg.value = True

			self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_special_value_false_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[bool](name='arg', display_name='Argument', description='', required=False)

		for false_value in ['false', 'no', 'nah', '👎', ':(', '☹', '0', 'negative']:

			returned_command = CommandParser(RootCommand).parse(['--arg', false_value])
			expected_command = RootCommand()
			expected_command.arg.value = False

			self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_path_arg_pass(self):

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Path](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', '/bin/sh'])
		expected_command = RootCommand()
		expected_command.arg.value = Path('/', 'bin', 'sh')

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_two_kwargs_pass(self):

		class Coordinates:
			def __init__(self, x: float, y: float):
				self.x = x
				self.y = y
			def __eq__(self, other):
				return self.x == other.x and self.y == other.y

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Coordinates](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'x=5,y=7'])
		expected_command = RootCommand()
		expected_command.arg.value = Coordinates(x=5.0, y=7.0)

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_two_kwargs_one_arg_pass(self):
		
		class Label:
			def __init__(self, name: str, x: float, y: float):
				self.name = name
				self.x = x
				self.y = y
			def __eq__(self, other):
				return self.name == other.name and self.x == other.x and self.y and other.y

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Label](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'center,x=5,y=7'])
		expected_command = RootCommand()
		expected_command.arg.value = Label('center', x=5.0, y=7.0)

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_one_string_arg_pass(self):

		class Robot:
			def __init__(self, name: str):
				self.name = name
			def __eq__(self, other):
				return self.name == other.name
		
		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Robot](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'butter'])
		expected_command = RootCommand()
		expected_command.arg.value = Robot('butter')

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_one_int_arg_pass(self):

		class Counter:
			def __init__(self, count: int):
				self.count = count
			def __eq__(self, other):
				return self.count == other.count

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Counter](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', '5555'])
		expected_command = RootCommand()
		expected_command.arg.value = Counter(5555)

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_two_path_arg_pass(self):

		class TwoPath:
			def __init__(self, a: Path, b: Path):
				self.a = a
				self.b = b
			def __eq__(self, other):
				return self.a == other.a and self.b == other.b

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[TwoPath](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', './a/,./b/'])
		expected_command = RootCommand()
		expected_command.arg.value = TwoPath(Path('.', 'a'), Path('.', 'b'))

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_escape_equal_arg_pass(self):

		class Book:
			def __init__(self, text: str):
				self.text = text
			def __eq__(self, other):
				return self.text == other.text
			def __repr__(self):
				return self.text

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Book](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'text=\=\=\=\='])
		expected_command = RootCommand()
		expected_command.arg.value = Book(text='====')

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_escape_comma_arg_pass(self):

		class Robot:
			def __init__(self, name: str):
				self.name = name
			def __eq__(self, other):
				return self.name == other.name
			def __repr__(self):
				return self.name

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Robot](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', 'name=Zurbafo\, Destroyer of zoop'])
		expected_command = RootCommand()
		expected_command.arg.value = Robot(name='Zurbafo, Destroyer of zoop')

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_empty_arg_pass(self):

		class Robot:
			def __init__(self, name: str):
				self.name = name
			def __eq__(self, other):
				return self.name == other.name
			def __repr__(self):
				return self.name

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			arg = Argument[Robot](name='arg', display_name='Argument', description='', required=False)

		returned_command = CommandParser(RootCommand).parse(['--arg', ''])
		expected_command = RootCommand()
		expected_command.arg.value = Robot(name='')

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcmd_no_arg_pass(self):

		class TestCommand(Command):
			command_details = CommandDetails(name='test', display_name='', description='')

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			test = TestCommand

		returned_command = CommandParser(RootCommand).parse(['test'])
		expected_command = TestCommand()

		self.assertEqual(returned_command, expected_command)

	def test_parse_nested_subcmd_no_arg_pass(self):

		class Test4Command(Command):
			command_details = CommandDetails(name='test4', display_name='', description='')

		class Test3Command(Command):
			command_details = CommandDetails(name='test3', display_name='', description='')
			test4 = Test4Command

		class Test2Command(Command):
			command_details = CommandDetails(name='test2', display_name='', description='')
			test3 = Test3Command

		class Test1Command(Command):
			command_details = CommandDetails(name='test1', display_name='', description='')
			test2 = Test2Command

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			test1 = Test1Command

		returned_command = CommandParser(RootCommand).parse(['test1', 'test2', 'test3', 'test4'])
		expected_command = Test4Command()

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcmd_with_string_arg_pass(self):

		class TestCommand(Command):
			command_details = CommandDetails(name='test', display_name='', description='')
			name = Argument[str](name='name', display_name='Name', description='', required=False, value='')
			count = Argument[int](name='count', display_name='Count', description='', required=False, value=0)

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			test = TestCommand

		returned_command = CommandParser(RootCommand).parse(['test', '--name', 'a test value'])
		expected_command = TestCommand()
		expected_command.name.value = 'a test value'

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcmd_with_int_arg_pass(self):

		class TestCommand(Command):
			command_details = CommandDetails(name='test', display_name='', description='')
			name = Argument[str](name='name', display_name='Name', description='', required=False, value='')
			count = Argument[int](name='count', display_name='Count', description='', required=False, value=0)

		class RootCommand(Command):
			command_details = BLANK_DETAILS
			test = TestCommand

		returned_command = CommandParser(RootCommand).parse(['test', '--count', '5545'])
		expected_command = TestCommand()
		expected_command.count.value = 5545

		self.assertEqual(returned_command, expected_command)
