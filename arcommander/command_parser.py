from typing import Union, Optional, Type
import typing
from enum import Enum
import re
import json
import inspect
from pathlib import Path

from arcommander.models import Command, Argument

class CommandParser:
	def __init__(self, command: Type[Command], parent_command: Command = None) -> None:
		self.command = command()
		self.command._parent_command = parent_command
		self._sub_commands = self.command.get_sub_commands()
		self._arguments = self.command.get_arguments()

	def parse(self, args: Union[str, list[str]]) -> Command:

		# make sure it's a list
		if type(args) == str:
			args = args.strip().split()

		print(f'I would parse {args}')

		# check if first argument is a sub command
		sub_command = None
		if len(args) > 0:
			sub_command = self.get_matching_sub_command(args[0])
		
		# if it is a sub command, pass it down
		if sub_command != None:
			return CommandParser(sub_command, parent_command=self.command).parse(args[1:])

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

				value = args[i+1]

			# boolean argument could not have a value
			if value != None and argument.type == bool and value.startswith('-'):
				value = None
			else:
				i += 1

			if value != None:
				self.set_value_to_argument(argument, value)
			elif argument.type == bool:
				argument.value = True

			print(f'ARGUMENT {argument.display_name} : {argument.value}')

		self.check_required()

		return self.command

	def check_required(self):
		for arg in self._arguments:
			if arg.required == True and arg.value is None:
				raise Exception(f'Missing required argument {arg.name}')

	def string_to_primitive_instance(self, string_value: str, t: Type) -> object:
		"""Converts a string to an instance of a given type"""

		if t == str:
			return string_value

		if t == bool:
			return string_value.lower() in ['true', 'yes', 'yup', '👍', ':)', '😊', '1', 'positive', 'ok']

		if t == int:
			return int(string_value)

		if t == float:
			return float(string_value)

		return None

	def string_to_known_instance(self, string_value: str, t: Type) -> object:
		"""Converts a string to an instance of a given type"""

		if t == Path:
			return Path(string_value)

		if t in Enum.__subclasses__():
			return t[string_value]
		
		return None
	
	def string_to_unknown_instance(self, string_value: str, t: Type) -> object:
		"""Attempts at intanciating an object from the given type"""

		#
		# the format of the value should look something like this:
		#
		# 1,2,3,4             <- only args
		# x=5,y=7             <- only kwargs
		# center,x=5,y=7      <- both args and kwargs
		#
		# they should map to the __init__ method's parameters
		#
		# center,x=5,y=7 -> Label.__init__(*['center'],**{'x':5.0,'y':7.0})
		# __init__ is defined as this: def __init__(name: str, x: float, y:float)
		# each values needs to be converted to 'center' -> str, '5' -> float, '7' -> float
		#

		args: list[object] = []
		kwargs: dict[str, object] = {}

		# split at all comma unless escaped
		args = re.split(r'(?<!\\),', string_value)

		# replace escaped comma to comma
		for i, arg in enumerate(args):
			args[i] = arg.replace('\,', ',')

		# find the keyword arguments
		for arg in args[:]:

			# split at equal unless escaped
			key_value = re.split(r'(?<!\\)=', arg, maxsplit=1)

			# if it did split, it's a keyword argument
			if len(key_value) > 1:

				# replace escaped equals to equals
				key_value[0] = key_value[0].replace('\=', '=')
				key_value[1] = key_value[1].replace('\=', '=')

				# keyword argument should not be in the args list
				args.remove(arg)

				kwargs[key_value[0]] = key_value[1]

		# this part is to convert the argument to the expected type

		init_signature = inspect.signature(t.__init__)

		# convert the keyword arguments
		for key, value in kwargs.items():

			# skip if in the parameters
			if key not in init_signature.parameters:
				continue

			parameter = init_signature.parameters[key]
			
			# convert the keyword argument using the parameter type

			instanced_value = self.string_to_primitive_instance(value, parameter.annotation)

			if instanced_value == None:
				instanced_value = self.string_to_known_instance(value, parameter.annotation)

			kwargs[key] = instanced_value

		parameters = list(init_signature.parameters.values())

		# convert the arguments
		for i, value in enumerate(args):

			# if there are more arguments than parameters, break. (+1 to skip the self param)
			if i+1 >= len(init_signature.parameters):
				break

			parameter = parameters[i+1]

			# convert the keyword argument using the parameter type
			instanced_value = self.string_to_primitive_instance(value, parameter.annotation)

			if instanced_value == None:
				instanced_value = self.string_to_known_instance(value, parameter.annotation)

			args[i] = instanced_value

		return t(*args, **kwargs)

	def set_value_to_argument(self, argument: Argument, value: str):

		argument.value = self.string_to_primitive_instance(value, argument.type)

		if argument.value != None:
			return
		
		argument.value = self.string_to_known_instance(value, argument.type)

		if argument.value != None:
			return
		
		argument.value = self.string_to_unknown_instance(value, argument.type)

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
				if argument.short != None and arg == argument.short.lower():
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