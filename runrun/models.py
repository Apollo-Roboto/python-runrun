from typing import TypeVar, Generic, Optional, Union
import typing
import inspect
import copy

T = TypeVar('T')

class Argument(Generic[T]):

	def __init__(self,
		t: type[T],
		name: str,
		*,
		display_name: str | None = None,
		description: str = '',
		aliases: list[str] = [],
		short: Optional[str] = None,
		default_value: T = None, # type: ignore
		position: Optional[int] = None,
		required: bool = True,
		# str_to_type: Optional[Callable[[str], T]] = None,
	) -> None:

		self.type = t

		if display_name is None:
			display_name = name

		self.name = name
		self.display_name = display_name
		self.description = description
		
		self.aliases = aliases
		self.short = short
		self.position = position

		if default_value is not None:
			self.default_value: T = default_value
			self.required = False
			self._value: T = default_value
		else:
			self.required = required

			# value will be populated later
			self._value: T = None # type: ignore

		# self.str_to_type = str_to_type



	@property
	def value(self) -> T:
		if self._value is None:
			raise Exception('_value was never set')
		return self._value
	
	@value.setter
	def value(self, value: T):
		if value is None:
			raise Exception('value cannot be None')
		self._value = value

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, self.__class__):
			return False

		return self._value == other._value

	def __str__(self):
		return str(self.value)

class BaseCommand:

	# command_details: Optional[CommandDetails] = None

	def __init__(self,
		name: str,
		display_name: str | None = None,
		description: str = '',
		aliases: list[str] = []
	):

		# diplay name defaults to name
		if not display_name:
			display_name = name

		self.command_name = name
		self.command_display_name = display_name
		self.command_description = description
		self.command_aliases = aliases

		# instanciate all arguments at the instance level
		for key, value in inspect.getmembers(self):

			if type(value) is Argument:
				setattr(self, key, copy.deepcopy(value))

		self.context = Context()

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, self.__class__):
			return False
		if (
			self.command_name != other.command_name or
			self.command_display_name != other.command_display_name or
			self.command_description != other.command_description or
			self.command_aliases != other.command_aliases
		):
			return False
		
		return self.get_arguments() == other.get_arguments()

	def __repr__(self) -> str:
		arguments = ','.join([ f'{a.name}:{a.value}' for a in self.get_arguments()])
		sub_commands = ','.join([ f'{a.command_name}' for a in self.get_sub_commands()])
		return f'{self.__class__.__name__}(name={self.command_name}, args={arguments}, sub_cmd={sub_commands})'

	def run(self):
		help = getattr(self, 'help')
		if help in BaseCommand.__subclasses__():
			help(self).run()

	def get_sub_commands(self) -> list['BaseCommand']:
		sub_commands = []

		for key, value in inspect.getmembers(self):

			if isinstance(value, BaseCommand):
				sub_commands.append(value)

		return sub_commands
	
	def get_arguments(self) -> list[Argument]:
		arguments = []

		for key, value in inspect.getmembers(self):

			if type(value) is Argument:
				arguments.append(value)

		return arguments

class BaseApplication(BaseCommand):

	def __init__(self,
		name: str,
		version: str = '',
		author: str = '',
		website: str = '',
		copyright: str = '',
		display_name: str | None = None,
		description: str = '',
	):
		super().__init__(name, display_name, description, [])
		self.application_version = version
		self.application_author = author
		self.application_website = website
		self.application_copyright = copyright

class Context:
	# application: Application
	def __init__(self,
		root_command: Optional[BaseCommand] = None,
		original_arguments: list[str] = [],
		scoped_arguments: list[str] = [],
		parent_command: Optional[BaseCommand] = None,
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
