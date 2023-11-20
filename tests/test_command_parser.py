import unittest
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

from runrun.models import Argument, BaseCommand, Context
from runrun.command_parser import CommandParser
from runrun.exceptions import CLIException, ParserException, ValidationException, InvalidValueException, MissingArgumentException, UnknownArgumentException

class TestCommandParser(unittest.TestCase):

	def test_parse_cmd_with_two_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](name='arg1')
			arg2 = Argument[str](name='arg2')

		returned_command = CommandParser(RootCommand()).parse(['--arg1', 'aaa', '--arg2', 'bbb'])
		expected_command = RootCommand()
		expected_command.arg1.value = 'aaa'
		expected_command.arg2.value = 'bbb'

		self.assertEqual(returned_command, expected_command)

	# region parse method

	def test_parse_cmd_with_int_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[int](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', '1515'])
		expected_command = RootCommand()
		expected_command.arg.value = 1515

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_true_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'true'])
		expected_command = RootCommand()
		expected_command.arg.value = True

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_false_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'false'])
		expected_command = RootCommand()
		expected_command.arg.value = False

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_invalid_bool_arg_fail(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](name='arg')

		with self.assertRaises(InvalidValueException):
			CommandParser(RootCommand()).parse(['--arg', 'invalid'])

	def test_parse_cmd_with_invalid_int_arg_fail(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[int](name='arg')

		with self.assertRaises(InvalidValueException):
			CommandParser(RootCommand()).parse(['--arg', 'invalid'])

	def test_parse_cmd_with_float_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[float](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', '1515.5'])
		expected_command = RootCommand()
		expected_command.arg.value = 1515.5

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_invalid_float_arg_fail(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[float](name='arg')

		with self.assertRaises(InvalidValueException):
			CommandParser(RootCommand()).parse(['--arg', 'invalid'])

	def test_parse_cmd_with_enum_arg_pass(self):
		class TestEnum(Enum):
			A = 1
			B = 2
			C = 3

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[TestEnum](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'B'])
		expected_command = RootCommand()
		expected_command.arg.value = TestEnum.B

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_invalid_enum_arg_fail(self):
		class TestEnum(Enum):
			A = 1
			B = 2
			C = 3

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[TestEnum](name='arg')

		with self.assertRaises(InvalidValueException):
			CommandParser(RootCommand()).parse(['--arg', 'invalid'])

	def test_parse_cmd_with_enum_arg_ignore_case_pass(self):
		class TestEnum(Enum):
			A = 1
			B = 2
			C = 3

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[TestEnum](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'b'])
		expected_command = RootCommand()
		expected_command.arg.value = TestEnum.B

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_no_value_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg'])
		expected_command = RootCommand()
		expected_command.arg.value = True

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_different_values_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[bool](name='arg1')
			arg2 = Argument[bool](name='arg2')
			arg3 = Argument[bool](name='arg3')

		returned_command = CommandParser(RootCommand()).parse(['--arg1', '--arg2', 'true', '--arg3', 'false'])
		expected_command = RootCommand()
		expected_command.arg1.value = True
		expected_command.arg2.value = True
		expected_command.arg3.value = False

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_special_value_true_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](name='arg')

		for true_value in ['true', 'yes', 'yup', '👍', ':)', '😊', '1', 'positive', 'OK']:

			returned_command = CommandParser(RootCommand()).parse(['--arg', true_value])
			expected_command = RootCommand()
			expected_command.arg.value = True

			self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_arg_special_value_false_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](name='arg')

		for false_value in ['false', 'no', 'nah', '👎', ':(', '☹', '0', 'negative']:

			returned_command = CommandParser(RootCommand()).parse(['--arg', false_value])
			expected_command = RootCommand()
			expected_command.arg.value = False

			self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_path_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Path](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', '/bin/sh'])
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

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Coordinates](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'x=5,y=7'])
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

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Label](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'center,x=5,y=7'])
		expected_command = RootCommand()
		expected_command.arg.value = Label('center', x=5.0, y=7.0)

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_one_string_arg_pass(self):

		class Robot:
			def __init__(self, name: str):
				self.name = name
			def __eq__(self, other):
				return self.name == other.name
		
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Robot](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'butter'])
		expected_command = RootCommand()
		expected_command.arg.value = Robot('butter')

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_one_int_arg_pass(self):

		class Counter:
			def __init__(self, count: int):
				self.count = count
			def __eq__(self, other):
				return self.count == other.count

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Counter](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', '5555'])
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

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[TwoPath](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', './a/,./b/'])
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

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Book](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'text=\=\=\=\='])
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

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Robot](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'name=Zurbafo\, Destroyer of zoop'])
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

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Robot](name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', ''])
		expected_command = RootCommand()
		expected_command.arg.value = Robot(name='')

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_custom_class_arg_duplicated_key_arg_fail(self):

		class Robot:
			def __init__(self, name: str):
				self.name = name
			def __eq__(self, other):
				return self.name == other.name
			def __repr__(self):
				return self.name

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[Robot](name='arg')

		with self.assertRaises(InvalidValueException):
			CommandParser(RootCommand()).parse(['--arg', 'name=zurbafo,name=wablah'])

	def test_parse_cmd_with_str_positional_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[str](position=0, name='arg')

		returned_command = CommandParser(RootCommand()).parse(['The color is yellow'])
		expected_command = RootCommand()
		expected_command.arg.value = 'The color is yellow'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_positional_true_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](position=0, name='arg')

		returned_command = CommandParser(RootCommand()).parse(['true'])
		expected_command = RootCommand()
		expected_command.arg.value = True

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_positional_false_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](position=0, name='arg')

		returned_command = CommandParser(RootCommand()).parse(['False'])
		expected_command = RootCommand()
		expected_command.arg.value = False

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_list_of_str_positional_false_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[list[str]](position=0, name='arg')

		returned_command = CommandParser(RootCommand()).parse(['one,two,three'])
		expected_command = RootCommand()
		expected_command.arg.value = ['one', 'two', 'three']

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_bool_positional_missing_fail(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[bool](position=0, name='arg', required=True)

		with self.assertRaises(MissingArgumentException):
			CommandParser(RootCommand()).parse([])

	def test_parse_cmd_with_str_positional_missing_fail(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[str](position=0, name='arg', required=True)

		with self.assertRaises(MissingArgumentException):
			CommandParser(RootCommand()).parse([])

	def test_parse_cmd_with_str_positional_and_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](name='arg2')

		returned_command = CommandParser(RootCommand()).parse(['arg1', '--arg2', 'arg2'])
		expected_command = RootCommand()
		expected_command.arg1.value = 'arg1'
		expected_command.arg2.value = 'arg2'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_multiple_int_positional_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[int](position=0, name='arg1')
			arg2 = Argument[int](position=1, name='arg2')
			arg3 = Argument[int](position=2, name='arg3')
			arg4 = Argument[int](position=3, name='arg4')

		returned_command = CommandParser(RootCommand()).parse(['1', '2', '3', '4'])
		expected_command = RootCommand()
		expected_command.arg1.value = 1
		expected_command.arg2.value = 2
		expected_command.arg3.value = 3
		expected_command.arg4.value = 4

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_multiple_int_positional_and_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](position=1, name='arg2')
			arg3 = Argument[str](name='arg3')
			arg4 = Argument[str](name='arg4')

		returned_command = CommandParser(RootCommand()).parse(['arg1', 'arg2', '--arg3', 'arg3', '--arg4', 'arg4'])
		expected_command = RootCommand()
		expected_command.arg1.value = 'arg1'
		expected_command.arg2.value = 'arg2'
		expected_command.arg3.value = 'arg3'
		expected_command.arg4.value = 'arg4'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_misplaced_positional_and_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](position=1, name='arg2')
			arg3 = Argument[str](name='arg3')
			arg4 = Argument[str](name='arg4')

		returned_command = CommandParser(RootCommand()).parse(['arg1', '--arg3', 'arg3', 'arg2', '--arg4', 'arg4'])
		expected_command = RootCommand()
		expected_command.arg1.value = 'arg1'
		expected_command.arg2.value = 'arg2'
		expected_command.arg3.value = 'arg3'
		expected_command.arg4.value = 'arg4'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_str_positional_as_argument_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[str](position=0, name='arg')

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'The color is yellow'])
		expected_command = RootCommand()
		expected_command.arg.value = 'The color is yellow'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_required_arg_pass(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[str](name='arg', required=True)

		returned_command = CommandParser(RootCommand()).parse(['--arg', 'a test value'])
		expected_command = RootCommand()
		expected_command.arg.value = 'a test value'

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_missing_required_arg_fail(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[str](name='arg', required=True)
	
		with self.assertRaises(MissingArgumentException):
			CommandParser(RootCommand()).parse([])

	def test_parse_cmd_with_unknown_arg_fail(self):

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg = Argument[str](name='arg', required=True)
	
		with self.assertRaises(UnknownArgumentException):
			CommandParser(RootCommand()).parse(['shouldnotexists'])

	def test_parse_subcmd_no_arg_pass(self):

		class TestCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			test = TestCommand()

		returned_command = CommandParser(RootCommand()).parse(['test'])
		expected_command = TestCommand()

		self.assertEqual(returned_command, expected_command)

	def test_parse_nested_subcmd_no_arg_pass(self):

		class Test4Command(BaseCommand):
			def __init__(self):
				super().__init__(name='test4')

		class Test3Command(BaseCommand):
			def __init__(self):
				super().__init__(name='test3')
			test4 = Test4Command()

		class Test2Command(BaseCommand):
			def __init__(self):
				super().__init__(name='test2')
			test3 = Test3Command()

		class Test1Command(BaseCommand):
			def __init__(self):
				super().__init__(name='test1')
			test2 = Test2Command()

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			test1 = Test1Command()

		returned_command = CommandParser(RootCommand()).parse(['test1', 'test2', 'test3', 'test4'])
		expected_command = Test4Command()

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcmd_with_string_arg_pass(self):

		class TestCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')
			name = Argument[str](name='name', value='')
			count = Argument[int](name='count', value=0)

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			test = TestCommand()

		returned_command = CommandParser(RootCommand()).parse(['test', '--name', 'a test value'])
		expected_command = TestCommand()
		expected_command.name.value = 'a test value'

		self.assertEqual(returned_command, expected_command)

	def test_parse_subcmd_with_int_arg_pass(self):

		class TestCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='test')
			name = Argument[str](name='name', value='')
			count = Argument[int](name='count', value=0)

		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			test = TestCommand()

		returned_command = CommandParser(RootCommand()).parse(['test', '--count', '5545'])
		expected_command = TestCommand()
		expected_command.count.value = 5545

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_list_of_str_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			names = Argument[list[str]](name='names', value=[])
		
		returned_command = CommandParser(RootCommand()).parse(['--names', 'farfofu,blarara,bibabobabi'])
		expected_command = RootCommand()
		expected_command.names.value = ['farfofu', 'blarara', 'bibabobabi']

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_list_of_int_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			things = Argument[list[int]](name='things', value=[])
		
		returned_command = CommandParser(RootCommand()).parse(['--things', '1,3,3,7'])
		expected_command = RootCommand()
		expected_command.things.value = [1,3,3,7]

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_list_of_enum_arg_pass(self):
		class TestEnum(Enum):
			A = 1
			B = 2
			C = 3
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			things = Argument[list[TestEnum]](name='things', value=[])

		returned_command = CommandParser(RootCommand()).parse(['--things', 'A,B,B,C'])
		expected_command = RootCommand()
		expected_command.things.value = [TestEnum.A,TestEnum.B,TestEnum.B,TestEnum.C]

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_dict_of_str_str_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			things = Argument[dict[str,str]](name='things', value={})
		
		returned_command = CommandParser(RootCommand()).parse(['--things', 'name=Wabla,last_name=Forfafui'])
		expected_command = RootCommand()
		expected_command.things.value = {'name':'Wabla', 'last_name':'Forfafui'}

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_dict_of_str_int_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			things = Argument[dict[str,int]](name='things', value={})
		
		returned_command = CommandParser(RootCommand()).parse(['--things', 'a=1,b=3,c=3,d=7'])
		expected_command = RootCommand()
		expected_command.things.value = {'a':1, 'b':3, 'c':3, 'd':7}

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_dict_of_str_enum_arg_pass(self):
		class TestEnum(Enum):
			A = 1
			B = 2
			C = 3
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			things = Argument[dict[str,TestEnum]](name='things', value={})

		returned_command = CommandParser(RootCommand()).parse(['--things', 'Liwia=A,Clementia=B,Jia=B,Pomare=C'])
		expected_command = RootCommand()
		expected_command.things.value = {'Liwia':TestEnum.A, 'Clementia':TestEnum.B, 'Jia':TestEnum.B, 'Pomare':TestEnum.C}

		self.assertEqual(returned_command, expected_command)

	def test_parse_cmd_with_dict_arg_missing_equal_fail(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			things = Argument[dict[str,str]](name='things', value={})
		
		with self.assertRaises(InvalidValueException):
			CommandParser(RootCommand()).parse(['--things', 'name,last_name=Forfafui'])

	# endregion

	# region validate_command method

	def test_validate_command_duplicate_position_fail(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](position=0, name='arg2')

		with self.assertRaises(ValidationException):
			CommandParser(RootCommand())

	def test_validate_command_position_not_starting_at_zero_fail(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=1, name='arg1')
			arg2 = Argument[str](position=2, name='arg2')

		with self.assertRaises(ValidationException):
			CommandParser(RootCommand())

	def test_validate_command_position_number_skip_fail(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](position=2, name='arg2')

		with self.assertRaises(ValidationException):
			CommandParser(RootCommand())

	def test_validate_command_position_only_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](position=1, name='arg2')

		CommandParser(RootCommand())

	def test_validate_command_position_with_args_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](position=0, name='arg1')
			arg2 = Argument[str](position=1, name='arg2')
			arg3 = Argument[str](name='arg3')
			arg4 = Argument[str](name='arg4')

		CommandParser(RootCommand())

	def test_validate_command_no_position_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			arg1 = Argument[str](name='arg1')
			arg2 = Argument[str](name='arg2')

		CommandParser(RootCommand())

	# endregion

	# region context

	def test_context_has_root_command_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')

		returned_command = CommandParser(RootCommand()).parse([])

		self.assertEqual(returned_command.context.root_command, RootCommand())

	def test_context_root_cmd_has_no_parent_command_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')

		returned_command = CommandParser(RootCommand()).parse([])

		self.assertEqual(returned_command.context.parent_command, None)

	def test_context_sub_cmd_has_parent_command_pass(self):
		class SubCommand2(BaseCommand):
			def __init__(self):
				super().__init__(name='sub2')
		class SubCommand1(BaseCommand):
			def __init__(self):
				super().__init__(name='sub1')
			sub = SubCommand2()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			sub = SubCommand1()

		returned_command = CommandParser(RootCommand()).parse(['sub1', 'sub2'])

		self.assertEqual(returned_command.context.parent_command, SubCommand1())

	def test_context_sub_cmd_has_root_command_pass(self):
		class SubCommand2(BaseCommand):
			def __init__(self):
				super().__init__(name='sub2')
		class SubCommand1(BaseCommand):
			def __init__(self):
				super().__init__(name='sub1')
			sub = SubCommand2()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			sub = SubCommand1()

		returned_command = CommandParser(RootCommand()).parse(['sub1', 'sub2'])

		self.assertEqual(returned_command.context.root_command, RootCommand())

	def test_context_sub_cmd_original_arguments_pass(self):
		class SubCommand2(BaseCommand):
			def __init__(self):
				super().__init__(name='sub2')
			arg1 = Argument[str](name='arg1')
		class SubCommand1(BaseCommand):
			def __init__(self):
				super().__init__(name='sub1')
			sub = SubCommand2()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			sub = SubCommand1()

		returned_command = CommandParser(RootCommand()).parse(['sub1', 'sub2', '--arg1', 'test'])

		self.assertEqual(returned_command.context.original_arguments, ['sub1', 'sub2', '--arg1', 'test'])

	def test_context_sub_cmd_scoped_arguments_pass(self):
		class SubCommand2(BaseCommand):
			def __init__(self):
				super().__init__(name='sub2')
			arg1 = Argument[str](name='arg1')
		class SubCommand1(BaseCommand):
			def __init__(self):
				super().__init__(name='sub1')
			sub = SubCommand2()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			sub = SubCommand1()

		returned_command = CommandParser(RootCommand()).parse(['sub1', 'sub2', '--arg1', 'test'])

		self.assertEqual(returned_command.context.scoped_arguments, ['--arg1', 'test'])

	# endregion
