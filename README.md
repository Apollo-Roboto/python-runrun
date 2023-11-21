# Run Run

A typed command line parser for Python.

## Example

```py
# main.py
import random
from runrun import Command
from runrun.models import Argument
from runrun.runner import Runner

class RollCommand(Command):
	def __init__(self):
		super().__init__(
			name='roll',
			description='Roll a dice',
		)
	
	num_of_dice = Argument[int](
		name='num',
		description='Number of dice to roll',
		value=1,
	)

	faces = Argument[int](
		name='faces',
		description='how many faces per dice',
		value=6,
	)

	def run(self):
		total = 0
		for _ in range(self.num_of_dice.value):
			total += random.randint(1, self.faces.value)
		
		print(f'🎲 {total}')

Runner(RollCommand()).run()
```

Run it!
```powershell
python .\main.py --num 5 --faces 20
```

Or check the generated help command.
```powershell
python .\main.py help
```

```txt

  Roll a dice

 USAGE 
  roll [arguments]

 ARGUMENTS 
  faces             --faces <int>                              | how many faces per dice
  num               --num <int>                                | Number of dice to roll

 COMMANDS 
  Help              help                                       | Show help about this command

```

The help command has it's own help docs !?
```powershell
python .\main.py help help
```

```txt

  Show help about this command

 USAGE 
  roll help [arguments]

 ARGUMENTS 
  Filter            --filter <str>                             | Filter the help results, this can help to find what you are looking for
  Output Format     --format {STD, JSON}                       | The output format of the command details
  Required Only     --required-only [true|false]               | Only show required arguments

 COMMANDS 
  Help              help                                       | Show help about this command
```

*Finally a help that can be filtered*
