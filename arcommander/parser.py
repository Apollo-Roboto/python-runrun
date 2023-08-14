from typing import Union

class Parser:
	def __init__(self, command) -> None:
		self.command = command

	def parse(self, args: Union[str, list[str]]):
		print(f'I would parse {args}')
