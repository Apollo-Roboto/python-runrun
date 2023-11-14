
from runrun.models import BaseCommand, BaseApplication
from runrun.builtin_command import HelpCommand, VersionCommand, InfoCommand

class Command(BaseCommand):
	help = HelpCommand()

class Application(BaseApplication):
	help = HelpCommand()
	version = VersionCommand()
	info = InfoCommand()
