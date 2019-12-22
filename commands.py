import sys

import file_utils
from res_strs import *

commands_list = [
					"init",
					"add",
					"commit",
					"rm",
					"log",
					"global-log",
					"find",
					"status",
					"checkout",
					"branch",
					"rm-branch",
					"reset",
					"merge",
				]

class Command:

	command_map = {
					"init": lambda: InitCommand
				}

	def get_command(command):
		return Command.command_map[command]()

	def check_args_count(self, args):
		if self.arg_count != len(args):
			print(ErrorMessages.invalid_parameters)
			sys.exit(0)

class InitCommand(Command):

	arg_count = 0

	def run(self, args):
		self.check_args_count(args)

		if file_utils.is_initialized():
			print(ErrorMessages.already_initialized_dir)
			sys.exit(0)
		file_utils.initialize_git()