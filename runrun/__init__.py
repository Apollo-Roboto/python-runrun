
from runrun.models import BaseCommand
from runrun.builtin_command import HelpCommand

class Command(BaseCommand):
	help = HelpCommand()
