from typing import Union, Optional, Type
import typing
from enum import Enum
import re
import json
import inspect
from pathlib import Path

from arcommander.models import Command, Argument, Context
from arcommander.exceptions import ParserException, ValidationException

class CommandParser:
	def __init__(self, command: Command, parent_command: Command = None, context: Context = None) -> None:
		self.command = command
		# self.command._parent_command = parent_command
		self._sub_commands = self.command.get_sub_commands()
		self._arguments = self.command.get_arguments()

		# create context if not given
		self.command.context = context
		if self.command.context == None:
			self.command.context = Context()

		# set the parent command
		self.command.context.parent_command = parent_command

		# set the root command
		if self.command.context.root_command == None:
			self.command.context.root_command = command

		self.validate_command()

	def validate_command(self):

		# command contains a command_details
		if self.command.command_details is None:
			raise ValidationException('A command must define the command_details attribute')

		# validate positions are in order and not duplicated
		counter = 0

		positional_arguments = filter(lambda x: x.position != None, self._arguments)
		positional_arguments = sorted(positional_arguments, key=lambda x: x.position)

		for arg in positional_arguments:
			if arg.position == counter:
				counter += 1
			else:
				raise ValidationException('Positions must be incremental and unique, starting from 0')

	def parse(self, args: Union[str, list[str]]) -> Command:

		# make sure it's a list
		if type(args) == str:
			args = args.strip().split()

		print(f'I would parse {args}')

		# if never set before, set the arguments
		if self.command.context.original_arguments == None:
			self.command.context.original_arguments = args

		# check if first argument is a sub command
		sub_command = None
		if len(args) > 0:
			sub_command = self.get_matching_sub_command(args[0])

		# if it is a sub command, pass it down
		if sub_command != None:
			return CommandParser(sub_command, parent_command=self.command, context=self.command.context).parse(args[1:])

		# set the scoped argumetns for this command
		self.command.context.scoped_arguments = args

		# go through the arguments and find their values

		positional_i = 0 # track the number of the positional
		i = -1
		while(True):
			i += 1
			if i >= len(args):
				break
			arg = args[i]

			argument = self.get_matching_argument_by_name(arg)

			if argument == None:
				argument = self.get_matching_argument_by_position(positional_i)

			# invalid argument
			if argument == None:
				raise ParserException(f'Invalid argument name \'{arg}\'')

			is_positional = argument.position != None
			if is_positional:
				positional_i += 1

			# is there a value?
			value = None
			if not is_positional and i+1 < len(args):
				value = args[i+1]
			elif is_positional:
				value = arg

			# boolean argument could not have a value
			if value != None and argument.type == bool and value.startswith('-'):
				value = None
			elif not is_positional:
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
				raise ParserException(f'Missing required argument {arg.name}')

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
			# get value ignoring case
			for member in t.__members__.keys():
				if member.lower() == string_value.lower():
					return t[member]
		
		return None
	
	def string_to_unknown_instance(self, string_value: str, t: Type) -> object:
		"""Attempts at instanciating an object of the given class from a string of arguments"""

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
	
	def string_to_list_instance(self, string_value: str, t: list[type]) -> list[object]:
		# split at all comma unless escaped
		args = re.split(r'(?<!\\),', string_value)

		# get type (default to str if not there)
		type = str
		if len(typing.get_args(t)) > 0:
			type = typing.get_args(t)[0]

		for i, arg in enumerate(args):
			# replace escaped comma to comma
			arg = arg.replace('\,', ',')

			args[i] = self.string_to_primitive_instance(arg, type)

			if args[i] != None:
				continue

			args[i] = self.string_to_known_instance(arg, type)

		return args

	def string_to_dict_instance(self, string_value: str, t: dict[str, type]) -> dict[str, type]:

		kwargs = {}

		# split at all comma unless escaped
		args = re.split(r'(?<!\\),', string_value)

		# get type of the key (default to str if not there)
		key_type = str
		if len(typing.get_args(t)) > 0:
			key_type = typing.get_args(t)[0]

		# get type of the value (default to str if not there)
		value_type = str
		if len(typing.get_args(t)) > 1:
			value_type = typing.get_args(t)[1]

		for i, arg in enumerate(args):
			# replace escaped comma to comma
			arg = arg.replace('\,', ',')
			
			# split at equal unless escaped
			key_value = re.split(r'(?<!\\)=', arg, maxsplit=1)

			# if it did split, it's a keyword argument
			if len(key_value) > 1:

				# replace escaped equals to equals
				key = key_value[0].replace('\=', '=')
				value = key_value[1].replace('\=', '=')
			
			# otherwise it's not valid
			else:
				pass
			
			key_value[0] = self.string_to_primitive_instance(key, key_type)
			if key_value[0] == None:
				key_value[0] = self.string_to_known_instance(key, key_type)

			key_value[1] = self.string_to_primitive_instance(value, value_type)
			if key_value[1] == None:
				key_value[1] = self.string_to_known_instance(value, value_type)

			kwargs.update({key_value[0]:key_value[1]})

		return kwargs

	def set_value_to_argument(self, argument: Argument, value: str):

		# handle lists
		if typing.get_origin(argument.type) == list:
			argument.value = self.string_to_list_instance(value, argument.type)
			return
		
		# handle dicts
		if typing.get_origin(argument.type) == dict:
			argument.value = self.string_to_dict_instance(value, argument.type)
			return

		argument.value = self.string_to_primitive_instance(value, argument.type)

		if argument.value != None:
			return

		argument.value = self.string_to_known_instance(value, argument.type)

		if argument.value != None:
			return

		argument.value = self.string_to_unknown_instance(value, argument.type)

	def get_matching_argument_by_position(self, pos: int) -> Optional[Argument]:
		for arg in self._arguments:
			if arg.position == pos:
				return arg

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
				
	def get_matching_sub_command(self, arg: str) -> Optional[Command]:
		arg = arg.lower()

		for sub_command in self._sub_commands:
			name = sub_command.command_details.name.lower()
			if name == arg:
				return sub_command
			aliases = [a.lower() for a in sub_command.command_details.aliases]
			if arg in aliases:
				return sub_command
		
		return None
