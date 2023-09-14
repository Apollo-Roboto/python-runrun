from typing import Union, Optional, Type
import os
from enum import Enum
from importlib.metadata import version
import importlib.metadata
from pathlib import Path
import json
import textwrap

from colorama import Fore, Style, Back

from arcommander.models import Command, CommandDetails, Argument

class HelpFormat(Enum):
	STD = 0
	JSON = 1

class HelpCommand(Command):

	command_details = CommandDetails(
		name='help',
		display_name='Help',
		description='Show help about this command',
	)

	format = Argument[HelpFormat](
		name='format',
		display_name='Output Format',
		description='The output format of the command details',
		short='f',
		required=False,
		value=HelpFormat.JSON
	)

	def __init__(self, help_of_help=True):
		super().__init__()
		# help of help can create a recursive loop
		if help_of_help:
			self.help = HelpCommand(help_of_help=False)
		else:
			self.help = None

	def print_json(self):
		data = {}

		parent_command = self.context.parent_command
		root_command = self.context.root_command
		arguments = parent_command.get_arguments()
		sub_commands = parent_command.get_sub_commands()

		data['command'] = {
			'name': parent_command.command_details.name,
			'display_name': parent_command.command_details.display_name,
			'description': parent_command.command_details.description,
			'aliases': parent_command.command_details.aliases,
		}

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
				'name': cmd.command_details.name,
				'display_name': cmd.command_details.display_name,
				'description': cmd.command_details.description,
				'aliases': cmd.command_details.aliases,
			}
			for cmd in sub_commands
		]

		data['usage'] = self.get_usage()

		data['application'] = {
			'name': 'IDK',
			'version': 'IDK',
			'description': 'IDK',
			'author': 'IDK',
			'website': 'IDK',
		}

		print(json.dumps(data, indent='  '))

	def get_full_command_name(self, command: Command) -> str:
		if command.context.parent_command == None:
			return command.command_details.name

		return self.get_full_command_name(command.context.parent_command) + ' ' + command.command_details.name

	def get_usage(self) -> str:
		# TODO this should show the positional arguments

		# text = self.context.parent_command.command_details.name
		text = self.get_full_command_name(self.context.parent_command)

		# checking bigger than 1 to filter out the included help
		if len(self.context.parent_command.get_sub_commands()) > 1:
			text += ' [command]'

		if len(self.context.parent_command.get_arguments()) > 0:
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
			f'{argument.description}'
		]
		widths = [15, 30, 40] # TODO: this should be at the class level

		text = self.columned_text(columns, widths)

		# just in case there is not text returned
		if len(text) == 0:
			return
		
		# the first line gets a slightly different style
		print(f"  {Style.BRIGHT}{text[0][0]}{Style.RESET_ALL}  {text[0][1]} | {text[0][2]}")

		for line in text[1:]:
			print(f"  {Style.BRIGHT}{line[0]}  {Style.DIM}{line[1]}{Style.RESET_ALL}   {line[2]}")

	def print_command(self, cmd: Command):
		details = cmd.command_details
		aliases_text = ', '.join(details.aliases)
		
		columns = [
			f'{details.display_name}',
			f'{details.name}\n{aliases_text}',
			f'{details.description}'
		]
		widths = [15, 30, 40] # TODO: this should be at the class level

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

	def print_std(self):

		self.print_header('Usage')
		self.print_usage()

		arguments = self.context.parent_command.get_arguments()
		commands = self.context.parent_command.get_sub_commands()

		if len(arguments) > 0:
			self.print_header('Arguments')

		for arg in arguments:
			self.print_argument(arg)

		if len(commands) > 0:
			self.print_header('Commands')

		for cmd in commands:
			self.print_command(cmd)

	def run(self):
		if self.format.value == HelpFormat.JSON:
			self.print_json()
		elif self.format.value == HelpFormat.STD:
			self.print_std()
		else:
			raise NotImplementedError('That\'s not implemented yet, oops')















class InfoCommand(Command):

	command_details = CommandDetails(
		name='info',
		display_name='Information',
		description='Application information',
	)

	def run(self):
		print('IDK')

