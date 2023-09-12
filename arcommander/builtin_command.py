from typing import Union, Optional, Type
import os
from enum import Enum
from importlib.metadata import version
import importlib.metadata
from pathlib import Path
import json

from colorama import Fore, Style, Back

from arcommander.models import Command, CommandDetails, Argument

class HelpFormat(Enum):
	STD = 0
	JSON = 1

class HelpCommand2(Command):

	command_details = CommandDetails(
		name='help',
		display_name='Help',
		description='Help about this command',
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
			self.help = HelpCommand2(help_of_help=False)
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

		print(json.dumps(data, indent='\t'))

	def get_full_command_name(self, command: Command) -> str:
		if command.context.parent_command == None:
			return command.command_details.name

		return self.get_full_command_name(command.context.parent_command) + " " + command.command_details.name

	def get_usage(self) -> str:

		# text = self.context.parent_command.command_details.name
		text = self.get_full_command_name(self.context.parent_command)

		# checking bigger than 1 to filter out the included help
		if len(self.context.parent_command.get_sub_commands()) > 1:
			text += ' [command]'

		if len(self.context.parent_command.get_arguments()) > 0:
			text += ' [arguments]'
		
		return text

	def print_usage(self):
		print(self.get_usage())
	
	def print_std(self):

		# only print the banner on the root command
		if self.context.parent_command == self.context.root_command:
			self.print_banner(self.context.application.banner)

		self.print_usage()

		self.print_application(self.context.application)

		for arg in self.context.parent_command.get_arguments():
			self.print_argument(arg)

		for cmd in self.context.parent_command.get_sub_commands():
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




















class HelpCommand(Command):
	# Can this be done by loading and rendering a jinja template?
	# TODO: find a way to get app informations, such as version, name, author, copyright, ect
	#       maybe with https://docs.python.org/3/library/importlib.metadata.html

	command_details = CommandDetails(
		display_name='Help',
		name='help',
		description='List details about this command',
	)

	_terminal_width: int = 80

	def h2(self, text: str):
		min_width = 40

		width = int(self._terminal_width/2.5)

		if width < min_width:
			width = min_width

		print(f'{Fore.BLACK}{Back.WHITE}{text.center(width)}{Style.RESET_ALL}')

	def h3(self, text: str):
		print(f' {Fore.CYAN}• {text} {Style.RESET_ALL}')
	
	def print_argument(self, argument: Argument):
		margin = 5
		self.h3(argument.display_name)

		parameter_text = f'{" "*margin}--{argument.name} {("-" + argument.short) if argument.short != None else ""}'

		if argument.required:
			parameter_text += f'{" "*(28-len(parameter_text))}{Fore.YELLOW}[ REQUIRED ]{Fore.RESET}'
		
		parameter_text_length = len(parameter_text) + (0 if argument.required else 10)

		print(parameter_text + " "*(55-parameter_text_length) + " " + argument.description)

		if len(argument.aliases) > 0:
			print(f'{Fore.LIGHTBLACK_EX}{" "*margin}--{" --".join(argument.aliases)}{Style.RESET_ALL}')

		print()

	def print_sub_command(self, command: Type[Command]):
		margin = 5
		self.h3(command.command_details.display_name)

		full_sub_command = self._parent_command.get_full_command_name() + " " + command.command_details.name

		name_text = f'{" "*margin}{full_sub_command}'

		print(f'{name_text}{" "*(46-len(name_text))}{command.command_details.description}')

		print(f'{Fore.LIGHTBLACK_EX}{" "*margin}{" ".join(command.command_details.aliases)}{Style.RESET_ALL}')
	
	def print_current_command(self, command: Command):

		print()

		self.h3('Usage')

		print(f' > {command.get_full_command_name()} [subcommand] [parameters]')

		print()

		print(f'   {command.command_details.description}')

		print()
		print()


	def run(self):
		sub_commands = self._parent_command.get_sub_commands()
		arguments = self._parent_command.get_arguments()

		try:
			self._terminal_width = os.get_terminal_size().columns
		except: pass

		self.h2('Command')

		self.print_current_command(self._parent_command)

		# print arguments
		if len(arguments) > 0:
			print()

			self.h2('Arguments')

			# sort, place required at the top
			arguments.sort(key=lambda x: (not x.required, x.name.lower()))
			
			print()

			for argument in arguments:
				print()
				self.print_argument(argument)
				print()

		# print sub commands
		if len(sub_commands) > 0:

			print()

			self.h2('Sub Commands')

			print()

			for sub_command in sub_commands:
				print()
				self.print_sub_command(sub_command)
				print()
				
			print()
