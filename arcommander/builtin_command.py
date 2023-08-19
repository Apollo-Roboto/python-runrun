from typing import Union, Optional, Type
import os

from colorama import Fore, Style, Back

from arcommander.models import Command, CommandDetails, Argument

class HelpCommand(Command):

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

		print(f' > {command.get_full_command_name()}')

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
