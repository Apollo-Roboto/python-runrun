import unittest

from arcommander.builtin_command import HelpCommand2
from arcommander.command_parser import CommandParser
from arcommander.models import Command, CommandDetails, Argument, Context

class TestHelpCommand(unittest.TestCase):
    
	def test_get_usage_nothing_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand2()
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root', root.help.get_usage())

	def test_get_usage_one_arg_pass(self):
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand2()
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
			help = HelpCommand2()
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
			help = HelpCommand2()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.help.context = Context(parent_command=root,root_command=root)
		self.assertEqual('root [command] [arguments]', root.help.get_usage())

	def test_get_usage_sub_cmd_nothing_pass(self):
		class SubCommand(Command):
			command_details = CommandDetails(name='subcmd', display_name='Sub Command', description='A test command')
			help = HelpCommand2()
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand2()
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
			help = HelpCommand2()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand2()
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
			help = HelpCommand2()
			cmd = TCommand()
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand2()
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
			help = HelpCommand2()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
			cmd = TCommand()
		class RootCommand(Command):
			command_details = CommandDetails(name='root', display_name='Root', description='A test command')
			help = HelpCommand2()
			cmd = SubCommand()
			arg = Argument[str](name='arg', display_name='Argument', description='A test argument')
		root = RootCommand()
		root.context = Context(root_command=root)
		root.cmd.context = Context(parent_command=root, root_command=root)
		root.cmd.help.context = Context(parent_command=root.cmd, root_command=root)
		self.assertEqual('root subcmd [command] [arguments]', root.cmd.help.get_usage())
