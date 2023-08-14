import logging
import sys
from colorama import Fore, Style

from models import Argument, Command, CommandDetails
from builtin_command import HelpCommand

logging.basicConfig(
	stream=sys.stdout,
	level=logging.INFO,
	datefmt='%Y-%m-%d %H:%M:%S',
	format='%(levelname)s [ %(asctime)s ] %(name)s : %(message)s',
)

log = logging.getLogger(__name__)

class CreateCommand(Command):

	command_details = CommandDetails(
		name='create',
		display_name='Create',
		description='Create a thing'
	)

	title = Argument[str](
		name='title',
		display_name='Title',
		short='t',
		description='The title of this thing',
		required=True,
	)

	test = Argument[str](
		name='test',
		display_name='Test',
		description='Doing some silly testing',
		required=True,
	)

	description = Argument[str](
		name='description',
		display_name='Description',
		description='Add a description to the thing',
		aliases=['desc', 'test'],
		short='d',
		required=False,
		value=''
	)

	help = HelpCommand

	def run(self):
		print(f'{Fore.BLUE}{Style.BRIGHT}{self.title.value}{Style.RESET_ALL}')
		print(f'{Fore.YELLOW}{self.description.value}{Style.RESET_ALL}')

class RootCommand(Command):

	command_details = CommandDetails(
		name='thing',
		display_name='Thing',
		description='It does things!',
	)

	create = CreateCommand
	help = HelpCommand

def main():

	# create --title 'A thing' --description 'Would you believe it? It is a thing!'
	root_cmd = RootCommand()
	create_cmd = root_cmd.create(root_cmd)
	create_cmd.title.value = 'A thing'
	create_cmd.description.value = 'Would you believe it? It is a thing!'
	# create_cmd.run()

	create_cmd.help(create_cmd).run()

	# root_cmd.run()

	# root_cmd = RootCommand()
	# print(root_cmd.get_sub_commands())


if __name__ == '__main__':
	main()
