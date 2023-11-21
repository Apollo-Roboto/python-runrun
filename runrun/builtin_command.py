from typing import Union, Optional, Type
import os
from enum import Enum
from importlib.metadata import version
import importlib.metadata
from pathlib import Path
import json
import textwrap
import sys

from colorama import Fore, Style, Back

from runrun.models import BaseCommand, Argument, BaseApplication



class HelpFormat(Enum):
	STD = 0
	JSON = 1



class HelpCommand(BaseCommand):

	format = Argument[HelpFormat](
		name='format',
		display_name='Output Format',
		description='The output format of the command details',
		short='f',
		required=False,
		value=HelpFormat.STD,
	)

	filter = Argument[str](
		name='filter',
		display_name='Filter',
		description='Filter the help results, this can help to find what you are looking for',
		required=False,
		value='',
	)

	required_only = Argument[bool](
		name='required-only',
		display_name='Required Only',
		description='Only show required arguments',
		value=False,
	)

	def __init__(self, help_of_help=True):
		super().__init__(
			name='help',
			display_name='Help',
			description='Show help about this command',
		)

		# help of help can create a recursive loop
		if help_of_help:
			self.help = HelpCommand(help_of_help=False)
		else:
			self.help = None

	def print_json(self):
		data = {}

		parent_command = self.context.parent_command
		root_command = self.context.root_command

		arguments = self.get_parent_arguments()
		sub_commands = self.get_parent_sub_commands()
		
		data['command'] = {
			'name': parent_command.command_name,
			'display_name': parent_command.command_display_name,
			'description': parent_command.command_description,
			'aliases': parent_command.command_aliases,
		} if parent_command else None

		data['arguments'] = [
			{
				'name': arg.name,
				'display_name': arg.display_name,
				'description': arg.description,
				'position': arg.position,
				'required': arg.required,
				'short': arg.short,
				'type': arg.type.__name__,
				'aliases': arg.aliases,
			}
			for arg in arguments
		]

		data['sub_commands'] = [
			{
				'name': cmd.command_name,
				'display_name': cmd.command_display_name,
				'description': cmd.command_description,
				'aliases': cmd.command_aliases,
			}
			for cmd in sub_commands
		]

		data['usage'] = self.get_usage()

		data['application'] = {
			'name': root_command.command_name,
			'display_name': root_command.command_display_name,
			'description': root_command.command_description,
			'version': root_command.application_version,
			'author': root_command.application_author,
			'website': root_command.application_website,
			'copyright': root_command.application_copyright,
		} if isinstance(root_command, BaseApplication) else None

		print(json.dumps(data, indent='  '))

	def get_full_command_name(self, command: BaseCommand) -> str:
		if command.context.parent_command is None:
			return command.command_name

		return self.get_full_command_name(command.context.parent_command) + ' ' + command.command_name

	def get_usage(self) -> str:
		parent_command = self.context.parent_command
		if parent_command is None:
			return ''
		
		arguments = parent_command.get_arguments()

		text = self.get_full_command_name(parent_command)

		# checking bigger than 1 to filter out the included help
		if len(parent_command.get_sub_commands()) > 1:
			text += ' [command]'

		positional_arguments = filter(lambda arg: arg.position is not None, arguments)
		positional_arguments = sorted(positional_arguments, key=lambda x: sys.maxsize if x.position is None else x.position)

		# positionals arguments
		for arg in positional_arguments:
			text += f' <{arg.name}>'

		# if there is non positional arguments
		if len(arguments) - len(positional_arguments) > 0:
			text += ' [arguments]'

		return text

	def print_usage(self):
		print(f'  {self.get_usage()}')

	def print_argument(self, argument: Argument):
		aliases = ['--' + alias for alias in argument.aliases]

		if argument.short:
			aliases.append('-' + argument.short)

		aliases_text = ', '.join(argument.aliases)

		argument_type_text = ''

		if argument.type == bool:
			# boolean value are optional (using square brackets)
			argument_type_text = '[true|false]'
		elif issubclass(argument.type, Enum):
			# if enum, write the options
			argument_type_text = '{' + ', '.join(argument.type.__members__) + '}'
		else:
			argument_type_text = '<' + argument.type.__name__ + '>'

		columns = [
			f'{argument.display_name}',
			f'--{argument.name} {argument_type_text}\n{aliases_text}',
			f'{"Required" if argument.required else ""}',
			f'{argument.description}'
		]
		widths = [16, 29, 12, 60] # TODO: this should be at the class level

		text = self.columned_text(columns, widths)

		# just in case there is not text returned
		if len(text) == 0:
			return
		
		# the first line gets a slightly different style
		print(f"  {Style.BRIGHT}{text[0][0]}{Style.RESET_ALL}  {text[0][1]} {text[0][2]} | {text[0][3]}")

		for line in text[1:]:
			print(f"  {Style.BRIGHT}{line[0]}  {Style.DIM}{line[1]}{Style.RESET_ALL}   {line[2]}")

	def print_command(self, cmd: BaseCommand):
		aliases_text = ', '.join(cmd.command_aliases)
		
		columns = [
			f'{cmd.command_display_name}',
			f'{cmd.command_name}\n{aliases_text}',
			f'{cmd.command_description}'
		]
		widths = [16, 42, 60] # TODO: this should be at the class level

		text = self.columned_text(columns, widths)

		# just in case there is not text returned
		if len(text) == 0:
			return

		# the first line gets a slightly different style
		print(f"  {Style.BRIGHT}{text[0][0]}{Style.RESET_ALL}  {text[0][1]} | {text[0][2]}")

		for line in text[1:]:
			print(f"  {Style.BRIGHT}{line[0]}  {Style.DIM}{line[1]}{Style.RESET_ALL}   {line[2]}")

	def columned_text(self, columns:list[str], widths:list[int]=[40,40]) -> list[list[str]]:
		if len(columns) != len(widths):
			raise ValueError('There must be as many columns than widths')
		
		lines = []

		# wrap text in each column
		for i, col in enumerate(columns):
			col_lines = col.split('\n')
			wrapped_col_lines = []
			for line in col_lines:
				wrapped_lines = textwrap.wrap(line, width=widths[i])
				wrapped_col_lines.extend(wrapped_lines)
			
			lines.append(wrapped_col_lines)

		# find the maximum number of lines across all columns
		max_lines = max(len(col_lines) for col_lines in lines)
		
		final_lines = []

		for line_num in range(max_lines):
			line = []
			for i, col_lines in enumerate(lines):
				if line_num < len(col_lines):
					line.append(col_lines[line_num].ljust(widths[i]))
				else:
					line.append(' ' * widths[i])
			final_lines.append(line)

		return final_lines

	def print_header(self, text: str):
		print()
		print(f'{Back.WHITE}{Style.BRIGHT} {text.upper()} {Style.RESET_ALL}')

	def print_parent_description(self):
		parent_command = self.context.parent_command

		if parent_command is None:
			return

		print()
		print(f'  {parent_command.command_description}')

	def get_parent_arguments(self) -> list[Argument]:
		if self.context.parent_command is None:
			return []

		arguments = self.context.parent_command.get_arguments()

		# text based filter 
		if self.filter.value != '':
			filter_text = self.filter.value if self.filter.value is not None else ''
			arguments = list(filter(lambda arg: filter_text in arg.name, arguments))
		
		# required filter
		if self.required_only.value:
			arguments = list(filter(lambda arg: arg.required, arguments))

		return arguments

	def get_parent_sub_commands(self) -> list[BaseCommand]:
		if self.context.parent_command is None:
			return []

		sub_commands = self.context.parent_command.get_sub_commands()

		if self.filter.value != '':
			filter_text = self.filter.value if self.filter.value is not None else ''
			sub_commands = list(filter(lambda cmd: filter_text in cmd.command_name, sub_commands))

		return sub_commands

	def print_std(self):

		self.print_parent_description()

		self.print_header('Usage')
		self.print_usage()

		arguments = self.get_parent_arguments()
		commands = self.get_parent_sub_commands()

		if len(arguments) > 0:
			self.print_header('Arguments')

		for arg in arguments:
			self.print_argument(arg)

		if len(commands) > 0:
			self.print_header('Commands')

		for cmd in commands:
			self.print_command(cmd)

		print()

	def run(self):
		if self.format.value == HelpFormat.JSON:
			self.print_json()
		elif self.format.value == HelpFormat.STD:
			self.print_std()
		else:
			raise NotImplementedError('That\'s not implemented yet, oops')



