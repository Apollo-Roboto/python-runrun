from typing import Union, Optional, Type
import typing

from arcommander.models import Command, Argument

class CommandParser:
	def __init__(self, command: Type[Command], parent_command: Command = None) -> None:
		self.command = command()
		self._sub_commands = self.command.get_sub_commands()
		self._arguments = self.command.get_arguments()

	def parse(self, args: Union[str, list[str]]) -> Command:
		print(f'I would parse {args}')

		# make sure it's a list
		if type(args) == str:
			args = args.strip().split()

		# if no arguments, return now
		if len(args) == 0:
			return self.command

		# check if first argument is a sub command
		sub_command = self.get_matching_sub_command(args[0])
		
		# if it is a sub command, pass it down
		if sub_command != None:
			return CommandParser(sub_command).parse(args[1:])

		# go through the arguments and find their values

		i = -1
		while(True):
			i += 1
			if i >= len(args):
				break
			arg = args[i]

			argument = self.get_matching_argument_by_name(arg)
			
			if argument == None:
				argument = self.get_matching_argument_by_position(i)
			
			# invalid argument
			if argument == None:
				raise Exception('Invalid argument name')

			# is there a value?
			value = None
			if i+1 < len(args):
				i += 1
				value = args[i]

			if value != None:
				argument.value = argument.type(value)

			print(f'ARGUMENT {argument.display_name} : {argument.value}')

		# todo are required satisfied?

		return self.command

	def get_matching_argument_by_position(self, pos: int) -> Optional[Argument]:
		pass

	def get_matching_argument_by_name(self, arg: str) -> Optional[Argument]:
		arg = arg.lower()

		if arg.startswith('--'):
			arg = arg.removeprefix('--')

			for argument in self._arguments:
				name = argument.name.lower()
				if arg == name:
					return argument
				aliases = [a.lower() for a in argument.aliases]
				if arg in aliases:
					return argument
		
		elif arg.startswith('-'):
			arg = arg.removeprefix('-')

			for argument in self._arguments:
				if arg == argument.short.lower():
					return argument
				
		return None
				
	def get_matching_sub_command(self, arg: str) -> Optional[Type[Command]]:
		arg = arg.lower()

		for sub_command in self._sub_commands:
			name = sub_command.command_details.name.lower()
			if name == arg:
				return sub_command
			aliases = [a.lower() for a in sub_command.command_details.aliases]
			if arg in aliases:
				return sub_command
		
		return None