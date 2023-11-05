import unittest

from runrun.models import Argument, BaseCommand, Context

class TestCommand(unittest.TestCase):

	def test_equal_simple_pass(self):
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='a')

		self.assertEqual(TCommand(), TCommand())

	def test_equal_with_same_arg_pass(self):
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='a')
			arg = Argument[str](name='arg', required=True)
		
		a = TCommand()
		a.arg.value = 'test'
		b = TCommand()
		b.arg.value = 'test'

		self.assertEqual(a, b)

	def test_equal_with_diff_arg_pass(self):
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='a')
			arg = Argument[str](name='arg', required=True)
		
		a = TCommand()
		a.arg.value = 'a value'
		b = TCommand()
		b.arg.value = 'a different value'

		self.assertNotEqual(a, b)

	def test_get_arguments_pass(self):
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='a')
			arg1 = Argument[str](name='arg1', required=True)
			arg2 = Argument[int](name='arg2', value=5)
			arg3 = Argument[float](name='arg3', required=True)
		
		returned_arguments = TCommand().get_arguments()
		expected_arguments = [
			Argument[str](name='arg1', required=True),
			Argument[int](name='arg2', value=5),
			Argument[float](name='arg3', required=True),
		]

		self.assertEqual(returned_arguments, expected_arguments)

	def test_get_sub_commands_pass(self):
		class Sub_command_1(BaseCommand):
			def __init__(self): super().__init__(name='a')
		class Sub_command_2(BaseCommand):
			def __init__(self): super().__init__(name='b')
		class Sub_command_3(BaseCommand):
			def __init__(self): super().__init__(name='c')
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='test')
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

class TestContext(unittest.TestCase):
	
	def test_equal_pass(self):
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='t')

		context1 = Context(
			original_arguments=['add', '1', '2'],
			scoped_arguments=['1', '2'],
			root_command=TCommand()
		)

		context2 = Context(
			original_arguments=['add', '1', '2'],
			scoped_arguments=['1', '2'],
			root_command=TCommand()
		)

		self.assertEqual(context1, context2)

	def test_unequal_pass(self):
		class TCommand(BaseCommand):
			def __init__(self): super().__init__(name='t')

		context1 = Context(
			original_arguments=['add', '1', '2'],
			scoped_arguments=['1', '2'],
			root_command=TCommand(),
			parent_command=TCommand(),
		)

		context2 = Context(
			original_arguments=['multiply', '1', '2'],
			scoped_arguments=['1', '2'],
			root_command=TCommand(),
			parent_command=TCommand(),
		)

		self.assertNotEqual(context1, context2)

class TestArgument(unittest.TestCase):

	def test_str_pass(self):
		year_arg = Argument[int](name='year')
		year_arg.value = 1234
		self.assertEqual(f'{year_arg}', '1234')
