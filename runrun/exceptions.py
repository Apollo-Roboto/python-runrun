from enum import Enum

import Levenshtein
from colorama import Fore, Style

from runrun.models import BaseCommand, Argument

class CLIException(Exception): pass

class ParserException(CLIException):
	def __init__(self, command: BaseCommand, *args: object) -> None:
		self.command = command
		super().__init__(*args)

class UnknownArgumentException(ParserException):
	def __init__(self, command: BaseCommand, unknown_argument: str = '') -> None:
		super().__init__(command, f'Unknown argument \'{unknown_argument}\'')
		self.unknown_argument = unknown_argument

class MissingArgumentException(ParserException):
	def __init__(self, command: BaseCommand, missing_arguments: list[Argument] = []) -> None:
		super().__init__(command, f'Missing required arguments: {", ".join([arg.name for arg in missing_arguments])}')
		self.missing_arguments = missing_arguments

class InvalidValueException(ParserException):
	def __init__(self, command: BaseCommand, argument: Argument, given_value: str) -> None:
		super().__init__(command, f'Invalid value given for argument \'{argument.name}\'')
		self.argument = argument
		self.given_value = given_value

class ValidationException(CLIException): pass

class BaseExceptionHandler:
	def handle_exception(self, exception: Exception):
		print(str(exception))

class DefaultExceptionHandler(BaseExceptionHandler):

	def handle_exception(self, exception: Exception):

		# only handle this library's exceptions
		if not isinstance(exception, CLIException):
			return

		# print a list of suggestions
		if isinstance(exception, UnknownArgumentException):
			self.print_unknown_argument_exception(exception)

		# print all the missing required arguments
		if isinstance(exception, MissingArgumentException):
			self.print_missing_argument_exception(exception)

		# print value suggestion (mostly if bool or enum)
		if isinstance(exception, InvalidValueException):
			self.print_invalid_value_exception(exception)

	def print_invalid_value_exception(self, exception: InvalidValueException):

		# TODO: print usage
		# exception.command.help.print_usage()

		print(f'{Fore.RED}Invalid value given for argument {exception.argument.display_name}{Style.RESET_ALL}')

		# TODO: the format here should be the same as the help format
		# exception.command.help.print_argument(exception.argument)

		if exception.argument.type == bool:
			print('Valid values are \'true\' or \'false\'')
			return

		if exception.argument.type == int:
			print('Expected an integer')
			return

		if issubclass(exception.argument.type, Enum):
			valid_values = [e.name for e in exception.argument.type]
			valid_values_str = ', '.join(valid_values)
			print(f'Valid values are {valid_values_str}')

	def print_missing_argument_exception(self, exception: MissingArgumentException):

		# TODO: print usage
		# exception.command.help.print_usage()

		if len(exception.missing_arguments) == 1:
			print(f'{Fore.RED}Missing one required argument{Style.RESET_ALL}')
		else:
			print(f'{Fore.RED}Missing multiple required arguments{Style.RESET_ALL}')

		for arg in exception.missing_arguments:
			print(f'  {Style.BRIGHT}{arg.display_name}{Style.RESET_ALL} (--{arg.name})')
			# TODO: the format here should be the same as the help format
			# exception.command.help.print_argument(arg)

	def print_unknown_argument_exception(self, exception: UnknownArgumentException):

		# TODO: print usage
		# exception.command.help.print_usage()

		argument_suggestions: list[Argument] = []
		command_suggestions: list[BaseCommand] = []

		if exception.unknown_argument.startswith('--'):
			print(f'{Fore.RED}Unknown argument \'{exception.unknown_argument}\'{Style.RESET_ALL}')
			argument_suggestions += self.get_argument_suggestions(exception)
		else:
			print(f'{Fore.RED}Unknown command \'{exception.unknown_argument}\'{Style.RESET_ALL}')
			command_suggestions += self.get_sub_command_suggestions(exception)

		# if there is no suggestion, nothing else to do
		if len(argument_suggestions) == 0 and len(command_suggestions) == 0:
			return
		
		print('Do you mean:')

		for arg in argument_suggestions:
			print(f'  {Style.BRIGHT}{arg.display_name}{Style.RESET_ALL} (--{arg.name})')
			# TODO: the format here should be the same as the help format
			# exception.command.help.print_argument(arg)
		
		for cmd in command_suggestions:
			print(f'  {Style.BRIGHT}{cmd.command_display_name}{Style.RESET_ALL} ({cmd.command_name})')
			# exception.command.help.print_command(arg)

	def get_argument_suggestions(self, exception: UnknownArgumentException) -> list[Argument]:
		suggestions = []

		for arg in exception.command.get_arguments():
			distance = Levenshtein.distance(exception.unknown_argument.removeprefix('--').lower(), arg.name.lower(), score_cutoff=2)
			if distance <= 2:
				suggestions.append(arg)

		return suggestions

	def get_sub_command_suggestions(self, exception: UnknownArgumentException) -> list[BaseCommand]:
		suggestions = []

		for sub_command in exception.command.get_sub_commands():

			distance = Levenshtein.distance(exception.unknown_argument.lower(), sub_command.command_name.lower(), score_cutoff=2)
			if distance <= 2:
				suggestions.append(sub_command)

		return suggestions
