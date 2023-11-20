import unittest

from runrun.builtin_command import HelpCommand, InfoCommand, VersionCommand
from runrun.command_parser import CommandParser
from runrun.models import BaseCommand, Argument, Context

class TestHelpCommand(unittest.TestCase):

	def test_get_usage_nothing_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root', root.help.get_usage())

	def test_get_usage_one_arg_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			arg = Argument[str](name='arg')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [arguments]', root.help.get_usage())

	def test_get_usage_one_sub_command_pass(self):
		class SubCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='subcmd')
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			cmd = SubCommand()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command]', root.help.get_usage())

	def test_get_usage_one_sub_command_one_arg_pass(self):
		class SubCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='subcmd')
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command] [arguments]', root.help.get_usage())

	def test_get_usage_sub_cmd_nothing_pass(self):
		class SubCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='subcmd')
			help = HelpCommand()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd', root.cmd.help.get_usage())

	def test_get_usage_sub_cmd_one_arg_pass(self):
		class SubCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='subcmd')
			help = HelpCommand()
			arg = Argument[str](name='arg')
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [arguments]', root.cmd.help.get_usage())

	def test_get_usage_sub_cmd_one_sub_command_pass(self):
		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='t')
		class SubCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='subcmd')
			help = HelpCommand()
			cmd = TCommand()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [command]', root.cmd.help.get_usage())

	def test_get_usage_sub_cmd_one_sub_command_one_arg_pass(self):
		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='t')
		class SubCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='subcmd')
			help = HelpCommand()
			arg = Argument[str](name='arg')
			cmd = TCommand()
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			cmd = SubCommand()
			arg = Argument[str](name='arg')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [command] [arguments]', root.cmd.help.get_usage())

	def test_get_usage_one_positional_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			arg = Argument[int](name='arg', position=0)
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg>', root.help.get_usage())

	def test_get_usage_one_positional_one_argument_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			arg1 = Argument[int](name='arg1', position=0)
			arg2 = Argument[int](name='arg2')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg1> [arguments]', root.help.get_usage())

	def test_get_usage_two_positional_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			arg1 = Argument[int](name='arg1', position=0)
			arg2 = Argument[str](name='arg2', position=1)
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg1> <arg2>', root.help.get_usage())

	def test_get_usage_two_positional_correct_order_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			arg1 = Argument[int](name='arg1', position=1)
			arg2 = Argument[str](name='arg2', position=0)
			arg3 = Argument[str](name='arg3', position=3)
			arg4 = Argument[str](name='arg4', position=2)
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root <arg2> <arg1> <arg4> <arg3>', root.help.get_usage())

	def test_get_usage_one_positional_with_sub_cmd_pass(self):
		class TCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='t')
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()
			arg = Argument[int](name='arg', position=0)
			cmd = TCommand()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command] <arg>', root.help.get_usage())

	def test_calling_help_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			help = HelpCommand()

		command = CommandParser(RootCommand()).parse(['help'])
		command.run()

	def test_calling_info_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			info = InfoCommand()

		command = CommandParser(RootCommand()).parse(['info'])
		command.run()

	def test_calling_version_pass(self):
		class RootCommand(BaseCommand):
			def __init__(self):
				super().__init__(name='root')
			version = VersionCommand()

		command = CommandParser(RootCommand()).parse(['version'])
		command.run()
