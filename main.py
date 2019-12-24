import sys

import commands
from res_strs import *

if __name__ == "__main__" :
	args = sys.argv[1:]
	if len(args) < 1:
		print(ErrorMessages.no_command)
		sys.exit(0)

	command = args[0]
	if command not in commands.Command.command_map:
		print(ErrorMessages.non_existing_command)
		sys.exit(0)

	command_obj = commands.Command.get_command(command)()
	command_obj.run(args[1:])