class InfoCommand(BaseCommand):

	def __init__(self):
		super().__init__(
			name='info',
			display_name='Information',
			description='Application information'
		)

	def run(self):
		if not isinstance(self.context.parent_command, BaseApplication):
			print(f'Could not find version, parent command is not {BaseApplication}')
			return

		print(f'\n{Style.BRIGHT}{Back.WHITE} {self.context.parent_command.command_display_name} {Style.RESET_ALL}\n')

		if self.context.parent_command.application_version:
			print(f'  {Style.BRIGHT}Version{Style.RESET_ALL}:   {self.context.parent_command.application_version}')
		if self.context.parent_command.application_website:
			print(f'  {Style.BRIGHT}Website{Style.RESET_ALL}:   {self.context.parent_command.application_website}')
		if self.context.parent_command.application_author:
			print(f'  {Style.BRIGHT}Author{Style.RESET_ALL}:    {self.context.parent_command.application_author}')
		if self.context.parent_command.application_copyright:
			print(f'  {Style.BRIGHT}Copyright{Style.RESET_ALL}: {self.context.parent_command.application_copyright}')
		
		print()



class VersionCommand(BaseCommand):

	def __init__(self):
		super().__init__(
			name='version',
			display_name='Print the version',
			description='Application version',
		)

	def run(self):
		if not isinstance(self.context.parent_command, BaseApplication):
			print(f'Could not find version, parent command is not {BaseApplication}')
			return

		version = self.context.parent_command.application_version
		print(version)
