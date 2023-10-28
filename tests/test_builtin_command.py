import unittest

from runrun.builtin_command import HelpCommand
from runrun.command_parser import CommandParser
from runrun.models import Command, CommandDetails, Argument, Context

class TestHelpCommand(unittest.TestCase):

	def test_get_usage_nothing_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root', root.help.get_usage())

	def test_get_usage_one_arg_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [arguments]', root.help.get_usage())

	def test_get_usage_one_sub_command_pass(self):
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			cmd = SubCommand()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command]', root.help.get_usage())

	def test_get_usage_one_sub_command_one_arg_pass(self):
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command] [arguments]', root.help.get_usage())

	def test_get_usage_sub_cmd_nothing_pass(self):
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
			help = HelpCommand()
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd', root.cmd.help.get_usage())

	def test_get_usage_sub_cmd_one_arg_pass(self):
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
			help = HelpCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [arguments]', root.cmd.help.get_usage())

	def test_get_usage_sub_cmd_one_sub_command_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='t', display_name='T', description='A test command')
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
			help = HelpCommand()
			cmd = TCommand()
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [command]', root.cmd.help.get_usage())

	def test_get_usage_sub_cmd_one_sub_command_one_arg_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='t', display_name='T', description='A test command')
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
			help = HelpCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
			cmd = TCommand()
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [command] [arguments]', root.cmd.help.get_usage())

	def test_get_usage_one_positional_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			arg = Argument[int](name='arg', display_name='Argument', position=0, description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg> [arguments]', root.help.get_usage())

	def test_get_usage_two_positional_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			arg1 = Argument[int](name='arg1', display_name='Argument 1', position=0, description='A test argument')
			arg2 = Argument[str](name='arg2', display_name='Argument 2', position=1, description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg1> <arg2> [arguments]', root.help.get_usage())

	def test_get_usage_two_positional_correct_order_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			arg1 = Argument[int](name='arg1', display_name='Argument 1', position=1, description='A test argument')
			arg2 = Argument[str](name='arg2', display_name='Argument 2', position=0, description='A test argument')
			arg3 = Argument[str](name='arg3', display_name='Argument 3', position=3, description='A test argument')
			arg4 = Argument[str](name='arg4', display_name='Argument 4', position=2, description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg2> <arg1> <arg4> <arg3> [arguments]', root.help.get_usage())

	def test_get_usage_one_positional_with_sub_cmd_pass(self):
		class TCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand()
			arg = Argument[int](name='arg', display_name='Argument', position=0, description='A test argument')
			cmd = TCommand()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command] <arg> [arguments]', root.help.get_usage())
