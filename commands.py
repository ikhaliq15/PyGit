import sys
import os

import file_utils
from commits import *
from res_strs import *
from hash_utils import *

class Command:

	command_map = {
					"init": lambda: InitCommand,
					"add": lambda: AddCommand,
					"commit": lambda: CommitCommand,
					"rm": lambda: RemoveCommand,
					"log": lambda: LogCommand,
					"find": lambda: FindCommand,
				}

	def get_command(command):
		return Command.command_map[command]()

	def check_args_count(self, args):
		if self.arg_count != len(args):
			print(ErrorMessages.invalid_parameters)
			sys.exit(0)

	def require_initialized(self):
		if not file_utils.is_initialized():
			print(ErrorMessages.non_initialized_dir)
			sys.exit(0)

class InitCommand(Command):
	arg_count = 0

	def run(self, args):
		self.check_args_count(args)

		if file_utils.is_initialized():
			print(ErrorMessages.already_initialized_dir)
			sys.exit(0)

		file_utils.initialize_git_dir()

class AddCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		file = args[0]

		if not file_utils.file_exists(file):
			print(ErrorMessages.add_file_not_found)
			sys.exit(0)

		current_commit = file_utils.read_object(file_utils.read_head_file())
		if file in current_commit.blobs and current_commit.blobs[file] == hash_file(file):
			file_utils.unstage_file(file)
		else:
			file_utils.stage_file(file)

class CommitCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		commit_message = args[0]
		if commit_message == "":
			print(ErrorMessages.invalid_commit_message)
			sys.exit(0)

		current_commit = file_utils.read_object(file_utils.read_head_file())
		new_commit = Commit(msg=args[0], parent=file_utils.read_head_file())
		marked_rm_files = file_utils.get_marked_for_remove()

		for blob in current_commit.blobs:
			new_commit.blobs[blob] = current_commit.blobs[blob]

		for file in os.listdir(file_utils.get_staging_dir()):
			filename = os.fsdecode(file)
			new_commit.add_file(filename)

		for file in marked_rm_files:
			if file in new_commit.blobs:
				del new_commit.blobs[file]

		if current_commit.blobs == new_commit.blobs:
			print(ErrorMessages.no_new_changes)
			sys.exit(0)

		file_utils.clear_stage_dir()
		file_utils.clear_marked_for_remove()
		file_utils.write_commit(new_commit)
		file_utils.write_head(new_commit)

class RemoveCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		filename = args[0]

		is_staged = file_utils.is_staged(filename)
		file_utils.unstage_file(filename)

		current_commit = file_utils.read_object(file_utils.read_head_file())
		is_tracked = filename in current_commit.blobs

		if is_tracked:
			file_utils.mark_for_remove(filename)
			os.remove(filename)

		if not (is_tracked or is_staged):
			print(ErrorMessages.no_reason_to_remove)
			sys.exit(0)

class LogCommand(Command):
	arg_count = 0

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		current_commit = file_utils.read_object(file_utils.read_head_file())

		while current_commit is not Commit.empty:
			print("===")
			print(current_commit.clean_str(), end="\n")
			print("")
			current_commit = file_utils.read_object(current_commit.parent)

class FindCommand(Command):
	arg_count = 1

	def run(self, args):
		self.check_args_count(args)
		self.require_initialized()

		search_query = args[0]

		current_commit = file_utils.read_object(file_utils.read_head_file())
		found = False
		while current_commit is not Commit.empty:
			if current_commit.message == search_query:
				found = True
				print(hash_commit(current_commit))
			current_commit = file_utils.read_object(current_commit.parent)

		if not found:
			print(ErrorMessages.found_no_commits)
			sys.exit(0)


commands_list = [
					"init",
					"add",
					"commit",
					"rm",
					"log",
					# "global-log",
					"find",
					# "status",
					# "checkout",
					# "branch",
					# "rm-branch",
					# "reset",
					# "merge",
				]