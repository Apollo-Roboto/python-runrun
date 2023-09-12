import sys
import requests
import json

from arcommander.models import Command, CommandDetails, Argument
from arcommander.command_parser import CommandParser
from arcommander.builtin_command import HelpCommand2
from arcommander.exceptions import CLIException, DefaultExceptionHandler

BASE_URL = 'https://api.spacetraders.io/v2/'

class StatusCommand(Command):
	command_details = CommandDetails(
		name='status',
		display_name='Status',
		description='Check status',
	)

	help = HelpCommand2()

	def run(self):
		res = requests.get(BASE_URL)
		if not res.ok:
			raise Exception('Did not reply with 200')

		data = json.loads(res.content)
		print(json.dumps(data, indent='  '))

class RegisterCommand(Command):
	command_details = CommandDetails(
		name='register',
		display_name='Register',
		description='Register a new agent',
	)

	symbol = Argument[str](
		name='symbol',
		display_name='Symbol',
		description='',
		required=True,
	)

	faction = Argument[str](
		name='faction',
		display_name='Faction',
		description='',
		required=True
	)

	help = HelpCommand2()

	def run(self):
		body = {
			'symbol': self.symbol.value,
			'faction': self.faction.value,
		}
		res = requests.post(BASE_URL + 'register', json=body)
		if not res.ok:
			print(res.content)
			raise Exception(f'Did not reply with 200, was {res.status_code}')
		
		data = json.loads(res.content)
		print(json.dumps(data, indent='  '))

class FactionCommand(Command):
	command_details = CommandDetails(
		name='faction',
		display_name='Faction',
		description='Faction stuff',
	)

	token = Argument[str](
		name='token',
		display_name='Token',
		description='Authorization token',
		required=True,
	)

	def run(self):
		res = requests.get(BASE_URL + 'factions')
		if not res.ok:
			print(res.content)
			raise Exception(f'Did not reply with 200, was {res.status_code}')

		data = json.loads(res.content)
		print(json.dumps(data, indent='  '))

class RootCommand(Command):
	command_details = CommandDetails(
		name='startrader',
		display_name='Space Traders',
		description='A command line interface for Space Traders',
		aliases=['st']
	)

	help = HelpCommand2()
	status = StatusCommand()
	register = RegisterCommand()
	faction = FactionCommand()

	def run(self):
		# self.help.run()
		pass



if __name__ == '__main__':
	try:
		cmd = CommandParser(RootCommand()).parse(['help'])
		# cmd = CommandParser(RootCommand()).parse(sys.argv[1:])
	
		cmd.run()
	except CLIException as e:
		DefaultExceptionHandler().handle_exception(e)

	# CommandRunner(RootCommand())