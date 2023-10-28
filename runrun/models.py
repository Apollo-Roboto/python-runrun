from typing import TypeVar, Generic, Optional, Callable, Type
import typing
from dataclasses import dataclass, field
import inspect
import copy

T = TypeVar('T')

class Argument(Generic[T]):

	def __init__(self, *,
		name: str,
		display_name: str,
		description: str,
		required: bool = False,
		aliases: list[str] = [],
		short: Optional[str] = None,
		value: Optional[T] = None,
		position: Optional[int] = None,
		# str_to_type: Optional[Callable[[str], T]] = None,
	) -> None:

		self.name = name
		self.display_name = display_name
		self.description = description
		self.required = required
		self.aliases = aliases
		self.short = short
		self.value = value
		self.position = position

		# self.str_to_type = str_to_type

		self._type: Optional[Type[T]] = None

	@property
	def type(self) -> Type[T]:
		if self._type == None:
			# pylint: disable=E1101
			self._type = typing.get_args(self.__orig_class__)[0] # type: ignore
			# pylint: enable=E1101
		return self._type # type: ignore

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, self.__class__):
			return False

		return self.value == other.value

	def __str__(self):
		return str(self.value)

class CommandDetails:

	def __init__(self, *,
		name: str,
		display_name: str,
		description: str,
		aliases: list[str] = [],
		# examples: list[str] = [],
	):
		self.name = name
		self.display_name = display_name
		self.description = description
		self.aliases = aliases
		# self.examples = examples

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, self.__class__):
			return False
		return (
			self.name == other.name and
			self.display_name == other.display_name and
			self.description == other.description and
			self.aliases == other.aliases
		)

class Command:

	command_details: Optional[CommandDetails] = None

	def __init__(self):
		# instanciate all arguments at the instance level
		for key, value in inspect.getmembers(self):

			if type(value) is Argument:
				setattr(self, key, copy.deepcopy(value))

		self.context = Context()

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, self.__class__):
			return False
		if self.command_details != other.command_details:
			return False
		
		return self.get_arguments() == other.get_arguments()

	def __repr__(self) -> str:
		arguments = ','.join([ f'{a.name}:{a.value}' for a in self.get_arguments()])
		sub_commands = ','.join([ f'{a.command_details.name}' for a in self.get_sub_commands()])
		return f'{self.__class__.__name__}(name={self.command_details.name}, args={arguments}, sub_cmd={sub_commands})'

	def run(self):
		help = getattr(self, 'help')
		if help in Command.__subclasses__():
			help(self).run()

	def get_sub_commands(self) -> list['Command']:
		sub_commands = []

		for key, value in inspect.getmembers(self):

			if isinstance(value, Command):
				sub_commands.append(value)

		return sub_commands
	
	def get_arguments(self) -> list[Argument]:
		arguments = []

		for key, value in inspect.getmembers(self):

			if type(value) is Argument:
				arguments.append(value)

		return arguments

class Context:
	# application: Application
	def __init__(self,
		root_command: Optional[Command] = None,
		original_arguments: list[str] = [],
		scoped_arguments: list[str] = [],
		parent_command: Optional[Command] = None,
	) -> None:
		self.root_command = root_command
		self.original_arguments = original_arguments
		self.scoped_arguments = scoped_arguments
		self.parent_command = parent_command

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		return (
			self.root_command == other.root_command and
			self.original_arguments == other.original_arguments and
			self.scoped_arguments == other.scoped_arguments and
			self.parent_command == other.parent_command
		)
