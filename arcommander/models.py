from typing import TypeVar, Generic, Optional, Callable, Type
from dataclasses import dataclass, field
import inspect


T = TypeVar('T')

@dataclass(kw_only=True)
class Argument(Generic[T]):
	name: str
	display_name: str
	description: str
	required: bool
	aliases: list[str] = field(default_factory=list)
	short: Optional[str] = None
	value: Optional[T] = None
	
	# position: Optional[int] = None

@dataclass
class CommandDetails:
	name: str
	display_name: str
	description: str
	aliases: list[str] = field(default_factory=list)

@dataclass(kw_only=True, init=False)
class Command:

	command_details: CommandDetails
	_parent_command: Optional['Command'] = None

	def __init__(self, parent_command: Optional['Command'] = None):
		self._parent_command = parent_command

	def run(self):
		help = getattr(self, 'help')
		if help in Command.__subclasses__():
			help(self).run()

	def get_sub_commands(self) -> list['Command']:
		sub_commands = []

		for key, value in inspect.getmembers(self):
			if key == '__class__':
				continue

			if value in Command.__subclasses__():
				sub_commands.append(value)

		return sub_commands
	
	def get_arguments(self) -> list[Argument]:
		arguments = []

		for key, value in inspect.getmembers(self):

			if type(value) is Argument:
				arguments.append(value)

		return arguments
	
	def get_full_command_display_name(self) -> str:
		if self._parent_command == None:
			return self.command_details.display_name

		return self._parent_command.get_full_command_display_name() + " " + self.command_details.display_name
	
	def get_full_command_name(self) -> str:
		if self._parent_command == None:
			return self.command_details.name

		return self._parent_command.get_full_command_name() + " " + self.command_details.name
